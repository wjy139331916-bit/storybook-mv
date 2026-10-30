#!/usr/bin/env python3
"""Build local artifact reviews and truthful handoffs. Never invent user consent."""
import argparse
import base64
import copy
import html
import json
import math
import mimetypes
from pathlib import Path
import re
import subprocess
import sys

from input_contracts import content_digest, sha
from workflow_gate import NEXT, default_workflow, design_digest, inspect_package, local_file, read_json, target_duration, workflow_errors

LABELS = {'design':'设计与完整脚本', 'prototype':'限定样片', 'animatic':'全曲粗剪', 'full':'精细制作'}
PURPOSE = {'design':'prototype', 'prototype':'animatic', 'animatic':'production'}


def inside(project, value, exists=True):
    path = Path(value)
    path = path if path.is_absolute() else project/path
    path = path.absolute()
    try:
        rel = path.relative_to(project)
    except ValueError:
        raise ValueError('review artifacts must stay inside the project')
    if '..' in rel.parts or any(p.is_symlink() for p in [path,*path.parents] if p == project or project in p.parents):
        raise ValueError('resolve review paths and symlinks explicitly')
    if exists and not path.is_file():
        raise ValueError('missing review artifact: '+str(rel))
    return path


def binding(project, value, role=None):
    path = inside(project,value)
    result = {'path':path.relative_to(project).as_posix(), 'sha256':sha(path)}
    if role:result['role']=role
    return result


def write_json(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+'.tmp')
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    temp.replace(path)


def status(project, brief=None):
    brief=brief or read_json(project/'brief.json')
    from check_brief import entry_errors
    draft=copy.deepcopy(brief);draft['phase']='design'
    direction_errors=entry_errors(draft,project,'design',operation='check')
    allowed='discovery' if direction_errors else 'design'
    stages=[];notes=[]
    for stage in NEXT:
        errors=workflow_errors(brief,project,PURPOSE[stage])
        flow=brief.get('workflow') or {}
        record=(flow.get('packages') or {}).get(stage)
        package_errors=[]
        package=inspect_package(brief,project,stage,record,package_errors) if record else None
        accepted=bool(record) and not errors
        if package:notes.extend(package.get('limits') or [])
        stages.append({'stage':stage,'label':LABELS[stage],'revision':(package or {}).get('revision'),
                       'presented':bool(package) and not package_errors,'accepted':accepted,
                       'package':record,'approval':(flow.get('approvals') or {}).get(stage),
                       'problems':errors if record else ['尚未形成该阶段的完整稿件']})
        if accepted and allowed==stage:allowed=NEXT[stage]
    execution_errors=[]
    if allowed in LABELS:
        draft=copy.deepcopy(brief);draft['phase']=allowed
        execution_errors=entry_errors(draft,project,'production' if allowed=='full' else allowed,operation='check')
    issues=[]
    if (project/'review.json').is_file():
        issues=[x for x in read_json(project/'review.json').get('issues',[]) if x.get('status')!='resolved']
    return {'schema_version':1,'phase':brief.get('phase'),'user_authorized_stage':allowed,'stages':stages,
            'pending_issues':issues,'pending_notes':list(dict.fromkeys(notes)),'execution_problems':direction_errors+execution_errors,
            'scope':'Derived from current artifacts and recorded real decisions; does not authenticate messages or grant new acceptance.'}


def save_status(project, brief=None):
    data=status(project,brief)
    lines=['# 项目状态','', '当前工作：'+LABELS.get(data['phase'],str(data['phase'])),
           '使用者已允许进入：'+LABELS.get(data['user_authorized_stage'],'继续澄清方向'),'',
           '| 阶段 | 稿件版本 | 使用者验收 |','|---|---|---|']
    for stage in data['stages']:
        lines.append('| '+stage['label']+' | '+str(stage['revision'] or '尚无完整稿件').replace('|','\\|')+' | '+('已确认' if stage['accepted'] else '待确认／需更新')+' |')
    lines += ['', '## 待修改事项','']+[ '- '+str(x.get('id',''))+': '+str(x.get('observation','待检查')) for x in data['pending_issues']]
    if not data['pending_issues']:lines.append('没有已记录的未解决事项；不代表作品无需审片。')
    lines += ['','## 已知不足','']+['- '+str(x) for x in data['pending_notes']]
    lines += ['', '## 交接','', '复用已确认方向和上述稿件；先核对当前文件及真实回复，再执行允许的下一阶段。',
              '技术检查失败时先修复对应问题；不得自行填写验收通过。']
    write_json(project/'plan/status.json',data)
    (project/'plan/STATUS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return data


def inspect_video(project, brief, video, stage, bounds, out):
    video=inside(project,video)
    if not all(isinstance(t,(int,float)) and math.isfinite(t) for t in bounds) or not 0<=bounds[0]<bounds[1]:
        raise ValueError('provide the actual source interval as --range START:END')
    media=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)],stderr=subprocess.PIPE))
    stream=next((s for s in media.get('streams',[]) if s.get('codec_type')=='video'),None)
    if not stream:raise ValueError('review target needs an encoded video')
    measured=float(stream.get('duration') or media['format']['duration'])
    if abs(measured-(bounds[1]-bounds[0]))>.125:raise ValueError('source interval differs from actual video duration')
    subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],check=True,capture_output=True)
    audio=None;comparison=None
    music=brief.get('music') or {}
    if music.get('audio'):
        source=inside(project,music['audio'])
        if sha(source)!=music.get('audio_sha256'):raise ValueError('selected audio changed; resolve the input first')
        if not any(s.get('codec_type')=='audio' for s in media['streams']):raise ValueError('selected soundtrack is missing')
        audio=binding(project,source)
        # Measure the actual streams. Ambiguous/silent/repetitive comparisons
        # remain candidates and never become sung-word or listening approval.
        from media_audit import audio_audit
        comparison_dir=out.parent/(out.stem+'-audio')
        comparison_dir.mkdir(parents=True,exist_ok=False)
        try:
            comparison=audio_audit(source,video,comparison_dir,bounds[0])
        except ValueError as exc:
            comparison={'status':'unverified','reason':str(exc)}
    report={'schema_version':1,'status':'passed','production_stage':stage,'range':bounds,
            'duration':measured,'width':stream['width'],'height':stream['height'],'audio':audio,
            'encoded':{'full_decode':True,'audio':any(s.get('codec_type')=='audio' for s in media['streams'])},
            'artifacts':[binding(project,video)],'audio_comparison':comparison,
            'scope':'Actual probe/decode and optional soundtrack comparison; source range is retained from the actual render command, not inferred from pixels. No acting, taste or sung-word approval.'}
    write_json(out,report)
    return report


def data_url(path):
    mime=mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
    return 'data:'+mime+';base64,'+base64.b64encode(path.read_bytes()).decode('ascii')


def create_preview(project, video, target):
    """Create a same-timeline WebM alternative; preserve and identify the master."""
    source=inside(project,video);target=inside(project,target,False)
    if target.exists():raise ValueError('preserve the earlier preview revision')
    subprocess.run(['ffmpeg','-y','-v','error','-i',str(source),'-map','0:v:0','-map','0:a?',
                    '-c:v','libvpx-vp9','-deadline','realtime','-cpu-used','8','-b:v','0','-crf','28',
                    '-c:a','libopus','-b:a','96k',str(target)],check=True,capture_output=True)
    subprocess.run(['ffmpeg','-v','error','-i',str(target),'-f','null','-'],check=True,capture_output=True)
    def media(path):
        d=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)]))
        v=next(s for s in d['streams'] if s.get('codec_type')=='video')
        return d,v
    a,av=media(source);b,bv=media(target)
    if [av['width'],av['height']]!=[bv['width'],bv['height']] or abs(float(a['format']['duration'])-float(b['format']['duration']))>.125 or any(s.get('codec_type')=='audio' for s in a['streams']) != any(s.get('codec_type')=='audio' for s in b['streams']):
        raise ValueError('compatibility preview changed dimensions, duration or soundtrack presence')
    result=binding(project,target,'video_preview');result['source_sha256']=sha(source)
    return result


def review_html(project, package, package_record, limits, max_bytes):
    artifacts=package['artifacts'];used=sum(4*(((project/a['path']).stat().st_size+2)//3) for a in artifacts if a['role'] in ('design_frame','video','video_preview'))
    if used>max_bytes:raise ValueError('embedded review exceeds the selected byte budget; choose a smaller rough export or explicitly raise --max-embed-mb')
    esc=lambda v:html.escape(str(v),quote=True)
    stage=package['stage'];parts=[];clip=None
    for a in artifacts:
        path=project/a['path'];role=a['role']
        if role=='proposal':
            parts.append('<section><h2>整体方案</h2><pre>'+esc(path.read_text(encoding='utf-8'))+'</pre></section>')
        elif role=='script':
            script=read_json(path)
            rows=''.join('<tr>'+''.join('<td>'+esc(v)+'</td>' for v in (str(s['start'])+'–'+str(s['end'])+'秒',s.get('visual',''),s.get('visible_change',''),s.get('lyric_treatment',''),s.get('transition',{}).get('type','')))+'</tr>' for s in script.get('shots',[]))
            parts.append('<section><h2>完整分镜脚本</h2><div class="table"><table><thead><tr><th>时间</th><th>画面</th><th>变化</th><th>歌词</th><th>转场</th></tr></thead><tbody>'+rows+'</tbody></table></div></section>')
        elif role=='design_frame':parts.append('<figure><img src="'+data_url(path)+'" alt="设计图 '+esc(path.stem)+'"><figcaption>'+esc(path.stem)+'</figcaption></figure>')
        elif role=='video':
            clip=a
            preview=next((x for x in artifacts if x['role']=='video_preview' and x.get('source_sha256')==a['sha256']),None)
            sources=('<source src="'+data_url(project/preview['path'])+'" type="video/webm">') if preview else ''
            sources+='<source data-original="true" src="'+data_url(path)+'" type="'+html.escape(mimetypes.guess_type(path.name)[0] or 'video/mp4')+'">'
            parts.append('<section><h2>实际视频</h2><video id="clip" controls preload="auto">'+sources+'</video><p id="playback-error" hidden>当前浏览器无法播放此预览。请下载视频查看，或请制作 agent 提供兼容预览。</p><a id="download-original" download="'+esc(path.name)+'">下载原视频</a><p>观看后可记录具体时间点的问题；这些意见不会自动成为验收。</p><label>意见 <input id="note" placeholder="例如：转场后字幕来不及读"></label><button id="add">记录当前时间</button><ol id="notes"></ol><button id="export">导出时间点意见</button></section>')
        elif role=='review':
            review=read_json(path)
            parts.append('<section><h2>实际检查与已知不足</h2><pre>'+esc(review.get('observations') or review.get('issues') or '请结合下面的已知不足审片。')+'</pre></section>')
    next_label=LABELS[NEXT[stage]]
    clip_duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(project/clip['path'])],stderr=subprocess.PIPE,text=True, encoding='utf-8')) if clip else None
    feedback={'schema_version':1,'kind':'timestamp-feedback','package_sha256':package_record['sha256'],
              'revision':package['revision'],'target_sha256':clip['sha256'] if clip else None,
              'target':{'path':clip['path'],'sha256':clip['sha256'],'duration':clip_duration} if clip else None,'notes':[],'is_user_approval':False}
    script='''const feedback=FEEDBACK;
const video=document.getElementById('clip');
if(video){
  document.getElementById('download-original').href=video.querySelector('source[data-original]').src;
  video.addEventListener('error',()=>document.getElementById('playback-error').hidden=false);
  document.getElementById('add').onclick=()=>{
    const input=document.getElementById('note');if(!input.value.trim()||video.readyState<2||!Number.isFinite(video.duration))return;
    const end=Math.min(video.duration,feedback.target.duration);
    const start=Math.min(Math.round(video.currentTime*1000)/1000,Math.max(0,end-.25));
    const note={id:'viewer-'+Date.now().toString(36)+'-'+feedback.notes.length,range:[start,Math.min(end,start+.25)],severity:'minor',observation:input.value.trim()};
    feedback.notes.push(note);const li=document.createElement('li');li.textContent=note.range[0]+'秒：'+note.observation;document.getElementById('notes').append(li);input.value='';
  };
  document.getElementById('export').onclick=()=>{const url=URL.createObjectURL(new Blob([JSON.stringify(feedback,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='video-feedback.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
}'''.replace('FEEDBACK',json.dumps(feedback,ensure_ascii=True).replace('<','\\u003c'))
    return '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(LABELS[stage]+' · '+package['revision'])+'</title><style>body{margin:0;background:#f5f3ef;color:#202522;font:16px/1.7 system-ui,sans-serif}main{max-width:1100px;margin:auto;padding:28px 18px}header,section,figure,aside{margin:0 0 24px;padding:22px;background:white;border-radius:16px}h1{font-size:28px}h2{font-size:21px}img,video{max-width:100%;display:block;margin:auto;border-radius:8px}pre{white-space:pre-wrap;font:inherit}table{border-collapse:collapse;min-width:650px;width:100%}th,td{padding:12px;text-align:left;border-bottom:1px solid #ddd}.table{overflow:auto}aside{border-left:5px solid #688c74}input{font:inherit;padding:8px;width:min(70%,600px)}button{font:inherit;padding:9px 14px;margin:8px;border:0;border-radius:8px;background:#315e49;color:#fff}small{color:#59645d}</style><main><header><small>作品审阅 · '+esc(LABELS[stage])+'</small><h1>'+esc(package['revision'])+'</h1><p>本次请审阅本页展示的完整稿件。确认后仅进入：<strong>'+esc(next_label)+'</strong>。</p><p>请把接受或修改意见回复给制作 agent。本页不会自行确认或启动制作。</p></header><aside><strong>已知不足与待定事项</strong><ul>'+''.join('<li>'+esc(x)+'</li>' for x in limits)+'</ul></aside>'+''.join(parts)+'<footer>审片意见、AI 自检与使用者验收分别保存。新阶段的稿件需要单独展示。</footer></main><script>'+script+'</script></html>'


def present(project, brief, args):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,70}',args.revision):raise ValueError('use a short stable revision such as design-r1')
    stage=args.stage;draft=copy.deepcopy(brief);draft['phase']=stage
    from check_brief import entry_errors
    blocked=entry_errors(draft,project,stage,operation='check')
    if blocked:raise ValueError('; '.join(blocked))
    folder=project/'plan/reviews'/stage/args.revision
    if folder.exists():raise ValueError('review revision already exists; preserve it and choose a new revision')
    pairs=[('proposal',args.proposal),('script',args.script),('visual_spec',args.visual_spec)] if stage=='design' else [('video',args.video),('render_report',args.render_report),('review',args.review)]
    pairs += [('design_frame',f) for f in args.frame]
    sources=getattr(args,'source',[]) or []
    if sources and stage!='design':raise ValueError('design sources belong to the design presentation')
    pairs += [('design_source',f) for f in sources]
    if any(v is None for _,v in pairs):raise ValueError('provide all actual artifacts for the selected stage')
    data={'stage':stage,'revision':args.revision,'content_sha256':content_digest(brief),'design_sha256':design_digest(brief),
          'target_duration':target_duration(brief,project),'artifacts':[binding(project,v,k) for k,v in pairs],
          'limits':args.limit}
    if stage=='design':
        if not args.pilot_range or not args.objective:raise ValueError('design needs --pilot-range START:END and --objective')
        a,b=map(float,args.pilot_range.split(':'));data['pilot']={'start':a,'end':b,'objectives':args.objective}
    else:
        data['design_package_sha256']=brief['workflow']['packages']['design']['sha256']
        if stage=='animatic':data.update(fidelity='rough',prototype_package_sha256=brief['workflow']['packages']['prototype']['sha256'])
    folder.mkdir(parents=True)
    if args.webm_preview and stage!='design':
        source=next(x for x in data['artifacts'] if x['role']=='video')
        data['artifacts'].append(create_preview(project,source['path'],folder/'preview.webm'))
    package_path=folder/'package.json';write_json(package_path,data)
    candidate=copy.deepcopy(brief);candidate['phase']=stage;candidate.setdefault('workflow',default_workflow())['packages'][stage]=binding(project,package_path)
    errors=[];inspect_package(candidate,project,stage,candidate['workflow']['packages'][stage],errors)
    if errors:
        package_path.unlink();(folder/'preview.webm').unlink(missing_ok=True);folder.rmdir();raise ValueError('; '.join(errors))
    try:page=review_html(project,data,candidate['workflow']['packages'][stage],args.limit,args.max_embed_mb*1024*1024)
    except Exception:
        package_path.unlink();(folder/'preview.webm').unlink(missing_ok=True);folder.rmdir();raise
    (folder/'review.html').write_text(page,encoding='utf-8')
    write_json(project/'brief.json',candidate)
    state=save_status(project,candidate)
    return {'package':candidate['workflow']['packages'][stage],'page':str((folder/'review.html').relative_to(project)),
            'next':'Show these artifacts, identify this revision, then end the turn and wait for the actual user reply.',
            'user_authorized_stage':state['user_authorized_stage']}


def accept(project, brief, args):
    reply=Path(args.reply_file).read_text(encoding='utf-8').strip()
    if not reply or not args.message_id.strip():raise ValueError('retain the actual nonempty reply and its real message reference')
    stage=args.stage;flow=brief.get('workflow') or {};package_record=(flow.get('packages') or {}).get(stage)
    errors=[];package=inspect_package(brief,project,stage,package_record,errors)
    if errors or not package:raise ValueError('; '.join(errors))
    if args.decision=='approved' and not args.presented_message_id:raise ValueError('ordinary acceptance needs the actual presentation message reference')
    value={'origin':'user-message','message_id':args.message_id,'user_reply':reply,'presented_message_id':args.presented_message_id,
           'stage':stage,'revision':package['revision'],'content_sha256':content_digest(brief),'package_sha256':package_record['sha256'],
           'decision':args.decision,'next_stage':NEXT[stage]}
    if args.decision=='waived':
        if not args.waiver_review:raise ValueError('named user waiver still needs a completed self-review file')
        value.update(explicit_skip=True,waived_stage=stage,scope='this_stage_only',self_review=read_json(Path(args.waiver_review)))
    target=project/'plan/reviews'/stage/package['revision']/'user-decision.json'
    if target.exists():raise ValueError('decision revision already exists; preserve the actual history')
    write_json(target,value)
    candidate=copy.deepcopy(brief);candidate['workflow'].setdefault('approvals',{})[stage]=binding(project,target)
    errors=workflow_errors(candidate,project,PURPOSE[stage])
    if errors:
        target.unlink();raise ValueError('; '.join(errors))
    if args.advance:candidate['phase']=NEXT[stage]
    write_json(project/'brief.json',candidate)
    return save_status(project,candidate)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project',type=Path,required=True)
    commands=parser.add_subparsers(dest='command',required=True)
    commands.add_parser('status')
    commands.add_parser('handoff')
    p=commands.add_parser('inspect-video');p.add_argument('--video',required=True);p.add_argument('--stage',choices=('prototype','animatic','full'),required=True);p.add_argument('--range',required=True);p.add_argument('--out',required=True)
    p=commands.add_parser('present');p.add_argument('--stage',choices=NEXT,required=True);p.add_argument('--revision',required=True)
    for name in ('proposal','script','visual-spec','video','render-report','review','pilot-range','objective'):p.add_argument('--'+name)
    p.add_argument('--frame',action='append',default=[]);p.add_argument('--source',action='append',default=[]);p.add_argument('--limit',action='append',required=True);p.add_argument('--max-embed-mb',type=int,default=64);p.add_argument('--webm-preview',action='store_true')
    p=commands.add_parser('accept');p.add_argument('--stage',choices=NEXT,required=True);p.add_argument('--reply-file',required=True);p.add_argument('--message-id',required=True);p.add_argument('--presented-message-id');p.add_argument('--decision',choices=('approved','waived'),default='approved');p.add_argument('--waiver-review');p.add_argument('--advance',action='store_true')
    args=parser.parse_args();project=args.project.expanduser().resolve()
    try:
        brief=read_json(project/'brief.json')
        if args.command=='status':result=status(project,brief)
        elif args.command=='handoff':result=save_status(project,brief)
        elif args.command=='inspect-video':
            out=inside(project,args.out,False)
            if out.exists():raise ValueError('preserve prior inspection; choose a new output revision')
            out.parent.mkdir(parents=True,exist_ok=True)
            result=inspect_video(project,brief,args.video,args.stage,list(map(float,args.range.split(':'))),out)
        elif args.command=='present':result=present(project,brief,args)
        else:result=accept(project,brief,args)
        print(json.dumps(result,ensure_ascii=False,indent=2));return 0
    except (OSError,ValueError,TypeError,KeyError,subprocess.SubprocessError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    import sys
    for _stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(_stream, 'reconfigure'):
            _stream.reconfigure(encoding='utf-8')
    raise SystemExit(main())

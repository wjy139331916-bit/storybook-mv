#!/usr/bin/env python3
"""Build/apply an offline seven-module director workbench, preserving project gates."""
import argparse
import base64
import copy
import hashlib
import json
import math
import os
import re
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'assets/director-workbench'
LIMIT=4*1024*1024


def load(path):
    if Path(path).stat().st_size>LIMIT:raise ValueError('director model/report exceeds 4 MiB')
    return json.loads(Path(path).read_text(encoding='utf-8'))


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path,value):
    Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def safe_json(value):return json.dumps(value,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')


def validate(data):
    code="require(process.argv[1]);const C=require(process.argv[2]);let s='';process.stdin.setEncoding('utf8');process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>{try{C.validate(JSON.parse(s));process.stdout.write('ok')}catch(e){process.stderr.write(e.message);process.exitCode=2}})"
    r=subprocess.run(['node','-e',code,str(ROOT/'assets/pixel-workbench/core.js'),str(ASSETS/'core.js')],input=json.dumps(data),capture_output=True,text=True,encoding='utf-8')
    if r.returncode:raise ValueError('director model: '+r.stderr)
    return data


def seed(duration=6,width=960,height=540,fps=30,example=False):
    model={'schema_version':1,'kind':'mv-director','revision':'draft-r1','duration':duration,'canvas':{'width':width,'height':height},'fps':fps,
           'assets':[],'scenes':[{'id':'scene-1','name':'场景草稿','background':'#ffffff','layers':[],'camera':{'x':0,'y':0,'zoom':1,'keys':[]},'contacts':[]}],
           'shots':[{'id':'s01','scene_id':'scene-1','start':0,'end':duration,'objective':'待填写已确认的镜头意图','lyric_ids':[],'transition':{'type':'cut','duration':0}}],
           'cues':[],'caption':{'enabled':False,'size':.045,'y':.9,'font':'sans-serif','color':'#263a43','highlight':'#c58b31'},'notes':[]}
    if example:
        model['assets']=[
          {'id':'actor','name':'原创构造角色','kind':'rig','heads':4.8,'unit':.105,'colors':{'ink':'#293945','skin':'#e7b698','shirt':'#548b95','pants':'#3a4b61'}},
          {'id':'floor','name':'地面','kind':'shape','shape':'rect','width':1,'height':.12,'fill':'#dce5dc'},
          {'id':'parcel','name':'原创信件','kind':'shape','shape':'rect','width':.065,'height':.07,'fill':'#d3b47d'},
          {'id':'stamp','name':'时间标记','kind':'text','text':'DAY 1','size':.055,'font':'sans-serif','fill':'#597572'}]
        layers=[{'id':'floor-layer','asset_id':'floor','x':.5,'y':.94,'scale':1,'rotation':0,'z':-1,'keys':[]},
          {'id':'lead','asset_id':'actor','x':.3,'y':.87,'scale':1,'rotation':0,'z':1,'pin_left':True,'keys':[{'time':0,'headTilt':-5,'handX':.65,'handY':-2.1},{'time':1,'headTilt':8,'lookX':1,'handX':1.15,'handY':-2.7},{'time':2,'headTilt':0,'handX':.7,'handY':-2.1}]},
          {'id':'letter','asset_id':'parcel','x':.43,'y':.58,'scale':1,'rotation':-6,'z':2,'keys':[]},
          {'id':'label','asset_id':'stamp','x':.8,'y':.18,'scale':1,'rotation':0,'z':0,'keys':[]}]
        model['scenes'][0].update(name='原创表演与接触练习',background='#f5f3e9',layers=layers,
            contacts=[{'id':'touch-letter','a':'lead','anchor_a':'hand','b':'letter','anchor_b':'grip','start':.8,'end':1.2,'tolerance':8}])
        model['scenes'].append(copy.deepcopy(model['scenes'][0]));model['scenes'][1].update(id='scene-2',name='原创镜头对照',background='#e5efef')
        model['scenes'][1]['camera']['keys']=[{'time':0,'zoom':1},{'time':2,'zoom':1.12,'x':.04}]
        model['shots']=[{'id':'s01','scene_id':'scene-1','start':0,'end':2,'objective':'看向并伸手接近信件','lyric_ids':['cue-1'],'transition':{'type':'crossfade','duration':.4}},
             {'id':'s02','scene_id':'scene-2','start':2,'end':4,'objective':'同一动作的镜头关系练习','lyric_ids':['cue-2'],'transition':{'type':'wipe','duration':.4}},
             {'id':'s03','scene_id':'scene-1','start':4,'end':6,'objective':'回到原构图，保留停顿','lyric_ids':[],'transition':{'type':'cut','duration':0}}]
        model['cues']=[{'id':'cue-1','text':'Notice the light','start':.2,'end':1.8,'timing_status':'original_synthetic','words':[{'text':'Notice ','start':.2,'end':.8},{'text':'the light','start':.8,'end':1.8}]},
                       {'id':'cue-2','text':'Hold for a moment','start':2.2,'end':3.8,'timing_status':'original_synthetic','words':[]}]
        model['caption']['enabled']=True
    return model


def project_file(project,name):
    project=Path(project).resolve()
    p=(project/name).resolve()
    if not p.is_relative_to(project) or not p.is_file():raise ValueError('input must be an existing project file: '+str(name))
    return p


def context(project,motion=False,self_test=False):
    project=Path(project).resolve() if project else None
    if self_test:
        if project:raise ValueError('isolated tool self-tests cannot select a user project')
        return {'project':None,'self_test':True,'phase':'tool-test','motion':motion,'range':[0,6],'sources':[]},None
    if not project:raise ValueError('provide the selected project or an isolated original --tool-self-test')
    from check_brief import entry_errors
    brief=load(project/'brief.json')
    errors=entry_errors(brief,project,operation='check')
    if errors:raise ValueError('; '.join(errors))
    phase=brief['phase'];allowed=[0,None]
    if motion and phase=='design':raise ValueError('DESIGN_STILLS_ONLY: no motion before design/script acceptance')
    if phase=='prototype':
        from workflow_gate import pilot_plan
        plan=pilot_plan(brief,project)
        if motion and not plan:raise ValueError('accepted pilot interval is required')
        if plan:allowed=[plan['start'],plan['end']]
    sources=[{'path':'brief.json','sha256':digest(project/'brief.json')}]
    for name in ('visual-spec.json','shot-map.json','review.json'):
        if (project/name).is_file():sources.append({'path':name,'sha256':digest(project/name)})
    for f in sorted((project/'src').rglob('*')):
        if f.is_file():sources.append({'path':f.relative_to(project).as_posix(),'sha256':digest(f)})
    return {'project':str(project),'self_test':False,'phase':phase,'motion':motion,'range':allowed,'sources':sources},brief


def from_project(project,brief):
    project=Path(project).resolve()
    from workflow_gate import target_duration
    duration=target_duration(brief,project)
    res=brief.get('output',{}).get('resolution') or [1280,720]
    model=seed(duration,*res,brief.get('output',{}).get('fps') or 30)
    model['shots'][0]['objective']='依据已确认脚本填写，空白画面不是完成的设计'
    design=brief.get('workflow',{}).get('packages',{}).get('design',{})
    if design.get('path'):
        package=load(project_file(project,design['path']))
        for item in package.get('artifacts',[]):
            if item.get('role')=='design_source':
                f=project_file(project,item['path'])
                if digest(f)!=item.get('sha256'):raise ValueError('director design source changed')
                candidate=load(f)
                if candidate.get('kind')=='mv-director':return validate(candidate)
        script=next((x for x in package.get('artifacts',[]) if x.get('role')=='script'),None)
        if script:
            actual=load(project_file(project,script['path']))
            shots=[]
            for i,s in enumerate(actual.get('shots',[])):
                scene=copy.deepcopy(model['scenes'][0]);scene.update(id='scene-'+str(i+1),name=s.get('visual') or s['id']);model['scenes'].append(scene)
                shots.append({'id':s['id'],'scene_id':scene['id'],'start':s['start'],'end':s['end'],'objective':s.get('objective') or '', 'lyric_ids':s.get('lyric_ids',[]),'transition':{'type':'cut','duration':0}})
            if shots:model['shots']=shots;model['scenes']=model['scenes'][1:]
    lyrics=brief.get('lyrics',{});record=lyrics.get('display_document')
    if record:
        f=project_file(project,record['path'])
        if digest(f)!=record.get('sha256'):raise ValueError('selected cue document changed')
        model['cues']=copy.deepcopy(load(f).get('cues',[]))
        for cue in model['cues']:cue.setdefault('timing_status','unverified')
    model['caption']['enabled']=lyrics.get('mode') in ('full','full-lines','key-lines')
    if lyrics.get('font',{}).get('family'):model['caption']['font']=lyrics['font']['family']
    return model


def output_path(project,out,new_revision=False):
    project=Path(project).resolve() if project else None
    p=Path(out).expanduser();p=(project/p if project and not p.is_absolute() else p).resolve()
    if p==ROOT or ROOT in p.parents:raise ValueError('project exports must stay outside the installed skill')
    if project and not p.is_relative_to(project):raise ValueError('workbench exports must belong to the selected project')
    if p.exists():
        if not new_revision:raise ValueError('existing work preserved; choose a new revision')
        initial=p;n=2
        while p.exists():p=initial.with_name(initial.name+'-r'+str(n));n+=1
    return p


def atomic(target,build):
    target.parent.mkdir(parents=True,exist_ok=True)
    temp=Path(tempfile.mkdtemp(prefix='.'+target.name+'-',dir=target.parent))
    try:
        result=build(temp);os.rename(temp,target);return result
    finally:
        if temp.exists():shutil.rmtree(temp)


def media(path,budget,kind):
    mime={'audio':{'mp3':'audio/mpeg','wav':'audio/wav','m4a':'audio/mp4','ogg':'audio/ogg','flac':'audio/flac'},'video':{'mp4':'video/mp4','webm':'video/webm'},'font':{'otf':'font/otf','ttf':'font/ttf','ttc':'font/collection'}}[kind].get(path.suffix[1:].lower())
    if not mime:raise ValueError('unsupported embedded '+kind+' format')
    size=4*((path.stat().st_size+2)//3)
    if size>budget[0]:raise ValueError('selected private media exceed the embedding budget; choose smaller previews')
    budget[0]-=size
    return 'data:'+mime+';base64,'+base64.b64encode(path.read_bytes()).decode()


def waveform(path):
    from array import array
    r=subprocess.run(['ffmpeg','-v','error','-i',str(path),'-ac','1','-ar','4000','-f','s16le','-'],capture_output=True)
    if r.returncode:raise ValueError('selected audio could not be decoded')
    samples=array('h',r.stdout)
    import sys
    if sys.byteorder!='little':samples.byteswap()
    step=max(1,math.ceil(len(samples)/1600))
    return [round(math.sqrt(sum(x*x for x in samples[i:i+step])/max(1,len(samples[i:i+step])))/32768,5) for i in range(0,len(samples),step)]


def build_editor(target,model,caps,brief,project,source=None,audio=None,video=None,video_range=None,max_mb=64,webm_preview=False):
    project=Path(project).resolve() if project else None
    audio=Path(audio).resolve() if audio else None;video=Path(video).resolve() if video else None
    validate(model)
    if not 1<=max_mb<=512:raise ValueError('embedding budget must be 1..512 MiB')
    if project:
        from workflow_gate import target_duration
        if abs(model['duration']-target_duration(brief,project))>.001:raise ValueError('director timeline differs from the confirmed project scope/recording')
    if caps['self_test']:
        marker=source.parent/'DIRECTOR_SELF_TEST.json' if source else None
        if model['duration']>6.001 or marker and (not marker.is_file() or load(marker)!={'tool':'storybook-mv.director','original_fixture_only':True}):raise ValueError('self-test build needs its original isolated source marker and at most six seconds')
    if caps['motion'] and not caps['self_test']:
        from director_contract import approved_model
        approved_model(brief,project,model)
    if caps['range'][1] is None:caps['range'][1]=model['duration']
    budget=[max_mb*1024*1024];boot={'caps':caps,'model':model,'media':{},'waveform':[],'review':None}
    if audio and project and digest(audio)!=(brief.get('music') or {}).get('audio_sha256'):raise ValueError('selected workbench audio differs from the bound recording')
    if audio:
        boot['media']['audio']=media(audio,budget,'audio');boot['waveform']=waveform(audio);boot['audio_sha256']=digest(audio)
    font=(brief or {}).get('lyrics',{}).get('font') or {}
    if font.get('path'):
        f=project_file(project,font['path'])
        if digest(f)!=font.get('sha256'):raise ValueError('selected font changed')
        boot['media']['font']=media(f,budget,'font');boot['font_family']=font['family']
    if video:
        duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(video)],text=True,encoding='utf-8'))
        bounds=video_range or ([0,model['duration']] if abs(duration-model['duration'])<.125 else None)
        if not bounds or abs(bounds[1]-bounds[0]-duration)>.125 or not 0<=bounds[0]<bounds[1]<=model['duration']+.001:raise ValueError('review video needs a duration-matching global --video-range')
        preview=None
        if webm_preview:
            from review_workspace import create_preview
            media_root=project or video.parent.resolve()
            temp_media=Path(tempfile.mkdtemp(prefix='.director-preview-',dir=media_root))
            try:
                record=create_preview(media_root,video,temp_media/'preview.webm')
                boot['media']['video']=media(temp_media/'preview.webm',budget,'video')
                preview={k:record[k] for k in ('sha256','source_sha256')}
            finally:shutil.rmtree(temp_media)
        else:boot['media']['video']=media(video,budget,'video')
        boot['review']={'target':{'sha256':digest(video),'path':str(video.relative_to(project)) if project else video.name},'range':bounds,'preview':preview}
    def save(temp):
        html=(ASSETS/'editor.html').read_text(encoding='utf-8')
        for key,value in [('BOOT','const DIRECTOR_BOOT='+safe_json(boot)+';'),('PIXEL',(ROOT/'assets/pixel-workbench/core.js').read_text(encoding='utf-8')),('CORE',(ASSETS/'core.js').read_text(encoding='utf-8')),('EDITOR',(ASSETS/'editor.js').read_text(encoding='utf-8'))]:html=html.replace('/*__'+key+'__*/',value)
        (temp/'workbench.html').write_text(html,encoding='utf-8');write(temp/'director.json',model)
        report={'schema_version':1,'tool':'storybook-mv.director','model_sha256':digest(temp/'director.json'),'source_sha256':digest(source) if source else None,'caps':caps,'review':boot['review'],'acceptance':'not_reviewed','modules':['acting','scene','lyrics','storyboard','transition','assets','review'],'embedded_media_bytes':max_mb*1024*1024-budget[0]}
        write(temp/'workbench-report.json',report)
        if caps['self_test']:write(temp/'DIRECTOR_SELF_TEST.json',{'tool':'storybook-mv.director','original_fixture_only':True})
        return {'editor':str(target/'workbench.html'),'model':str(target/'director.json'),'motion':caps['motion'],'modules':report['modules']}
    return atomic(target,save)


def check_workspace(project,workspace):
    project=Path(project).resolve();workspace=Path(workspace).resolve()
    report=load(workspace/'workbench-report.json')
    if report.get('tool')!='storybook-mv.director' or report['caps'].get('project')!=str(project):raise ValueError('workspace belongs to a different project')
    if digest(workspace/'director.json')!=report.get('model_sha256'):raise ValueError('workspace baseline changed; save edits separately and rebuild a new revision')
    for x in report['caps']['sources']:
        if digest(project_file(project,x['path']))!=x['sha256']:raise ValueError('project inputs changed; rebuild a workspace from the current stage')
    return report


def export_package(target,model,project,caps,workspace):
    project=Path(project).resolve();workspace=Path(workspace).resolve()
    validate(model)
    from director_contract import signature
    from check_brief import entry_errors
    if entry_errors(load(project/'brief.json'),project,operation='check'):raise ValueError('current project stage is blocked')
    base=load(workspace/'director.json')
    code="require(process.argv[1]);const C=require(process.argv[2]);let s='';process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>{const [a,b]=JSON.parse(s);console.log(JSON.stringify(C.impact(a,b)))})"
    result=subprocess.run(['node','-e',code,str(ROOT/'assets/pixel-workbench/core.js'),str(ASSETS/'core.js')],input=json.dumps([base,model]),capture_output=True,text=True,encoding='utf-8',check=True)
    impact=json.loads(result.stdout)
    def save(temp):
        write(temp/'director.json',model);write(temp/'impact.json',impact)
        write(temp/'lyrics-draft.json',{'schema_version':1,'timing_status':'unverified','source_audio_sha256':load(project/'brief.json').get('music',{}).get('audio_sha256'),'cues':model['cues']})
        write(temp/'shot-map-draft.json',{'schema_version':1,'duration':model['duration'],'shots':model['shots'],'status':'draft'})
        plans=[]
        for shot in model['shots']:
            scene=next(s for s in model['scenes'] if s['id']==shot['scene_id'])
            for layer in scene['layers']:
                a=next(a for a in model['assets'] if a['id']==layer['asset_id'])
                if a['kind'] in ('rig','pixel'):plans.append({'shot_id':shot['id'],'actor_layer_id':layer['id'],'intent':shot.get('objective',''),'key_poses':layer.get('keys',[]),'contacts':scene.get('contacts',[]),'review_status':'unreviewed'})
        write(temp/'performance-draft.json',{'schema_version':1,'shots':plans,'status':'draft_not_an_observed_performance'})
        repairs=[{'issue_id':n['id'],'range':[max(0,math.floor((n['range'][0]-.25)*model['fps'])/model['fps']),min(model['duration'],math.ceil((n['range'][1]+.25)*model['fps'])/model['fps'])],'shot_ids':[s['id'] for s in model['shots'] if s['end']>n['range'][0] and s['start']<n['range'][1]],'master_updated':False} for n in model['notes']]
        write(temp/'repair-plan.json',{'schema_version':1,'repairs':repairs,'acceptance':'not_reviewed'})
        report=load(workspace/'workbench-report.json')
        if report.get('review'):
            start,end=report['review']['range'];notes=[]
            for note in model['notes']:
                if not start<=note['range'][0]<note['range'][1]<=end:raise ValueError('viewer note lies outside the exact reviewed video')
                notes.append({**note,'range':[note['range'][0]-start,note['range'][1]-start]})
            write(temp/'review-notes.json',{'schema_version':1,'target':report['review']['target'],'notes':notes})
        write(temp/'package.json',{'schema_version':1,'kind':'director-package','project':str(project),'model':{'path':'director.json','sha256':digest(temp/'director.json')},'design_signature':signature(model),'source_inputs':caps['sources'],'impact':impact,'acceptance':'not_reviewed'})
        return {'package':str(target),'impact':impact,'next':'Present changed design sources/actual frames as needed; no approval or production phase was changed.'}
    return atomic(target,save)


def activate(project,package):
    project=Path(project).resolve();package=Path(package).resolve()
    from check_brief import entry_errors
    from director_contract import approved_model
    brief=load(project/'brief.json');errors=entry_errors(brief,project,operation='check')
    if errors:raise ValueError('; '.join(errors))
    if brief['execution']['engine'] not in ('canvas2d','remotion'):raise ValueError('DIRECTOR_ADAPTER_REQUIRED: retain the selected host and adapt the exported data explicitly')
    meta=load(package/'package.json');model_file=package/'director.json';model=validate(load(model_file))
    if meta.get('kind')!='director-package' or meta.get('project')!=str(project) or digest(model_file)!=meta['model']['sha256']:raise ValueError('director package/source changed or belongs to another project')
    for item in meta.get('source_inputs',[]):
        if digest(project_file(project,item['path']))!=item['sha256']:raise ValueError('project source changed after this export; rebuild/apply a fresh revision')
    if brief['execution'].get('context')!='tool-self-test' and brief['phase']!='design':approved_model(brief,project,model)
    mode=brief.get('lyrics',{}).get('mode')
    if model['caption']['enabled'] and mode not in ('full','full-lines','key-lines'):raise ValueError('caption policy differs from the selected brief')
    if model['caption']['enabled'] and brief['execution'].get('context')!='tool-self-test':
        record=brief['lyrics'].get('display_document')
        if not record:raise ValueError('adopt the reviewed canonical cue draft through the existing lyric workflow first')
        canonical=load(project_file(project,record['path']))
        def timing(cues):return [{k:c.get(k,[]) if k=='words' else c.get(k) for k in ('id','text','start','end','words')} for c in cues]
        if digest(project_file(project,record['path']))!=record['sha256'] or timing(model['cues'])!=timing(canonical.get('cues',[])):raise ValueError('director cues differ from the bound canonical cue document; timing exports remain drafts')
    from workflow_gate import target_duration
    if abs(model['duration']-target_duration(brief,project))>.001:raise ValueError('director timeline differs from the confirmed project scope/recording')
    resolution=brief.get('output',{}).get('resolution') or [model['canvas']['width'],model['canvas']['height']]
    fps=brief.get('output',{}).get('fps') or model['fps']
    if model['canvas']['width']*resolution[1]!=model['canvas']['height']*resolution[0]:raise ValueError('director canvas aspect differs from the selected output')
    if brief['phase']=='animatic':
        g=math.gcd(*resolution);ratio=[x//g for x in resolution];unit=max(2,int(960/max(ratio))//2*2);resolution=[x*unit for x in ratio];fps=min(15,fps)
    name=package.name
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,64}',name):raise ValueError('use a simple package revision name such as director-r1')
    config={'width':resolution[0],'height':resolution[1],'duration':math.ceil(model['duration']*fps-1e-7)/fps,'fps':fps,'fidelity':'rough' if brief['phase']=='animatic' else 'director-source'}
    from director_adapters import install
    return install(project,package,model,config,brief)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=('init','build','apply','activate'))
    for name in ('project','model','out','workspace','package','audio','video'):p.add_argument('--'+name,type=Path)
    p.add_argument('--mode',choices=('design','motion'),default='design');p.add_argument('--tool-self-test',action='store_true');p.add_argument('--new-revision',action='store_true');p.add_argument('--video-range');p.add_argument('--webm-preview',action='store_true');p.add_argument('--max-embed-mb',type=int,default=64)
    a=p.parse_args()
    try:
        project=a.project.expanduser().resolve() if a.project else None
        if a.command=='activate':
            if not project or not a.package:raise ValueError('activate needs --project and --package')
            package=project_file(project,(a.package/'package.json').as_posix()).parent
            result=activate(project,package)
        elif a.command=='apply':
            if not project or not a.workspace or not a.model or not a.out:raise ValueError('apply needs project/workspace/model/out')
            workspace=(project/a.workspace).resolve();report=check_workspace(project,workspace);source=project_file(project,a.model)
            target=output_path(project,a.out,a.new_revision);caps,brief=context(project,False,False)
            result=export_package(target,load(source),project,caps,workspace)
        else:
            if not a.out:raise ValueError('provide a new --out')
            caps,brief=context(project,a.mode=='motion',a.tool_self_test)
            source=project_file(project,a.model) if project and a.model else (a.model.resolve() if a.model else None)
            if a.command=='build' and source is None:raise ValueError('build needs the saved --model')
            if a.command=='init' and (source or a.mode!='design'):raise ValueError('init creates a static workspace; use build for a saved model/motion')
            data=load(source) if source else seed(example=True) if a.tool_self_test else from_project(project,brief)
            target=output_path(project,a.out,a.new_revision)
            audio=project_file(project,a.audio) if project and a.audio else project_file(project,brief['music']['audio']) if project and brief.get('music',{}).get('audio') else a.audio.resolve() if a.audio else None
            if audio and a.tool_self_test:raise ValueError('isolated test audio is generated by its test harness; do not pass a user recording')
            video=project_file(project,a.video) if project and a.video else a.video.resolve() if a.video else None
            bounds=list(map(float,a.video_range.split(':'))) if a.video_range else None
            result=build_editor(target,data,caps,brief,project,source,audio,video,bounds,a.max_embed_mb,a.webm_preview)
        print(json.dumps(result,ensure_ascii=False))
    except (OSError,ValueError,KeyError,TypeError,subprocess.SubprocessError) as exc:p.error(str(exc))


if __name__=='__main__':
    import sys
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'):stream.reconfigure(encoding='utf-8')
    main()


"""Destination exercise orchestration; legacy pulse helpers remain import-compatible."""
import argparse
from array import array
import hashlib
import io
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import wave
from runtime_environment import browser_candidates, platform_facts

ROOT = Path(__file__).resolve().parents[1]


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def run(cmd, **kwargs):
    return subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', check=True, **kwargs)


def signature(project):
    files = [project/'brief.json', project/'studio.html'] + sorted((project/'src').rglob('*'))
    return {p.relative_to(project).as_posix(): sha(p) for p in files if p.is_file()}


def prepare(target, engine, runtime, cjk, font, retry):
    options = {'engine':engine, 'runtime':runtime, 'cjk':cjk, 'font_sha256':sha(font) if font else None}
    if target == ROOT or ROOT in target.parents: raise ValueError('self-tests belong outside the installed skill')
    if target.exists():
        marker=target/'RUNTIME_SELF_TEST.json'
        if not retry or not marker.is_file(): raise ValueError('existing work preserved; use a fresh directory, --new-revision, or --retry for an unmodified tool-owned self-test')
        data=json.loads(marker.read_text(encoding='utf-8'))
        if data.get('purpose')!='isolated-runtime-exercise' or data.get('options')!=options or data.get('source_files')!=signature(target): raise ValueError('self-test source/options changed; use a new revision')
        return data['duration']
    duration=6 if cjk or engine=='painted-p5' else 2
    target.parent.mkdir(parents=True,exist_ok=True)
    temp=Path(tempfile.mkdtemp(prefix='.runtime-prepare-',dir=target.parent));temp.rmdir()
    try:
        if engine=='canvas2d':
            run([sys.executable,str(ROOT/'scripts/build_study.py'),str(temp),'--kind','runtime','--subject','abstract','--style','flat','--width','640','--height','360','--tool-self-test'])
        else:
            run([sys.executable,str(ROOT/'scripts/scaffold.py'),str(temp),'--engine',engine,'--duration',str(duration),'--width','640','--height','360','--fps','30','--tool-self-test'])
        if engine!='remotion':
            config={'duration':duration,'width':640,'height':360,'fps':30,'bpm':120,'offset':0,'boil':0,'prototype':True}
            (temp/'src/config.js').write_text('const PROJECT='+json.dumps(config)+';globalThis.PROJECT=PROJECT;\n',encoding='utf-8')
        if engine=='painted-p5':
            (temp/'src/scenes/story.js').write_text("shots([[0,function(t){boilSeed('original-brush-probe');paint(rectPts(W*.1,H*.2,W*.65,H*.5),{wash:'#B7CCD3',washOp:170,ink:null});paint(rectPts(W*(.15+.12*Math.sin(t)),H*.35,W*.18,H*.2),{fill:'#C98E79',fillOp:180,ink:'#293945',sw:1});}]]);\n",encoding='utf-8')
        brief=json.loads((temp/'brief.json').read_text(encoding='utf-8'));brief['execution']['runtime']=runtime;brief['prototype']['duration']=duration
        cues=[{'start':0,'end':duration/2,'text':'窗边还有一盏灯。' if cjk else 'Runtime cue A'},{'start':duration/2,'end':duration,'text':'我沿着微光慢慢往前走。' if cjk else 'Runtime cue B'}]
        if cjk:
            from font_check import inspect_font
            doc=temp/'assets/cjk-original.json';doc.write_text(json.dumps({'lines':[{'id':str(i),'text':c['text']} for i,c in enumerate(cues)]},ensure_ascii=False),encoding='utf-8')
            glyphs=inspect_font(font,doc)
            if not glyphs['ok']: raise ValueError('selected font lacks original Chinese probe glyphs: '+str(glyphs['missing']))
            dest=temp/('assets/cjk-font'+font.suffix);shutil.copy2(font,dest)
            brief['lyrics'].update(language='zh',font={'path':dest.relative_to(temp).as_posix(),'sha256':sha(dest),'family':glyphs['family']})
            (temp/'cjk-glyph-check.json').write_text(json.dumps(glyphs,ensure_ascii=False,indent=2),encoding='utf-8')
        if engine!='remotion':
            (temp/'src/data/lyrics.js').write_text('globalThis.STORY_LYRICS_MODE="full-lines";globalThis.STORY_LYRICS='+json.dumps({'alignment_status':'synthetic_known','cues':cues},ensure_ascii=False)+';\n',encoding='utf-8')
            if cjk:
                overlay="(function(r){const before=r.overlayHook;r.overlayHook=function(c,t){if(before)before(c,t);const q=r.STORY_LYRICS.cues.find(q=>t>=q.start&&t<q.end);if(!q)return;c.save();const w=c.canvas.width,h=c.canvas.height;c.font='24px '+(r.STORY_TEXT_STYLE?.font||'sans-serif');c.textAlign='left';c.textBaseline='alphabetic';const x=(w-c.measureText(q.text).width)/2,y=h*.92;c.fillStyle='#F4F2ED';c.fillRect(w*.02,h*.82,w*.96,h*.16);c.fillStyle='#263A43';c.fillText(q.text,x,y);const n=Math.floor((t-q.start)/(q.end-q.start)*q.text.length);c.fillStyle='#B98A32';c.fillText(q.text.slice(0,n),x,y);c.restore();};})(globalThis);\n"
                (temp/'src/cjk-probe.js').write_text(overlay,encoding='utf-8')
                html=temp/'studio.html';html.write_text(html.read_text(encoding='utf-8').replace('</body>','<script src="src/cjk-probe.js"></script></body>'),encoding='utf-8')
                entry=temp/'src/render-entry.json'
                if entry.is_file():
                    data=json.loads(entry.read_text(encoding='utf-8'));data['scripts'].append('src/cjk-probe.js');entry.write_text(json.dumps(data),encoding='utf-8')
        else:
            (temp/'src/probe-cues.json').write_text(json.dumps(cues,ensure_ascii=False),encoding='utf-8')
        from runtime_smoke import pulses
        audio=temp/'assets/runtime-pulses.wav';pulses(audio)
        if duration>2:
            with wave.open(str(audio),'rb') as w: params=w.getparams();buf=w.readframes(w.getnframes())
            with wave.open(str(audio),'wb') as w: w.setparams(params);w.writeframes(buf+b'\0'*(round(duration*params.framerate)*params.nchannels*params.sampwidth-len(buf)))
        (temp/'brief.json').write_text(json.dumps(brief,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        marker={'purpose':'isolated-runtime-exercise','not_a_user_mv':True,'options':options,'duration':duration,'source_files':signature(temp)}
        (temp/'RUNTIME_SELF_TEST.json').write_text(json.dumps(marker,indent=2),encoding='utf-8');os.rename(temp,target)
        return duration
    finally:
        if temp.exists(): shutil.rmtree(temp)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('project',type=Path);p.add_argument('--runtime',choices=('node-canvas','browser'),required=True)
    p.add_argument('--engine',choices=('canvas2d','painted-p5','remotion'),default='canvas2d')
    p.add_argument('--canvas-module',type=Path);p.add_argument('--chrome',type=Path);p.add_argument('--font',type=Path)
    for name in ('cjk','install','retry','new-revision','soft-gl'): p.add_argument('--'+name,action='store_true')
    p.add_argument('--deps-from',type=Path);p.add_argument('--record-in',type=Path)
    a=p.parse_args();target=a.project.expanduser().resolve()
    try:
        if a.engine!='canvas2d' and a.runtime!='browser': raise ValueError('p5/Remotion require their actual browser backend')
        if a.new_revision and target.exists():
            base=target;i=2
            while target.exists():target=base.with_name(base.name+'-r'+str(i));i+=1
        font=a.font.expanduser().resolve() if a.font else None
        if a.cjk and (not font or not font.is_file()): raise ValueError('--cjk requires an explicit local --font')
        if a.record_in:
            prod=a.record_in.expanduser().resolve();brief=json.loads((prod/'brief.json').read_text(encoding='utf-8'))
            if prod==ROOT or ROOT in prod.parents:raise ValueError('receipts belong outside the skill')
            if brief.get('execution',{}).get('engine')!=a.engine or brief.get('execution',{}).get('runtime')!=a.runtime:raise ValueError('receipt destination must select the tested engine/runtime')
            if (prod/'runtime-report.json').exists() or (prod/'out/runtime-check').exists():raise ValueError('existing receipt preserved; use a new reviewed revision')
        duration=prepare(target,a.engine,a.runtime,a.cjk,font,a.retry)
        if a.deps_from and not (target/'node_modules').exists():
            source=a.deps_from.expanduser().resolve()
            if not source.is_dir():raise ValueError('--deps-from needs an existing node_modules directory')
            (target/'node_modules').symlink_to(source,target_is_directory=True)
        if a.install:
            cmd=['npm','ci' if (target/'package-lock.json').is_file() else 'install','--no-audit','--no-fund']
            if a.runtime=='node-canvas':cmd=['npm','install','--save-exact','@napi-rs/canvas@0.1.100','--no-audit','--no-fund']
            run(cmd,cwd=target)
        chrome=next(iter(browser_candidates(a.chrome)),None)
        cmd=[sys.executable,str(ROOT/'scripts/preflight.py'),'--project',str(target),'--engine',a.engine,'--runtime',a.runtime,'--strict','--json']
        if chrome:cmd+=['--chrome',chrome]
        if a.canvas_module:cmd+=['--canvas-module',str(a.canvas_module.resolve())]
        if a.cjk:cmd+=['--require-cjk','--font',str(font)]
        diagnostic=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8')
        if diagnostic.returncode:raise ValueError('Runtime prerequisites incomplete. Use --install or --deps-from, then rerun with --retry.\n'+(diagnostic.stdout or diagnostic.stderr))
        times='0.5,1,1.5,3.5,4.5' if duration==6 else '0.5,1,1.5'
        if a.runtime=='node-canvas':
            cmd=['node',str(ROOT/'scripts/render_canvas.mjs'),'--project='+str(target),'--out=out/runtime','--audio=assets/runtime-pulses.wav','--times='+times,'--resume']
            if a.canvas_module:cmd+=['--canvas-module='+str(a.canvas_module.resolve())]
            run(cmd)
        else:
            extra=(['--chrome='+chrome] if chrome else [])+(['--soft-gl'] if a.soft_gl else [])
            run(['node','render.mjs','--clip','--out=out/runtime/clip.mp4','--audio=assets/runtime-pulses.wav','--fps=30',*extra],cwd=target)
            run(['node','render.mjs','--stills='+times,'--out=out/runtime/stills',*extra],cwd=target)
        clip=target/'out/runtime/clip.mp4';report_file=target/'out/runtime/render-report.json'
        report=json.loads(report_file.read_text(encoding='utf-8')) if report_file.is_file() else {}
        if a.runtime=='browser' and a.engine!='remotion':
            sampled=run(['node','render.mjs','--probe','--times=0.5,1,1.5']+(['--chrome='+chrome] if chrome else [])+(['--soft-gl'] if a.soft_gl else []),cwd=target)
            candidates=[line for line in sampled.stdout.splitlines() if line.startswith('{')]
            if not candidates:raise ValueError('selected browser mechanism probe returned no runtime evidence')
            report['mechanism_probe']=json.loads(candidates[-1])
        info=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_format','-show_streams','-of','json',str(clip)]));v=next(s for s in info['streams'] if s['codec_type']=='video')
        if (v['width'],v['height'],int(v.get('nb_read_frames',0)))!=(640,360,duration*30) or abs(float(info['format']['duration'])-duration)>.12 or not any(s['codec_type']=='audio' for s in info['streams']):raise ValueError('runtime encode dimensions/frame count/audio/duration failed')
        run(['ffmpeg','-v','error','-i',str(clip),'-f','null','-'])
        pcm=array('h',subprocess.check_output(['ffmpeg','-v','error','-i',str(clip),'-map','0:a:0','-ar','8000','-ac','1','-f','s16le','-']))
        if sys.byteorder!='little':pcm.byteswap()
        starts=[];active=False
        for i in range(0,len(pcm),160):
            block=pcm[i:i+160];loud=math.sqrt(sum(x*x for x in block)/max(1,len(block)))/32768>.03
            if loud and not active:starts.append(i/8000)
            active=loud
        if len(starts)!=2 or any(abs(x-y)>.06 for x,y in zip(starts,[.5,1.5])):raise ValueError('synthetic audio pulse offsets failed: '+str(starts))
        report.update(schema_version=2,status='passed',engine=a.engine,runtime_backend=a.runtime,destination=platform_facts(),prerequisites=json.loads(diagnostic.stdout),encoded={'full_decode':True,'video':True,'audio':True,'frames':duration*30},sync_test={'scope':'original synthetic pulses only','expected':[.5,1.5],'observed':starts,'tolerance_seconds':.06},artifact={'path':clip.relative_to(target).as_posix(),'sha256':sha(clip)},scope='Selected destination engine/backend exercise only; no natural acting, real singing, project aesthetics or other-platform certification.')
        if a.cjk:
            from PIL import Image
            samples=[]
            for time in (.75,1.75):
                buf=subprocess.check_output(['ffmpeg','-v','error','-ss',str(time),'-i',str(clip),'-frames:v','1','-f','image2pipe','-vcodec','png','-'])
                image=Image.open(io.BytesIO(buf)).convert('RGB');crop=image.crop((0,round(image.height*.82),image.width,image.height))
                samples.append({'time':time,'caption_region_sha256':hashlib.sha256(crop.tobytes()).hexdigest(),'highlight_pixels':sum(r>120 and 65<g<200 and b<130 and r>g for r,g,b in crop.getdata())})
            if not all(s['highlight_pixels']>4 for s in samples) or samples[0]['caption_region_sha256']==samples[1]['caption_region_sha256']:raise ValueError('encoded Chinese synthetic highlight did not visibly change')
            report['cjk']={'glyphs':json.loads((target/'cjk-glyph-check.json').read_text()),'encoded_samples':samples,'timing':'original authored synthetic timings, never inferred real singing'}
        (target/'runtime-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        if a.record_in:
            shutil.copytree(target/'out/runtime',prod/'out/runtime-check');report['artifact']['path']='out/runtime-check/clip.mp4'
            (prod/'runtime-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'status':'passed','engine':a.engine,'runtime':a.runtime,'project':str(target),'pulse_offsets':starts,'cjk':a.cjk,'scope':report['scope']},ensure_ascii=False))
    except (OSError,ValueError,KeyError,StopIteration,subprocess.SubprocessError) as exc:
        detail=getattr(exc,'stderr','') or ''
        if isinstance(detail,bytes):detail=detail.decode(errors='replace')
        p.error(str(exc)+(': '+detail[-2000:] if detail else ''))

"""Original selected-host adapters for the shared director scene model."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]


def install(project,package,model,config,brief):
    from director_workbench import safe_json
    from workflow_gate import pilot_plan
    from director_contract import sha
    engine=brief['execution']['engine'];name=package.name
    if engine not in ('canvas2d','remotion'):raise ValueError('DIRECTOR_ADAPTER_REQUIRED: keep the selected painterly/3D/custom host; exported data need an explicit adapter')
    dest=(project/'src/director'/name).resolve();backup=(project/'plan/director-activation'/name).resolve()
    if not dest.is_relative_to(project) or not backup.is_relative_to(project):raise ValueError('activation paths must remain in the selected project')
    if dest.exists() or backup.exists():raise ValueError('activation revision already exists; choose a new package revision')
    plan=pilot_plan(brief,project) if brief['phase']=='prototype' else None
    bounds=[plan['start'],plan['end']] if plan else [0,model['duration']]
    rel=lambda p:p.relative_to(project).as_posix()
    files={dest/'director-core.js':(ROOT/'assets/director-workbench/core.js').read_bytes(),
           dest/'pixel-core.js':(ROOT/'assets/pixel-workbench/core.js').read_bytes(),
           dest/'director.json':(package/'director.json').read_bytes(),
           project/'check_brief.py':(ROOT/'scripts/check_brief.py').read_bytes(),
           project/'director_contract.py':(ROOT/'scripts/director_contract.py').read_bytes()}
    if engine=='canvas2d':
        files[dest/'model.js']=('globalThis.DIRECTOR_MODEL='+safe_json(model)+';\n').encode()
        files[dest/'config.js']=('const PROJECT='+safe_json(config)+';\nglobalThis.STORY_LYRICS_MODE='+safe_json(brief.get('lyrics',{}).get('mode'))+';\n').encode()
        scene="globalThis.drawFrame=function(c,t,s){globalThis.MV_FRAME_CHECKS=MVDirector.render(c,DIRECTOR_MODEL,t,{width:s.width,height:s.height,captions:false,rough:PROJECT.fidelity==='rough'});};\nglobalThis.overlayHook=function(c,t){const d=Object.assign({},DIRECTOR_MODEL);if(globalThis.STORY_LYRICS&&globalThis.STORY_LYRICS.cues)d.cues=globalThis.STORY_LYRICS.cues;const W=c.canvas.width,H=c.canvas.height,m={boxes:[],warnings:[]};c.save();c.scale(W/d.canvas.width,H/d.canvas.height);MVDirector.drawCaptions(c,d,t,m);c.restore();if(globalThis.MV_FRAME_CHECKS)MV_FRAME_CHECKS.warnings.push(...m.warnings);if(globalThis.MV_FRAME_CHECKS)MV_FRAME_CHECKS.boxes.push(...m.boxes.map(b=>Object.assign({},b,{x:b.x*W/d.canvas.width,y:b.y*H/d.canvas.height,w:b.w*W/d.canvas.width,h:b.h*H/d.canvas.height})));};\n"
        files[dest/'scene.js']=scene.encode()
        scripts=[rel(dest/n) for n in ['config.js','pixel-core.js','director-core.js','model.js','scene.js']]
        files[project/'src/render-entry.json']=json.dumps({'scripts':scripts}).encode()
        html='<!doctype html><html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Director Canvas preview</title><style>body{margin:0;background:#f3f4ef}canvas{width:100%;height:auto}input{width:80%}</style><canvas id="out"></canvas><input id="scrub" type="range" min="0" value="0" step="0.033333"><span id="tt"></span>'+''.join('<script src="'+s+'"></script>' for s in scripts+['src/runtime.js'])+'</html>'
        files[project/'studio.html']=html.encode()
    else:
        jsx="""// Original director composition. All art is supplied by the accepted data source.
import React,{useRef,useState,useEffect,useLayoutEffect} from 'react';
import {AbsoluteFill,Audio,Composition,registerRoot,useCurrentFrame,useVideoConfig,delayRender,continueRender,cancelRender,staticFile} from 'remotion';
import './director/REV/pixel-core.js';
import './director/REV/director-core.js';
import model from './director/REV/director.json';
import defaults from './project.json';
function Scene({audio=null,font=null,cues=[],config=defaults}){
 const canvas=useRef(),frame=useCurrentFrame(),{width,height,fps}=useVideoConfig();
 const [ready,setReady]=useState(!font),[handle]=useState(()=>font?delayRender('director selected font'):null);
 useEffect(()=>{if(!font)return;new FontFace(font.family,'url('+JSON.stringify(staticFile(font.file))+')').load().then(f=>{document.fonts.add(f);setReady(true);}).catch(cancelRender);},[font?.file]);
 useLayoutEffect(()=>{if(!ready||!canvas.current)return;const d=Object.assign({},model,{cues:cues.length?cues:model.cues});globalThis.MVDirector.render(canvas.current.getContext('2d'),d,frame/fps,{width,height,rough:config.fidelity==='rough'});if(handle!==null)continueRender(handle);},[frame,width,height,fps,ready,cues]);
 return <AbsoluteFill><canvas ref={canvas} width={width} height={height} style={{width:'100%',height:'100%'}}/>{audio?<Audio src={staticFile(audio)}/>:null}</AbsoluteFill>;
}
registerRoot(()=> <Composition id="MV" component={Scene} durationInFrames={Math.round(defaults.duration*defaults.fps)} fps={defaults.fps} width={defaults.width} height={defaults.height} defaultProps={{config:defaults,cues:[]}} calculateMetadata={({props})=>({durationInFrames:Math.round(props.config.duration*props.config.fps),fps:props.config.fps,width:props.config.width,height:props.config.height})}/>);
"""
        files[project/'src/index.jsx']=jsx.replace('REV',name).encode()
        files[project/'src/project.json']=json.dumps(config).encode()
        scripts=[rel(dest/'pixel-core.js'),rel(dest/'director-core.js'),'src/index.jsx','src/project.json']
    record={'schema_version':1,'engine':engine,'model':{'path':rel(dest/'director.json'),'sha256':hashlib.sha256(files[dest/'director.json']).hexdigest()},
            'scripts':[{'path':p,'sha256':hashlib.sha256(files[project/p]).hexdigest()} for p in scripts],
            'package':rel(package/'package.json'),'acceptance':'not_reviewed'}
    files[project/'director-active.json']=(json.dumps(record,indent=2)+'\n').encode()
    originals={}
    for path in files:
        if not path.resolve().is_relative_to(project):raise ValueError('activation target escapes the project')
        if path.is_symlink():raise ValueError('activation does not replace symlinked files')
        originals[path]=path.read_bytes() if path.is_file() else None
    backup.mkdir(parents=True)
    for path,content in originals.items():
        if content is not None:
            saved=backup/path.relative_to(project);saved.parent.mkdir(parents=True,exist_ok=True);saved.write_bytes(content)
    (backup/'activation.json').write_text(json.dumps({'engine':engine,'changed_files':[rel(p) for p in files],'previous_files':[rel(p) for p,v in originals.items() if v is not None],'status':'prepared'},indent=2)+'\n',encoding='utf-8')
    written=[]
    try:
        for path,content in files.items():
            path.parent.mkdir(parents=True,exist_ok=True);written.append(path);path.write_bytes(content)
    except OSError as exc:
        for path in reversed(written):
            previous=originals[path]
            if previous is None:path.unlink(missing_ok=True)
            else:path.write_bytes(previous)
        if dest.exists():shutil.rmtree(dest)
        try:
            (backup/'activation.json').write_text(json.dumps({'engine':engine,'status':'rolled_back','error':str(exc)},indent=2)+'\n',encoding='utf-8')
        except OSError:pass
        raise
    (backup/'activation.json').write_text(json.dumps({'engine':engine,'changed_files':[rel(p) for p in files],'previous_files':[rel(p) for p,v in originals.items() if v is not None],'status':'installed'},indent=2)+'\n',encoding='utf-8')
    return {'activated':rel(dest),'engine':engine,'backup':rel(backup),'range':bounds,'render_entry':'src/render-entry.json' if engine=='canvas2d' else 'src/index.jsx','user_approvals_changed':False}


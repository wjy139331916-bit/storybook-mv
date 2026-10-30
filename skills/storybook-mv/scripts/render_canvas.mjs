// Original optional CPU Canvas2D runner. This is not a Chrome/p5/WebGL compatibility test.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import os from 'node:os';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import {spawn,spawnSync} from 'node:child_process';
import {assertProduction} from './production_gate.mjs';

const args={};
for(const a of process.argv.slice(2)){if(!a.startsWith('--'))throw Error('use --key=value arguments');const i=a.indexOf('=');args[a.slice(2,i<0?undefined:i)]=i<0?true:a.slice(i+1);}
const known=new Set(['help','project','out','canvas-module','stills-only','times','audio','fps','range','resume','estimate','max-seconds','max-cache-bytes']);
for(const key of Object.keys(args))if(!known.has(key))throw Error('unsupported render option: '+key);
if(args.help){console.log('node render_canvas.mjs --project=DIR --out=out/study [--canvas-module=/path/to/index.js] [--stills-only] [--times=0.5,3.6,4.8] [--audio=assets/test.wav] [--range=START:END] [--resume] [--estimate]');process.exit(0);}
const project=path.resolve(args.project||'.'),out=path.resolve(project,args.out||'out/canvas-study');
const operation=args.estimate?'estimate':args['stills-only']?'stills':'video';
const stillCount=args.times?String(args.times).split(',').length:3;
const brief=assertProduction(project,{audio:args.audio||undefined,operation,still_count:stillCount});
const require=createRequire(path.join(project,'package.json'));
let canvasModule;
try{canvasModule=require(args['canvas-module']?path.resolve(args['canvas-module']):'@napi-rs/canvas');}
catch(e){throw Error('Install the selected optional runtime: npm install --save-exact @napi-rs/canvas@0.1.100, or pass --canvas-module. '+e.message);}
const {createCanvas}=canvasModule;
if(brief.lyrics?.font?.path){const font=path.resolve(project,brief.lyrics.font.path);if(!canvasModule.GlobalFonts?.registerFromPath(font))throw Error('selected lyric font could not be registered in this runtime');}
const sha=b=>createHash('sha256').update(b).digest('hex');
function inputs(){
  const files=[];
  function visit(p){if(!fs.existsSync(p))return;const st=fs.lstatSync(p);if(st.isSymbolicLink())throw Error('resolve input symlinks explicitly before a reproducible render');if(st.isDirectory()){for(const n of fs.readdirSync(p).sort())visit(path.join(p,n));}else if(st.isFile())files.push({path:path.relative(project,p).split(path.sep).join('/'),sha256:sha(fs.readFileSync(p))});}
  for(const n of ['src','data','assets','visual-spec.json','package.json','package-lock.json','render_canvas.mjs','render.mjs','studio.html','production_gate.mjs','check_brief.py','input_contracts.py','pilot_gate.py','project_contracts.py','workflow_gate.py'])visit(path.join(project,n));
  files.sort((a,b)=>Buffer.compare(Buffer.from(a.path),Buffer.from(b.path)));
  return {files,digest:sha(files.map(f=>f.path+'\0'+f.sha256+'\n').join(''))};
}
const manifest=inputs();
const context=vm.createContext({console,makeStudyCanvas:createCanvas,STUDY:undefined});
if(brief.lyrics?.font?.family)context.STORY_TEXT_STYLE={font:JSON.stringify(brief.lyrics.font.family)+',sans-serif'};
const entry=path.join(project,'src/render-entry.json');
const scripts=fs.existsSync(entry)?JSON.parse(fs.readFileSync(entry,'utf8')).scripts:['src/config.js','src/scene.js','src/data/lyrics.js','src/lyrics-overlay.js'];
for(const rel of scripts){const f=path.resolve(project,rel);if(!f.startsWith(project+path.sep))throw Error('render entry must stay inside project');vm.runInContext(fs.readFileSync(f,'utf8'),context,{filename:rel});}
if(brief.phase!=='design'&&brief.execution?.context!=='tool-self-test'&&['full','full-lines'].includes(brief.lyrics?.mode)){
  if(typeof context.overlayHook!=='function')throw Error('full-line subtitles require the actual overlay renderer');
  const cues=JSON.parse(fs.readFileSync(path.resolve(project,brief.lyrics.display_document.path),'utf8'));
  context.STORY_LYRICS=cues;context.STORY_LYRICS_MODE='full-lines';
  if(brief.lyrics.font?.family)context.STORY_TEXT_STYLE={...(context.STORY_TEXT_STYLE||{}),font:JSON.stringify(brief.lyrics.font.family)+',sans-serif'};
}
const config=vm.runInContext('PROJECT',context),{width,height,duration}=config,fps=Number(args.fps||config.fps||30);
const bounds=args.range?String(args.range).split(':').map(Number):[0,duration];
if(bounds.length!==2||bounds.some(x=>!Number.isFinite(x))||bounds[0]<0||bounds[1]>duration||bounds[1]<=bounds[0])throw Error('invalid render range');
const [rangeStart,rangeEnd]=bounds,startFrame=Math.round(rangeStart*fps),endFrame=Math.round(rangeEnd*fps),outputDuration=(endFrame-startFrame)/fps;
if(Math.abs(startFrame/fps-rangeStart)>1e-6||Math.abs(endFrame/fps-rangeEnd)>1e-6)throw Error('range endpoints must be frame aligned');
const audioPath=args.audio?path.resolve(project,args.audio):(brief.music?.audio?path.resolve(project,brief.music.audio):null);
assertProduction(project,{duration:outputDuration,audio:audioPath||undefined,resolution:[width,height],fps,timeline_duration:duration,operation,still_count:stillCount,timeline_range:bounds});
const selected=brief.output?.resolution;
if(brief.phase!=='animatic'&&brief.execution?.context!=='tool-self-test'&&selected&&(selected[0]!==width||selected[1]!==height))throw Error('render config dimensions differ from the approved output');
if(![width,height].every(n=>Number.isInteger(n)&&n>0&&n%2===0)||!Number.isFinite(duration)||duration<=0||!Number.isFinite(fps)||fps<=0)throw Error('invalid render dimensions/timing');
const canvas=createCanvas(width,height);
const frameAudit={metadata_frames:0,findings:[],samples:[],scope:'Declared text/action boxes, local actor poses and contact metadata from the actual drawing code. Undeclared content and semantic occlusion are not verified.'},poseStates=new Map(),issueRanges=new Map();
function finding(category,id,t,note){const key=category+'|'+id,old=issueRanges.get(key);if(old&&t>=old.range[1]-1e-6&&t-old.range[1]<2/fps+1e-6){old.range[1]=t+1/fps;return;}const item={category,id,range:[t,t+1/fps],observation:note,disposition:'needs_review'};frameAudit.findings.push(item);issueRanges.set(key,item);}
function inspectFrame(t){
  const data=context.MV_FRAME_CHECKS;if(!data)return;frameAudit.metadata_frames++;
  const boxes=data.boxes||[],actors=data.actors||[];
  for(const b of boxes){if(![b.x,b.y,b.w,b.h].every(Number.isFinite)||b.w<0||b.h<0)throw Error('invalid declared layout box');if(b.kind==='text'&&(b.x<-.5||b.y<-.5||b.x+b.w>width+.5||b.y+b.h>height+.5))finding('text_outside_frame',b.id,t,'Declared text box extends past the encoded frame.');}
  for(const text of boxes.filter(b=>b.kind==='text'))for(const action of boxes.filter(b=>b.kind==='action')){const overlap=Math.max(0,Math.min(text.x+text.w,action.x+action.w)-Math.max(text.x,action.x))*Math.max(0,Math.min(text.y+text.h,action.y+action.h)-Math.max(text.y,action.y));if(overlap>Math.min(text.w*text.h,action.w*action.h)*.08)finding('text_action_overlap',text.id+'|'+action.id,t,'Declared text and action boxes overlap; inspect actual silhouettes and intent.');}
  const present=new Set(actors.map(a=>a.id));for(const id of poseStates.keys())if(!present.has(id))poseStates.delete(id);
  for(const a of actors){if(a.reachable===false)finding('unreachable_actor_target',a.id,t,'The drawn actor reports an unreachable target.');const sig=[...(a.pose_signature||[]),a.view||0],previous=poseStates.get(a.id);if(!sig.length||sig.some(x=>!Number.isFinite(x)))continue;if(previous&&previous.signature.length===sig.length&&sig.every((x,i)=>Math.abs(x-previous.signature[i])<.001)){if(t-previous.start>=3)finding('unchanged_local_pose',a.id,t,'Local articulated pose is unchanged for at least three seconds; root/camera motion is excluded. Purposeful holds can be valid.');}else poseStates.set(a.id,{signature:sig,start:t});}
  if(data.contact&&(!Number.isFinite(data.contact.distance)||data.contact.distance>3))finding('contact_gap','prop-contact',t,'Declared contact points differ by more than three encoded pixels.');
  for(const contact of data.contacts||[]){if(!Number.isFinite(contact.distance)||!Number.isFinite(contact.tolerance)||contact.distance>contact.tolerance)finding('contact_gap',contact.id||'director-contact',t,'Actual declared contact distance exceeds its project tolerance; inspect the encoded interaction.');}
  for(const [i,warning] of (data.warnings||[]).entries())if(typeof warning==='string')finding('declared_scene_warning','scene-warning-'+i,t,warning);
  if(frameAudit.samples.length<18&&(!frameAudit.samples.length||t-frameAudit.samples.at(-1).t>.45))frameAudit.samples.push({t,boxes:JSON.parse(JSON.stringify(boxes)),contact:data.contact?JSON.parse(JSON.stringify(data.contact)):null});
}
async function frame(t,inspect=false){canvas.width=width;canvas.height=height;const c=canvas.getContext('2d');await context.drawFrame(c,t,{width,height,project:config});if(context.overlayHook)context.overlayHook(c,t);if(context.STORY_LYRICS_OVERFLOW)throw Error(`caption overflow at ${t.toFixed(3)}s; fix layout before encoding`);if(inspect)inspectFrame(t);return canvas.toBuffer('image/png');}
const ts=(args.times?String(args.times).split(',').map(Number):[rangeStart,rangeStart+outputDuration*.5,rangeStart+outputDuration*.9]);
if(!ts.length||ts.some(t=>!Number.isFinite(t)||t<0||t>duration))throw Error('invalid still times');
const probeTimes=[rangeStart,rangeStart+outputDuration*.37,rangeStart+outputDuration*.73],first=[];
for(const t of probeTimes)first.push(sha(await frame(t)));
const deterministic=[];
for(let i=probeTimes.length-1;i>=0;i--){const hash=sha(await frame(probeTimes[i]));deterministic.push({t:probeTimes[i],sha256:hash,passed:hash===first[i]});}
if(deterministic.some(x=>!x.passed))throw Error('same-time frames changed after reverse seek');
if(args.estimate||args['max-seconds']||args['max-cache-bytes']){
  const samples=[];for(const t of ts){const start=performance.now(),buf=await frame(t);samples.push({t,milliseconds:performance.now()-start,png_bytes:buf.length});}
  const ms=samples.map(x=>x.milliseconds).sort((a,b)=>a-b),bytes=samples.reduce((a,b)=>a+b.png_bytes,0)/samples.length;
  const estimate={mode:'estimate',range:bounds,frames:endFrame-startFrame,frame_samples:samples,median_frame_ms:ms[Math.floor(ms.length/2)],sample_max_frame_ms:ms.at(-1),estimated_render_seconds:(endFrame-startFrame)*ms[Math.floor(ms.length/2)]/1000,estimated_png_cache_bytes:Math.ceil(Math.max(...samples.map(x=>x.png_bytes))*(endFrame-startFrame)),scope:'Measured sample estimate; allow additional encoding, review and repair time. No price or aesthetic prediction.'};
  for(const [flag,value] of [['max-seconds',estimate.estimated_render_seconds],['max-cache-bytes',estimate.estimated_png_cache_bytes]]){if(args[flag]&&(!Number.isFinite(Number(args[flag]))||Number(args[flag])<=0||value>Number(args[flag])))throw Error('measured sample exceeds '+flag+' budget; choose an explicit scope/quality tradeoff');}
  if(args.estimate){console.log(JSON.stringify(estimate));process.exit(0);}
}
const signature=sha(JSON.stringify({input:manifest.digest,renderer:sha(fs.readFileSync(new URL(import.meta.url))),width,height,fps,bounds,audio:audioPath?sha(fs.readFileSync(audioPath)):null}));
const checkpointPath=path.join(out,'checkpoint.json');let checkpoint={signature,frames:{}},reused=0;
if(fs.existsSync(out)&&fs.readdirSync(out).length){
  if(!args.resume||!fs.existsSync(checkpointPath))throw Error('output directory must be empty, or use --resume with its matching checkpoint');
  checkpoint=JSON.parse(fs.readFileSync(checkpointPath,'utf8'));
  if(checkpoint.signature!==signature)throw Error('resume source/config/audio/range changed; preserve this output and select a new revision');
  if(checkpoint.clip_sha256&&fs.existsSync(path.join(out,'clip.mp4'))&&sha(fs.readFileSync(path.join(out,'clip.mp4')))!==checkpoint.clip_sha256)throw Error('completed clip was changed outside this render; previous work preserved');
}
fs.mkdirSync(out,{recursive:true});if(args.resume)fs.mkdirSync(path.join(out,'frames'),{recursive:true});
function saveCheckpoint(){const tmp=checkpointPath+'.tmp';fs.writeFileSync(tmp,JSON.stringify(checkpoint));fs.renameSync(tmp,checkpointPath);}
if(args.resume)saveCheckpoint();
const stills=[];
for(let i=0;i<ts.length;i++){const f=`frame-${String(i).padStart(2,'0')}.png`,buf=await frame(ts[i],!!args['stills-only']);fs.writeFileSync(path.join(out,f),buf);stills.push({t:ts[i],file:f,sha256:sha(buf)});}
// Exact same renderer draws the sheet; all cells share scale.
const cols=Math.min(3,ts.length),cw=480,ch=Math.round(cw*height/width),sheet=createCanvas(cw*cols,ch*Math.ceil(ts.length/cols));
const sc=sheet.getContext('2d');
for(let i=0;i<ts.length;i++){await frame(ts[i]);sc.drawImage(canvas,(i%cols)*cw,Math.floor(i/cols)*ch,cw,ch);}
fs.writeFileSync(path.join(out,'sheet.png'),sheet.toBuffer('image/png'));
let frames=0,probe=null,clip=null,audio=null;
const start=performance.now();
if(!args['stills-only']){
  if(audioPath&&!fs.existsSync(audioPath))throw Error('audio input missing');
  if(audioPath)audio={path:path.relative(project,audioPath).split(path.sep).join('/'),sha256:sha(fs.readFileSync(audioPath))};
  clip=path.join(out,'clip.mp4');frames=endFrame-startFrame;
  const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate',String(fps),'-c:v','png','-i','-',...(audioPath?['-ss',String(rangeStart),'-i',audioPath,'-map','0:v:0','-map','1:a:0','-c:a','aac','-b:a','128k','-t',String(frames/fps)]:[]),'-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',clip],{stdio:['pipe','ignore','pipe']});
  let err='';ff.stderr.on('data',b=>err+=b.toString());
  const done=new Promise((ok,bad)=>{ff.on('error',bad);ff.on('close',code=>code===0?ok():bad(Error('ffmpeg failed: '+err)));});done.catch(()=>{});
  ff.stdin.on('error',()=>{});
  try{for(let i=startFrame;i<endFrame;i++){
    const t=i/fps,file=path.join(out,'frames',String(i).padStart(8,'0')+'.png'),cached=checkpoint.frames[i];let buf;
    if(args.resume&&cached&&fs.existsSync(file)&&sha(fs.readFileSync(file))===cached.sha256){buf=fs.readFileSync(file);context.MV_FRAME_CHECKS=cached.metadata;inspectFrame(t);reused++;}
    else{buf=await frame(t,true);if(args.resume){fs.writeFileSync(file,buf);checkpoint.frames[i]={sha256:sha(buf),metadata:context.MV_FRAME_CHECKS?JSON.parse(JSON.stringify(context.MV_FRAME_CHECKS)):null};saveCheckpoint();}}
    await new Promise((ok,bad)=>ff.stdin.write(buf,e=>e?bad(e):ok()));
  }ff.stdin.end();await done;}
  catch(e){ff.kill();throw e;}
  const inspect=spawnSync('ffprobe',['-v','error','-count_frames','-show_streams','-show_format','-of','json',clip],{encoding:'utf8'});
  if(inspect.status!==0)throw Error('ffprobe failed: '+inspect.stderr);
  probe=JSON.parse(inspect.stdout);const video=probe.streams.find(s=>s.codec_type==='video');
  if(!video||video.width!==width||video.height!==height||Number(video.nb_read_frames)!==frames||Math.abs(Number(probe.format.duration)-frames/fps)>.12)throw Error('encoded metadata/frame count mismatch');
  if(audioPath&&!probe.streams.some(s=>s.codec_type==='audio'))throw Error('encoded audio missing');
  const decode=spawnSync('ffmpeg',['-v','error','-i',clip,'-f','null','-'],{encoding:'utf8'});if(decode.status!==0)throw Error('decode check failed: '+decode.stderr);
}
let version='unknown';try{version=require(path.join(path.dirname(require.resolve(args['canvas-module']?path.resolve(args['canvas-module']):'@napi-rs/canvas')),'package.json')).version;}catch{}
const report={schema_version:1,status:'passed',renderer:'node-canvas',runtime:{node:process.version,canvas:version,platform:os.platform(),arch:os.arch(),ffmpeg:spawnSync('ffmpeg',['-version'],{encoding:'utf8'}).stdout?.split('\n')[0]||null},width,height,fps,duration:outputDuration,timeline_duration:duration,range:bounds,frames,reused_frames:reused,project_acceptance:"not_assessed",production_stage:brief.phase,input_digest:manifest.digest,source_manifest:manifest.files,determinism:deterministic,stills,audio,elapsed_seconds:(performance.now()-start)/1000,encoded:probe?{video:true,audio:probe.streams.some(s=>s.codec_type==='audio'),full_decode:true}:null,scope:'Actual CPU Canvas2D frames, reverse-seek equality and encoded-file checks; not browser/p5/WebGL compatibility, real-song sync or aesthetic acceptance.'};
if(args.resume&&clip){checkpoint.clip_sha256=sha(fs.readFileSync(clip));saveCheckpoint();}
report.renderer_sha256=sha(fs.readFileSync(new URL(import.meta.url)));
frameAudit.schema_version=1;frameAudit.coverage=frameAudit.metadata_frames?(frames?'all_encoded_frames_with_declared_metadata':'selected_stills'):'no_declared_metadata';frameAudit.target=clip?{path:path.relative(project,clip).split(path.sep).join('/'),sha256:sha(fs.readFileSync(clip)),input_digest:manifest.digest}:null;report.frame_audit={path:path.relative(project,path.join(out,'frame-audit.json')).split(path.sep).join('/'),coverage:frameAudit.coverage,findings:frameAudit.findings.length};fs.writeFileSync(path.join(out,'frame-audit.json'),JSON.stringify(frameAudit,null,2)+'\n');
for(const n of fs.readdirSync(out).sort()){const f=path.join(out,n);if(n!=='render-report.json'&&fs.statSync(f).isFile())(report.artifacts??=[]).push({path:path.relative(project,f).split(path.sep).join('/'),sha256:sha(fs.readFileSync(f))});}
fs.writeFileSync(path.join(out,'render-report.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({status:report.status,renderer:report.renderer,frames,out,scope:report.scope}));

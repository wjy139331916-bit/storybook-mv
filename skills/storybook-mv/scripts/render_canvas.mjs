// Original optional CPU Canvas2D runner. This is not a Chrome/p5/WebGL compatibility test.
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import os from 'node:os';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import {spawn,spawnSync} from 'node:child_process';

const args={};
for(const a of process.argv.slice(2)){if(!a.startsWith('--'))throw Error('use --key=value arguments');const i=a.indexOf('=');args[a.slice(2,i<0?undefined:i)]=i<0?true:a.slice(i+1);}
if(args.help){console.log('node render_canvas.mjs --project=DIR --out=out/study [--canvas-module=/path/to/index.js] [--stills-only] [--times=0.5,3.6,4.8] [--audio=assets/test.wav]');process.exit(0);}
const project=path.resolve(args.project||'.'),out=path.resolve(project,args.out||'out/canvas-study');
const require=createRequire(path.join(project,'package.json'));
let canvasModule;
try{canvasModule=require(args['canvas-module']?path.resolve(args['canvas-module']):'@napi-rs/canvas');}
catch(e){throw Error('Install the selected optional runtime: npm install --save-exact @napi-rs/canvas@0.1.100, or pass --canvas-module. '+e.message);}
const {createCanvas}=canvasModule;
const sha=b=>createHash('sha256').update(b).digest('hex');
function inputs(){
  const files=[];
  function visit(p){if(!fs.existsSync(p))return;const st=fs.lstatSync(p);if(st.isSymbolicLink())throw Error('resolve input symlinks explicitly before a reproducible render');if(st.isDirectory()){for(const n of fs.readdirSync(p).sort())visit(path.join(p,n));}else if(st.isFile())files.push({path:path.relative(project,p).split(path.sep).join('/'),sha256:sha(fs.readFileSync(p))});}
  for(const n of ['src','data','assets','visual-spec.json','package.json','package-lock.json','render_canvas.mjs','render.mjs','studio.html'])visit(path.join(project,n));
  files.sort((a,b)=>Buffer.compare(Buffer.from(a.path),Buffer.from(b.path)));
  return {files,digest:sha(files.map(f=>f.path+'\0'+f.sha256+'\n').join(''))};
}
if(fs.existsSync(out)&&fs.readdirSync(out).length)throw Error('output directory must be empty; previous work preserved');
const manifest=inputs();
fs.mkdirSync(out,{recursive:true});
const context=vm.createContext({console,makeStudyCanvas:createCanvas,STUDY:undefined});
const entry=path.join(project,'src/render-entry.json');
const scripts=fs.existsSync(entry)?JSON.parse(fs.readFileSync(entry,'utf8')).scripts:['src/config.js','src/scene.js','src/data/lyrics.js','src/lyrics-overlay.js'];
for(const rel of scripts){const f=path.resolve(project,rel);if(!f.startsWith(project+path.sep))throw Error('render entry must stay inside project');vm.runInContext(fs.readFileSync(f,'utf8'),context,{filename:rel});}
const config=vm.runInContext('PROJECT',context),{width,height,duration}=config,fps=Number(args.fps||config.fps||30);
if(![width,height].every(n=>Number.isInteger(n)&&n>0&&n%2===0)||!Number.isFinite(duration)||duration<=0||!Number.isFinite(fps)||fps<=0)throw Error('invalid render dimensions/timing');
const canvas=createCanvas(width,height);
async function frame(t){canvas.width=width;canvas.height=height;const c=canvas.getContext('2d');await context.drawFrame(c,t,{width,height,project:config});if(context.overlayHook)context.overlayHook(c,t);if(context.STORY_LYRICS_OVERFLOW)throw Error(`caption overflow at ${t.toFixed(3)}s; fix layout before encoding`);return canvas.toBuffer('image/png');}
const ts=(args.times?String(args.times).split(',').map(Number):[0,duration*.5,duration*.9]);
if(!ts.length||ts.some(t=>!Number.isFinite(t)||t<0||t>duration))throw Error('invalid still times');
const probeTimes=[0,duration*.37,duration*.73],first=[];
for(const t of probeTimes)first.push(sha(await frame(t)));
const deterministic=[];
for(let i=probeTimes.length-1;i>=0;i--){const hash=sha(await frame(probeTimes[i]));deterministic.push({t:probeTimes[i],sha256:hash,passed:hash===first[i]});}
if(deterministic.some(x=>!x.passed))throw Error('same-time frames changed after reverse seek');
const stills=[];
for(let i=0;i<ts.length;i++){const f=`frame-${String(i).padStart(2,'0')}.png`,buf=await frame(ts[i]);fs.writeFileSync(path.join(out,f),buf);stills.push({t:ts[i],file:f,sha256:sha(buf)});}
// Exact same renderer draws the sheet; all cells share scale.
const cols=Math.min(3,ts.length),cw=480,ch=Math.round(cw*height/width),sheet=createCanvas(cw*cols,ch*Math.ceil(ts.length/cols));
const sc=sheet.getContext('2d');
for(let i=0;i<ts.length;i++){await frame(ts[i]);sc.drawImage(canvas,(i%cols)*cw,Math.floor(i/cols)*ch,cw,ch);}
fs.writeFileSync(path.join(out,'sheet.png'),sheet.toBuffer('image/png'));
let frames=0,probe=null,clip=null,audio=null;
const start=performance.now();
if(!args['stills-only']){
  const audioPath=args.audio?path.resolve(project,args.audio):null;
  if(audioPath&&!fs.existsSync(audioPath))throw Error('audio input missing');
  if(audioPath)audio={path:path.relative(project,audioPath).split(path.sep).join('/'),sha256:sha(fs.readFileSync(audioPath))};
  clip=path.join(out,'clip.mp4');frames=Math.round(duration*fps);
  const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate',String(fps),'-c:v','png','-i','-',...(audioPath?['-i',audioPath,'-map','0:v:0','-map','1:a:0','-c:a','aac','-b:a','128k','-t',String(frames/fps)]:[]),'-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',clip],{stdio:['pipe','ignore','pipe']});
  let err='';ff.stderr.on('data',b=>err+=b.toString());
  const done=new Promise((ok,bad)=>{ff.on('error',bad);ff.on('close',code=>code===0?ok():bad(Error('ffmpeg failed: '+err)));});done.catch(()=>{});
  ff.stdin.on('error',()=>{});
  try{for(let i=0;i<frames;i++){const buf=await frame(i/fps);await new Promise((ok,bad)=>ff.stdin.write(buf,e=>e?bad(e):ok()));}ff.stdin.end();await done;}
  catch(e){ff.kill();throw e;}
  const inspect=spawnSync('ffprobe',['-v','error','-count_frames','-show_streams','-show_format','-of','json',clip],{encoding:'utf8'});
  if(inspect.status!==0)throw Error('ffprobe failed: '+inspect.stderr);
  probe=JSON.parse(inspect.stdout);const video=probe.streams.find(s=>s.codec_type==='video');
  if(!video||video.width!==width||video.height!==height||Number(video.nb_read_frames)!==frames||Math.abs(Number(probe.format.duration)-frames/fps)>.12)throw Error('encoded metadata/frame count mismatch');
  if(audioPath&&!probe.streams.some(s=>s.codec_type==='audio'))throw Error('encoded audio missing');
  const decode=spawnSync('ffmpeg',['-v','error','-i',clip,'-f','null','-'],{encoding:'utf8'});if(decode.status!==0)throw Error('decode check failed: '+decode.stderr);
}
let version='unknown';try{version=require(path.join(path.dirname(require.resolve(args['canvas-module']?path.resolve(args['canvas-module']):'@napi-rs/canvas')),'package.json')).version;}catch{}
const report={schema_version:1,status:'passed',renderer:'node-canvas',runtime:{node:process.version,canvas:version,platform:os.platform(),arch:os.arch(),ffmpeg:spawnSync('ffmpeg',['-version'],{encoding:'utf8'}).stdout?.split('\n')[0]||null},width,height,fps,duration,frames,input_digest:manifest.digest,source_manifest:manifest.files,determinism:deterministic,stills,audio,elapsed_seconds:(performance.now()-start)/1000,encoded:probe?{video:true,audio:probe.streams.some(s=>s.codec_type==='audio'),full_decode:true}:null,scope:'Actual CPU Canvas2D frames, reverse-seek equality and encoded-file checks; not browser/p5/WebGL compatibility, real-song sync or aesthetic acceptance.'};
report.renderer_sha256=sha(fs.readFileSync(new URL(import.meta.url)));
for(const n of fs.readdirSync(out).sort()){const f=path.join(out,n);if(fs.statSync(f).isFile())(report.artifacts??=[]).push({path:path.relative(project,f).split(path.sep).join('/'),sha256:sha(fs.readFileSync(f))});}
fs.writeFileSync(path.join(out,'render-report.json'),JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify({status:report.status,renderer:report.renderer,frames,out,scope:report.scope}));

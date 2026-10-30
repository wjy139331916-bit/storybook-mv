// Original Remotion adapter; the local Python content/stage contract stays authoritative.
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {createHash} from 'node:crypto';
import {createRequire} from 'node:module';
import {spawnSync} from 'node:child_process';
import {assertProduction} from './production_gate.mjs';

const args={};for(const a of process.argv.slice(2)){if(!a.startsWith('--'))throw Error('use --key=value options');const i=a.indexOf('=');args[a.slice(2,i<0?undefined:i)]=i<0?true:a.slice(i+1);}
const known=new Set(['stills','clip','range','out','estimate','times','audio','chrome','soft-gl','fps','max-seconds','max-cache-bytes']);
for(const k of Object.keys(args))if(!known.has(k))throw Error('unsupported Remotion option: '+k);
for(const k of ['max-seconds','max-cache-bytes'])if(args[k]&&(!Number.isFinite(Number(args[k]))||Number(args[k])<=0))throw Error(k+' must be positive');
const project=process.cwd(),operation=args.stills?'stills':args.estimate?'estimate':'video',ts=String(args.stills||args.times||'0').split(',').map(Number);
const brief=assertProduction(project,{operation,still_count:ts.length,audio:args.audio||undefined});
if(brief.execution?.engine!=='remotion')throw Error('This adapter requires the selected Remotion route');
const require=createRequire(path.join(project,'package.json'));let bundle,renderer;
try{({bundle}=require('@remotion/bundler'));renderer=require('@remotion/renderer');require('react');require('react-dom');}
catch(e){throw Error('Selected Remotion dependencies are missing. Run npm ci with the bundled lockfile or npm install in this project, then run preflight.py --project <project> --strict --json. '+e.message);}
const hash=f=>createHash('sha256').update(fs.readFileSync(f)).digest('hex');
const config=JSON.parse(fs.readFileSync('src/project.json','utf8')),isTest=brief.execution.context==='tool-self-test';
if(args.fps)config.fps=Number(args.fps);
let audio=args.audio||brief.music?.audio||null;
if(audio){const p=spawnSync('ffprobe',['-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',audio],{encoding:'utf8'});if(p.status!==0)throw Error('Selected audio cannot be measured');if(!isTest)config.duration=Math.ceil(Number(p.stdout)*config.fps-1e-7)/config.fps;}
if(brief.phase==='animatic'&&config.fidelity!=='rough')throw Error('Set up a genuinely simplified rough scene; dimensions alone do not create an animatic');
let bounds=[0,config.duration];
if(brief.phase==='prototype'&&!isTest){const p=brief.workflow.packages.design;const pilot=JSON.parse(fs.readFileSync(p.path,'utf8')).pilot;bounds=[pilot.start,pilot.end];}
if(args.range||typeof args.clip==='string')bounds=String(args.range||args.clip).split(':').map(Number);
if(bounds.length!==2||bounds.some(n=>!Number.isFinite(n))||bounds[0]<0||bounds[0]>=bounds[1]||bounds[1]>config.duration+.001)throw Error('Invalid global source interval');
for(const n of bounds)if(Math.abs(n*config.fps-Math.round(n*config.fps))>1e-6)throw Error('Range endpoints must align to frames');
assertProduction(project,{operation,still_count:ts.length,audio:audio||undefined,duration:bounds[1]-bounds[0],timeline_duration:config.duration,timeline_range:bounds,resolution:[config.width,config.height],fps:config.fps});
if(ts.some(t=>!Number.isFinite(t)||t<0||t>=config.duration)||ts.length>12)throw Error('Use at most twelve in-range static times');
const output=path.resolve(project,args.out||(args.stills?'out/design-r1':'out/remotion/clip.mp4'));
if(output===project||!output.startsWith(project+path.sep))throw Error('Output must remain inside the selected project');
if(fs.existsSync(output)&&!isTest)throw Error('Existing output preserved; use a new output revision');
const temporary=fs.mkdtempSync(path.join(os.tmpdir(),'mv-remotion-'));
const publicDir=path.join(temporary,'public');fs.mkdirSync(publicDir);
const inputProps={config,cues:[],probe:isTest,audio:null,font:null};
if(audio){inputProps.audio='selected-audio'+path.extname(audio);fs.copyFileSync(audio,path.join(publicDir,inputProps.audio));}
if(brief.lyrics?.font?.path){const f=brief.lyrics.font;inputProps.font={family:f.family,file:'selected-font'+path.extname(f.path)};fs.copyFileSync(f.path,path.join(publicDir,inputProps.font.file));}
if(isTest&&fs.existsSync('src/probe-cues.json'))inputProps.cues=JSON.parse(fs.readFileSync('src/probe-cues.json','utf8'));
else if(['full','full-lines','key-lines'].includes(brief.lyrics?.mode)&&brief.lyrics.display_document?.path)inputProps.cues=JSON.parse(fs.readFileSync(brief.lyrics.display_document.path,'utf8')).cues||[];
const common={inputProps,browserExecutable:args.chrome||process.env.CHROME_PATH,chromiumOptions:args['soft-gl']?{gl:'swangle'}:{}};
let browser;const start=Date.now();
try{
  const serveUrl=await bundle({entryPoint:path.join(project,'src/index.jsx'),outDir:path.join(temporary,'bundle'),publicDir});
  browser=await renderer.openBrowser('chrome',{browserExecutable:common.browserExecutable,chromiumOptions:common.chromiumOptions});
  const browserFacts=(await browser.connection.send('Browser.getVersion')).value;
  const options={...common,serveUrl,puppeteerInstance:browser},composition=await renderer.selectComposition({...options,id:'MV'});
  if(composition.width!==config.width||composition.height!==config.height||composition.fps!==config.fps||composition.durationInFrames!==Math.round(config.duration*config.fps))throw Error('Composition metadata conflicts with approved dimensions/timebase');
  if(args.estimate||args['max-seconds']||args['max-cache-bytes']){
    const times=args.times?ts:[bounds[0]+.1*(bounds[1]-bounds[0]),(bounds[0]+bounds[1])/2,bounds[0]+.9*(bounds[1]-bounds[0])],samples=[];
    for(const t of times){const f=path.join(temporary,'estimate-'+samples.length+'.png'),s=Date.now();await renderer.renderStill({...options,composition,frame:Math.floor(t*config.fps),output:f,imageFormat:'png',overwrite:false});samples.push({time:t,milliseconds:Date.now()-s,png_bytes:fs.statSync(f).size});}
    const n=Math.round((bounds[1]-bounds[0])*config.fps),ms=samples.map(x=>x.milliseconds).sort((a,b)=>a-b),seconds=n*ms[Math.floor(ms.length/2)]/1000,bytes=n*Math.max(...samples.map(x=>x.png_bytes));
    if(args['max-seconds']&&seconds>Number(args['max-seconds'])||args['max-cache-bytes']&&bytes>Number(args['max-cache-bytes']))throw Error('Measured estimate exceeds declared budget');
    if(args.estimate)console.log(JSON.stringify({mode:'estimate',engine:'remotion',samples,range:bounds,frames:n,estimated_render_seconds:seconds,estimated_frame_cache_bytes:bytes,scope:'Still-sample extrapolation includes sample setup; not a speed guarantee. Allow encoding/review/repair overhead.'}));
  }
  if(!args.estimate&&args.stills){
    fs.mkdirSync(output,{recursive:true});for(const t of ts)await renderer.renderStill({...options,composition,frame:Math.round(t*config.fps),output:path.join(output,'t'+t.toFixed(2).replace('.','_')+'.png'),imageFormat:'png',overwrite:isTest});
    console.log(JSON.stringify({output,stills:ts,production_stage:brief.phase}));
  }else if(!args.estimate){
    fs.mkdirSync(path.dirname(output),{recursive:true});const tempVideo=path.join(temporary,'clip.mp4');
    await renderer.renderMedia({...options,composition,codec:'h264',outputLocation:tempVideo,frameRange:[Math.round(bounds[0]*config.fps),Math.round(bounds[1]*config.fps)-1],concurrency:1,overwrite:false,logLevel:'error'});
    const decoded=spawnSync('ffmpeg',['-v','error','-i',tempVideo,'-f','null','-'],{encoding:'utf8'});if(decoded.status!==0)throw Error('Actual output full decode failed: '+decoded.stderr);
    const probe=spawnSync('ffprobe',['-v','error','-show_streams','-show_format','-of','json',tempVideo],{encoding:'utf8'});if(probe.status!==0)throw Error('Actual output media probe failed');const media=JSON.parse(probe.stdout),actual=Number(media.format.duration);
    if(Math.abs(actual-(bounds[1]-bounds[0]))>.125||!media.streams.some(s=>s.codec_type==='video')||audio&&!media.streams.some(s=>s.codec_type==='audio'))throw Error('Actual output duration/streams differ from the selected scope');
    fs.copyFileSync(tempVideo,output);
    const versions={};for(const name of ['remotion','@remotion/renderer','@remotion/bundler','@remotion/cli','react','react-dom'])versions[name]=JSON.parse(fs.readFileSync(path.join(project,'node_modules',name,'package.json'),'utf8')).version;
    const report={schema_version:2,status:'passed',engine:'remotion',runtime:{node:process.version,platform:os.platform(),arch:os.arch(),browser:browserFacts.product,browser_revision:browserFacts.revision,browser_protocol:browserFacts.protocolVersion,browserExecutable:common.browserExecutable||'Remotion managed browser',versions,ffmpeg:spawnSync('ffmpeg',['-version'],{encoding:'utf8'}).stdout?.split('\n')[0]},production_stage:brief.phase,range:bounds,duration:actual,fps:config.fps,artifacts:[{path:path.relative(project,output).split(path.sep).join('/'),sha256:hash(output)}],audio:audio?{path:audio,sha256:hash(audio)}:null,encoded:{full_decode:true,video:true,audio:media.streams.some(s=>s.codec_type==='audio')},elapsed_seconds:(Date.now()-start)/1000,project_acceptance:'not_assessed',scope:'Actual selected Remotion composition/export only; no user taste, natural acting or sung-word accuracy certification.'};
    fs.writeFileSync(path.join(path.dirname(output),'render-report.json'),JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({output,...report}));
  }
}finally{await browser?.close({silent:true});fs.rmSync(temporary,{recursive:true,force:true});}

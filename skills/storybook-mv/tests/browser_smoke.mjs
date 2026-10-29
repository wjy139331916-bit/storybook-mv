// Actual local Chromium Canvas2D and review-page probe; not p5/WebGL certification.
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import {createRequire} from 'node:module';
import {spawn,spawnSync} from 'node:child_process';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.MV_PLAYWRIGHT_MODULE||'playwright');
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const output=process.argv[2]?path.resolve(process.argv[2]):fs.mkdtempSync(path.join(os.tmpdir(),'mv-browser-v34-'));
const project=path.join(output,'project'),python=process.env.MV_PYTHON||'python3';
const run=(cmd,args,options={})=>{const r=spawnSync(cmd,args,{encoding:'utf8',...options});if(r.status!==0)throw Error(r.stderr||r.stdout||String(r.error));return r.stdout;};
const sha=b=>createHash('sha256').update(b).digest('hex');
fs.mkdirSync(output,{recursive:true});
run(python,[path.join(root,'scripts/creative_probe.py'),project,'--case','abstract','--prepare-only','--tool-self-test']);
const browser=await chromium.launch({headless:true});
try{
  const page=await browser.newPage({viewport:{width:1280,height:900}}),unexpected=[];
  page.on('request',request=>{if(/^https?:/.test(request.url()))unexpected.push(request.url());});
  await page.goto(pathToFileURL(path.join(project,'studio.html')).href+'?render');
  await page.waitForFunction(()=>window.ready===true);
  const frame=async t=>Buffer.from((await page.evaluate(async t=>await window.renderAt(t),t)).split(',')[1],'base64');
  const a=await frame(2),b=await frame(8),again=await frame(2);
  if(sha(a)!==sha(again)||sha(a)===sha(b))throw Error('browser same-time determinism or visible-development probe failed');
  fs.writeFileSync(path.join(output,'browser-frame.png'),a);
  const video=path.join(project,'out/browser.mp4'),audio=path.join(project,'assets/original-score.wav');
  const ff=spawn('ffmpeg',['-y','-v','error','-f','image2pipe','-framerate','12','-c:v','png','-i','-','-i',audio,'-map','0:v:0','-map','1:a:0','-c:a','aac','-t','12','-c:v','libx264','-pix_fmt','yuv420p','-movflags','+faststart',video],{stdio:['pipe','ignore','pipe']});
  let error='';ff.stderr.on('data',b=>error+=b);
  const done=new Promise((ok,bad)=>{ff.on('error',bad);ff.on('close',c=>c?bad(Error(error)):ok());});done.catch(()=>{});
  for(let i=0;i<144;i++){const buf=await frame(i/12);await new Promise((ok,bad)=>ff.stdin.write(buf,e=>e?bad(e):ok()));}
  ff.stdin.end();await done;
  run('ffmpeg',['-v','error','-i',video,'-f','null','-']);
  // Render a neutral self-test review, without a fabricated project approval.
  const htmlCode="import sys,json;from pathlib import Path;sys.path.insert(0,sys.argv[1]);import review_workspace as w;from input_contracts import sha;p=Path(sys.argv[2]);v=p/'out/browser.mp4';preview=w.create_preview(p,v,p/'out/browser-preview.webm');d={'stage':'prototype','revision':'original-browser-probe','artifacts':[w.binding(p,v,'video'),preview]};(p/'out/review.html').write_text(w.review_html(p,d,{'sha256':sha(v)},['Original runtime self-test; no user acceptance or singing claim.'],64*1024*1024),encoding='utf-8')";
  run(python,['-c',htmlCode,path.join(root,'scripts'),project]);
  await page.goto(pathToFileURL(path.join(project,'out/review.html')).href);
  await page.waitForFunction(()=>document.querySelector('video').readyState>=2);
  await page.locator('video').evaluate(v=>{v.currentTime=2;});
  await page.waitForFunction(()=>{const v=document.querySelector('video');return v.readyState>=2&&Math.abs(v.currentTime-2)<.1&&!v.seeking;});
  await page.locator('video').click();
  await page.locator('video').evaluate(v=>v.play());
  await page.waitForFunction(()=>document.querySelector('video').currentTime>2.15);
  await page.locator('video').evaluate(v=>v.pause());
  if(process.env.MV_CJK_FONT){
    const data='data:font/otf;base64,'+fs.readFileSync(process.env.MV_CJK_FONT).toString('base64');
    await page.evaluate(async data=>{const face=new FontFace('MV Review QA','url('+JSON.stringify(data)+')');await face.load();document.fonts.add(face);document.body.style.fontFamily='"MV Review QA",sans-serif';},data);
  }
  await page.getByLabel('意见').fill('Original browser feedback probe');
  await page.getByRole('button',{name:'记录当前时间',exact:true}).click();
  if(!(await page.locator('#notes').innerText()).includes('Original browser feedback probe'))throw Error('timepoint feedback was not visible');
  const download=page.waitForEvent('download');await page.getByRole('button',{name:'导出时间点意见',exact:true}).click();
  const file=await download;const feedbackPath=path.join(output,'feedback.json');await file.saveAs(feedbackPath);
  const feedback=JSON.parse(fs.readFileSync(feedbackPath,'utf8'));
  if(feedback.is_user_approval!==false||feedback.target.sha256!==sha(fs.readFileSync(video))||feedback.notes.length!==1)throw Error('feedback identity or consent separation failed');
  fs.writeFileSync(path.join(project,'review.json'),JSON.stringify({scope:'prototype',target:{path:'out/browser.mp4',sha256:sha(fs.readFileSync(video))},checks:[],issues:[]}));
  run(python,[path.join(root,'scripts/review_notes.py'),feedbackPath,'--project',project,'--out',path.join(output,'merged-review.json')]);
  const merged=JSON.parse(fs.readFileSync(path.join(output,'merged-review.json'),'utf8'));
  if(merged.issues.length!==1||merged.issues[0].status!=='open'||merged.checks.length)throw Error('feedback merge changed acceptance/checks or lost the pending issue');
  if(unexpected.length)throw Error('offline probes made unexpected network requests');
  await page.screenshot({path:path.join(output,'review-page.png'),fullPage:true});
  const receipt={status:'passed',runtime:'Chromium '+browser.version(),platform:os.platform(),encoded_video_sha256:sha(fs.readFileSync(video)),frames:144,duration:12,reverse_seek:true,feedback_bound:true,feedback_merge_preserves_pending:true,browser_playback:'decoded, sought and advanced same-timeline WebM preview; original MP4 kept',review_cjk_font:process.env.MV_CJK_FONT?'selected local font':'system fonts',external_requests:0,scope:'Actual Chromium Canvas2D interface and offline review playback/feedback; not p5, WebGL, Windows, sung words or artistic acceptance.'};
  fs.writeFileSync(path.join(output,'browser-receipt.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify(receipt));
}finally{await browser.close();}

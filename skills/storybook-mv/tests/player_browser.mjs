// Optional real-browser test of the offline review player; generated/local fixtures only.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import http from 'node:http';
import os from 'node:os';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),require=createRequire(import.meta.url);
const {chromium}=require(process.env.MV_PLAYWRIGHT_MODULE||'playwright');
const temp=fs.mkdtempSync(path.join(os.tmpdir(),'mv-player-test-'));
const video=path.join(temp,'fixture.mp4');
const ff=spawnSync('ffmpeg',['-v','error','-f','lavfi','-i','testsrc2=size=320x180:rate=24:duration=3','-c:v','libx264','-pix_fmt','yuv420p',video],{encoding:'utf8'});if(ff.status!==0)throw Error(ff.stderr);
const html=fs.readFileSync(path.join(root,'assets/review-player.html'));
const server=http.createServer((req,res)=>{if(req.url!=='/'){res.writeHead(404);res.end();return;}res.setHeader('Content-Type','text/html; charset=utf-8');res.end(html);});
await new Promise(ok=>server.listen(0,'127.0.0.1',ok));
let browser;
try{
  browser=await chromium.launch({headless:true,...(process.env.MV_CHROME?{executablePath:process.env.MV_CHROME}:{}),args:['--no-sandbox']});
  const page=await browser.newPage({viewport:{width:390,height:844}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://127.0.0.1:'+server.address().port+'/');
  await page.locator('#fileA').setInputFiles(video);
  await page.waitForFunction(()=>!document.getElementById('add').disabled&&document.getElementById('a').duration===3);
  await page.locator('#next').click();
  await page.locator('#comment').fill('A timestamped original test note');
  await page.locator('#add').click();
  assert.equal(await page.locator('#notes li').count(),1);
  const download=page.waitForEvent('download');await page.locator('#export').click();
  const saved=await download,file=path.join(temp,'notes.json');await saved.saveAs(file);
  const notes=JSON.parse(fs.readFileSync(file,'utf8'));assert.match(notes.target.sha256,/^[a-f0-9]{64}$/);assert.equal(notes.notes.length,1);assert(notes.notes[0].range[1]>notes.notes[0].range[0]);
  await page.locator('#fileB').setInputFiles(video);await page.waitForFunction(()=>!document.getElementById('compare').hidden);assert.equal(await page.locator('#b').evaluate(v=>v.muted),true);
  const wrong={...notes,target:{...notes.target,sha256:'0'.repeat(64)}};
  await page.locator('#import').setInputFiles({name:'wrong.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(wrong))});await page.waitForFunction(()=>document.getElementById('state').textContent.includes('不一致'));
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
  assert.deepEqual(errors,[]);
  console.log(JSON.stringify({ok:true,browser:await browser.version(),checks:['load/hash local video','frame step','timestamp note','bound export','muted comparison','reject another target','phone viewport','no page errors']}));
}finally{if(browser)await browser.close();await new Promise(ok=>server.close(ok));fs.rmSync(temp,{recursive:true,force:true});}

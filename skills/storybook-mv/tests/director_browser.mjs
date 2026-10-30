// Actual seven-module interactions, saved-source roundtrip and bounded motion.
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {spawnSync} from 'node:child_process';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
const require=createRequire(import.meta.url),{chromium}=require(process.env.MV_PLAYWRIGHT_MODULE||'playwright');
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),out=path.resolve(process.argv[2]||'');
if(!process.argv[2]||fs.existsSync(out))throw Error('provide a new isolated output directory');
fs.mkdirSync(out,{recursive:true});
const python=process.env.MV_PYTHON||'python3';
function cli(...args){const r=spawnSync(python,[path.join(root,'scripts/director_workbench.py'),...args],{encoding:'utf8',env:{...process.env,PYTHONDONTWRITEBYTECODE:'1'}});if(r.status!==0)throw Error(r.stderr);return JSON.parse(r.stdout);}
const initial=cli('init','--tool-self-test','--out',path.join(out,'design'));
let video=process.argv[3]?path.resolve(process.argv[3]):path.join(out,'original-video.mp4');
if(!process.argv[3]){const f=spawnSync('ffmpeg',['-v','error','-f','lavfi','-i','testsrc2=size=320x180:rate=30:duration=2','-c:v','libx264','-pix_fmt','yuv420p',video],{encoding:'utf8'});if(f.status!==0)throw Error(f.stderr);}
const masterVideo=video;
if(!video.toLowerCase().endsWith('.webm')){const preview=path.join(out,'original-review.webm'),f=spawnSync('ffmpeg',['-v','error','-i',video,'-c:v','libvpx-vp9','-deadline','realtime','-cpu-used','8','-b:v','0','-crf','28','-c:a','libopus',preview],{encoding:'utf8'});if(f.status!==0)throw Error(f.stderr);video=preview;}
const browser=await chromium.launch({headless:true,...(process.env.CHROME_PATH?{executablePath:process.env.CHROME_PATH}:{}),args:['--no-sandbox']});
const page=await browser.newPage({viewport:{width:1400,height:1000}}),errors=[],external=[];
page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>{if(/^https?:/.test(r.url()))external.push(r.url());});
const get=()=>page.evaluate(()=>directorWorkbench.getModel());
async function change(id,value){await page.locator('#'+id).fill(String(value));await page.locator('#'+id).dispatchEvent('change');}
async function saveDownload(id,file){const p=page.waitForEvent('download');await page.locator('#'+id).click();await(await p).saveAs(file);return JSON.parse(fs.readFileSync(file,'utf8'));}
try{
 await page.goto(pathToFileURL(initial.editor).href);await page.waitForSelector('#pose-headTilt');
 if(!(await page.locator('#play').isDisabled()))throw Error('design motion is available before acceptance');
 await page.evaluate(()=>directorWorkbench.setTime(.8));
 await change('pose-headTilt',14);await change('pose-handX',1.1);await page.locator('#pose-easing').selectOption('smooth');
 let m=await get(),lead=m.scenes[0].layers.find(x=>x.id==='lead');
 if(!lead.keys.some(k=>Math.abs(k.time-.8)<1e-5&&k.headTilt===14)||lead.easing!=='smooth')throw Error('acting edits were not saved');
 await page.locator('#tab-scene').click();await page.locator('#layer-select').selectOption('lead');const box=await page.locator('#stage').boundingBox();const oldX=(await get()).scenes[0].layers.find(x=>x.id==='lead').x;
 await page.mouse.move(box.x+box.width*.3,box.y+box.height*.6);await page.mouse.down();await page.mouse.move(box.x+box.width*.3+26,box.y+box.height*.6+8);await page.mouse.up();
 if((await get()).scenes[0].layers.find(x=>x.id==='lead').x===oldX)throw Error('actual pointer drag did not move the selected scene layer');
 await change('camera-zoom',1.08);if(!(await get()).scenes[0].camera.keys.length)throw Error('camera key not saved');
 await page.locator('#tab-lyrics').click();
 for(const label of await page.locator('.file-field>span').all()){const r=await label.boundingBox();if(r.width<150||r.height>50)throw Error('lyric import label is squeezed into vertical text');}
 await page.locator('#cue-file').setInputFiles({name:'original.lrc',mimeType:'text/plain',buffer:Buffer.from('[00:00.20]Original line A\n[00:01.80]Original line B\n')});
 await page.waitForFunction(()=>directorWorkbench.getModel().cues[0]?.text==='Original line A');
 await change('cue-end',1.6);await page.locator('#add-word').click();await page.evaluate(()=>directorWorkbench.setTime(.8));await page.locator('#split-word-0').click();
 m=await get();if(m.cues[0].words.length!==2||m.cues[0].words[0].end!==.8||m.cues[0].timing_status!=='unverified')throw Error('explicit word split/retiming lost its draft status');
 const cueBox=await page.locator('.track button').first().boundingBox();await page.mouse.move(cueBox.x+cueBox.width/2,cueBox.y+cueBox.height/2);await page.mouse.down();await page.mouse.move(cueBox.x+cueBox.width/2+2,cueBox.y+cueBox.height/2);await page.mouse.up();
 await page.locator('#tab-storyboard').click();await page.evaluate(()=>directorWorkbench.setTime(2.5));
 await page.locator('#shot-list [data-shot="s02"]').getByRole('button',{name:'↑',exact:true}).click();m=await get();
 if(m.shots[0].id!=='s02'||m.shots[0].start!==0||m.shots.at(-1).end!==6)throw Error('storyboard reorder did not preserve global duration');
 await page.evaluate(()=>directorWorkbench.setTime(.5));await page.locator('#tab-transition').click();await page.locator('#transition-type').selectOption('match');await change('match-from-0',.25);await change('match-to-0',.7);
 if((await get()).shots[0].transition.type!=='match')throw Error('transition edit lost');
 const aBox=await page.locator('#transition-a').boundingBox();await page.mouse.click(aBox.x+aBox.width*.3,aBox.y+aBox.height*.5);
 if(Math.abs((await get()).shots[0].transition.from[0]-.3)>.02)throw Error('transition source anchor pointer failed');
 await page.locator('#tab-assets').click();await page.locator('#asset-list .card').filter({hasText:'原创构造角色'}).getByRole('button',{name:'编辑',exact:true}).click();await change('asset-color-shirt','#cc7755');
 const impact=await page.evaluate(()=>directorWorkbench.getImpact());if(!impact.changed_assets.includes('actor')||impact.affected_shots.length!==3)throw Error('shared asset impact did not identify actual shots');
 const px=spawnSync(python,['-c',"import sys,json;sys.path.insert(0,sys.argv[1]);from pixel_workbench import seed;print(json.dumps(seed()))",path.join(root,'scripts')],{encoding:'utf8'});
 if(px.status!==0)throw Error(px.stderr);
 await page.locator('#asset-file').setInputFiles({name:'original-character.json',mimeType:'application/json',buffer:Buffer.from(px.stdout)});
 await page.waitForFunction(()=>directorWorkbench.getModel().assets.some(a=>a.kind==='pixel'));const pixel=(await get()).assets.find(a=>a.kind==='pixel');
 await page.locator('#tab-scene').click();await page.locator('#insert-asset').selectOption(pixel.id);
 if(!(await get()).scenes.some(s=>s.layers.some(l=>l.asset_id===pixel.id)))throw Error('pixel asset did not enter actual scene');
 await page.locator('#tab-review').click();await page.locator('#review-file').setInputFiles(video);await page.waitForFunction(()=>document.getElementById('review-video').readyState>=2);await change('review-start',2);
 await page.locator('#compare-file').setInputFiles(video);await page.waitForFunction(()=>document.getElementById('compare-video').readyState>=2);
 await page.locator('#review-video').evaluate(v=>v.currentTime=.3);await page.locator('#note-text').fill('Original observation: inspect the hand/letter gap.');await page.locator('#add-note').click();
 const notes=await saveDownload('export-notes',path.join(out,'viewer-notes.json'));
 const hash=createHash('sha256').update(fs.readFileSync(video)).digest('hex');if(notes.target.sha256!==hash||Math.abs(notes.notes[0].range[0]-.3)>.03)throw Error('viewer notes are not bound to exact video/relative clip time');
 const repairs=await saveDownload('export-repairs',path.join(out,'repair-plan.json'));if(repairs.repairs[0].master_updated!==false||repairs.repairs[0].range[0]>2.3)throw Error('repair handles/source range missing');
 const edited=path.join(out,'design/edited.json');const saved=await saveDownload('save',edited);
 await page.locator('#model-file').setInputFiles(edited);await page.waitForTimeout(120);if(JSON.stringify((await get()).assets)!==JSON.stringify(saved.assets))throw Error('saved model did not roundtrip');
 const rebuilt=cli('build','--model',edited,'--out',path.join(out,'rebuilt'),'--tool-self-test');
 await page.goto(pathToFileURL(rebuilt.editor).href);await page.waitForSelector('#pose-headTilt');if((await get()).notes.length!==1)throw Error('CLI rebuild lost feedback');
 const injected={...saved,caps:{motion:true,phase:'full'},motion:true};await page.locator('#model-file').setInputFiles({name:'cannot-promote.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(injected))});
 if((await page.evaluate(()=>directorWorkbench.getCaps())).motion||!(await page.locator('#play').isDisabled()))throw Error('JSON import promoted the stage');
 await page.screenshot({path:path.join(out,'director-desktop.png'),fullPage:true});await page.setViewportSize({width:412,height:915});
 for(const id of ['acting','scene','lyrics','storyboard','transition','assets','review']){await page.locator('#tab-'+id).click();if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1))throw Error('phone page overflow in '+id);}
 await page.locator('#tab-scene').click();await page.screenshot({path:path.join(out,'director-phone.png'),fullPage:true});
 const motion=cli('build','--model',edited,'--out',path.join(out,'motion'),'--mode','motion','--tool-self-test');
 await page.goto(pathToFileURL(motion.editor).href);await page.waitForSelector('#pose-headTilt');await page.locator('#guides').uncheck();const first=await page.locator('#stage').evaluate(c=>c.toDataURL());
 await page.locator('#play').click();await page.waitForTimeout(250);const later=await page.locator('#stage').evaluate(c=>c.toDataURL());await page.locator('#play').click();if(first===later)throw Error('bounded playback did not change actual pixels');
 const projectRoot=path.resolve(path.dirname(masterVideo),'../..');let boundPreview=false;
 if(fs.existsSync(path.join(projectRoot,'brief.json'))&&fs.existsSync(path.join(projectRoot,'director-current.json'))){const bound=cli('build','--project',projectRoot,'--model','director-current.json','--out','plan/bound-preview-'+path.basename(out),'--mode','motion','--video',path.relative(projectRoot,masterVideo),'--video-range=2:4','--webm-preview');await page.goto(pathToFileURL(bound.editor).href);await page.waitForSelector('#pose-headTilt');await page.locator('#tab-review').click();await page.waitForFunction(()=>document.getElementById('review-video').readyState>=2);await page.locator('#review-video').evaluate(v=>v.currentTime=.4);await page.locator('#note-text').fill('Original bound preview observation.');await page.locator('#add-note').click();const n=await saveDownload('export-notes',path.join(out,'master-bound-notes.json'));if(n.target.sha256!==createHash('sha256').update(fs.readFileSync(masterVideo)).digest('hex'))throw Error('codec preview notes lost original MP4 binding');const range=await page.evaluate(()=>directorWorkbench.getCaps().range);if(range[0]!==2||range[1]!==4)throw Error('bound project preview expanded the pilot');boundPreview=true;}
 if(errors.length||external.length)throw Error(JSON.stringify({errors,external}));
 const receipt={status:'passed',runtime:'Chromium '+browser.version(),platform:process.platform,arch:process.arch,modules:expectedModules(),master_bound_codec_preview:boundPreview,model_sha256:createHash('sha256').update(fs.readFileSync(edited)).digest('hex'),checks:['acting key/curve controls','scene pointer drag and camera key','actual LRC import and explicit word split','storyboard reorder preserving full duration','paired transition anchor selection','shared asset usage and color propagation','pixel model import into scene','bound video comparison and relative-time feedback','repair range handles without master overwrite','browser JSON save/import and CLI rebuild','JSON cannot elevate design stage','bounded action playback changes pixels','seven-module portrait layout','zero external requests'],scope:'Original isolated editor and actual local video feedback; no user approval, natural acting or Android destination certification.'};
 fs.writeFileSync(path.join(out,'director-browser-receipt.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify(receipt));
}finally{await browser.close();}
function expectedModules(){return ['acting','scene','lyrics','storyboard','transition','assets','review'];}


/* Original shared director data and frame implementation; no approval inference. */
(function(root){
'use strict';
const clone=x=>JSON.parse(JSON.stringify(x)),clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x)),mix=(a,b,u)=>a+(b-a)*u;
const safe=s=>typeof s==='string'&&/^[A-Za-z0-9_-]{1,64}$/.test(s)&&!['__proto__','constructor','prototype'].includes(s);
const finite=(x,a=-1e6,b=1e6)=>typeof x==='number'&&Number.isFinite(x)&&x>=a&&x<=b;
const color=s=>typeof s==='string'&&/^#[0-9a-f]{6}$/i.test(s);
const poseFields=['x','y','scale','rotation','headTilt','lean','lookX','lookY','smile','blink','handX','handY','leftX','leftY','rightX','rightY'];
function demand(v,message){if(!v)throw Error(message);}
function validate(d){
 demand(d&&d.schema_version===1&&d.kind==='mv-director','需要 schema 1 的 mv-director 数据');
 demand(finite(d.duration,.1,7200)&&d.canvas&&Number.isInteger(d.canvas.width)&&Number.isInteger(d.canvas.height)&&d.canvas.width>=16&&d.canvas.height>=16&&d.canvas.width<=8192&&d.canvas.height<=8192&&d.canvas.width%2===0&&d.canvas.height%2===0&&finite(d.fps,1,120),'画幅、帧率或总时长无效');
 function safeTree(x,depth=0){demand(depth<48,'数据嵌套过深');if(x&&typeof x==='object')for(const [k,v]of Object.entries(x)){demand(!['__proto__','constructor','prototype'].includes(k),'不安全的字段');safeTree(v,depth+1);}else if(typeof x==='number')demand(Number.isFinite(x),'数据含非有限数');}safeTree(d);
 function ids(xs,max,label){demand(Array.isArray(xs)&&xs.length<=max,label+'数量无效');const set=new Set();for(const x of xs){demand(x&&safe(x.id)&&!set.has(x.id),label+' ID 需唯一且安全');set.add(x.id);}return set;}
 const assets=ids(d.assets,240,'素材'),scenes=ids(d.scenes,300,'场景');ids(d.shots,1000,'镜头');ids(d.cues,2000,'歌词');
 for(const a of d.assets){
  demand(['rig','shape','text','pixel'].includes(a.kind)&&typeof a.name==='string','素材类型或名称无效');
  if(a.kind==='rig'){demand(finite(a.heads,3.2,8)&&finite(a.unit,.01,.25),'角色比例无效');for(const v of Object.values(a.colors||{}))demand(color(v),'角色颜色需为 #RRGGBB');}
  if(a.kind==='shape')demand(['rect','ellipse','line'].includes(a.shape)&&finite(a.width,.001,4)&&finite(a.height,.001,4)&&color(a.fill),'形状尺寸或颜色无效');
  if(a.kind==='text')demand(typeof a.text==='string'&&a.text.length<=2000&&finite(a.size,.005,.5)&&color(a.fill),'文字素材无效');
  if(a.kind==='pixel'){demand(root.PixelModel,'缺少像素模型模块');root.PixelModel.validate(a.model);}
 }
 for(const s of d.scenes){s.contacts??=[];s.camera??={x:0,y:0,zoom:1,keys:[]};s.camera.keys??=[];demand(Array.isArray(s.contacts)&&s.contacts.length<=300,'接触数量无效');demand(color(s.background),'背景颜色无效');const ls=ids(s.layers,240,'图层');for(const l of s.layers){l.keys??=[];demand(assets.has(l.asset_id)&&finite(l.x,-2,3)&&finite(l.y,-2,3)&&finite(l.scale,.02,20)&&finite(l.rotation,-720,720)&&finite(l.z,-1000,1000),'图层变换或素材引用无效');keys(l.keys||[],poseFields);}
  const cam=s.camera||{x:0,y:0,zoom:1,keys:[]};demand(finite(cam.x,-2,2)&&finite(cam.y,-2,2)&&finite(cam.zoom,.1,10),'镜头参数无效');keys(cam.keys||[],['x','y','zoom']);
  for(const c of s.contacts||[]){demand(ls.has(c.a)&&ls.has(c.b)&&finite(c.start,0,d.duration)&&finite(c.end,0,d.duration)&&c.end>c.start&&finite(c.tolerance,.1,1000),'接触约束无效');demand(['origin','hand','left','right','head','grip','foot'].includes(c.anchor_a)&&['origin','hand','left','right','head','grip','foot'].includes(c.anchor_b),'接触锚点无效');}
 }
 function keys(xs,fields){demand(Array.isArray(xs)&&xs.length<=500,'关键帧数量无效');let t=-1;for(const k of xs){demand(finite(k.time,0,d.duration)&&k.time>t,'关键帧需按时间严格递增');t=k.time;for(const [n,v]of Object.entries(k))if(n!=='time'){demand(fields.includes(n)||n==='pixel_pose','未知关键帧属性');if(n==='pixel_pose')demand(safe(v),'像素姿态 ID 无效');else demand(finite(v,-1000,1000),'关键帧值无效');}if('scale'in k)demand(k.scale>=.02&&k.scale<=20,'缩放越界');if('zoom'in k)demand(k.zoom>=.1&&k.zoom<=10,'镜头缩放越界');}}
 let last=0;for(const s of d.shots){demand(scenes.has(s.scene_id)&&finite(s.start,0,d.duration)&&finite(s.end,0,d.duration)&&s.end>s.start&&Math.abs(s.start-last)<.001,'镜头应连续覆盖，且引用实际场景');last=s.end;const tr=s.transition||{type:'cut',duration:0};demand(['cut','crossfade','wipe','match'].includes(tr.type)&&finite(tr.duration,0,s.end-s.start),'转场类型或时长无效');for(const k of ['from','to'])if(tr[k])demand(Array.isArray(tr[k])&&tr[k].length===2&&tr[k].every(v=>finite(v,0,1)),'匹配点需归一化到 0..1');}
 if(d.shots.length)demand(Math.abs(last-d.duration)<.001,'镜头未覆盖完整时长');
 let end=0;for(const c of d.cues){demand(typeof c.text==='string'&&c.text.trim()&&finite(c.start,0,d.duration)&&finite(c.end,0,d.duration)&&c.end>c.start&&c.start>=end-.0001,'歌词时间无效或单轨歌词发生重叠');end=c.end;let wordEnd=c.start;for(const w of c.words||[]){demand(typeof w.text==='string'&&w.text.length&&finite(w.start,c.start,c.end)&&finite(w.end,c.start,c.end)&&w.end>w.start&&w.start>=wordEnd-.0001,'词段需位于句内并按时间排列');wordEnd=w.end;}}
 demand(d.caption&&typeof d.caption.enabled==='boolean'&&finite(d.caption.size,.005,.3)&&finite(d.caption.y,0,1)&&color(d.caption.color)&&color(d.caption.highlight),'字幕样式无效');
 demand(Array.isArray(d.notes)&&d.notes.length<=3000,'批注无效');for(const n of d.notes)demand(safe(n.id)&&Array.isArray(n.range)&&finite(n.range[0],0,d.duration)&&finite(n.range[1],0,d.duration)&&n.range[0]<n.range[1]&&typeof n.observation==='string'&&n.observation.trim()&&['minor','major','blocker'].includes(n.severity),'批注需包含有效时间段和观察');
 return d;
}
function tween(base,keys,t){let a={...base},b=null,ta=0;for(const k of keys||[]){if(k.time<=t){a={...a,...k};ta=k.time;}else{b=k;break;}}if(!b)return a;let u=clamp((t-ta)/(b.time-ta));if(base.easing==='smooth')u=u*u*(3-2*u);if(base.easing==='hold')u=0;for(const k of Object.keys(b))if(k!=='time'&&typeof b[k]==='number')a[k]=mix(Number(a[k]??b[k]),b[k],u);return a;}
function shotAt(d,t){return d.shots.find(s=>t>=s.start&&t<s.end)|| (t===d.duration?d.shots.at(-1):null);}
function uses(d,id){const sceneIds=new Set(d.scenes.filter(s=>s.layers.some(l=>l.asset_id===id)).map(s=>s.id));return d.shots.filter(s=>sceneIds.has(s.scene_id)).map(s=>s.id);}
function reorder(d,index,direction){const j=index+direction;if(j<0||j>=d.shots.length)return;[d.shots[index],d.shots[j]]=[d.shots[j],d.shots[index]];let time=0;for(const s of d.shots){const len=s.end-s.start;s.start=time;s.end=time+len;time=s.end;}return d;}
function retime(d,id,start,end){const c=d.cues.find(c=>c.id===id);demand(c&&end>start,'歌词时间无效');const ratio=(end-start)/(c.end-c.start);for(const w of c.words||[]){w.start=start+(w.start-c.start)*ratio;w.end=start+(w.end-c.start)*ratio;}c.start=start;c.end=end;c.timing_status='unverified';return d;}
function repair(d,note,handles=.25){const shots=d.shots.filter(s=>s.end>note.range[0]&&s.start<note.range[1]),start=Math.max(0,Math.floor((note.range[0]-handles)*d.fps)/d.fps),end=Math.min(d.duration,Math.ceil((note.range[1]+handles)*d.fps)/d.fps);return {issue_id:note.id,shot_ids:shots.map(s=>s.id),range:[start,end],handles,action:'render_new_revision_then_inspect_joins',master_updated:false};}
function impact(a,b){const changed=[];for(const x of b.assets)if(JSON.stringify(x)!==JSON.stringify(a.assets.find(y=>y.id===x.id)))changed.push(x.id);for(const x of a.assets)if(!b.assets.some(y=>y.id===x.id))changed.push(x.id);const shots=new Set(changed.flatMap(id=>[...uses(a,id),...uses(b,id)]));for(const s of b.scenes)if(JSON.stringify(s)!==JSON.stringify(a.scenes.find(x=>x.id===s.id)))for(const sh of b.shots.filter(x=>x.scene_id===s.id))shots.add(sh.id);if(JSON.stringify(a.shots)!==JSON.stringify(b.shots))for(const s of [...a.shots,...b.shots])shots.add(s.id);if(JSON.stringify(a.cues)!==JSON.stringify(b.cues)||JSON.stringify(a.caption)!==JSON.stringify(b.caption))for(const s of b.shots)shots.add(s.id);return {changed_assets:[...new Set(changed)],affected_shots:[...shots],review_status:'unreviewed',approvals_changed:false};}
function limb(a,b,l1,l2,bend=1){const dx=b[0]-a[0],dy=b[1]-a[1],raw=Math.hypot(dx,dy),r=clamp(raw,Math.abs(l1-l2)+1e-6,l1+l2-1e-6),theta=Math.atan2(dy,dx),alpha=Math.acos(clamp((l1*l1+r*r-l2*l2)/(2*l1*r),-1,1));return {joint:[a[0]+l1*Math.cos(theta+bend*alpha),a[1]+l1*Math.sin(theta+bend*alpha)],end:[a[0]+r*Math.cos(theta),a[1]+r*Math.sin(theta)],reachable:Math.abs(raw-r)<.002};}
function rig(c,a,p,unit,world,rough=false){
 const h=a.heads,ink=a.colors?.ink||'#293945',skin=a.colors?.skin||'#e7b698',shirt=a.colors?.shirt||'#548b95',pants=a.colors?.pants||'#3a4b61';
 const hip=[(p.lean||0)*.7,-(h-2.5)],neck=[(p.lean||0)*1.3,-h+1.4],hand=[p.handX??.72,p.handY??-2.1];
 const left=[p.leftX??-.2,p.leftY??0],right=[p.rightX??.2,p.rightY??0];
 const legs=[limb([hip[0]-.18,hip[1]],left,(h-2.5)*.54,(h-2.5)*.54,1),limb([hip[0]+.18,hip[1]],right,(h-2.5)*.54,(h-2.5)*.54,-1)],arm=limb([neck[0]+.38,neck[1]+.15],hand,.78,.75,-1);
 c.scale(unit,unit);c.lineCap='round';c.lineJoin='round';
 function path(points,width,col){c.beginPath();points.forEach((q,i)=>i?c.lineTo(...q):c.moveTo(...q));c.lineWidth=width;c.strokeStyle=col;c.stroke();}
 const geometry={hand:world(arm.end,unit),left:world(legs[0].end,unit),right:world(legs[1].end,unit),head:world([neck[0],-h+.5],unit),origin:world([0,0],unit),reachable:arm.reachable&&legs.every(x=>x.reachable),pose_signature:[...arm.joint,...arm.end,...legs.flatMap(x=>[...x.joint,...x.end]),p.headTilt||0,p.lookX||0,p.lookY||0,p.smile||0]};
 if(rough){legs.forEach((v,i)=>path([[hip[0]+(i?1:-1)*.18,hip[1]],v.joint,v.end],.08,ink));path([hip,neck],.08,ink);path([[neck[0]+.38,neck[1]+.15],arm.joint,arm.end],.07,ink);c.beginPath();c.ellipse(neck[0],-h+.5,.45,.53,0,0,Math.PI*2);c.lineWidth=.05;c.strokeStyle=ink;c.stroke();return geometry;}
 legs.forEach((v,i)=>{path([[hip[0]+(i?1:-1)*.18,hip[1]],v.joint,v.end],.26,pants);path([[v.end[0]-.13,v.end[1]],[v.end[0]+.23,v.end[1]]],.14,ink);});
 path([neck,hip],.78,shirt);path([[neck[0]-.36,neck[1]+.15],[-.67,-2.35],[-.55,-1.95]],.19,skin);path([[neck[0]+.38,neck[1]+.15],arm.joint,arm.end],.2,skin);
 c.save();c.translate(neck[0],-h+.5);c.rotate((p.headTilt||0)*Math.PI/180);c.fillStyle=skin;c.beginPath();c.ellipse(0,0,.45,.53,0,0,Math.PI*2);c.fill();c.fillStyle=ink;c.beginPath();c.ellipse(0,-.22,.46,.35,0,Math.PI,Math.PI*2);c.fill();
 const ex=clamp(p.lookX||0,-1,1)*.06,ey=clamp(p.lookY||0,-1,1)*.05;c.fillStyle=ink;for(const x of[-.17,.17]){c.beginPath();c.ellipse(x+ex,ey,.04,Math.max(.009,.05*(1-clamp(p.blink||0))),0,0,Math.PI*2);c.fill();}c.beginPath();c.moveTo(-.12,.22);c.quadraticCurveTo(0,.22+(p.smile||0)*.18,.12,.22);c.lineWidth=.035;c.strokeStyle=ink;c.stroke();c.restore();
 return geometry;
}
function pixel(c,a,p,H){const m=a.model,f=m.frames.find(f=>f.id===p.pixel_pose)||m.frames[0],px=root.PixelModel.pixels(m,f),scale=Math.max(1,Math.round(H*(a.unit||.18)/m.canvas.height));c.imageSmoothingEnabled=false;const foot=f.anchors.foot;for(let y=0;y<m.canvas.height;y++)for(let x=0;x<m.canvas.width;){const i=(y*m.canvas.width+x)*4;if(!px[i+3]){x++;continue;}let n=1;while(x+n<m.canvas.width&&[0,1,2,3].every(j=>px[i+j]===px[i+n*4+j]))n++;c.fillStyle='rgb('+[px[i],px[i+1],px[i+2]].join(',')+')';c.fillRect((x-foot[0])*scale,(y-foot[1])*scale,n*scale,scale);x+=n;}return {foot:[0,0],grip:[(f.anchors.grip[0]-foot[0])*scale,(f.anchors.grip[1]-foot[1])*scale]};}
function paintScene(c,d,shot,t,metrics,rough=false){
 const W=d.canvas.width,H=d.canvas.height,scene=d.scenes.find(s=>s.id===shot.scene_id);if(!scene)return;
 c.fillStyle=scene.background;c.fillRect(0,0,W,H);const local=clamp(t-shot.start,0,shot.end-shot.start)+(shot.scene_offset||0),cam=tween(scene.camera||{x:0,y:0,zoom:1},scene.camera?.keys,local);
 c.save();c.translate(W/2,H/2);c.scale(cam.zoom,cam.zoom);c.translate(-W/2-cam.x*W,-H/2-cam.y*H);
 const positions={};for(const layer of [...scene.layers].sort((a,b)=>a.z-b.z)){
  if(layer.visible===false)continue;const asset=d.assets.find(a=>a.id===layer.asset_id);if(!asset)continue;
  const p=tween(layer,layer.keys,local),angle=p.rotation*Math.PI/180,X=p.x*W,Y=p.y*H,S=p.scale;
  const world=(point,u=1)=>{const x=point[0]*u*S,y=point[1]*u*S;return [(X+x*Math.cos(angle)-y*Math.sin(angle)-W/2-cam.x*W)*cam.zoom+W/2,(Y+x*Math.sin(angle)+y*Math.cos(angle)-H/2-cam.y*H)*cam.zoom+H/2];};
  c.save();c.translate(X,Y);c.rotate(angle);c.scale(S,S);let anchors={origin:world([0,0])};
  if(asset.kind==='rig'){
   const u=H*asset.unit;
   for(const [pin,x,k]of[['pin_left',-.2,'left'],['pin_right',.2,'right']])if(layer[pin]){const target=[(layer.x*W+x*u-X)/S,(layer.y*H-Y)/S];p[k+'X']=(target[0]*Math.cos(angle)+target[1]*Math.sin(angle))/u;p[k+'Y']=(-target[0]*Math.sin(angle)+target[1]*Math.cos(angle))/u;}
   anchors=rig(c,asset,p,u,world,rough);metrics.actors.push({id:layer.id,reachable:anchors.reachable,pose_signature:anchors.pose_signature,view:1});
   const q=world([-1,-asset.heads-1],u),r=world([1,0],u);metrics.boxes.push({id:layer.id,kind:'action',x:Math.min(q[0],r[0]),y:Math.min(q[1],r[1]),w:Math.abs(r[0]-q[0]),h:Math.abs(r[1]-q[1])});
  }else if(asset.kind==='pixel'){let a;if(rough){const f=asset.model.frames.find(f=>f.id===p.pixel_pose)||asset.model.frames[0],size=Math.max(1,Math.round(H*(asset.unit||.18)/asset.model.canvas.height));c.strokeStyle='#597572';c.lineWidth=2;c.strokeRect(-f.anchors.foot[0]*size,-f.anchors.foot[1]*size,asset.model.canvas.width*size,asset.model.canvas.height*size);a={foot:[0,0],grip:[(f.anchors.grip[0]-f.anchors.foot[0])*size,(f.anchors.grip[1]-f.anchors.foot[1])*size]};}else a=pixel(c,asset,p,H);anchors={origin:world([0,0]),foot:world(a.foot),grip:world(a.grip)};}
  else if(asset.kind==='text'){const fs=asset.size*H;c.font=fs+'px '+(asset.font||'sans-serif');c.textAlign='center';c.textBaseline='middle';c.fillStyle=asset.fill;c.fillText(asset.text,0,0);const w=c.measureText(asset.text).width,q=world([-w/2,-fs/2]);metrics.boxes.push({id:layer.id,kind:'text',x:q[0],y:q[1],w:w*S*cam.zoom,h:fs*S*cam.zoom});}
  else{const w=asset.width*W,h=asset.height*H;c.fillStyle=asset.fill;c.strokeStyle=asset.fill;c.lineWidth=Math.max(1,h);if(asset.shape==='rect')c.fillRect(-w/2,-h/2,w,h);if(asset.shape==='ellipse'){c.beginPath();c.ellipse(0,0,w/2,h/2,0,0,Math.PI*2);c.fill();}if(asset.shape==='line'){c.beginPath();c.moveTo(-w/2,0);c.lineTo(w/2,0);c.stroke();}anchors.grip=world([0,0]);}
  positions[layer.id]=anchors;c.restore();
 }
 c.restore();
 for(const x of scene.contacts||[])if(local>=x.start&&local<=x.end){const a=positions[x.a]?.[x.anchor_a],b=positions[x.b]?.[x.anchor_b];if(a&&b)metrics.contacts.push({id:x.id||x.a+'-'+x.b,a,b,distance:Math.hypot(a[0]-b[0],a[1]-b[1]),tolerance:x.tolerance});else metrics.warnings.push('接触锚点缺失：'+x.a+' / '+x.b);}
 metrics.positions=positions;
}
function drawCaptions(c,d,t,metrics){if(!d.caption.enabled)return;const cue=d.cues.find(x=>t>=x.start&&t<x.end);if(!cue)return;const W=d.canvas.width,H=d.canvas.height,fs=d.caption.size*H;c.save();c.font=fs+'px '+(d.caption.font||'sans-serif');c.textAlign='left';c.textBaseline='middle';const max=W*.86,lines=[];let line='';for(const ch of Array.from(cue.text)){if(ch==='\n'||(line&&c.measureText(line+ch).width>max)){lines.push(line);line='';if(ch==='\n')continue;}line+=ch;}if(line)lines.push(line);let offset=0;
 for(let i=0;i<lines.length;i++){const str=lines[i],w=c.measureText(str).width,x=(W-w)/2,y=H*d.caption.y+(i-(lines.length-1)/2)*fs*1.3;c.fillStyle=d.caption.color;c.fillText(str,x,y);const completed=(cue.words||[]).filter(w=>t>=w.end).map(w=>w.text).join('');const active=(cue.words||[]).find(w=>t>=w.start&&t<w.end);const progress=completed+(active?active.text:'');const prefix=progress.slice(offset,offset+str.length);if(prefix){c.save();c.beginPath();c.rect(x,y-fs*.65,c.measureText(prefix).width,fs*1.3);c.clip();c.fillStyle=d.caption.highlight;c.fillText(str,x,y);c.restore();}offset+=str.length;metrics.boxes.push({id:cue.id+'-'+i,kind:'text',x,y:y-fs*.65,w,h:fs*1.3});}
 if(lines.length>2)metrics.warnings.push('字幕超过两行，需检查阅读时长与构图');c.restore();}
function render(c,d,t,{width=d.canvas.width,height=d.canvas.height,guides=false,captions=true,rough=false}={}){
 const metrics={shot_id:null,actors:[],boxes:[],contacts:[],warnings:[],positions:{}};c.save();c.scale(width/d.canvas.width,height/d.canvas.height);c.clearRect(0,0,d.canvas.width,d.canvas.height);const shot=shotAt(d,t);
 if(shot){metrics.shot_id=shot.id;paintScene(c,d,shot,t,metrics,rough);const idx=d.shots.indexOf(shot),next=d.shots[idx+1],tr=shot.transition||{type:'cut',duration:0};if(next&&tr.type!=='cut'&&tr.duration>0&&t>=shot.end-tr.duration){const u=clamp((t-shot.end+tr.duration)/tr.duration);if(tr.type==='match'){const a=tr.from||[.5,.5],b=tr.to||[.5,.5];c.save();c.translate((b[0]-a[0])*d.canvas.width*u,(b[1]-a[1])*d.canvas.height*u);paintScene(c,d,shot,t,{actors:[],boxes:[],contacts:[],warnings:[],positions:{}},rough);c.restore();}c.save();if(tr.type==='wipe'){c.beginPath();c.rect(0,0,d.canvas.width*u,d.canvas.height);c.clip();}else c.globalAlpha=u;paintScene(c,d,next,next.start,{actors:[],boxes:[],contacts:[],warnings:[],positions:{}},rough);c.restore();}}
 if(captions)drawCaptions(c,d,t,metrics);
 if(guides){c.lineWidth=1;c.strokeStyle='#e77845';for(const [id,anchors]of Object.entries(metrics.positions))for(const [key,p]of Object.entries(anchors))if(Array.isArray(p)&&p.length===2&&p.every(Number.isFinite)){c.beginPath();c.arc(p[0],p[1],4,0,Math.PI*2);c.stroke();}for(const x of metrics.contacts){c.strokeStyle=x.distance>x.tolerance?'#ce5246':'#508876';c.beginPath();c.moveTo(...x.a);c.lineTo(...x.b);c.stroke();}}
 c.restore();const sx=width/d.canvas.width,sy=height/d.canvas.height;metrics.boxes=metrics.boxes.map(b=>({...b,x:b.x*sx,y:b.y*sy,w:b.w*sx,h:b.h*sy}));metrics.contacts=metrics.contacts.map(x=>({...x,distance:x.distance*Math.max(sx,sy),tolerance:x.tolerance*Math.max(sx,sy)}));return metrics;
}
root.MVDirector={clamp,clone,validate,tween,shotAt,uses,reorder,retime,repair,impact,render,drawCaptions,poseFields};if(typeof module!=='undefined')module.exports=root.MVDirector;
})(typeof globalThis!=='undefined'?globalThis:this);

'use strict';
const $=id=>document.getElementById(id),M=PixelModel;
let model=M.validate(M.copy(PIXEL_CONFIG.model)),frameIndex=0,layerIndex=0,colorKey=Object.keys(model.palette)[0],eraser=false,zoom=6,history=[],playing=false,playToken=0,painting=false;
const motion=PIXEL_CONFIG.motion===true,limit=motion?64:12;
const frame=()=>model.frames[frameIndex],layer=()=>model.layers[layerIndex],part=()=>{frame().layers??={};return frame().layers[layer().id]??={};};
function message(s,bad=false){$('status').textContent=s;$('status').classList.toggle('danger',bad);}
function checkpoint(){history.push(JSON.stringify(model));if(history.length>40)history.shift();}
function stop(){playing=false;playToken++;$('play').textContent='播放';}
function change(fn){stop();checkpoint();try{fn();M.validate(model);draw();message('已修改，请保存数据');}catch(e){model=JSON.parse(history.pop());draw();message(e.message,true);}}
function draw(){
  const f=frame(),l=layer(),p=f.layers?.[l.id]||{};M.draw($('art'),model,f);
  $('art').style.width=(model.canvas.width*zoom)+'px';$('art').style.height='auto';$('grid').style.backgroundSize=`${100/model.canvas.width}% ${100/model.canvas.height}%`;
  $('zoom-label').textContent=zoom+'×';$('model-name').textContent=model.name||'像素角色';$('dimensions').textContent=`${model.canvas.width} × ${model.canvas.height} · ${model.frames.length} 个姿势`;
  $('part-name').textContent=l.name||l.id;$('dx').value=p.dx||0;$('dy').value=p.dy||0;$('visible').checked=p.visible??l.visible??true;$('flip').checked=p.flip_x||false;$('duration').value=f.duration_ms;
  const a=f.anchors[$('anchor').value];$('anchor-x').value=a[0];$('anchor-y').value=a[1];$('color').value=model.palette[colorKey];$('color-key').textContent=colorKey+' · '+model.palette[colorKey];
  $('layers').replaceChildren();model.layers.forEach((l,i)=>{const b=document.createElement('button');b.className='layer'+(i===layerIndex?' active':'');b.textContent=l.name||l.id;b.onclick=()=>{stop();layerIndex=i;draw();};$('layers').append(b);});
  $('palette').replaceChildren();Object.entries(model.palette).forEach(([key,col])=>{const b=document.createElement('button');b.className='swatch'+(colorKey===key?' active':'');b.style.background=col;b.setAttribute('aria-label','颜色 '+key);b.onclick=()=>{colorKey=key;draw();};$('palette').append(b);});
  $('poses').replaceChildren();model.frames.forEach((f,i)=>{const b=document.createElement('button');b.className='pose'+(i===frameIndex?' active':'');const c=document.createElement('canvas');M.draw(c,model,f);b.append(c,document.createTextNode(f.label||f.id));b.onclick=()=>{stop();frameIndex=i;draw();};$('poses').append(b);});
  const chosen=$('action').value;$('action').replaceChildren();Object.keys(model.actions||{}).forEach(key=>{const o=document.createElement('option');o.value=key;o.textContent=key;$('action').append(o);});if(Object.hasOwn(model.actions||{},chosen))$('action').value=chosen;
  $('duplicate').disabled=model.frames.length>=limit;$('undo').disabled=!history.length;
}
function position(event){const r=$('art').getBoundingClientRect();return [Math.floor((event.clientX-r.left)*model.canvas.width/r.width),Math.floor((event.clientY-r.top)*model.canvas.height/r.height)];}
function paint(event){
  const [x,y]=position(event),l=layer(),p=part(),rows=p.rows||l.rows,ox=l.origin[0]+(p.dx||0),oy=l.origin[1]+(p.dy||0),xx=p.flip_x?rows[0].length-1-(x-ox):x-ox,yy=y-oy;
  if(xx<0||yy<0||yy>=rows.length||xx>=rows[0].length)return;
  const target=$('pose-only').checked?(p.rows??=rows.slice()):l.rows;
  target[yy]=target[yy].slice(0,xx)+(eraser?'.':colorKey)+target[yy].slice(xx+1);draw();message('已绘制，请保存数据');
}
$('art').addEventListener('pointerdown',e=>{if(e.button!==0)return;e.preventDefault();stop();checkpoint();painting=true;$('art').setPointerCapture(e.pointerId);paint(e);});
$('art').addEventListener('pointermove',e=>{if(painting)paint(e);});
for(const name of ['pointerup','pointercancel','lostpointercapture'])$('art').addEventListener(name,()=>painting=false);
$('pen').onclick=()=>{eraser=false;$('pen').classList.add('active');$('erase').classList.remove('active');};$('erase').onclick=()=>{eraser=true;$('erase').classList.add('active');$('pen').classList.remove('active');};
$('undo').onclick=()=>{stop();if(history.length){model=M.validate(JSON.parse(history.pop()));frameIndex=Math.min(frameIndex,model.frames.length-1);layerIndex=Math.min(layerIndex,model.layers.length-1);if(!Object.hasOwn(model.palette,colorKey))colorKey=Object.keys(model.palette)[0];draw();message('已撤销');}};
$('color').onchange=e=>change(()=>model.palette[colorKey]=e.target.value);
for(const key of ['dx','dy'])$(key).onchange=e=>change(()=>part()[key]=Number(e.target.value));
$('visible').onchange=e=>change(()=>part().visible=e.target.checked);$('flip').onchange=e=>change(()=>part().flip_x=e.target.checked);
$('duration').onchange=e=>change(()=>frame().duration_ms=Number(e.target.value));
$('anchor').onchange=draw;for(const [key,index]of [['anchor-x',0],['anchor-y',1]])$(key).onchange=e=>change(()=>frame().anchors[$('anchor').value][index]=Number(e.target.value));
$('grid-toggle').onchange=e=>$('grid').hidden=!e.target.checked;$('zoom-in').onclick=()=>{zoom=Math.min(12,zoom+1);draw();};$('zoom-out').onclick=()=>{zoom=Math.max(2,zoom-1);draw();};
$('duplicate').onclick=()=>change(()=>{const f=M.copy(frame());let i=model.frames.length+1;while(model.frames.some(f=>f.id==='pose-'+i))i++;f.id='pose-'+i;f.label='新姿势 '+i;model.frames.push(f);frameIndex=model.frames.length-1;});
function download(name,blob){const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);message('已导出 '+name);}
function png(canvas,name){canvas.toBlob(b=>{if(b)download(name,b);else message('图片导出失败',true);},'image/png');}
$('save').onclick=()=>download('character.json',new Blob([JSON.stringify(model,null,2)+'\n'],{type:'application/json'}));
$('png').onclick=()=>{const c=document.createElement('canvas');M.draw(c,model,frame());png(c,'pose-'+frame().id+'.png');};
$('board').onclick=()=>{const c=document.createElement('canvas'),s=4,w=model.canvas.width*s+24,h=model.canvas.height*s+40,n=Math.min(4,model.frames.length);c.width=w*n;c.height=h*Math.ceil(model.frames.length/n);const ctx=c.getContext('2d');ctx.fillStyle='#f4f1e9';ctx.fillRect(0,0,c.width,c.height);ctx.imageSmoothingEnabled=false;model.frames.forEach((f,i)=>{const p=document.createElement('canvas');M.draw(p,model,f);const x=i%n*w+12,y=Math.floor(i/n)*h+12;ctx.drawImage(p,x,y,model.canvas.width*s,model.canvas.height*s);ctx.fillStyle='#293945';ctx.font='12px sans-serif';ctx.fillText(f.label||f.id,x,y+model.canvas.height*s+18);});png(c,'design-board.png');};
$('sheet').onclick=()=>{if(!motion)return message('当前仅允许静态设计',true);const c=document.createElement('canvas');c.width=model.canvas.width*model.frames.length;c.height=model.canvas.height;const ctx=c.getContext('2d');model.frames.forEach((f,i)=>{const p=document.createElement('canvas');M.draw(p,model,f);ctx.drawImage(p,i*model.canvas.width,0);});png(c,'sprites.png');};
$('load').onclick=()=>$('file').click();$('file').onchange=async e=>{stop();const f=e.target.files[0];if(!f)return;try{if(f.size>2*1024*1024)throw Error('文件不能超过 2 MiB');const next=M.validate(JSON.parse(await f.text()));if(next.frames.length>limit)throw Error('当前阶段最多允许 '+limit+' 个静态姿势');checkpoint();model=next;frameIndex=layerIndex=0;colorKey=Object.keys(model.palette)[0];draw();message('已导入；验收状态不会改变');}catch(e){message(e.message,true);}e.target.value='';};
$('play').onclick=()=>{if(!motion)return message('请先完成设计与脚本验收',true);if(playing){stop();return;}const ids=model.actions?.[$('action').value];if(!ids?.length)return message('数据中尚未定义动作',true);const frames=ids.map(id=>model.frames.find(f=>f.id===id)),total=frames.reduce((s,f)=>s+f.duration_ms,0);if(total>8000)return message('动作预览应控制在 8 秒内',true);playing=true;$('play').textContent='暂停';const token=++playToken,start=performance.now();function tick(now){if(!playing||token!==playToken)return;let t=(now-start)%total;let f=frames.at(-1);for(const candidate of frames){if(t<candidate.duration_ms){f=candidate;break;}t-=candidate.duration_ms;}M.draw($('art'),model,f);requestAnimationFrame(tick);}requestAnimationFrame(tick);};
$('phase').textContent=motion?'动作编辑 · 待审看':'设计阶段 · 静态编辑';$('motion-controls').hidden=!motion;$('sheet').hidden=!motion;$('notice').textContent=motion?'本页只预览角色动作，不代表样片、全曲粗剪或成片已验收。':'先审看角色造型与完整方案。动作播放和精灵图导出在设计验收后开放。';
window.pixelWorkbench={getModel:()=>M.copy(model),motionEnabled:motion,validate:M.validate};draw();

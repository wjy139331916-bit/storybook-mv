// Original pixel model renderer. No dependencies, services or approval inference.
(function(root){
  'use strict';
  const copy = value => JSON.parse(JSON.stringify(value));
  const int = (n,a,b) => Number.isInteger(n) && n>=a && n<=b;
  const id = s => typeof s==='string' && /^[A-Za-z0-9_-]{1,48}$/.test(s) && !['__proto__','constructor','prototype'].includes(s);
  function validate(d){
    if(!d || d.schema_version!==1 || d.kind!=='pixel-character')throw Error('需要有效的像素角色数据');
    const w=d.canvas?.width,h=d.canvas?.height;
    if(!int(w,8,128)||!int(h,8,128))throw Error('画布尺寸必须在 8—128 像素之间');
    if(!d.palette || Array.isArray(d.palette) || typeof d.palette!=='object' || !int(Object.keys(d.palette).length,1,32) || Object.entries(d.palette).some(([k,v])=>!/^[A-Za-z0-9]$/.test(k)||typeof v!=='string'||!/^#[0-9a-fA-F]{6}$/.test(v)))throw Error('调色板需要 1—32 个有效颜色');
    const rows = r=>{if(!Array.isArray(r)||!int(r.length,1,h)||typeof r[0]!=='string'||!int(r[0].length,1,w)||r.some(s=>typeof s!=='string'||s.length!==r[0].length||Array.from(s).some(c=>c!=='.'&&!Object.hasOwn(d.palette,c))))throw Error('像素矩阵或颜色不正确');};
    if(!Array.isArray(d.layers)||!int(d.layers.length,1,24)||!Array.isArray(d.frames)||!int(d.frames.length,1,64))throw Error('部件或姿势数量不正确');
    const layers=new Set(),frames=new Set();
    for(const l of d.layers){if(!l||!id(l.id)||layers.has(l.id)||!Array.isArray(l.origin)||l.origin.length!==2||l.origin.some(n=>!int(n,-128,128))||('visible' in l&&typeof l.visible!=='boolean'))throw Error('部件编号、位置或可见性不正确');layers.add(l.id);rows(l.rows);}
    for(const f of d.frames){
      if(!f||!id(f.id)||frames.has(f.id)||!int(f.duration_ms,40,2000))throw Error('姿势编号或显示时间不正确');frames.add(f.id);
      if(f.layers && (Array.isArray(f.layers)||typeof f.layers!=='object'))throw Error('姿势部件不正确');
      for(const [key,p] of Object.entries(f.layers||{})){if(!layers.has(key)||!p||typeof p!=='object'||Array.isArray(p)||!int(p.dx??0,-128,128)||!int(p.dy??0,-128,128)||['flip_x','visible'].some(k=>k in p&&typeof p[k]!=='boolean'))throw Error('姿势位移不正确');if('rows' in p)rows(p.rows);}
      if(!f.anchors||!Object.hasOwn(f.anchors,'foot')||!Object.hasOwn(f.anchors,'grip')||Object.entries(f.anchors).some(([k,v])=>!id(k)||!Array.isArray(v)||v.length!==2||v.some(n=>!int(n,-128,256))))throw Error('缺少脚底或持物基准点');
    }
    if(d.actions && (Array.isArray(d.actions)||typeof d.actions!=='object'||Object.keys(d.actions).length>24||Object.entries(d.actions).some(([k,a])=>!id(k)||!Array.isArray(a)||!int(a.length,1,64)||a.some(f=>!frames.has(f)))))throw Error('动作引用了不存在的姿势');
    return d;
  }
  function pixels(d,f){
    const w=d.canvas.width,h=d.canvas.height,rgba=new Uint8ClampedArray(w*h*4);
    for(const l of d.layers){const p=f.layers?.[l.id]||{};if(!(p.visible??l.visible??true))continue;const rows=p.rows||l.rows,ox=l.origin[0]+(p.dx||0),oy=l.origin[1]+(p.dy||0);
      rows.forEach((r,y)=>Array.from(r).forEach((key,x)=>{const xx=ox+(p.flip_x?r.length-1-x:x),yy=oy+y;if(key==='.'||xx<0||xx>=w||yy<0||yy>=h)return;const c=d.palette[key],i=(yy*w+xx)*4;rgba[i]=parseInt(c.slice(1,3),16);rgba[i+1]=parseInt(c.slice(3,5),16);rgba[i+2]=parseInt(c.slice(5,7),16);rgba[i+3]=255;}));
    }return rgba;
  }
  function draw(canvas,d,f){canvas.width=d.canvas.width;canvas.height=d.canvas.height;const c=canvas.getContext('2d');c.putImageData(new ImageData(pixels(d,f),canvas.width,canvas.height),0,0);return canvas;}
  root.PixelModel={copy,validate,pixels,draw};
  if(typeof module!=='undefined')module.exports=root.PixelModel;
})(globalThis);

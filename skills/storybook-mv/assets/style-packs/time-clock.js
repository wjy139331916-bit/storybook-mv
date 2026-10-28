// Original TIME -> clock -> TIME construction, 14 reusable geometric strokes.
// Same geometry and timing in both treatments. No fonts, images or randomness.
(() => {
 const PI=Math.PI, TAU=PI*2, bg='#F2EEE4', ink='#172D38', accent='#EF6A3B', guide='#D9D6CC';
 const clamp=x=>Math.max(0,Math.min(1,x));
 const ease=x=>{x=clamp(x);return x*x*x*(x*(x*6-15)+10);};
 const mix=(a,b,p)=>a+(b-a)*p;
 const source=[
  [216,260,296,260],[296,260,376,260],[296,260,296,450],
  [440,260,560,260],[500,260,500,450],[440,450,560,450],
  [624,450,624,260],[624,260,718,356],[718,356,812,260],[812,260,812,450],
  [876,260,876,450],[876,260,1064,260],[876,355,1032,355],[876,450,1064,450]
 ];
 const color=i=>i===12?accent:ink;
 function clockLine(i,t){
  const cx=640,cy=355;
  if(i<12){const a=-PI/2+i*TAU/12;return [cx+Math.cos(a)*163,cy+Math.sin(a)*163,cx+Math.cos(a)*193,cy+Math.sin(a)*193];}
  const g=clamp((t-2)/2.1),a=i===12?-PI/6+TAU*1.25*g:-5*PI/6+TAU*1.25*g/12;
  const len=i===12?143:100;
  return [cx,cy,cx+Math.cos(a)*len,cy+Math.sin(a)*len];
 }
 function pose(a,b,p,i){
  const am=[(a[0]+a[2])/2,(a[1]+a[3])/2],bm=[(b[0]+b[2])/2,(b[1]+b[3])/2];
  const aa=Math.atan2(a[3]-a[1],a[2]-a[0]),ba=Math.atan2(b[3]-b[1],b[2]-b[0]);
  let da=((ba-aa+PI) % TAU+TAU)%TAU-PI;
  const angle=aa+da*p,len=mix(Math.hypot(a[2]-a[0],a[3]-a[1]),Math.hypot(b[2]-b[0],b[3]-b[1]),p);
  const bow=Math.sin(PI*p)*(i%2?22:-22),x=mix(am[0],bm[0],p)+bow,y=mix(am[1],bm[1],p)-Math.sin(PI*p)*18;
  return [x-Math.cos(angle)*len/2,y-Math.sin(angle)*len/2,x+Math.cos(angle)*len/2,y+Math.sin(angle)*len/2];
 }
 function rasterLine(c,a,w,col){
  // Integer logical cells; no Canvas antialiasing in pixel treatment.
  const [x1,y1,x2,y2]=a,dx=x2-x1,dy=y2-y1,l2=dx*dx+dy*dy,r=w/2;
  const x0=Math.floor(Math.min(x1,x2)-r),xN=Math.ceil(Math.max(x1,x2)+r),y0=Math.floor(Math.min(y1,y2)-r),yN=Math.ceil(Math.max(y1,y2)+r);
  c.fillStyle=col;
  for(let y=y0;y<yN;y++)for(let x=x0;x<xN;x++){
   const u=l2?clamp(((x+.5-x1)*dx+(y+.5-y1)*dy)/l2):0;
   if((x+.5-x1-u*dx)**2+(y+.5-y1-u*dy)**2<=r*r)c.fillRect(x,y,1,1);
  }
 }
 function render(c,t,pixel){
  const S=pixel?.25:1;
  c.fillStyle=bg;c.fillRect(0,0,1280*S,720*S);
  const drawLine=(a,w,col)=>{
   if(pixel)rasterLine(c,a.map(v=>Math.round(v*S)),Math.max(1,Math.round(w*S)),col);
   else {c.strokeStyle=col;c.lineWidth=w;c.lineCap='square';c.beginPath();c.moveTo(a[0],a[1]);c.lineTo(a[2],a[3]);c.stroke();}
  };
  // A quiet framing system is constant in both versions; clock ring is a reveal.
  drawLine([80,80,128,80],3,ink);drawLine([80,80,80,128],3,ink);
  drawLine([1200,640,1152,640],3,ink);drawLine([1200,640,1200,592],3,ink);
  const enter=ease((t-1.25)/.7),leave=1-ease((t-4.1)/.7),ring=enter*leave;
  if(ring>0){
   if(pixel){
    const bayer=[0,8,2,10,12,4,14,6,3,11,1,9,15,7,13,5];c.fillStyle=guide;
    for(let y=33;y<145;y++)for(let x=104;x<216;x++){
     const d=Math.hypot(x+.5-160,y+.5-88.75);
     if(Math.abs(d-53)<.48&&bayer[(x%4)+(y%4)*4]/16<ring)c.fillRect(x,y,1,1);
    }
   }else{c.save();c.globalAlpha=ring;c.strokeStyle=guide;c.lineWidth=2;c.beginPath();c.arc(640,355,212,0,TAU);c.stroke();c.restore();}
  }
  const lines=[];
  for(let i=0;i<source.length;i++){
   let p=0;
   if(t<4.1)p=ease((t-.65-i*.019)/1.1);
   else p=1-ease((t-4.1-(13-i)*.019)/1.0);
   const a=pose(source[i],clockLine(i,t),p,i),w=mix(26,i<12?15:i===12?17:23,p);
   lines.push({id:i,line:a,width:w,morph:p,color:color(i)});drawLine(a,w,color(i));
  }
  const pin=ease((t-1.75)/.25)*(1-ease((t-4.1)/.3));
  if(pin>0){
   if(pixel){if(pin>.5){c.fillStyle=accent;c.fillRect(158,87,4,4);}}
   else {c.save();c.globalAlpha=pin;c.fillStyle=accent;c.beginPath();c.arc(640,355,8,0,TAU);c.fill();c.restore();}
  }
  globalThis.TYPE_COMPONENTS=lines;
  const points=lines.flatMap(o=>[[o.line[0],o.line[1]],[o.line[2],o.line[3]]]);
  const box={id:'time-transform',kind:'text',x:Math.min(...points.map(p=>p[0]))-18,y:Math.min(...points.map(p=>p[1]))-18,w:0,h:0};
  box.w=Math.max(...points.map(p=>p[0]))+18-box.x;box.h=Math.max(...points.map(p=>p[1]))+18-box.y;
  globalThis.MV_FRAME_CHECKS={boxes:[box],actors:[],phase:t<.65?'TIME':t<2?'transform-to-clock':t<4.1?'clock-flow':t<5.35?'transform-to-word':'TIME'};
 }
 let low=null;
 globalThis.drawFrame=(c,t,settings)=>{
  const pixel=PROJECT.treatment==='pixel';
  // Pixel timing uses held pairs of frames: intentional 15 fps motion in 30 fps file.
  t=pixel?Math.floor((t+1e-6)*15)/15:t;
  if(pixel){
   if(!low)low=typeof makeStudyCanvas==='function'?makeStudyCanvas(320,180):Object.assign(document.createElement('canvas'),{width:320,height:180});
   render(low.getContext('2d'),t,true);c.imageSmoothingEnabled=false;c.drawImage(low,0,0,1280,720);
  }else render(c,t,false);
 };
})();

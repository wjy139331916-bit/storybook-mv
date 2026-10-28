// Host-neutral deterministic Canvas2D frame interface for the shared renderer.
const W=PROJECT.width||1920,H=PROJECT.height||1080,DUR=PROJECT.duration;
(function(root){
  const canvas=document.getElementById('out');canvas.width=W;canvas.height=H;
  const c=canvas.getContext('2d'),scene=document.createElement('canvas');scene.width=W;scene.height=H;const scn=scene.getContext('2d');
  root.renderAt=async function(t,type='image/png',quality=.92){
    if(!Number.isFinite(t)||t<0||t>DUR)throw Error('frame time outside prototype');
    if(scn.reset)scn.reset();else scene.width=W;
    await root.drawFrame(scn,t,{width:W,height:H,project:PROJECT});
    if(c.reset)c.reset();else canvas.width=W;c.drawImage(scene,0,0);
    if(root.overlayHook)root.overlayHook(c,t);
    return canvas.toDataURL(type,quality);
  };
  root.renderSheet=async function(times,cols=3,width=640,crop=null,at=null){
    if(at)throw Error('this adapter supports screen-space --crop; world-following crops require an explicit project adapter');
    if(!Array.isArray(times)||!times.length||!Number.isFinite(cols)||cols<1||width<=0)throw Error('invalid sheet');
    const sw=crop?crop[2]:W,sh=crop?crop[3]:H;if(sw<=0||sh<=0)throw Error('invalid crop');
    const cellHeight=Math.round(width*sh/sw),sheet=document.createElement('canvas');sheet.width=cols*width;sheet.height=Math.ceil(times.length/cols)*cellHeight;
    const sc=sheet.getContext('2d'),ms=[];sc.fillStyle='#fff';sc.fillRect(0,0,sheet.width,sheet.height);
    for(let i=0;i<times.length;i++){
      const start=performance.now();await root.renderAt(times[i]);ms.push(performance.now()-start);
      sc.drawImage(canvas,crop?crop[0]:0,crop?crop[1]:0,sw,sh,(i%cols)*width,Math.floor(i/cols)*cellHeight,width,cellHeight);
    }
    return {url:sheet.toDataURL('image/jpeg',.92),ms};
  };
  root.gpuInfo=()=> 'Canvas2D adapter; GPU acceleration not asserted';
  root.ready=true;
  if(!location.search.includes('render')){
    const s=document.getElementById('scrub'),label=document.getElementById('tt');s.max=DUR;
    s.oninput=()=>root.renderAt(Number(s.value)).then(()=>{label.textContent=Number(s.value).toFixed(2)+'s';});
    root.renderAt(0);
  }
})(globalThis);

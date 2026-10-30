// Original Canvas sprite adapter. Loading assets never grants production approval.
(function(root){
  function frameAt(meta,action,seconds){
    const ids=meta.actions?.[action];if(!ids?.length||!Number.isFinite(seconds))throw Error('unknown action or invalid time');
    const frames=ids.map(id=>{const f=meta.frames.find(x=>x.id===id);if(!f||!(f.duration_ms>0))throw Error('invalid sprite timing');return f;}),total=frames.reduce((s,f)=>s+f.duration_ms,0);
    let t=((seconds*1000)%total+total)%total;for(const f of frames){if(t<f.duration_ms)return f;t-=f.duration_ms;}return frames.at(-1);
  }
  function draw(ctx,image,meta,frame,x,y,scale=1,anchor='foot'){
    if(!meta.sheet||!Number.isInteger(scale)||scale<1||![x,y].every(Number.isFinite))throw Error('sprite needs a sheet, integer scale and finite position');
    const f=typeof frame==='string'?meta.frames.find(f=>f.id===frame):frame,a=f?.anchors?.[anchor],r=f?.rect;if(!r||!a)throw Error('unknown frame or anchor');
    ctx.save();ctx.imageSmoothingEnabled=false;ctx.drawImage(image,r.x,r.y,r.w,r.h,Math.round(x-a[0]*scale),Math.round(y-a[1]*scale),r.w*scale,r.h*scale);ctx.restore();
    return {foot:f.anchors.foot.map((v,i)=>[x,y][i]+(v-a[i])*scale),grip:f.anchors.grip.map((v,i)=>[x,y][i]+(v-a[i])*scale)};
  }
  root.PixelSprite={frameAt,draw};if(typeof module!=='undefined')module.exports=root.PixelSprite;
})(globalThis);

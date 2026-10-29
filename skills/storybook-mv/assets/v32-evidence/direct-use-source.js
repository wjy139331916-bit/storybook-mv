// Original geometry, independently rendered in the current-skill project.
// Pure timestamp state; every evaluation is independent of seek history.
(() => {
  const clamp01=x=>Math.max(0,Math.min(1,x));
  const smooth=x=>{x=clamp01(x);return x*x*(3-2*x);};
  const directions=[[0,-1],[1,0],[0,1],[-1,0]];
  globalThis.circleState=function(t){
    const frame=Math.max(0,Math.min(23,t*12));
    let spread;
    if(frame<=2)spread=0;
    else if(frame<10)spread=smooth((frame-2)/8);
    else if(frame<=13)spread=1;
    else if(frame<21)spread=1-smooth((frame-13)/8);
    else spread=0;
    return {spread,radius:56-28*spread,distance:118*spread};
  };
  globalThis.drawFrame=function(c,t,{width,height}){
    const state=circleState(t),cx=width/2,cy=height/2;
    c.fillStyle='#ffffff';c.fillRect(0,0,width,height);
    c.fillStyle='#000000';
    const shapes=state.spread===0?[[0,0]]:directions,boxes=[];
    for(let i=0;i<shapes.length;i++){
      const [dx,dy]=shapes[i],x=cx+dx*state.distance,y=cy+dy*state.distance;
      c.beginPath();c.arc(x,y,state.radius,0,Math.PI*2);c.fill();
      boxes.push({id:'circle-'+i,kind:'action',x:x-state.radius,y:y-state.radius,w:2*state.radius,h:2*state.radius});
    }
    globalThis.MV_FRAME_CHECKS={boxes,actors:[],abstract_state:{...state,visible_primitives:shapes.length}};
  };
})();

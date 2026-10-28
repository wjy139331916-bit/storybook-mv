// Original limited stylized-human example renderer; not a universal anatomy/acting engine.
(function(root){
  function path(c,points,stroke,width,fill=null){c.beginPath();points.forEach((p,i)=>i?c.lineTo(...p):c.moveTo(...p));if(fill){c.closePath();c.fillStyle=fill;c.fill();}if(stroke){c.strokeStyle=stroke;c.lineWidth=width;c.stroke();}}
  function actor(c,{x,y,scale=40,heads=4.8,facing=1,walk=null,hand=[.62,-2.1],look=1,palette={shirt:'#42727b',skin:'#d7aa88',hair:'#303949',trousers:'#435161'},paper=false}={}){
    const parent=c.getTransform(),parentScale=Math.hypot(parent.a,parent.b);
    if(Math.abs(parentScale-Math.hypot(parent.c,parent.d))>1e-6||Math.abs(parent.a*parent.c+parent.b*parent.d)>1e-6||Math.abs(facing)!==1)throw Error('example actor requires uniform parent scale and a drawn left/right view');
    const M=root.MVMotion,leg=(heads-2.5)/2,hip=[0,(walk?walk.hipY:-2*leg+.04)+(walk?walk.bob:0)],shoulder=[.36,-heads+1.35];
    const left=walk?[walk.left.x,walk.left.y]:[-.2,0],right=walk?[walk.right.x,walk.right.y]:[.2,0];
    const legs=[M.twoBone([hip[0]-.13,hip[1]],left,leg,leg,-1),M.twoBone([hip[0]+.13,hip[1]],right,leg,leg,-1)];
    const arm=M.twoBone(shoulder,hand,.85,.85,1),farHand=[-.5+(walk?walk.swing*.2:0),-2.15];
    c.save();c.translate(x,y);c.scale(scale,scale);c.scale(facing,1);c.lineCap='round';c.lineJoin='round';
    if(paper){c.shadowColor='rgba(30,48,55,.18)';c.shadowBlur=2;c.shadowOffsetX=1;c.shadowOffsetY=2;}
    c.fillStyle='rgba(25,35,55,.12)';c.beginPath();c.ellipse(0,.04,.65,.10,0,0,Math.PI*2);c.fill();
    for(let i=0;i<2;i++){
      const hipPart=[hip[0]+(i? .13:-.13),hip[1]],k=legs[i];
      path(c,[hipPart,k.joint,k.end],i?palette.trousers:'#61727c',.26);
      path(c,[[k.end[0]-.12,k.end[1]],[k.end[0]+.23,k.end[1]]],'#e8e7df',.15);
    }
    path(c,[[-.34,shoulder[1]+.08],[-.43,-2.7],farHand],palette.shirt,.23);
    path(c,[[-.43,shoulder[1]],[.4,shoulder[1]+.02],[.36,hip[1]+.1],[-.34,hip[1]+.08]],paper?'#2e3f4a':null,.025,palette.shirt);
    path(c,[[0,-heads+1],[0,shoulder[1]]],palette.skin,.27);
    path(c,[shoulder,arm.joint,arm.end],palette.shirt,.23);
    c.fillStyle=palette.skin;c.beginPath();c.arc(...arm.end,.13,0,Math.PI*2);c.fill();
    c.fillStyle=palette.skin;c.beginPath();c.ellipse(0,-heads+.53,.45,.53,0,0,Math.PI*2);c.fill();
    c.fillStyle=palette.hair;c.beginPath();c.ellipse(-.04,-heads+.26,.48,.32,-.1,Math.PI,2*Math.PI);c.lineTo(.37,-heads+.52);c.lineTo(.23,-heads+.15);c.lineTo(-.39,-heads+.5);c.closePath();c.fill();
    c.fillStyle='#243640';c.beginPath();c.arc(.12+.08*look,-heads+.53,.035,0,Math.PI*2);c.fill();
    path(c,[[.15,-heads+.78],[.28,-heads+.76]],'#8d6355',.025);
    c.restore();
    const world=p=>{const xx=x+p[0]*scale*facing,yy=y+p[1]*scale;return [parent.a*xx+parent.c*yy+parent.e,parent.b*xx+parent.d*yy+parent.f];};
    const screenScale=scale*parentScale;
    return {hand:world(arm.end),reachable:arm.reachable&&legs.every(k=>k.reachable),feet:[world(legs[0].end),world(legs[1].end)],limbs:[
      {a:world(shoulder),b:world(arm.joint),length_px:.85*screenScale},{a:world(arm.joint),b:world(arm.end),length_px:.85*screenScale},
      ...legs.flatMap((k,i)=>[{a:world([hip[0]+(i?.13:-.13),hip[1]]),b:world(k.joint),length_px:leg*screenScale},{a:world(k.joint),b:world(k.end),length_px:leg*screenScale}])],head_px:screenScale,height_px:heads*screenScale,heads};
  }
  root.MVActors={actor,path};
})(globalThis);

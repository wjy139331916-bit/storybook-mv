// Original optional stylized acting study. Views and proportions here are examples, not project defaults.
(function(root){
  const M=root.MVMotion,clamp=M.clamp,mix=M.mix;
  function performance(t,{start=0,duration=2,emotion='calm',gaze=[1,0],gesture='rest'}={}){
    if(!Number.isFinite(t)||!(duration>0))throw Error('invalid acting time');
    const u=clamp((t-start)/duration),anticipate=Math.sin(Math.PI*clamp(u/.2)),action=M.ease((u-.15)/.6),settle=Math.sin(Math.PI*clamp((u-.7)/.3));
    const blinkPhase=((t+1.73)%4.1+4.1)%4.1,blink=blinkPhase<.13?Math.sin(Math.PI*blinkPhase/.13):0;
    const mood={calm:[0,.1,0],curious:[-.16,.05,-.04],sad:[.18,-.14,.12],hopeful:[-.07,.3,-.05],surprised:[-.25,0,-.06]}[emotion];
    if(!mood)throw Error('unknown example emotion');
    const hand=gesture==='wave'?[.7+.32*Math.sin(t*9)*action,-3.85]:gesture==='offer'?[mix(.6,1.75,action),mix(-2.1,-2.9,action)]:gesture==='chest'?[.18,-3.0]:[.6,-2.1];
    return {gaze:[clamp(gaze[0],-1,1),clamp(gaze[1],-1,1)],blink,brow:mood[0],smile:mood[1],headTilt:mood[2]+anticipate*.035-settle*.018,lean:anticipate*-.025+settle*.012,hand,phase:{anticipation:anticipate,action,settle}};
  }
  function actor(c,{id='actor',x,y,size=40,view=1,pose,walk=null,hand=null,palette={shirt:'#427f85',skin:'#edc2a3',hair:'#293641',trousers:'#3c505e'},paper=false}={}){
    if(!pose||![x,y,size,view].every(Number.isFinite)||size<=0||Math.abs(view)>1)throw Error('invalid performance actor');
    const parent=c.getTransform(),sx=Math.hypot(parent.a,parent.b),sy=Math.hypot(parent.c,parent.d);
    if(Math.abs(sx-sy)>1e-6||Math.abs(parent.a*parent.c+parent.b*parent.d)>1e-6)throw Error('acting example needs uniform parent transforms');
    const facing=view>=0?1:-1,profile=Math.abs(view),headWidth=mix(.62,.48,profile),heads=4.95,leg=1.15;
    const hip=[pose.lean,walk?walk.hipY+walk.bob:-2.26],shoulder=[.34+pose.lean,-3.45],nearHand=hand||pose.hand;
    const foots=walk?[[walk.left.x,walk.left.y],[walk.right.x,walk.right.y]]:[[-.2,0],[.2,0]];
    const legs=foots.map((f,i)=>M.twoBone([hip[0]+(i?.13:-.13),hip[1]],f,leg,leg,-1));
    const arm=M.twoBone(shoulder,nearHand,.88,.88,1),farHand=[-.46+ (walk?walk.swing*.22:0),-2.15];
    const line=(pts,col,width)=>{c.beginPath();pts.forEach((p,i)=>i?c.lineTo(...p):c.moveTo(...p));c.strokeStyle=col;c.lineWidth=width;c.stroke();};
    c.save();c.translate(x,y);c.scale(size*facing,size);c.lineCap='round';c.lineJoin='round';
    if(paper){c.shadowColor='rgba(24,40,48,.15)';c.shadowBlur=3;c.shadowOffsetY=2;}
    c.fillStyle='rgba(26,40,50,.12)';c.beginPath();c.ellipse(0,.03,.62,.095,0,0,Math.PI*2);c.fill();
    legs.forEach((k,i)=>{line([[hip[0]+(i?.13:-.13),hip[1]],k.joint,k.end],i?palette.trousers:'#61747a',.25);line([[k.end[0]-.12,k.end[1]],[k.end[0]+.24,k.end[1]]],'#f8f0dc',.14);});
    line([[-.3,-3.4],[-.47,-2.83],farHand],palette.shirt,.23);
    c.beginPath();c.moveTo(-.43,-3.4);c.quadraticCurveTo(0,-3.55,.48,-3.4);c.lineTo(.4,hip[1]+.06);c.lineTo(-.4,hip[1]+.08);c.closePath();c.fillStyle=palette.shirt;c.fill();
    line([[-.25,-2.72],[-.25,-2.47],[.04,-2.47],[.04,-2.72]],'rgba(248,239,219,.45)',.035);
    line([[pose.lean,-3.8],[pose.lean,-3.35]],palette.skin,.24);
    line([shoulder,arm.joint,arm.end],palette.shirt,.23);c.fillStyle=palette.skin;c.beginPath();c.arc(...arm.end,.12,0,Math.PI*2);c.fill();
    c.save();c.translate(pose.lean,-4.25);c.rotate(pose.headTilt);
    c.fillStyle=palette.skin;c.beginPath();c.ellipse(0,0,headWidth,.64,0,0,Math.PI*2);c.fill();
    c.fillStyle=palette.hair;c.beginPath();c.ellipse(-.04,-.29,headWidth+.03,.35,0,Math.PI,Math.PI*2);c.lineTo(headWidth*.75,-.01);c.lineTo(headWidth*.4,-.28);c.lineTo(-headWidth,.07);c.closePath();c.fill();
    const eyeY=.015+pose.gaze[1]*.045,eyeX=.04+.16*profile+pose.gaze[0]*.045;
    const eye=(xx)=>{if(pose.blink>.45)line([[xx-.045,eyeY],[xx+.045,eyeY]],'#263744',.025);else{c.fillStyle='#263744';c.beginPath();c.ellipse(xx,eyeY,.027,.04,0,0,Math.PI*2);c.fill();}line([[xx-.075,eyeY-.13+pose.brow],[xx+.06,eyeY-.12-pose.brow*.4]],palette.hair,.027);};
    eye(eyeX);if(profile<.65)eye(-.18+pose.gaze[0]*.04);
    c.strokeStyle='#995c50';c.lineWidth=.025;c.beginPath();c.moveTo(.05,.26);c.quadraticCurveTo(.17,.26+pose.smile*.2,.27,.23);c.stroke();
    c.restore();c.restore();
    const world=p=>{const xx=x+p[0]*size*facing,yy=y+p[1]*size;return [parent.a*xx+parent.c*yy+parent.e,parent.b*xx+parent.d*yy+parent.f];};
    const local=[[-.65,-heads],[Math.max(.65,arm.end[0]+.15),-heads],[Math.max(.65,arm.end[0]+.15),.12],[-.65,.12]],corners=local.map(world),xx=corners.map(p=>p[0]),yy=corners.map(p=>p[1]);
    return {id,hand:world(arm.end),feet:legs.map(k=>world(k.end)),reachable:arm.reachable&&legs.every(k=>k.reachable),pose_signature:[...arm.joint,...arm.end,...legs.flatMap(k=>[...k.joint,...k.end]),pose.brow,pose.smile,pose.headTilt],box:{id,kind:'action',x:Math.min(...xx),y:Math.min(...yy),w:Math.max(...xx)-Math.min(...xx),h:Math.max(...yy)-Math.min(...yy)},view};
  }
  root.MVPerformance={performance,actor};
})(globalThis);

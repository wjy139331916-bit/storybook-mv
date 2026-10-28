// Same content, camera, timing and geometry across optional style studies. Original code only.
(function(root){
  function scene(c,t,settings){
    const o=root.STUDY,M=root.MVMotion,T=root.MVTransitions,w=settings.width,h=settings.height;
    const pixel=o.style==='pixel',paper=o.style==='paper';
    let target=c,small=null;
    if(pixel){let factor=Math.max(1,Math.ceil(Math.max(w,h)/320));while(w%factor||h%factor)factor--;small=root.makeStudyCanvas(w/factor,h/factor);target=small.getContext('2d');}
    const cw=pixel?small.width:w,ch=pixel?small.height:h,k=Math.min(cw/960,ch/540);
    const palette=o.palette||['#e9eef0','#203b4d','#5c8d96','#c69a6d','#d9bca2'];
    target.save();target.fillStyle=palette[0];target.fillRect(0,0,cw,ch);target.translate((cw-960*k)/2,(ch-540*k)/2);target.scale(k,k);
    if(o.kind==='runtime'){
      target.fillStyle=palette[1];target.font='600 38px sans-serif';target.fillText('Canvas runtime',65,90);
      const x=100+760*M.phase(t,0,2);target.fillStyle=palette[2];target.beginPath();target.arc(x,250,42,0,Math.PI*2);target.fill();
      target.fillStyle=palette[1];target.font='24px sans-serif';target.fillText(t<1?'CUE A':'CUE B',65,440);
    }else if(o.subject==='figures'){
      const back=target.createLinearGradient(0,50,0,440);back.addColorStop(0,palette[0]);back.addColorStop(1,'#cbdadd');target.fillStyle=back;target.fillRect(0,0,960,410);
      target.fillStyle='#c0cfd1';for(let i=0;i<7;i++)target.fillRect(i*155+20,125+(i%3)*20,90,225);
      target.fillStyle='#d4d7cd';target.fillRect(0,410,960,130);
      target.fillStyle=palette[1];target.fillRect(650,330,172,12);target.fillRect(668,342,8,71);target.fillRect(797,342,8,71);
      target.fillStyle='#738f85';for(const x of [84,872]){target.fillRect(x,200,9,212);target.beginPath();target.ellipse(x,187,62,84,0,0,Math.PI*2);target.fill();}
      const walk=M.walk(t,{start:.15,duration:2,distance:3.6,heads:4.8}),transfer=M.handoff(t),scale=40,x=260+walk.x*scale;
      const a=root.MVActors.actor(target,{x,y:412,scale,walk,hand:transfer.giver,paper,palette:{shirt:palette[2],skin:palette[4],hair:palette[1],trousers:'#445b68'}});
      const b=root.MVActors.actor(target,{x:548,y:412,scale,facing:-1,hand:transfer.receiver,paper,palette:{shirt:palette[3],skin:palette[4],hair:palette[1],trousers:'#596975'},look:t<4.5?1:-.2});
      const p=transfer.owner==='giver'?a.hand:b.hand;
      target.save();target.translate(...p);target.rotate(.15*(1-transfer.release));target.fillStyle='#f7f0db';target.strokeStyle=palette[1];target.lineWidth=1;target.fillRect(-12,-8,24,16);target.strokeRect(-12,-8,24,16);target.restore();
      root.studyPose={frames:[{t,characters:[{id:'a',...a},{id:'b',...b}]}],contact:transfer.contact,owner:transfer.owner,handDistance:Math.hypot(a.hand[0]-b.hand[0],a.hand[1]-b.hand[1])};
      if(o.kind==='motion'&&t>=5){const q=M.phase(t,5,6);T.wipe(target,q,960,540,palette[1]);}
    }else if(o.subject==='type'){
      target.fillStyle=palette[1];target.font='22px sans-serif';target.fillText('WORD / SHAPE',70,80);
      T.wordToObject(target,M.phase(t,1,4),{word:'LIGHT',x:480,y:265,size:106,color:palette[2]});
      if(t>4)T.shapeMatch(target,M.phase(t,4,6),{x:480,y:265,rx:37,ry:37},{x:480,y:265,rx:280,ry:4},palette[2]);
    }else{
      target.strokeStyle=palette[2];target.lineWidth=3;
      for(let i=0;i<7;i++){target.beginPath();for(let x=0;x<=960;x+=8){const y=270+Math.sin(x*.008+t*.8+i*.3)*(40+i*15);x?target.lineTo(x,y):target.moveTo(x,y);}target.stroke();}
      T.shapeMatch(target,.5+.5*Math.sin(t),{x:350,y:260,rx:40,ry:40},{x:610,y:260,rx:100,ry:12,rotation:.5},palette[3]);
    }
    if(paper){
      // Static deterministic texture, with the same composition and timing as other studies.
      for(let i=0;i<1700;i++){const x=((i*127.13)%960),y=((i*71.71)%540);target.fillStyle=i%2?'rgba(38,58,69,.035)':'rgba(255,255,255,.2)';target.fillRect(x,y,1.3,1.3);}
      target.strokeStyle='rgba(35,57,65,.13)';target.lineWidth=2;target.strokeRect(14,14,932,512);
    }
    target.restore();
    if(pixel){c.save();c.imageSmoothingEnabled=false;c.drawImage(small,0,0,w,h);c.restore();}
  }
  root.drawFrame=scene;
})(globalThis);

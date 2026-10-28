// Original demonstration: a small light travels through six places. No private cast or existing song.
(function(root){
  let pack;
  const M=root.MVMotion;
  const captions=['A LITTLE LIGHT FINDS A WAY','THROUGH STATIONS AND DISTANCE','SOME DAYS THE SKY GROWS HEAVY','WE REST AND NOTICE SMALL LIGHTS','A MESSAGE WAITS ON THE TABLE','THERE IS STILL A WAY TO MEET'];
  function scene(c,t,kit){
    const film=root.DEMO.kind==='film',section=PROJECT.duration/6,part=film?Math.min(5,Math.floor(t/section)):0,u=film?(t-part*section)*10/section:t;
    kit.background(c,part,t);
    if(root.DEMO.subject==='figures'){
      let ax=410,bx=550,walk=null;
      if(!film||part===1||part===2){walk=M.walk(u,{start:.2,duration:2.2,distance:2.25,heads:4.8});ax=320+walk.x*40;}
      const exchange=!film||part===5,reach=M.phase(u,2.8,3.8),release=M.phase(u,4.6,5.5),contact=u>=3.8&&u<=4.6;
      let handA=exchange?M.point(M.point([.6,-2.1],[1.75,-2.9],reach),[.6,-2.1],release):part===2?[.6,-3.5]:[.7,-2.6];
      const handB=exchange?M.point(M.point([.6,-2.1],[1.75,-2.9],reach),[.7,-2.6],release):part===4?M.point([.6,-2.1],[.18,-3],M.phase(u,5.5,7.2)):[.6,-2.1];
      if(film&&part===2)handA=M.point([.6,-3.5],[.7,-3.2],M.phase(u,5,7));
      const emotion=part===2?'sad':part===3?(u>5?'hopeful':'curious'):part===5?'hopeful':'calm';
      const poseA=root.MVPerformance.performance(u,{start:part===3?4:0,emotion,gaze:[1,part===3?-.5:0],gesture:'rest'});
      const poseB=root.MVPerformance.performance(u+.4,{emotion:exchange&&u>4?'hopeful':'curious',gaze:[1,0]});
      // The head/body view has an actual frontal-to-profile drawing change. It is a limited 2D view study.
      let viewA=part===4?M.mix(.05,1,M.phase(u,1,3)):1;
      if(part===0&&film){ax=350;viewA=M.mix(-1,1,M.phase(u,6,7.4));handA=M.point(M.point([.6,-2.1],[1.4,-2.35],M.phase(u,1,2.2)),[.7,-2.6],M.phase(u,2.6,4));if(u>=6)handA=[.7*Math.abs(viewA),-2.6];}
      const a=kit.actor(c,{id:'courier-a',x:ax,y:414,view:viewA,pose:poseA,walk,hand:handA,color:kit.palette.blue});
      let b=null;
      if(exchange||part===4)b=kit.actor(c,{id:'courier-b',x:bx,y:414,view:-1,pose:poseB,hand:handB,color:kit.palette.coral});
      const owner=exchange&&u>=4.2&&b?b:a;
      if(part!==4&&!(part===0&&film&&u<2.4)){kit.star(c,...owner.hand,16,kit.palette.gold,'carried-light');root.MV_FRAME_CHECKS.boxes.push({id:'light',kind:'prop',x:owner.hand[0]-16,y:owner.hand[1]-16,w:32,h:32});}
      if(part===2)kit.umbrella(c,...a.hand);
      if(contact&&exchange){root.MV_FRAME_CHECKS.contact={distance:Math.hypot(a.hand[0]-b.hand[0],a.hand[1]-b.hand[1]),hands:[a.hand,b.hand]};}
      if(part===0&&film&&u<2.4)kit.star(c,294,320,15,kit.palette.gold,'letter-light');
      if(part===4)kit.star(c,681,298,16,kit.palette.gold,'message-light');
    }else if(root.DEMO.subject==='type'){
      const q=M.phase(u%8,2,5),lift=M.phase(u%8,5,6.5);
      const cells=kit.wordCells('LIGHT',480,220,56),points=cells.points;
      points.forEach((p,i)=>{const along=i/points.length*10,j=Math.floor(along),v=along-j,a=-Math.PI/2+j*Math.PI/5,b=a+Math.PI/5,ra=j%2?29:65,rb=j%2?65:29,tx=480+M.mix(Math.cos(a)*ra,Math.cos(b)*rb,v),ty=255+M.mix(Math.sin(a)*ra,Math.sin(b)*rb,v),x=M.mix(p[0],tx,q),y=M.mix(p[1],ty,q);kit.rect(c,x,y,cells.unit,cells.unit,q>.1?kit.palette.gold:kit.palette.ink,'type-cell'+i);});
      if(lift>0)kit.star(c,480,255,65*lift,kit.palette.gold,'word-light');
    }else{
      for(let i=0;i<14;i++){const a=i/14*Math.PI*2+t*.16,r=100+18*Math.sin(t*.9+i);kit.ellipse(c,480+Math.cos(a)*r,253+Math.sin(a)*r*.65,8+i%3*3,8+i%3*3,i%3?kit.palette.blue:kit.palette.gold,'abstract'+i);}
      kit.star(c,480,253,36+Math.sin(t*2)*4,kit.palette.gold,'abstract-light');
    }
    if(film){
      kit.text(c,captions[part],480,482,kit.pixel?21:23,part===3&&!kit.ink?kit.palette.paper:kit.palette.ink);
      if(t<2)kit.text(c,'THE LIGHT WE CARRY',480,27,kit.pixel?28:31,kit.palette.ink);
      if(part===5&&u>6){for(let i=0;i<5;i++)kit.star(c,340+i*75,150-Math.sin(i+u)*12,8+3*(i%2),kit.palette.gold,'last-light'+i);}
      // Switch the underlying scene only while the foreground star fully covers the frame.
      const before=u>9.2?M.phase(u,9.2,10):0,after=part>0&&u<.8?1-M.phase(u,0,.8):0;
      if(before>0||after>0)kit.star(c,480,270,1500*Math.max(before,after),kit.palette.gold,'transition-star');
    }else kit.text(c,root.DEMO.subject==='figures'?'A SMALL LIGHT CHANGES HANDS':root.DEMO.subject==='type'?'A WORD BECOMES A LIGHT':'SMALL LIGHTS FIND A PATTERN',480,482,kit.pixel?21:23,kit.palette.ink);
  }
  root.drawFrame=function(c,t,view){
    if(!pack)pack=root.MVStylePacks.create(root.DEMO.manifest);
    pack.render(c,t,view,scene);
  };
})(globalThis);

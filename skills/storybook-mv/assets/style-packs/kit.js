// Original scenic drawing kit. Each backend changes construction, texture, type and motion.
// Explicitly selected demonstration art; no project-wide defaults are installed by loading this file.
(function(root){
  const M=root.MVMotion,cache=new Map();
  const GLYPHS={A:['01110','10001','10001','11111','10001','10001','10001'],B:['11110','10001','10001','11110','10001','10001','11110'],C:['01111','10000','10000','10000','10000','10000','01111'],D:['11110','10001','10001','10001','10001','10001','11110'],E:['11111','10000','10000','11110','10000','10000','11111'],F:['11111','10000','10000','11110','10000','10000','10000'],G:['01111','10000','10000','10111','10001','10001','01111'],H:['10001','10001','10001','11111','10001','10001','10001'],I:['111','010','010','010','010','010','111'],J:['00111','00010','00010','00010','10010','10010','01100'],K:['10001','10010','10100','11000','10100','10010','10001'],L:['10000','10000','10000','10000','10000','10000','11111'],M:['10001','11011','10101','10101','10001','10001','10001'],N:['10001','11001','10101','10011','10001','10001','10001'],O:['01110','10001','10001','10001','10001','10001','01110'],P:['11110','10001','10001','11110','10000','10000','10000'],Q:['01110','10001','10001','10001','10101','10010','01101'],R:['11110','10001','10001','11110','10100','10010','10001'],S:['01111','10000','10000','01110','00001','00001','11110'],T:['11111','00100','00100','00100','00100','00100','00100'],U:['10001','10001','10001','10001','10001','10001','01110'],V:['10001','10001','10001','10001','10001','01010','00100'],W:['10001','10001','10001','10101','10101','10101','01010'],X:['10001','10001','01010','00100','01010','10001','10001'],Y:['10001','10001','01010','00100','00100','00100','00100'],Z:['11111','00001','00010','00100','01000','10000','11111'],' ':['000','000','000','000','000','000','000'],'.':['0','0','0','0','0','1','1'],'-':['000','000','000','111','000','000','000']};
  Object.assign(GLYPHS,{'0':['01110','10001','10011','10101','11001','10001','01110'],'1':['00100','01100','00100','00100','00100','00100','01110'],'2':['01110','10001','00001','00010','00100','01000','11111'],'3':['11110','00001','00001','01110','00001','00001','11110'],'4':['00010','00110','01010','10010','11111','00010','00010'],'5':['11111','10000','10000','11110','00001','00001','11110'],'6':['01110','10000','10000','11110','10001','10001','01110'],'7':['11111','00001','00010','00100','01000','01000','01000'],'8':['01110','10001','10001','01110','10001','10001','01110'],'9':['01110','10001','10001','01111','00001','00001','01110'],':':['0','1','1','0','1','1','0'],'/':['00001','00010','00010','00100','01000','01000','10000']});
  const hash=(str)=>{let h=2166136261;for(const ch of str){h^=ch.charCodeAt(0);h=Math.imul(h,16777619);}return h>>>0;};
  const random=(seed)=>{let x=hash(seed);return()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return(x>>>0)/4294967296;};};
  function create(manifest){
    if(!manifest||!['flat','cut-paper','pixel','ink'].includes(manifest.id)||!manifest.palette)throw Error('select an implemented style pack explicitly');
    const id=manifest.id,P=manifest.palette,pixel=id==='pixel',paper=id==='cut-paper',ink=id==='ink';
    const snap=x=>pixel?Math.round(x/4)*4:x;
    const path=(c,pts)=>{c.beginPath();pts.forEach((p,i)=>i?c.lineTo(snap(p[0]),snap(p[1])):c.moveTo(snap(p[0]),snap(p[1])));c.closePath();};
    function poly(c,points,color,key='shape'){
      c.save();let pts=points;
      if(paper){const r=random(key);pts=[];points.forEach((a,i)=>{const b=points[(i+1)%points.length],n=Math.max(1,Math.ceil(Math.hypot(b[0]-a[0],b[1]-a[1])/12));for(let j=0;j<n;j++){const u=j/n;pts.push([a[0]+(b[0]-a[0])*u+(r()-.5)*2.2,a[1]+(b[1]-a[1])*u+(r()-.5)*2.2]);}});c.shadowColor='rgba(39,45,44,.18)';c.shadowBlur=3;c.shadowOffsetX=1;c.shadowOffsetY=3;}
      path(c,pts);c.fillStyle=ink&&color!==P.gold&&color!==P.coral?P.paper:color;c.fill();
      if(ink&&color!==P.paper){c.clip();c.strokeStyle=color===P.night?P.blue:P.ink;c.lineWidth=.8;const xs=points.map(p=>p[0]),ys=points.map(p=>p[1]),lo=Math.min(...xs),hi=Math.max(...xs),top=Math.min(...ys),bottom=Math.max(...ys);for(let x=lo-(bottom-top);x<hi;x+=9){c.beginPath();c.moveTo(x,bottom);c.lineTo(x+bottom-top,top);c.stroke();}}
      c.restore();if(ink){path(c,points);c.lineWidth=1.5;c.strokeStyle=P.ink;c.stroke();}
    }
    const rect=(c,x,y,w,h,col,key)=>poly(c,[[x,y],[x+w,y],[x+w,y+h],[x,y+h]],col,key);
    function ellipse(c,x,y,rx,ry,col,key){
      const pts=[];for(let i=0;i<32;i++){const a=i/32*Math.PI*2;pts.push([x+Math.cos(a)*rx,y+Math.sin(a)*ry]);}poly(c,pts,col,key);
    }
    function line(c,pts,col,width=2){c.save();c.strokeStyle=col;c.lineWidth=pixel?Math.max(4,snap(width)):width;c.lineCap=pixel?'square':'round';c.beginPath();pts.forEach((p,i)=>i?c.lineTo(snap(p[0]),snap(p[1])):c.moveTo(snap(p[0]),snap(p[1])));c.stroke();c.restore();}
    function star(c,x,y,r,col=P.gold,key='star'){const pts=[];for(let i=0;i<10;i++){const a=-Math.PI/2+i*Math.PI/5,k=i%2?.45:1;pts.push([x+Math.cos(a)*r*k,y+Math.sin(a)*r*k]);}poly(c,pts,col,key);}
    function text(c,str,x,y,size=22,color=P.ink,kind='text'){
      if(pixel){const unit=Math.max(4,Math.round(size/7/4)*4),chars=Array.from(str.toUpperCase()),width=chars.reduce((s,ch)=>s+((GLYPHS[ch]?.[0].length||0)+1)*unit,0);if(chars.some(ch=>!GLYPHS[ch]))throw Error('pixel demo glyph not bundled: '+str);let xx=snap(x-width/2);c.fillStyle=color;for(const ch of chars){const rows=GLYPHS[ch];rows.forEach((row,yy)=>Array.from(row).forEach((v,k)=>{if(v==='1')c.fillRect(xx+k*unit,snap(y)+yy*unit,unit,unit);}));xx+=(rows[0].length+1)*unit;}root.MV_FRAME_CHECKS.boxes.push({id:str,kind,x:x-width/2,y,w:width,h:unit*7});return;}
      c.save();c.fillStyle=color;c.textAlign='center';c.textBaseline='top';c.font=`${size>=30?'600':'400'} ${size}px sans-serif`;c.fillText(str,x,y);const width=c.measureText(str).width;root.MV_FRAME_CHECKS.boxes.push({id:str,kind,x:x-width/2,y,w:width,h:size*1.2});c.restore();
    }
    function plant(c,x,y,s=1){rect(c,x-12*s,y-25*s,24*s,26*s,P.coral,'pot');for(let i=0;i<5;i++){const xx=x+(i-2)*12*s,yy=y-35*s-(i%2)*17*s;line(c,[[x,y-22*s],[xx,yy]],P.blue,3*s);ellipse(c,xx,yy,9*s,5*s,P.blue,'leaf'+i);}}
    function umbrella(c,x,y){line(c,[[x,y],[x,y-55]],P.ink,3);const pts=[[x-68,y-55],[x-58,y-80],[x-30,y-100],[x,y-110],[x+30,y-100],[x+58,y-80],[x+68,y-55],[x+44,y-64],[x+22,y-55],[x,y-65],[x-22,y-55],[x-44,y-64]];poly(c,pts,P.coral,'umbrella-canopy');line(c,[[x,y-106],[x,y-65]],P.paper,1);}
    function background(c,scene,t){
      rect(c,0,0,960,540,P.paper,'paper');
      if(scene===0){
        rect(c,65,60,450,290,P.pale,'wall');rect(c,98,84,264,202,P.ink,'window-frame');rect(c,108,94,244,182,P.pale,'window');
        ellipse(c,296,126,27,27,P.gold,'sun');poly(c,[[108,245],[185,170],[240,225],[295,185],[352,230],[352,276],[108,276]],P.blue,'hills');line(c,[[230,94],[230,276]],P.paper,8);line(c,[[108,185],[352,185]],P.paper,8);
        rect(c,580,128,245,17,P.blue,'shelf');for(let i=0;i<7;i++)rect(c,595+i*27,85-(i%2)*8,18,42+(i%2)*8,i%2?P.coral:P.gold,'book'+i);
        rect(c,85,353,300,18,P.ink,'desk');rect(c,102,370,12,70,P.blue,'leg');rect(c,354,370,12,70,P.blue,'leg2');plant(c,161,350,1.5);rect(c,225,324,94,24,P.paper,'letter');
      }else if(scene===1){
        rect(c,0,268,960,170,P.pale,'platform');for(let i=0;i<6;i++){const x=50+i*165;rect(c,x,90,14,270,P.blue,'pillar'+i);line(c,[[x,100],[x+83,60],[x+165,100]],P.ink,6);}
        rect(c,60,193,820,121,P.blue,'train');for(let i=0;i<9;i++)rect(c,86+i*88,209,57,56,P.paper,'train-window'+i);rect(c,28,328,904,8,P.ink,'track');ellipse(c,741,116,40,40,P.paper,'clock');line(c,[[741,91],[741,116],[764,123]],P.ink,3);
      }else if(scene===2){
        rect(c,0,0,960,540,P.pale,'rain-sky');poly(c,[[0,260],[140,200],[260,270],[400,210],[580,280],[790,195],[960,260],[960,455],[0,455]],P.blue,'town');
        for(let i=0;i<9;i++)rect(c,i*121,260+(i%3)*12,65,100,P.paper,'house'+i);
        rect(c,0,385,960,60,P.paper,'bridge');line(c,[[0,330],[960,330]],P.ink,5);for(let i=0;i<14;i++)line(c,[[i*75,330],[i*75,385]],P.ink,4);
        for(let i=0;i<65;i++){const x=(i*173+t*45)%1020-30,y=(i*97+t*155)%420;line(c,[[x,y],[x-5,y+12]],P.blue,pixel?4:1);}
      }else if(scene===3){
        rect(c,0,0,960,540,P.night,'night');for(let i=0;i<44;i++)star(c,32+(i*131)%900,30+(i*71)%270,3+(i%3),i%4?P.paper:P.gold,'sky-star'+i);
        ellipse(c,770,103,43,43,P.gold,'moon');poly(c,[[0,340],[170,240],[380,350],[620,225],[960,330],[960,540],[0,540]],P.blue,'mountain');poly(c,[[0,416],[260,330],[500,430],[760,318],[960,385],[960,540],[0,540]],P.ink,'hill');
        for(let i=0;i<12;i++)ellipse(c,300+(i*43)%400,270+Math.sin(t*1.5+i)*22+(i%3)*25,3,3,P.gold,'firefly'+i);
      }else if(scene===4){
        rect(c,62,55,818,295,P.pale,'studio-wall');for(let i=0;i<9;i++){const x=113+i*78,y=110+(i%3)*25;rect(c,x,y,58,68,P.paper,'postcard'+i);line(c,[[x+8,y+47],[x+24,y+25],[x+48,y+45]],i%2?P.coral:P.blue,3);}
        line(c,[[78,90],[885,80]],P.ink,2);rect(c,580,315,300,20,P.ink,'table');rect(c,600,335,12,100,P.blue,'table-leg');rect(c,850,335,12,100,P.blue,'table-leg2');plant(c,816,312,1.4);
      }else{
        rect(c,0,0,960,540,P.pale,'morning');ellipse(c,748,160,61,61,P.gold,'rising-sun');poly(c,[[0,280],[170,230],[325,300],[510,200],[720,280],[960,220],[960,540],[0,540]],P.blue,'morning-hill');
        poly(c,[[0,412],[180,375],[390,438],[575,362],[960,405],[960,540],[0,540]],P.paper,'riverbank');line(c,[[0,454],[185,427],[360,478],[550,427],[960,474]],P.gold,6);
        for(let i=0;i<6;i++)line(c,[[82+i*148,368],[95+i*148,350],[112+i*148,367]],P.ink,2);
      }
      rect(c,0,438,960,102,scene===3?P.night:P.paper,'floor');
      line(c,[[0,438],[960,438]],scene===3?P.blue:P.ink,1.5);
      if(paper){
        const key='grain';let texture=cache.get(key);if(!texture){texture=root.makeStudyCanvas(960,540);const tc=texture.getContext('2d'),r=random('material-grain');for(let i=0;i<5000;i++){tc.fillStyle=i%2?'rgba(255,255,255,.08)':'rgba(45,35,24,.035)';tc.fillRect(r()*960,r()*540,.8+r()*1.2,.6+r());}cache.set(key,texture);}c.drawImage(texture,0,0);
      }
    }
    function pixelActor(c,{id:actorId,x,y,pose,hand=null,walk=null,view=1,color=P.blue}){
      x=snap(x);y=snap(y);const facing=view>=0?1:-1,hh=hand||pose.hand,sz=40,world=(p)=>[snap(x+p[0]*sz*facing),snap(y+p[1]*sz)];
      const hip=[x,y-92],head=[x,y-172],feet=walk?[[walk.left.x,walk.left.y],[walk.right.x,walk.right.y]]:[[-.2,0],[.2,0]],handPoint=world(hh);
      c.fillStyle=P.ink;feet.forEach((f,i)=>{const end=world(f),knee=[snap((hip[0]+end[0])/2)-4,snap((hip[1]+end[1])/2)];line(c,[hip,knee,end],P.ink,12);rect(c,end[0]-8,end[1]-4,20,8,P.paper,'shoe');});
      rect(c,x-16,y-140,32,56,color,'pixel-torso');rect(c,x-16,y-192,32,36,P.gold,'pixel-head');rect(c,x-20,y-200,36,16,P.ink,'pixel-hair');
      line(c,[[x+facing*12,y-134],[snap((x+handPoint[0])/2),snap((y-134+handPoint[1])/2)],handPoint],color,12);rect(c,handPoint[0]-4,handPoint[1]-4,8,8,P.gold,'pixel-hand');
      rect(c,x+facing*8,y-180,4,pose.blink>.45?4:8,P.ink,'pixel-eye');
      if(pose.smile>.15)line(c,[[x+facing*4,y-164],[x+facing*12,y-164]],P.coral,4);
      return {id:actorId,hand:handPoint,feet:feet.map(world),reachable:true,pose_signature:[...hh,...feet.flat(),pose.brow,pose.smile,pose.headTilt],box:{id:actorId,kind:'action',x:x-36,y:y-204,w:100,h:208},view};
    }
    function actor(c,options){
      const data=pixel?pixelActor(c,options):root.MVPerformance.actor(c,{...options,size:40,paper,palette:{shirt:options.color||P.blue,skin:'#edc2a3',hair:P.ink,trousers:P.ink}});
      if(!pixel){const m=c.getTransform(),det=m.a*m.d-m.b*m.c,local=p=>[(m.d*(p[0]-m.e)-m.c*(p[1]-m.f))/det,(-m.b*(p[0]-m.e)+m.a*(p[1]-m.f))/det];data.hand=local(data.hand);data.feet=data.feet.map(local);const b=data.box,corners=[[b.x,b.y],[b.x+b.w,b.y],[b.x,b.y+b.h],[b.x+b.w,b.y+b.h]].map(local),xs=corners.map(p=>p[0]),ys=corners.map(p=>p[1]);Object.assign(b,{x:Math.min(...xs),y:Math.min(...ys),w:Math.max(...xs)-Math.min(...xs),h:Math.max(...ys)-Math.min(...ys)});}
      root.MV_FRAME_CHECKS.actors.push(data);root.MV_FRAME_CHECKS.boxes.push(data.box);return data;
    }
    function quantize(canvas){const c=canvas.getContext('2d'),image=c.getImageData(0,0,canvas.width,canvas.height),colors=Object.values(P).map(hex=>[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16)));for(let i=0;i<image.data.length;i+=4){let best=colors[0],dist=Infinity;for(const col of colors){const d=col.reduce((s,v,j)=>s+(v-image.data[i+j])**2,0);if(d<dist){dist=d;best=col;}}for(let j=0;j<3;j++)image.data[i+j]=best[j];image.data[i+3]=255;}c.save();c.setTransform(1,0,0,1,0,0);c.putImageData(image,0,0);c.restore();}
    function wordCells(str,x,y,size=56){const chars=Array.from(str.toUpperCase()),unit=Math.max(4,Math.round(size/7/4)*4);if(chars.some(ch=>!GLYPHS[ch]))throw Error('word-cell glyph not bundled');const width=chars.reduce((s,ch)=>s+(GLYPHS[ch][0].length+1)*unit,0),points=[];let xx=x-width/2;for(const ch of chars){GLYPHS[ch].forEach((row,yy)=>Array.from(row).forEach((bit,i)=>{if(bit==='1')points.push([xx+i*unit,y+yy*unit]);}));xx+=(GLYPHS[ch][0].length+1)*unit;}return{points,unit};}
    function render(c,t,view,sceneFunction){
      const width=view.width,height=view.height;
      root.MV_FRAME_CHECKS={boxes:[],actors:[],space:{width:960,height:540},style:id};
      const target=pixel?(cache.get('pixel-canvas')||root.makeStudyCanvas(240,135)):null;
      if(target)cache.set('pixel-canvas',target);
      const ctx=target?target.getContext('2d'):c;
      if(target){target.width=240;target.height=135;ctx.scale(.25,.25);}else{c.save();const scale=Math.min(width/960,height/540);c.fillStyle=P.paper;c.fillRect(0,0,width,height);c.translate((width-960*scale)/2,(height-540*scale)/2);c.scale(scale,scale);}
      sceneFunction(ctx,pixel?Math.floor(t*8)/8:t,{background,actor,star,rect,line,ellipse,text,wordCells,umbrella,palette:P,pixel,ink});
      if(target){quantize(target);const scale=Math.floor(Math.min(width/240,height/135));if(scale<1)throw Error('pixel demo output must fit a 240x135 drawing surface');c.fillStyle=P.paper;c.fillRect(0,0,width,height);c.imageSmoothingEnabled=false;c.drawImage(target,Math.floor((width-240*scale)/2),Math.floor((height-135*scale)/2),240*scale,135*scale);}else c.restore();
      const s=pixel?Math.floor(Math.min(width/240,height/135))/4:Math.min(width/960,height/540),ox=(width-960*s)/2,oy=(height-540*s)/2;
      for(const b of root.MV_FRAME_CHECKS.boxes){b.x=ox+b.x*s;b.y=oy+b.y*s;b.w*=s;b.h*=s;}
      if(root.MV_FRAME_CHECKS.contact){root.MV_FRAME_CHECKS.contact.distance*=s;root.MV_FRAME_CHECKS.contact.hands=root.MV_FRAME_CHECKS.contact.hands.map(p=>[ox+p[0]*s,oy+p[1]*s]);}
      root.MV_FRAME_CHECKS.space={width,height};
    }
    return {render,manifest};
  }
  root.MVStylePacks={create};
})(globalThis);

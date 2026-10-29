// Original bounded mechanism probes. These looks are examples, never project defaults.
const P=globalThis.PROBE;
const clamp=(v)=>Math.max(0,Math.min(1,v)),ease=v=>{v=clamp(v);return v*v*(3-2*v);};
const lerp=(a,b,t)=>a+(b-a)*t;
const pair=(a,b,t)=>[lerp(a[0],b[0],t),lerp(a[1],b[1],t)];
function shape(c,points,fill){c.beginPath();points.forEach((p,i)=>i?c.lineTo(...p):c.moveTo(...p));c.closePath();c.fillStyle=fill;c.fill();}
function line(c,a,b,color,width=5){c.strokeStyle=color;c.lineWidth=width;c.lineCap='round';c.beginPath();c.moveTo(...a);c.lineTo(...b);c.stroke();}
function circle(c,x,y,r,color){c.fillStyle=color;c.beginPath();c.arc(x,y,r,0,Math.PI*2);c.fill();}
function label(c,text,x,y,size=26,color='#344a4a'){c.fillStyle=color;c.font=`500 ${size}px "${P.font||'sans-serif'}",sans-serif`;c.textAlign='center';c.textBaseline='middle';c.fillText(text,x,y);}
function paper(c,t){const g=c.createLinearGradient(0,0,960,540);g.addColorStop(0,'#f8f2e4');g.addColorStop(1,'#e1e8d9');c.fillStyle=g;c.fillRect(0,0,960,540);for(let i=0;i<400;i++){const x=(i*137.33)%960,y=(i*73.71)%540;c.fillStyle=`rgba(95,80,59,${.018+(i%3)*.005})`;c.fillRect(x,y,1+(i%2),1);}}
function envelope(c,p,scale=1){c.save();c.translate(...p);c.scale(scale,scale);c.fillStyle='#ce7e54';c.fillRect(-26,-17,52,34);shape(c,[[-26,-17],[0,3],[26,-17]],'#e9a274');line(c,[-26,17],[0,-1],'#b56a4b',1.3);line(c,[26,17],[0,-1],'#b56a4b',1.3);c.restore();}
function person(c,x,t,hand,side,smile=false){
  const bob=Math.sin(t*1.2+side)*.8,head=[x,239+bob];
  c.fillStyle='rgba(48,64,53,.12)';c.beginPath();c.ellipse(x,437,36,7,0,0,Math.PI*2);c.fill();
  line(c,[x-10,351],[x-15,397],'#48565d',13);line(c,[x-15,397],[x-18,430],'#48565d',11);
  line(c,[x+9,351],[x+14,395],'#364851',13);line(c,[x+14,395],[x+24,430],'#364851',11);
  line(c,[x-23,432],[x-9,432],'#3b3530',8);line(c,[x+19,432],[x+34,432],'#3b3530',8);
  shape(c,[[x-23,274],[x+22,274],[x+29,354],[x-26,354]],side>0?'#546d70':'#ad7659');
  const shoulder=[x+side*21,285],elbow=[lerp(shoulder[0],hand[0],.48),lerp(shoulder[1],hand[1],.48)+24];
  line(c,shoulder,elbow,side>0?'#546d70':'#ad7659',14);line(c,elbow,hand,'#d7ab84',9);circle(c,...hand,5,'#d7ab84');
  line(c,[x-side*20,287],[x-side*24,347],side>0?'#546d70':'#ad7659',13);
  line(c,[x,265],[x,276],'#d7ab84',13);circle(c,...head,22,'#dbb28f');
  shape(c,[[x-23,240],[x-21,221],[x-3,212],[x+16,219],[x+22,235],[x+13,227],[x-3,231],[x-16,228]],'#443b35');
  const blink=(t%4.7)>4.52,pupil=side*2;
  for(const dx of [-8,8]){if(blink)line(c,[x+dx-2,head[1]+2],[x+dx+2,head[1]+2],'#443b35',1.5);else circle(c,x+dx+pupil,head[1]+1,1.7,'#443b35');}
  c.strokeStyle='#744e40';c.lineWidth=1.5;c.beginPath();c.arc(x+side*2,head[1]+8,5,smile?0:.2,smile?Math.PI:2.4);c.stroke();
  return {shoulder,hand,pose_signature:[...hand,elbow[1],bob,smile?1:0]};
}
function interaction(c,t){
  paper(c,t);circle(c,790,116,62,'#ead3a1');shape(c,[[65,397],[120,222],[170,397]],'#b5c5ad');shape(c,[[750,397],[824,185],[898,397]],'#9fb69f');
  c.fillStyle='#d6cfbb';c.fillRect(0,432,960,108);c.fillStyle='#717f75';c.fillRect(235,160,490,9);c.fillRect(260,169,7,267);c.fillRect(695,169,7,267);
  c.fillStyle='#8c8b74';c.fillRect(265,374,425,11);c.fillRect(280,385,7,50);c.fillRect(672,385,7,50);
  let a=pair([368,350],[480,302],ease((t-2)/2));
  let b=pair([592,350],[480,302],ease((t-3.0)/1));
  if(t>4.6){a=pair([480,302],[368,350],ease((t-4.6)/.9));b=pair([480,302],[591,330],ease((t-4.6)/1.3));}
  const left=person(c,347,t,a,1,t>5),right=person(c,613,t,b,-1,t>5);
  const owner=t<4.6?a:b;envelope(c,owner);
  globalThis.MV_FRAME_CHECKS={actors:[{id:'sender',...left},{id:'receiver',...right}],boxes:[],contact:t>=4&&t<=4.6?{distance:Math.hypot(a[0]-b[0],a[1]-b[1])}:null};
  if(t>8&&t<9){const u=ease(t-8);c.save();c.translate(480,300);c.scale(1+u*45,1+u*45);envelope(c,[0,0]);c.restore();}
  if(t>=9){paper(c,t);c.fillStyle='#6b7e78';c.fillRect(0,0,960,540);c.fillStyle='#ece3cf';c.fillRect(58,60,844,380);c.fillStyle='#cad8cf';c.fillRect(87,88,786,315);for(let i=0;i<5;i++){const x=(i*220+860-(t-9)*60)%1100-70;shape(c,[[x,386],[x+70,170],[x+140,386]],'#a3b5a6');}c.save();c.beginPath();c.rect(87,88,786,315);c.clip();person(c,530,t,[508,350],-1,true);envelope(c,[508,350]);c.restore();c.fillStyle='#e5dcc9';c.fillRect(475,60,10,380);circle(c,130,476,5,'#cf9870');circle(c,150,476,5,'#e8c8a6');circle(c,170,476,5,'#e8c8a6');}
  const lines=['把未说完的话','折进一封小小的信','你向前走 我慢慢挥手','下一站 还会有晴天'];
  if(P.font)label(c,lines[Math.min(3,Math.floor(t/3))],480,487,26,t>=9?'#f5f0e6':'#3e514b');
}
function typography(c,t){
  paper(c,t);const section=Math.min(3,Math.floor(t/3)),u=(t%3)/3;
  const lines=['等一束光','让时间慢一点','把距离折成纸飞机','把下一次留给晴天'];
  if(section===0){for(let i=0;i<4;i++){const x=330+i*100,y=228+Math.sin(t*2+i)*7;circle(c,x,y,43+i*2,['#d5ab75','#c8d1ba','#d79e82','#99b7ae'][i]);}label(c,lines[0],480,228,54);line(c,[300,306],[300+360*ease(u*1.8),306],'#9d7358',3);}
  if(section===1){circle(c,480,232,100,'#faf7ed');c.strokeStyle='#6f8e82';c.lineWidth=3;c.beginPath();c.arc(480,232,100,0,Math.PI*2);c.stroke();for(let i=0;i<12;i++){const a=i*Math.PI/6;line(c,[480+88*Math.sin(a),232-88*Math.cos(a)],[480+93*Math.sin(a),232-93*Math.cos(a)],'#6f8e82',2);}const a=(t-3)*.7;line(c,[480,232],[480+68*Math.sin(a),232-68*Math.cos(a)],'#af7859',4);line(c,[480,232],[445,204],'#495e55',5);circle(c,480,232,6,'#495e55');}
  if(section===2){const a=ease(u),x=170+610*a,y=275-65*Math.sin(a*Math.PI);c.save();c.translate(x,y);c.rotate(-.2+.35*a);shape(c,[[-48,25],[45,-22],[-13,37],[-12,9]],'#f9f5e9');shape(c,[[-48,25],[45,-22],[-12,9]],'#d9b68b');shape(c,[[-12,9],[-13,37],[2,18]],'#a8bbaa');c.restore();for(let i=0;i<16;i++){const xx=120+i*38;if(xx<x-45)circle(c,xx,300-30*Math.sin(i/5),2,'#c7b99f');}}
  if(section===3){c.fillStyle='#b5cabb';c.fillRect(310,114,340,230);circle(c,566,164,46,'#f2db9e');shape(c,[[310,304],[405,215],[487,288],[570,213],[650,304]],'#88a695');const open=ease(u*1.6);shape(c,[[310,114],[480-160*open,130],[480-160*open,333],[310,344]],'#e0bc93');shape(c,[[650,114],[480+160*open,130],[480+160*open,333],[650,344]],'#e9c9a5');}
  if(section>0)label(c,lines[section],480,418,34);else label(c,'原创文字与器乐机制验证',480,438,21,'#6b786c');
  globalThis.MV_FRAME_CHECKS={actors:[],boxes:[{id:'caption',kind:'text',x:170,y:389,w:620,h:60}]};
}
function abstract(c,t){
  c.fillStyle='#172a32';c.fillRect(0,0,960,540);const u=t/12;
  for(let i=0;i<9;i++){const a=i*Math.PI*2/9+Math.sin(u*Math.PI)*.9,r=60+140*Math.sin(Math.PI*u)**2,x=480+Math.cos(a)*r,y=270+Math.sin(a)*r*.66;c.save();c.translate(x,y);c.rotate(a+u*Math.PI*2);c.fillStyle=['#eed5a8','#97b4ac','#cf9179'][i%3];c.fillRect(-18,-18,36,36);c.restore();}
  c.strokeStyle='rgba(237,220,186,.3)';c.lineWidth=1;c.beginPath();c.ellipse(480,270,260,170,0,0,Math.PI*2);c.stroke();
  globalThis.MV_FRAME_CHECKS={actors:[],boxes:[]};
}
globalThis.drawFrame=(c,t)=>{c.save();c.scale(PROJECT.width/960,PROJECT.height/540);if(P.kind==='interaction')interaction(c,t);else if(P.kind==='type')typography(c,t);else abstract(c,t);c.restore();};

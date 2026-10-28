// Original optional Canvas/JS motion primitives. Units, palette and timing belong to the project.
(function(root){
  const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
  const ease=x=>{x=clamp(x);return x*x*(3-2*x);};
  const mix=(a,b,u)=>a+(b-a)*u;
  const point=(a,b,u)=>[mix(a[0],b[0],u),mix(a[1],b[1],u)];
  const phase=(t,a,b)=>ease((t-a)/(b-a));
  function twoBone(a,target,l1,l2,bend=1){
    if(![...a,...target,l1,l2].every(Number.isFinite)||l1<=0||l2<=0)throw Error('invalid limb');
    const dx=target[0]-a[0],dy=target[1]-a[1],raw=Math.hypot(dx,dy);
    const d=clamp(raw,Math.abs(l1-l2)+1e-6,l1+l2-1e-6),theta=Math.atan2(dy,dx);
    const alpha=Math.acos(clamp((l1*l1+d*d-l2*l2)/(2*l1*d),-1,1));
    return {joint:[a[0]+l1*Math.cos(theta+bend*alpha),a[1]+l1*Math.sin(theta+bend*alpha)],
      end:[a[0]+d*Math.cos(theta),a[1]+d*Math.sin(theta)],reachable:Math.abs(raw-d)<1e-5};
  }
  // Foot phase is driven by travelled distance. A stance foot is fixed in world space.
  function walk(t,{start=0,duration=2,distance=3,heads=4.8}={}){
    if(duration<=0||heads<3.2||heads>9||distance<0)throw Error('invalid optional humanoid walk');
    const leg=(heads-2.5)/2,L=Math.min(.8,leg*.65),s=distance*phase(t,start,start+duration);
    function foot(offset){
      const cycle=(s+offset)/(2*L),n=Math.floor(cycle),f=cycle-n,anchor=2*L*n-offset;
      const u=clamp((f-.5)*2),x=anchor+2*L*ease(u),y=-Math.sin(Math.PI*u)*.24;
      return {x:x-s,y,worldX:x,stance:f<.5};
    }
    let left=foot(0),right=foot(L);
    const settle=phase(t,start+duration,start+duration+.4);
    if(settle>0){
      // Keep the nearest foot planted; bring the other into a supported stop.
      const near=Math.abs(left.x)<Math.abs(right.x)?'left':'right';
      for(const [name,f] of [['left',left],['right',right]]){
        if(name!==near){f.x=mix(f.x,name==='left'?-.2:.2,settle);f.y-=Math.sin(Math.PI*settle)*.18;f.worldX=s+f.x;f.stance=settle===1;}
      }
    }
    return {x:s,left,right,hipY:-2*leg+mix(.23,.04,settle),bob:Math.sin(s/L*Math.PI)*.025*(1-settle),swing:Math.sin(s/L*Math.PI)*(1-settle),legLength:leg};
  }
  function handoff(t,{reach=[2.5,3.4],contact=[3.4,3.8],release=[3.8,4.6]}={}){
    if(!(reach[0]<reach[1]&&reach[1]<=contact[0]&&contact[0]<contact[1]&&contact[1]<=release[0]&&release[0]<release[1]))throw Error('invalid handoff phases');
    const q=phase(t,...reach),r=phase(t,...release);
    return {giver:point(point([.62,-2.1],[1.8,-2.9],q),[.62,-2.1],r),
      receiver:point(point([.62,-2.1],[1.8,-2.9],q),[.85,-2.55],r),
      owner:t<(contact[0]+contact[1])/2?'giver':'receiver',contact:t>=contact[0]&&t<=contact[1],reach:q,release:r};
  }
  function turn(t,start,end,from=1,to=-1){const u=phase(t,start,end);return {facing:mix(from,to,u),threeQuarter:Math.sin(Math.PI*u)};}
  root.MVMotion={clamp,ease,mix,point,phase,twoBone,walk,handoff,turn};
})(globalThis);

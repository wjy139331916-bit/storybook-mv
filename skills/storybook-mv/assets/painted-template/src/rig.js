// Original local-unit rig helpers for mature storybook humans. No drawing or p5 dependency.
(function(root){
  const finitePoint=p=>Array.isArray(p)&&p.length===2&&p.every(Number.isFinite);
  function restPose(heads){
    if(!Number.isFinite(heads)||heads<3||heads>6)throw Error('choose a supported 3..6-head storybook proportion');
    const shoulderY=-heads+1.25,hipY=-1.65;
    return {top:[0,-heads],head:[0,-heads+0.5],neck:[0,-heads+1.03],leftShoulder:[-.38,shoulderY],rightShoulder:[.38,shoulderY],hip:[0,hipY],leftHip:[-.25,hipY],rightHip:[.25,hipY],leftKnee:[-.27,-.83],rightKnee:[.27,-.83],leftFoot:[-.3,0],rightFoot:[.3,0]};
  }
  function mapPoints(points,{footX=0,footY=0,headPx=80,angle=0}={}){
    if(![footX,footY,headPx,angle].every(Number.isFinite)||headPx<=0)throw Error('finite uniform root transform required');
    const c=Math.cos(angle),s=Math.sin(angle),out={};
    for(const [k,p] of Object.entries(points)){if(!finitePoint(p))throw Error('invalid local point '+k);out[k]=[footX+headPx*(p[0]*c-p[1]*s),footY+headPx*(p[0]*s+p[1]*c)];}
    return out;
  }
  function twoBone(start,target,upper,lower,bend=1){
    if(!finitePoint(start)||!finitePoint(target)||![upper,lower,bend].every(Number.isFinite)||upper<=0||lower<=0)throw Error('invalid two-bone inputs');
    const dx=target[0]-start[0],dy=target[1]-start[1],requested=Math.hypot(dx,dy);
    if(requested<1e-8&&Math.abs(upper-lower)<1e-8)return {elbow:[start[0]+upper,start[1]],end:start.slice(),reachable:true,requestedTarget:target.slice(),upper,lower};
    const min=Math.max(Math.abs(upper-lower),1e-6),max=upper+lower;
    const distance=Math.max(min,Math.min(max,requested));
    const angle=requested>1e-8?Math.atan2(dy,dx):0;
    const cosine=Math.max(-1,Math.min(1,(upper*upper+distance*distance-lower*lower)/(2*upper*distance)));
    const elbowAngle=angle+(bend>=0?1:-1)*Math.acos(cosine);
    const elbow=[start[0]+upper*Math.cos(elbowAngle),start[1]+upper*Math.sin(elbowAngle)];
    const end=[start[0]+distance*Math.cos(angle),start[1]+distance*Math.sin(angle)];
    return {elbow,end,reachable:requested>=min-1e-6&&requested<=max+1e-6,requestedTarget:target.slice(),upper,lower};
  }
  const api={restPose,mapPoints,twoBone};root.StoryRig=api;
  if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(typeof globalThis!=='undefined'?globalThis:this);

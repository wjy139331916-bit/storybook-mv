// Original deterministic graphic transitions; choose them only when motivated by the film.
(function(root){
  function wipe(c,u,w,h,color='#314452',direction=1){u=root.MVMotion.clamp(u);c.save();c.fillStyle=color;const x=direction>0?-w+2*w*u:w-2*w*u;c.fillRect(x,0,w,h);c.restore();}
  function shapeMatch(c,u,from,to,color){const M=root.MVMotion,q=M.ease(u);c.save();c.fillStyle=color;c.beginPath();c.ellipse(M.mix(from.x,to.x,q),M.mix(from.y,to.y,q),M.mix(from.rx,to.rx,q),M.mix(from.ry,to.ry,q),M.mix(from.rotation||0,to.rotation||0,q),0,Math.PI*2);c.fill();c.restore();}
  function wordToObject(c,u,{word='LIGHT',x,y,size=64,color='#8eb8be'}={}){const q=root.MVMotion.ease(u);c.save();c.textAlign='center';c.textBaseline='middle';c.fillStyle=color;c.globalAlpha=1-q;c.font=`600 ${size}px sans-serif`;c.fillText(word,x,y);c.globalAlpha=q;c.beginPath();c.arc(x,y,Math.max(1,size*.35*q),0,Math.PI*2);c.fill();c.restore();}
  root.MVTransitions={wipe,shapeMatch,wordToObject};
})(globalThis);

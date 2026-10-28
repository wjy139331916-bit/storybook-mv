// Replace this prototype scene with the inspected character/world design.
// Build all human geometry in local head-height units via StoryRig.
(function(){
  shots([[0,function(t,lt,dur){
    boilSeed('prototype-ground');
    paint(rectPts(0,790,W,H-790),{wash:'#E7D4B8',washOp:90,ink:null});
    // Intentional empty scaffold. Do not present it as finished character art.
  }]]);
})();

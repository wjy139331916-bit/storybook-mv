// Original minimal composition. Blank user projects acquire their art from the approved design.
import React,{useEffect,useState} from 'react';
import {AbsoluteFill,Audio,Composition,continueRender,delayRender,cancelRender,registerRoot,staticFile,useCurrentFrame,useVideoConfig} from 'remotion';
import defaults from './project.json';

function Scene({cues=[],audio=null,font=null,probe=false}){
  const frame=useCurrentFrame(),{fps,width,height}=useVideoConfig(),t=frame/fps;
  const [handle]=useState(()=>font?delayRender('selected local lyric font'):null);
  useEffect(()=>{if(!font)return;new FontFace(font.family,'url('+JSON.stringify(staticFile(font.file))+')').load().then(face=>{document.fonts.add(face);continueRender(handle);}).catch(cancelRender);},[font?.file]);
  const cue=cues.find(c=>t>=c.start&&t<c.end),family=font?JSON.stringify(font.family):'sans-serif';
  // Authored synthetic character timing is allowed only in the isolated mechanism probe.
  const count=probe&&cue?Math.floor((t-cue.start)/(cue.end-cue.start)*cue.text.length):0;
  return <AbsoluteFill style={{backgroundColor:'#fff',fontFamily:family}}>
    {probe?<div style={{position:'absolute',width:width*.12,height:width*.12,left:width*(.15+.12*Math.sin(t)),top:height*.3,background:'#548b95',borderRadius:'50%'}}/>:null}
    {audio?<Audio src={staticFile(audio)}/>:null}
    {cue?<div style={{position:'absolute',left:'2%',right:'2%',top:'82%',height:'16%',background:'#F4F2ED',display:'flex',alignItems:'center',justifyContent:'center',fontSize:24*height/360,color:'#263A43',whiteSpace:'pre-wrap',textAlign:'center'}}><span>{count>0?<><span style={{color:'#B98A32'}}>{cue.text.slice(0,count)}</span>{cue.text.slice(count)}</>:cue.text}</span></div>:null}
  </AbsoluteFill>;
}
registerRoot(()=> <Composition id="MV" component={Scene} durationInFrames={Math.round(defaults.duration*defaults.fps)} fps={defaults.fps} width={defaults.width} height={defaults.height} defaultProps={{config:defaults,cues:[],probe:false}} calculateMetadata={({props})=>({durationInFrames:Math.round(props.config.duration*props.config.fps),fps:props.config.fps,width:props.config.width,height:props.config.height})}/>);

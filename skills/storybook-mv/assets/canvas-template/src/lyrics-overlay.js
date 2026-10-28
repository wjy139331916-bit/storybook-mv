// Complete-line subtitles. No guessed character-count karaoke.
(function(root){
  const FONT='"Noto Sans CJK SC", "Microsoft YaHei", "PingFang SC", sans-serif';
  function layout(c,text,maxWidth,options={}){
    const start=options.fontSize||46,min=options.minSize||30,font=options.font||FONT;
    let lines=[],fontSize=start;
    for(;fontSize>=min;fontSize-=Math.max(1,start/23)){
      c.font=`${fontSize}px ${font}`;lines=[];let line='';
      for(const char of Array.from(text)){
        if(char==='\n'){lines.push(line);line='';continue;}
        if(line&&c.measureText(line+char).width>maxWidth){lines.push(line);line=char;}else line+=char;
      }
      if(line)lines.push(line);
      if(lines.length<=2)return {lines,fontSize,overflow:false};
    }
    return {lines,fontSize:min,overflow:true};
  }
  const previous=root.overlayHook;
  root.overlayHook=function(c,t){
    if(previous)previous(c,t);
    root.STORY_LYRICS_OVERFLOW=false;
    const mode=root.STORY_LYRICS_MODE??'unset';
    if(['none','in-world','unset'].includes(mode))return;
    const cues=mode==='key-lines'?(root.STORY_DISPLAY_CUES??[]):(root.STORY_LYRICS?.cues??[]);
    const cue=cues.find(x=>t>=x.start&&t<x.end);if(!cue)return;
    c.save();const width=c.canvas?.width??1920,height=c.canvas?.height??1080;
    const style=root.STORY_TEXT_STYLE||{};
    const fitted=layout(c,cue.text,width*.9,{fontSize:style.fontSize||46*height/1080,minSize:style.minSize||30*height/1080,font:style.font||FONT});
    root.STORY_LYRICS_OVERFLOW=fitted.overflow;
    c.font=`${fitted.fontSize}px ${style.font||FONT}`;c.textAlign='center';c.textBaseline='middle';
    const lineHeight=fitted.fontSize*1.4,bottom=height*.925,top=bottom-(fitted.lines.length-1)*lineHeight;
    c.fillStyle=style.background||'rgba(243,244,246,0.92)';c.fillRect(width*.0375,top-lineHeight*.65,width*.925,fitted.lines.length*lineHeight+8);
    c.fillStyle=style.color||'#202630';fitted.lines.forEach((line,i)=>c.fillText(line,width/2,top+i*lineHeight));c.restore();
  };
  root.StoryLyricsLayout=layout;
})(typeof globalThis!=='undefined'?globalThis:this);

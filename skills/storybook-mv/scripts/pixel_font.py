#!/usr/bin/env python3
"""Create a monochrome, source-bound bitmap glyph atlas from the selected local font."""
import argparse
import json
import math
from pathlib import Path
import os
import shutil
import tempfile
from font_check import inspect_font
from input_contracts import lyric_lines, sha
from pixel_workbench import safe_output


def export_atlas(font, document, size, target):
    from PIL import Image, ImageDraw, ImageFont
    if not isinstance(size,int) or not 8<=size<=64:raise ValueError('glyph cell size must be 8..64')
    checked=inspect_font(font,document)
    if not checked['ok']:raise ValueError('selected font lacks required glyphs: '+str(checked['missing']))
    chars=sorted({c for l in lyric_lines(json.loads(document.read_text(encoding='utf-8'))) for c in l['text'] if not c.isspace()})
    if not 1<=len(chars)<=1024:raise ValueError('use 1..1024 actual characters per atlas')
    face=ImageFont.truetype(str(font),size-2);cols=min(16,len(chars));rows=math.ceil(len(chars)/cols)
    sheet=Image.new('RGBA',(cols*size,rows*size));glyphs={}
    for i,char in enumerate(chars):
        mask=Image.new('L',(size,size));draw=ImageDraw.Draw(mask);box=draw.textbbox((0,0),char,font=face);w,h=box[2]-box[0],box[3]-box[1]
        draw.text(((size-w)//2-box[0],(size-h)//2-box[1]),char,font=face,fill=255)
        mask=mask.point(lambda a:255 if a>=128 else 0);cell=Image.new('RGBA',(size,size),(0,0,0,255));cell.putalpha(mask)
        if not mask.getbbox():raise ValueError('selected size produced an empty glyph: '+char)
        x,y=i%cols*size,i//cols*size;sheet.paste(cell,(x,y));glyphs[char]={'x':x,'y':y,'w':size,'h':size,'advance':size}
    target.parent.mkdir(parents=True,exist_ok=True);temp=Path(tempfile.mkdtemp(prefix='.glyph-build-',dir=target.parent))
    try:
        sheet.save(temp/'glyphs.png')
        meta={'schema_version':1,'cell_size':size,'image':'glyphs.png','image_sha256':sha(temp/'glyphs.png'),'font_sha256':sha(font),'text_sha256':sha(document),'glyphs':glyphs,'acceptance':'not_reviewed','scope':'Actual selected-font rasterization and cmap coverage; inspect Chinese stroke clarity at the delivery size.'}
        (temp/'glyphs.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (temp/'glyph-check.json').write_text(json.dumps(checked,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        os.rename(temp,target)
        return meta
    finally:
        if temp.exists():shutil.rmtree(temp)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--font',type=Path,required=True);p.add_argument('--text',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--size',type=int,default=16);p.add_argument('--project',type=Path);p.add_argument('--tool-self-test',action='store_true');a=p.parse_args()
    try:
        project=a.project.expanduser().resolve() if a.project else None
        if a.tool_self_test and project:raise ValueError('isolated examples cannot select a user project')
        if not a.tool_self_test:
            if not project:raise ValueError('provide the selected --project or an isolated --tool-self-test')
            from check_brief import entry_errors
            b=json.loads((project/'brief.json').read_text(encoding='utf-8'));errors=entry_errors(b,project,operation='stills',still_count=1)
            if errors:raise ValueError('Production blocked: '+'; '.join(errors))
        if a.text.stat().st_size>2*1024*1024:raise ValueError('text document too large')
        target=safe_output(a.out,project);meta=export_atlas(a.font.expanduser().resolve(),a.text.expanduser().resolve(),a.size,target)
        print(json.dumps({'directory':str(target),'glyph_count':len(meta['glyphs']),'size':a.size,'acceptance':'not_reviewed'},ensure_ascii=False))
    except (OSError,ValueError,KeyError,ImportError) as exc:p.error(str(exc))


if __name__=='__main__':main()

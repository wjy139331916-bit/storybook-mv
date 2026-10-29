#!/usr/bin/env python3
"""Create an isolated original Chinese-caption/instrumental probe, not a sung-song test."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
from font_check import inspect_font
from input_contracts import sha


LINES=['窗边的灯还亮着','我带着微光往前走','雨落下时有人撑起伞','安静也能听见回答','把没说完的话留在桌上','下一次相遇仍有可能']


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('project',type=Path);p.add_argument('--font',type=Path,required=True);p.add_argument('--font-license',type=Path,required=True);p.add_argument('--tool-self-test',action='store_true');a=p.parse_args()
    if not a.tool_self_test:p.error('reserved for isolated toolkit verification, never user-MV production')
    if not a.font.is_file() or not a.font_license.is_file():p.error('supply the actual local font and its license')
    root=Path(__file__).resolve().parents[1]
    subprocess.run([sys.executable,str(root/'scripts/build_demo.py'),str(a.project),'--kind','film','--style','flat','--subject','figures','--duration','18','--width','640','--height','360','--fps','12','--tool-self-test'],check=True,capture_output=True,text=True)
    target=a.project.resolve();font=target/'assets'/('selected-font'+a.font.suffix);shutil.copy2(a.font,font);shutil.copy2(a.font_license,target/'assets/FONT_LICENSE.txt')
    doc=target/'data/original-chinese.json';doc.write_text(json.dumps({'lines':[{'id':f'line-{i+1:03d}','text':t} for i,t in enumerate(LINES)]},ensure_ascii=False,indent=2)+'\n')
    proof=inspect_font(font,doc);(target/'data/glyph-check.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
    if not proof['ok']:p.error('selected font lacks required glyphs; probe created with a failed glyph report')
    brief=json.loads((target/'brief.json').read_text());brief['lyrics'].update(language='zh-CN',font={'path':font.relative_to(target).as_posix(),'sha256':sha(font),'family':proof['family']});(target/'brief.json').write_text(json.dumps(brief,ensure_ascii=False,indent=2)+'\n')
    cues={'alignment_status':'synthetic_known_instrumental','cues':[{'id':f'line-{i+1:03d}','start':i*3,'end':(i+1)*3,'text':t} for i,t in enumerate(LINES)]}
    (target/'src/data/lyrics.js').write_text('globalThis.STORY_LYRICS_MODE="full-lines";globalThis.STORY_LYRICS='+json.dumps(cues,ensure_ascii=False)+';\n')
    scene=target/'src/scene.js';scene.write_text('\n'.join(x for x in scene.read_text().splitlines() if 'kit.text(c,captions[' not in x and 'if(t<2)kit.text' not in x)+'\n')
    print(json.dumps({'project':str(target),'font_family':proof['family'],'checked_glyphs':proof['checked_characters'],'scope':'18-second original instrumental-caption probe only; no real-song singing alignment or aesthetic acceptance.'},ensure_ascii=False))


if __name__=='__main__':main()

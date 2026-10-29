#!/usr/bin/env python3
"""Build/render bounded original mechanisms, never a user's MV or singing test."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys

from build_demo import original_score
from input_contracts import sha

CN=['把未说完的话','折进一封小小的信','你向前走 我慢慢挥手','下一站 还会有晴天',
    '等一束光','让时间慢一点','把距离折成纸飞机','把下一次留给晴天','原创文字与器乐机制验证']


def prepare(project,kind,font=None):
    root=Path(__file__).resolve().parents[1]
    if kind=='type' and not font:raise ValueError('the Chinese type probe needs a selected local --font')
    subprocess.run([sys.executable,str(root/'scripts/scaffold.py'),str(project),'--engine','canvas2d','--duration','12','--width','960','--height','540','--fps','12','--tool-self-test'],check=True,capture_output=True,text=True, encoding='utf-8')
    brief=json.loads((project/'brief.json').read_text(encoding='utf-8'));family=None
    if font:
        from font_check import inspect_font
        # Exercise the actual local cmap before claiming Chinese text coverage.
        document=project/'data/original-captions.json'
        document.write_text(json.dumps({'lines':[{'id':'probe-'+str(i),'text':line} for i,line in enumerate(CN)]},ensure_ascii=False)+'\n',encoding='utf-8')
        result=inspect_font(font,document)
        if not result['ok']:raise ValueError('selected font lacks probe glyphs')
        target=project/'assets'/('probe-font'+font.suffix);shutil.copy2(font,target)
        family=result['family']
        (project/'data/glyph-report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        brief['lyrics'].update(font={'path':target.relative_to(project).as_posix(),'sha256':sha(target),'family':family})
    brief.update(goal='Original bounded '+kind+' mechanism validation',asset_policy='all-code')
    brief['execution']['runtime']='node-canvas';brief['music'].update(kind='instrumental',source='original-code',audio='assets/original-score.wav',duration=12)
    score=original_score(project/'assets/original-score.wav',12);brief['music']['audio_sha256']=sha(project/'assets/original-score.wav')
    (project/'brief.json').write_text(json.dumps(brief,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    config=project/'src/config.js';config.write_text(config.read_text(encoding='utf-8')+'\nglobalThis.PROBE='+json.dumps({'kind':kind,'font':family})+';\n',encoding='utf-8')
    shutil.copy2(root/'assets/benchmarks/scene.js',project/'src/scene.js')
    (project/'PROBE.json').write_text(json.dumps({'kind':kind,'duration':12,'score':score,'font_checked':bool(font),
        'scope':'Original 12-second stylized mechanism, not a full real sung MV, user approval or general acting/style certification.'},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return {'project':str(project),'case':kind,'prepared':True,'font_checked':bool(font)}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('project',type=Path);p.add_argument('--case',choices=('interaction','type','abstract'),required=True);p.add_argument('--font',type=Path);p.add_argument('--canvas-module');p.add_argument('--prepare-only',action='store_true');p.add_argument('--tool-self-test',action='store_true')
    a=p.parse_args()
    if not a.tool_self_test:p.error('isolated original toolkit validation only: explicitly pass --tool-self-test')
    try:
        target=a.project.expanduser().resolve();result=prepare(target,a.case,a.font.expanduser().resolve() if a.font else None)
        if not a.prepare_only:
            if not a.canvas_module:raise ValueError('select --canvas-module or use --prepare-only for another actual runtime')
            command=['node',str(target/'render_canvas.mjs'),'--project='+str(target),'--out=out/probe','--canvas-module='+a.canvas_module,'--times=1,3,4.25,5.5,8.5,10.5']
            subprocess.run(command,check=True,capture_output=True,text=True, encoding='utf-8')
            result['rendered']=True;result['video']='out/probe/clip.mp4'
        print(json.dumps(result,ensure_ascii=False));return 0
    except (ValueError,OSError,subprocess.SubprocessError) as exc:
        p.error(getattr(exc,'stderr',None) or str(exc))


if __name__ == '__main__':
    import sys
    for _stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(_stream, 'reconfigure'):
            _stream.reconfigure(encoding='utf-8')
    raise SystemExit(main())

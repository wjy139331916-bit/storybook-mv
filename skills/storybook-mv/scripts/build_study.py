#!/usr/bin/env python3
"""Build an explicit optional code study, outside the reusable skill and existing projects."""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('project', type=Path)
    p.add_argument('--kind', choices=('style', 'motion', 'runtime'), required=True)
    p.add_argument('--subject', choices=('figures', 'type', 'abstract'), required=True)
    p.add_argument('--style', choices=('flat', 'paper', 'pixel'), required=True)
    p.add_argument('--width', type=int, default=960)
    p.add_argument('--height', type=int, default=540)
    p.add_argument('--fps', type=int, default=30)
    a = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    target = a.project.expanduser().resolve()
    duration = 2 if a.kind == 'runtime' else 6
    try:
        subprocess.run([sys.executable, str(root/'scripts/scaffold.py'), str(target), '--engine', 'canvas2d', '--duration', str(duration), '--width', str(a.width), '--height', str(a.height), '--fps', str(a.fps)], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        p.error((exc.stderr or str(exc)).strip())
    for name in ('motion.js', 'canvas-actors.js', 'transitions.js'):
        shutil.copy2(root/'assets/modules'/name, target/'src'/name)
    shutil.copy2(root/'assets/studies/scene.js', target/'src/scene.js')
    shutil.copy2(root/'scripts/render_canvas.mjs', target/'render_canvas.mjs')
    cfg = {'kind': a.kind, 'subject': a.subject, 'style': a.style, 'prototype_only': True, 'not_a_style_default': True}
    (target/'src/study.js').write_text('globalThis.STUDY = '+json.dumps(cfg)+';\nglobalThis.makeStudyCanvas=(w,h)=>{const c=document.createElement("canvas");c.width=w;c.height=h;return c;};\n', encoding='utf-8')
    # The CPU runner overrides only the DOM canvas factory, using the same scene/modules.
    (target/'src/study-node.js').write_text('globalThis.STUDY = '+json.dumps(cfg)+';\n', encoding='utf-8')
    common = ['src/config.js', 'src/motion.js', 'src/canvas-actors.js', 'src/transitions.js']
    (target/'src/render-entry.json').write_text(json.dumps({'scripts': common+['src/study-node.js','src/scene.js','src/data/lyrics.js','src/lyrics-overlay.js']}, indent=2)+'\n')
    html = (target/'studio.html').read_text()
    extra = ''.join('<script src="'+s+'"></script>' for s in common[1:]+['src/study.js'])
    (target/'studio.html').write_text(html.replace('<script src="src/scene.js">', extra+'<script src="src/scene.js">'))
    (target/'STUDY.json').write_text(json.dumps(cfg, indent=2)+'\n')
    print(json.dumps({'project':str(target),'duration':duration,'kind':a.kind,'subject':a.subject,'style':a.style,'note':'Controlled implementation study; does not select or validate a project style.'}))


if __name__ == '__main__':
    main()

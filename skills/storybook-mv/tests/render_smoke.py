#!/usr/bin/env python3
"""Optional native-Canvas probes of actual style outputs, including pixel-grid invariants."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from PIL import Image
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_demo


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--canvas-module', default=os.environ.get('MV_CANVAS_MODULE'))
    p.add_argument('--encode', action='store_true')
    p.add_argument('--keep', type=Path)
    a = p.parse_args()
    base = a.keep.resolve() if a.keep else Path(tempfile.mkdtemp(prefix='mv-render-probe-'))
    if base.exists() and a.keep and any(base.iterdir()):
        p.error('keep directory must be empty')
    base.mkdir(parents=True, exist_ok=True)
    results = []
    try:
        for style in ('flat', 'cut-paper', 'pixel', 'ink'):
            project = base / style
            build_demo.build(project, ROOT, 'style', 'figures', style, 960, 540, 12)
            args = ['node', str(ROOT / 'scripts/render_canvas.mjs'), '--project=' + str(project), '--out=out/probe', '--times=0.5,3.9,5.7']
            if a.canvas_module:
                args.append('--canvas-module=' + a.canvas_module)
            if a.encode and style in ('flat', 'pixel'):
                args.append('--audio=assets/original-score.wav')
            else:
                args.append('--stills-only')
            subprocess.run(args, check=True, capture_output=True, text=True, encoding='utf-8')
            report = json.loads((project / 'out/probe/render-report.json').read_text(encoding='utf-8'))
            assert all(x['passed'] for x in report['determinism']), 'reverse-seek result changed'
            audit = json.loads((project / 'out/probe/frame-audit.json').read_text(encoding='utf-8'))
            assert not any(f['category'] in ('contact_gap', 'unreachable_actor_target', 'text_outside_frame') for f in audit['findings']), audit['findings']
            item = {'style': style, 'reverse_seek': True, 'encoded_frames': report['frames'], 'declared_contact_and_bounds': 'no flagged defects in inspected frames'}
            if style == 'pixel':
                image = np.array(Image.open(project / 'out/probe/frame-01.png').convert('RGB'))
                assert len(np.unique(image.reshape(-1, 3), axis=0)) <= 7, 'pixel palette exceeded'
                assert np.array_equal(image, np.repeat(np.repeat(image[::4, ::4], 4, axis=0), 4, axis=1)), 'pixel grid is not integer aligned'
                item.update(pixel_grid=True, max_colors=7)
            results.append(item)
        # Synthetic declared geometry exercises ranges, not human acting quality.
        project = base / 'hold-fixture'
        subprocess.run([sys.executable, str(ROOT/'scripts/scaffold.py'), str(project), '--engine', 'canvas2d', '--duration', '5', '--width', '64', '--height', '64', '--fps', '12', '--tool-self-test'], check=True, capture_output=True, text=True, encoding='utf-8')
        (project/'src/scene.js').write_text("globalThis.drawFrame=(c,t)=>{c.fillStyle='#eeeeee';c.fillRect(0,0,64,64);c.fillStyle='#222222';c.fillRect(8,8,20,20);globalThis.MV_FRAME_CHECKS={actors:[{id:'synthetic-static-shape',pose_signature:[0,0],view:0}],boxes:[]};if(t>=4){c.font='8px sans-serif';c.fillText('TEST',62,12);MV_FRAME_CHECKS.boxes.push({id:'test-text',kind:'text',x:62,y:4,w:25,h:10});}};\n", encoding='utf-8')
        args=['node',str(ROOT/'scripts/render_canvas.mjs'),'--project='+str(project),'--out=out/probe']
        if a.canvas_module:
            args.append('--canvas-module='+a.canvas_module)
        subprocess.run(args,check=True,capture_output=True,text=True, encoding='utf-8')
        audit=json.loads((project/'out/probe/frame-audit.json').read_text(encoding='utf-8'))
        holds=[x for x in audit['findings'] if x['category']=='unchanged_local_pose']
        text=[x for x in audit['findings'] if x['category']=='text_outside_frame']
        assert len(holds)==1 and abs(holds[0]['range'][0]-3)<.09 and abs(holds[0]['range'][1]-5)<.09,holds
        assert len(text)==1 and abs(text[0]['range'][0]-4)<.09,text
        results.append({'fixture':'declared static geometry and overflowing text','hold_range_coalesced':True,'text_bounds_flagged':True,'not_an_acting_judgment':True})
        print(json.dumps({'ok': True, 'results': results, 'scope': 'Selected native-Canvas frames and optional encodes; not a general aesthetic or browser/p5 result.'}))
    finally:
        if not a.keep:
            shutil.rmtree(base)


if __name__ == '__main__':
    main()

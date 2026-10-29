#!/usr/bin/env python3
"""Render, mux, decode and inspect a two-second original Canvas2D runtime check."""
import argparse
from array import array
import hashlib
import json
import math
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import wave


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def pulses(path):
    rate = 24000
    with wave.open(str(path), 'wb') as w:
        w.setparams((1, 2, rate, 0, 'NONE', 'not compressed'))
        buf = bytearray()
        for i in range(rate*2):
            t, value = i/rate, 0.0
            for start, freq in ((.5, 660), (1.5, 880)):
                u = t-start
                if 0 <= u < .12:
                    value += .25*math.sin(math.pi*u/.12)*math.sin(2*math.pi*freq*u)
            buf += struct.pack('<h', round(32767*value))
        w.writeframes(buf)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('project', type=Path, help='new, isolated self-test project')
    p.add_argument('--runtime', choices=('node-canvas', 'browser'), required=True)
    p.add_argument('--canvas-module', type=Path)
    p.add_argument('--chrome', type=Path)
    p.add_argument('--record-in', type=Path, help='copy receipt and clip into an existing canvas2d project')
    a = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    target = a.project.expanduser().resolve()
    try:
        if a.record_in:
            prod = a.record_in.expanduser().resolve()
            if root == prod or root in prod.parents:
                raise ValueError('runtime receipts belong in the project, outside the installed skill')
            brief = json.loads((prod/'brief.json').read_text(encoding='utf-8'))
            if brief.get('execution', {}).get('engine') != 'canvas2d' or brief.get('execution', {}).get('runtime') != a.runtime:
                raise ValueError('receipt destination must explicitly select the tested canvas2d runtime')
            if (prod/'runtime-report.json').exists() or (prod/'out/runtime-check').exists():
                raise ValueError('existing receipt preserved; choose/review a new revision explicitly')
        subprocess.run([sys.executable, str(root/'scripts/build_study.py'), str(target), '--kind', 'runtime', '--subject', 'abstract', '--style', 'flat', '--width', '640', '--height', '360', '--tool-self-test'], capture_output=True, text=True, check=True, encoding='utf-8')
        audio = target/'assets/runtime-pulses.wav'
        pulses(audio)
        # Original synthetic cue text, unrelated to any song's lyrics.
        (target/'src/data/lyrics.js').write_text('globalThis.STORY_LYRICS_MODE="full-lines";globalThis.STORY_LYRICS={alignment_status:"synthetic_known",cues:[{start:0,end:1,text:"Runtime cue A"},{start:1,end:2,text:"Runtime cue B"}]};\n', encoding='utf-8')
        if a.runtime == 'node-canvas':
            cmd = ['node', str(root/'scripts/render_canvas.mjs'), '--project='+str(target), '--out=out/runtime', '--audio=assets/runtime-pulses.wav', '--times=0.5,1,1.5']
            if a.canvas_module:
                cmd.append('--canvas-module='+str(a.canvas_module.expanduser().resolve()))
            subprocess.run(cmd, capture_output=True, text=True, check=True, encoding='utf-8')
            report = json.loads((target/'out/runtime/render-report.json').read_text(encoding='utf-8'))
            clip = target/'out/runtime/clip.mp4'
        else:
            cmd = ['node', 'render.mjs', '--clip', '--out=out/runtime/clip.mp4', '--audio=assets/runtime-pulses.wav', '--fps=30']
            if a.chrome:
                cmd.append('--chrome='+str(a.chrome.expanduser().resolve()))
            subprocess.run(cmd, cwd=target, capture_output=True, text=True, check=True, encoding='utf-8')
            subprocess.run(['node', 'render.mjs', '--stills=0.5,1,1.5', '--out=out/runtime/stills']+(['--chrome='+str(a.chrome.expanduser().resolve())] if a.chrome else []), cwd=target, capture_output=True, text=True, check=True, encoding='utf-8')
            clip = target/'out/runtime/clip.mp4'
            report = {'status': 'passed', 'runtime': {'node': subprocess.check_output(['node', '--version'], text=True, encoding='utf-8').strip()}, 'scope': 'Canvas2D browser self-test only; no p5/WebGL or project aesthetics certification.'}
        info = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-count_frames', '-show_format', '-show_streams', '-of', 'json', str(clip)]))
        v = next(s for s in info['streams'] if s['codec_type']=='video')
        if (v['width'], v['height'], int(v.get('nb_read_frames', 0))) != (640, 360, 60) or abs(float(info['format']['duration'])-2) > .12 or not any(s['codec_type']=='audio' for s in info['streams']):
            raise ValueError('runtime encode dimensions/frame count/audio/duration failed')
        subprocess.run(['ffmpeg', '-v', 'error', '-i', str(clip), '-f', 'null', '-'], capture_output=True, check=True)
        pcm = array('h', subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(clip), '-map', '0:a:0', '-ar', '8000', '-ac', '1', '-f', 's16le', '-']))
        if sys.byteorder != 'little':
            pcm.byteswap()
        starts, active = [], False
        for i in range(0,len(pcm),160):
            block = pcm[i:i+160]
            rms = math.sqrt(sum(x*x for x in block)/max(1,len(block)))/32768
            loud = rms>.03
            if loud and not active:
                starts.append(i/8000)
            active = loud
        if len(starts)!=2 or any(abs(x-y)>.06 for x,y in zip(starts,[.5,1.5])):
            raise ValueError('synthetic audio pulse offsets failed: '+str(starts))
        report.update(schema_version=1, status='passed', engine='canvas2d', runtime_backend=a.runtime, encoded={'full_decode':True,'video':True,'audio':True,'frames':60}, sync_test={'scope':'synthetic pulses only','expected':[.5,1.5],'observed':starts,'tolerance_seconds':.06}, artifact={'path':clip.relative_to(target).as_posix(),'sha256':sha(clip)})
        (target/'runtime-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        if a.record_in:
            dest = prod/'out/runtime-check'
            dest.mkdir(parents=True)
            for f in (target/'out/runtime').rglob('*'):
                if f.is_file():
                    d = dest/f.relative_to(target/'out/runtime')
                    d.parent.mkdir(parents=True,exist_ok=True)
                    shutil.copy2(f,d)
            report['artifact']['path'] = 'out/runtime-check/clip.mp4'
            (prod/'runtime-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        print(json.dumps({'status':'passed','runtime':a.runtime,'project':str(target),'pulse_offsets':starts,'scope':report['scope']}))
    except (OSError, ValueError, KeyError, StopIteration, subprocess.SubprocessError) as exc:
        detail = getattr(exc,'stderr','') or ''
        if isinstance(detail,bytes):
            detail = detail.decode(errors='replace')
        p.error(str(exc)+(': '+detail[-1500:] if detail else ''))


if __name__ == '__main__':
    import sys
    for _stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(_stream, 'reconfigure'):
            _stream.reconfigure(encoding='utf-8')
    main()

#!/usr/bin/env python3
"""Measure audio metadata and an RMS/change guide; never infer verified beats, lyrics or story."""
import argparse
from array import array
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('audio', type=Path)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--window', type=float, default=.5)
    p.add_argument('--plot', type=Path)
    a = p.parse_args()
    if a.plot and a.plot.resolve()==a.out.resolve():
        p.error('JSON and plot outputs must be distinct')
    if not .05 <= a.window <= 10 or not math.isfinite(a.window):
        p.error('window must be 0.05..10 seconds')
    if a.out.exists() or (a.plot and a.plot.exists()):
        p.error('output exists; choose a new revision path')
    try:
        probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(a.audio)]))
        streams = [s for s in probe['streams'] if s.get('codec_type') == 'audio']
        if not streams:
            raise ValueError('no audio stream')
        duration = float(probe['format']['duration'])
        digest = hashlib.sha256()
        with a.audio.open('rb') as f:
            for part in iter(lambda: f.read(1024*1024), b''):
                digest.update(part)
        rate = 8000
        chunk = round(rate*a.window)*2
        proc = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', str(a.audio), '-map', '0:a:0', '-ac', '1', '-ar', str(rate), '-f', 's16le', '-'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        windows, t = [], 0.0
        while True:
            raw = proc.stdout.read(chunk)
            if not raw:
                break
            samples = array('h', raw)
            if sys.byteorder != 'little':
                samples.byteswap()
            rms = math.sqrt(sum(x*x for x in samples)/max(1, len(samples)))/32768
            windows.append({'start': round(t, 5), 'end': round(t+len(samples)/rate, 5), 'rms': round(rms, 6)})
            t += len(samples)/rate
        stderr = proc.stderr.read().decode(errors='replace')
        if proc.wait():
            raise ValueError('audio decode failed: '+stderr)
        changes = [{'time': w['start'], 'rms_delta': round(w['rms']-windows[i-1]['rms'], 6), 'status': 'candidate'} for i, w in enumerate(windows) if i and w['rms']-windows[i-1]['rms'] > .02]
        result = {'schema_version': 1, 'audio_sha256': digest.hexdigest(), 'duration': duration, 'sample_rate': streams[0].get('sample_rate'), 'channels': streams[0].get('channels'), 'analysis_rate': rate, 'window_seconds': a.window, 'windows': windows, 'energy_rise_candidates': changes, 'sections': [], 'sections_status': 'unreviewed', 'beats_status': 'not_measured', 'scope': 'Measured recording metadata and mono RMS energy only. Section boundaries, musical accents, meaning and beat timing require listening; RMS changes are not verified beats.'}
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        if a.plot:
            bars = ''.join(f'<rect x="{40+840*i/max(1,len(windows)):.2f}" y="{200-160*w["rms"]:.2f}" width="{max(.5,840/max(1,len(windows))):.2f}" height="{160*w["rms"]:.2f}" fill="#557d94"/>' for i,w in enumerate(windows))
            a.plot.parent.mkdir(parents=True, exist_ok=True)
            a.plot.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="920" height="240"><rect width="920" height="240" fill="#f4f6f7"/><text x="40" y="30" font-family="sans-serif" font-size="16">Measured RMS energy - section/beat markers need review</text>'+bars+f'<text x="40" y="225" font-family="sans-serif">0 s</text><text x="815" y="225" font-family="sans-serif">{duration:.2f} s</text></svg>', encoding='utf-8')
        print(json.dumps({'out': str(a.out), 'duration': duration, 'windows': len(windows), 'sections_verified': False}))
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        p.error(str(exc))


if __name__ == '__main__':
    import sys
    for _stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(_stream, 'reconfigure'):
            _stream.reconfigure(encoding='utf-8')
    main()

#!/usr/bin/env python3
"""Create an explicit original style/acting study or a complete original demonstration film."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import wave


def original_score(path, duration=60, rate=22050):
    import numpy as np
    count = int(duration * rate)
    song = np.zeros(count, dtype=np.float64)
    bpm, beat = 96, .625
    notes = [0, 4, 7, 9, 7, 4, 2, 4, 0, 7, 9, 12, 11, 7, 4, 2]
    rng = np.random.default_rng(4127)
    def add(start, frequency, length, gain, kind='note'):
        i = int(start * rate)
        n = min(int(length * rate), count - i)
        if n <= 0:
            return
        t = np.arange(n) / rate
        if kind == 'kick':
            signal = np.sin(2 * np.pi * (49 * t + 6 * (1 - np.exp(-t * 32)))) * np.exp(-t * 18)
        elif kind == 'snare':
            signal = rng.normal(0, .4, n) * np.exp(-t * 30)
        else:
            signal = (np.sin(2 * np.pi * frequency * t) + .18 * np.sin(2 * np.pi * frequency * 2 * t)) * (1 - np.exp(-t * 35)) * np.exp(-t * 3)
        song[i:i + n] += signal * gain
    for k in range(int(duration / beat)):
        chapter = min(5, int(k * beat / (duration / 6)))
        add(k * beat, 0, .25, .22 if chapter != 3 else .07, 'kick')
        if k % 4 in (1, 3):
            add(k * beat, 0, .15, .1 if chapter != 3 else .025, 'snare')
        semitone = notes[k % 16] + (12 if chapter == 5 and k % 4 == 0 else 0)
        add(k * beat + .01, 261.6256 * 2 ** (semitone / 12), .55, .10 if chapter != 3 else .055)
        if k % 4 == 0:
            chord = [(0, 4, 7), (-3, 0, 4), (5, 9, 12), (7, 11, 14)][(k // 16) % 4]
            for note in chord:
                add(k * beat, 130.8128 * 2 ** (note / 12), 2.2, .045)
    fade = min(rate, len(song) // 4)
    song[-fade:] *= np.linspace(1, 0, fade)
    song = np.clip(song, -.94, .94)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), 'wb') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(rate)
        f.writeframes((song * 32767).astype('<i2').tobytes())
    return {'origin': 'Original deterministic score synthesized by this script; no existing recording or private inputs.', 'bpm': bpm, 'first_beat': 0, 'duration': duration, 'sung_lyrics': False}


def build(target, root, kind, subject, style, width=960, height=540, fps=24, duration=None):
    import math
    if kind != 'film' and duration is not None:
        raise ValueError('custom duration is supported only for the film example')
    duration = (30 if duration is None else duration) if kind == 'film' else 8
    if not isinstance(duration,(int,float)) or not math.isfinite(duration) or duration < (12 if kind == 'film' else 1):
        raise ValueError('film example duration must be at least 12 seconds')
    manifest = json.loads((root / 'assets/style-packs' / (style + '.json')).read_text(encoding='utf-8'))
    subprocess.run([sys.executable, str(root / 'scripts/scaffold.py'), str(target), '--engine', 'canvas2d', '--duration', str(duration), '--width', str(width), '--height', str(height), '--fps', str(fps), '--tool-self-test'], capture_output=True, text=True, check=True, encoding='utf-8')
    for name in ('motion.js', 'acting.js'):
        shutil.copy2(root / 'assets/modules' / name, target / 'src' / name)
    shutil.copy2(root / 'assets/style-packs/kit.js', target / 'src/style-kit.js')
    shutil.copy2(root / 'assets/style-packs/demo-scene.js', target / 'src/scene.js')
    shutil.copy2(root / 'assets/review-player.html', target / 'review-player.html')
    demo = {'kind': kind, 'subject': subject, 'manifest': manifest, 'original_demo': True, 'not_a_project_default': True}
    (target / 'src/demo.js').write_text('globalThis.DEMO=' + json.dumps(demo) + ';\nif(!globalThis.makeStudyCanvas)globalThis.makeStudyCanvas=(w,h)=>{const c=document.createElement("canvas");c.width=w;c.height=h;return c;};\n', encoding='utf-8')
    scripts = ['src/config.js', 'src/motion.js', 'src/acting.js', 'src/style-kit.js', 'src/demo.js', 'src/scene.js', 'src/data/lyrics.js', 'src/lyrics-overlay.js']
    (target / 'src/render-entry.json').write_text(json.dumps({'scripts': scripts}, indent=2) + '\n', encoding='utf-8')
    html = (target / 'studio.html').read_text(encoding='utf-8')
    extra = ''.join('<script src="' + x + '"></script>' for x in scripts[1:5])
    (target / 'studio.html').write_text(html.replace('<script src="src/scene.js">', extra + '<script src="src/scene.js">'), encoding='utf-8')
    brief = json.loads((target / 'brief.json').read_text(encoding='utf-8'))
    brief.update(goal='Original demonstration of scenic progression and selected code drawing method', emotion='curiosity through difficulty to renewed possibility', asset_policy='all-code', request_mode='production', phase='prototype')
    brief['style'].update(direction=style, medium='Canvas2D original demonstration', palette=manifest['palette'], proportions='example stylized large-head figures' if subject == 'figures' else None, motion='articulated time-based poses' if subject == 'figures' else 'time-based graphic development')
    brief['structure'].update(mode='narrative' if subject == 'figures' else subject, outline=['a light is found', 'it travels', 'rain creates difficulty', 'small lights renew hope', 'a message is noticed', 'the light is shared'], ending='an open path remains')
    brief['characters'].update(required=subject == 'figures', roles=['courier-a', 'courier-b'] if subject == 'figures' else [])
    brief['lyrics'].update(mode='in-world', language='en')
    brief['output']['aspect_ratio'] = '16:9' if width * 9 == height * 16 else f'{width}:{height}'
    brief['execution'].update(runtime='node-canvas', production_authorized=False)
    score = original_score(target / 'assets/original-score.wav', duration)
    (target / 'data/score.json').write_text(json.dumps(score, indent=2) + '\n', encoding='utf-8')
    brief['music'].update(title='The Light We Carry - original procedural study', source='original-code', audio='assets/original-score.wav', duration=duration, scope=f'complete original {duration}-second instrumental demonstration' if kind == 'film' else 'eight-second controlled demonstration')
    brief['confirmed_fields'] = ['style.direction', 'asset_policy', 'characters.required', 'output.resolution']
    (target / 'brief.json').write_text(json.dumps(brief, indent=2) + '\n', encoding='utf-8')
    mapping = {'schema_version': 1, 'duration': duration, 'duration_status': 'recording_measured', 'sections': [], 'shots': [], 'audio_sha256': __import__('hashlib').sha256((target / 'assets/original-score.wav').read_bytes()).hexdigest()}
    events = ['discover the light', 'carry it through the station', 'protect it in rain', 'notice other lights', 'notice a waiting message', 'share the light and leave an open path'] if kind == 'film' else ['approach, reach, contact, transfer and release']
    for i, event in enumerate(events):
        start, end = (i * duration / 6, (i + 1) * duration / 6) if kind == 'film' else (0, 8)
        mapping['sections'].append({'id': f'part-{i + 1}', 'start': start, 'end': end, 'music_read': 'known synthesized 96 BPM score', 'emotion': event})
        mapping['shots'].append({'id': f's{i + 1:02d}', 'start': start, 'end': end, 'section_id': f'part-{i + 1}', 'objective': event, 'visible_change': event if subject == 'figures' else 'graphic arrangement develops through the selected subject', 'assets': ['light', 'courier-a', 'courier-b'] if subject == 'figures' else ['light'], 'transition': {'type': 'foreground star cover' if kind == 'film' else 'none', 'window': [.8, .8] if kind == 'film' else None}})
    (target / 'shot-map.json').write_text(json.dumps(mapping, indent=2) + '\n', encoding='utf-8')
    (target / 'DEMO.json').write_text(json.dumps(demo, indent=2) + '\n', encoding='utf-8')
    return {'project': str(target), 'kind': kind, 'style': style, 'subject': subject, 'duration': duration, 'audio': 'assets/original-score.wav', 'scope': 'Original optional example; no claim that this design satisfies a different project or matches a reference.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('project', type=Path)
    p.add_argument('--kind', choices=('style', 'film'), required=True)
    p.add_argument('--style', choices=('flat', 'cut-paper', 'pixel', 'ink'), required=True)
    p.add_argument('--subject', choices=('figures', 'type', 'abstract'), required=True)
    p.add_argument('--width', type=int, default=960)
    p.add_argument('--height', type=int, default=540)
    p.add_argument('--fps', type=int, default=24)
    p.add_argument('--duration', type=float, help='film only; default 30 seconds, six scenes')
    p.add_argument('--tool-self-test', action='store_true', help='isolated toolkit example only, never a requested user MV')
    a = p.parse_args()
    if not a.tool_self_test:
        p.error('this builder is for isolated tool verification; --tool-self-test cannot replace user content confirmation')
    try:
        print(json.dumps(build(a.project.expanduser().resolve(), Path(__file__).resolve().parents[1], a.kind, a.subject, a.style, a.width, a.height, a.fps, a.duration)))
    except subprocess.CalledProcessError as e:
        p.error(e.stderr or str(e))
    except (ValueError, OSError) as e:
        p.error(str(e))


if __name__ == '__main__':
    import sys
    for _stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(_stream, 'reconfigure'):
            _stream.reconfigure(encoding='utf-8')
    main()

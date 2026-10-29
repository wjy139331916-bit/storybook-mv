#!/usr/bin/env python3
"""Measure reference/output media. Findings are review candidates, never aesthetic scores."""
import argparse
import hashlib
import io
import json
import math
from pathlib import Path
import re
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def command(args):
    r = subprocess.run(args, capture_output=True)
    if r.returncode:
        raise ValueError(r.stderr.decode(errors='replace')[-2000:])
    return r.stdout


def probe(path):
    p = Path(path).expanduser().resolve()
    if not p.is_file():
        raise ValueError('input file is missing')
    return json.loads(command(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(p)]))


def output_dir(path):
    p = Path(path).expanduser().resolve()
    if p.exists() and (not p.is_dir() or any(p.iterdir())):
        raise ValueError('output directory must be empty; previous evidence was preserved')
    p.mkdir(parents=True, exist_ok=True)
    return p


def save(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def crop_filter(crop, video):
    if not crop:
        return []
    a = [int(x) for x in crop.split(',')]
    if len(a) != 4:
        raise ValueError('crop is x,y,width,height')
    x, y, w, h = a
    if min(x, y) < 0 or min(w, h) <= 0 or x + w > video['width'] or y + h > video['height']:
        raise ValueError('crop must be inside the video')
    return [f'crop={w}:{h}:{x}:{y}']


def ranges(flags, fps, minimum=0):
    result, start = [], None
    for i, yes in enumerate(list(flags) + [False]):
        if yes and start is None:
            start = i
        if not yes and start is not None:
            if (i - start) / fps >= minimum:
                result.append([round(start / fps, 4), round(i / fps, 4)])
            start = None
    return result


def apply_exceptions(findings, policy, duration):
    exemptions = policy.get('intentional_ranges', [])
    for e in exemptions:
        a, b = e.get('range', [None, None])
        if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in (a, b)) or not 0 <= a < b <= duration + .1 or not e.get('reason') or not e.get('categories'):
            raise ValueError('intentional ranges need valid bounds, categories and an explanation')
    for f in findings:
        f['disposition'] = 'needs_review'
        for e in exemptions:
            if f['category'] in e['categories'] and e['range'][0] <= f['range'][0] and e['range'][1] >= f['range'][1] - .001:
                f.update(disposition='declared_intent', reason=e['reason'])
                break
    return findings


def still(path, t, filters):
    data = command(['ffmpeg', '-v', 'error', '-ss', str(t), '-i', str(path), '-vf', ','.join(filters + ['scale=640:-2']), '-frames:v', '1', '-f', 'image2pipe', '-c:v', 'png', '-'])
    return Image.open(io.BytesIO(data)).convert('RGB')


def video_audit(path, out, crop=None, sample_fps=12, mapping=None, policy=None):
    if not math.isfinite(sample_fps) or not 1 <= sample_fps <= 30:
        raise ValueError('sample fps must be 1..30')
    info = probe(path)
    v = next((s for s in info['streams'] if s['codec_type'] == 'video'), None)
    if not v:
        raise ValueError('input has no video stream')
    duration = float(info['format']['duration'])
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError('invalid media duration')
    filters = crop_filter(crop, v)
    args = ['ffmpeg', '-v', 'error', '-i', str(path), '-vf', ','.join(filters + [f'fps={sample_fps}', 'scale=128:72', 'format=gray']), '-f', 'rawvideo', '-']
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    prev, differences, luma, black = None, [], [], []
    while True:
        raw = proc.stdout.read(128 * 72)
        if not raw:
            break
        if len(raw) != 128 * 72:
            proc.kill()
            raise ValueError('truncated decoded measurement frame')
        a = np.frombuffer(raw, dtype=np.uint8).astype(np.float32) / 255
        differences.append(0.0 if prev is None else float(np.mean(np.abs(a - prev))))
        luma.append(float(a.mean()))
        black.append(float(a.mean()) < .018 and float(np.quantile(a, .99)) < .07)
        prev = a
    error = proc.stderr.read().decode(errors='replace')
    proc.stdout.close()
    proc.stderr.close()
    if proc.wait() or not differences:
        raise ValueError(error or 'no decodable frames')
    d = np.array(differences)
    cuts = []
    for i in range(1, len(d)):
        around = np.r_[d[max(1, i - 4):i], d[i + 1:i + 5]]
        if d[i] > .12 and d[i] > 2.5 * max(.001, float(np.median(around)) if len(around) else 0):
            if not cuts or i / sample_fps - cuts[-1] > 1 / sample_fps:
                cuts.append(round(i / sample_fps, 4))
    motion_threshold = float((policy or {}).get('low_change_threshold', .002))
    hold_seconds = float((policy or {}).get('low_change_seconds', 3))
    if not 0 <= motion_threshold < 1 or not math.isfinite(hold_seconds) or hold_seconds <= 0:
        raise ValueError('invalid measurement thresholds')
    findings = [{'category': 'low_change', 'range': r, 'observation': 'Small grayscale frame differences; camera/texture motion can hide unchanged acting.'} for r in ranges(d < motion_threshold, sample_fps, hold_seconds)]
    findings += [{'category': 'near_black', 'range': r, 'observation': 'Measured near-black frames; check intentional fades and cuts.'} for r in ranges(black, sample_fps)]
    planned = [float(s['start']) for s in (mapping or {}).get('shots', []) if s.get('start', 0) > 0]
    tolerance = max(.15, 2 / sample_fps)
    if planned:
        findings += [{'category': 'unplanned_cut_candidate', 'range': [t, min(duration, t + 1 / sample_fps)], 'observation': 'Large isolated frame difference away from a planned boundary; effects can also cause this.'} for t in cuts if min(abs(t - c) for c in planned) > tolerance]
    apply_exceptions(findings, policy or {}, duration)
    times = np.linspace(0, max(0, duration - 1 / sample_fps), min(12, max(3, int(duration / 2) + 1)))
    frames = [still(path, float(t), filters) for t in times]
    thumb_w, thumb_h = 320, max(80, round(320 * frames[0].height / frames[0].width))
    sheet = Image.new('RGB', (thumb_w * 3, (thumb_h + 26) * math.ceil(len(frames) / 3)), '#ececec')
    draw = ImageDraw.Draw(sheet)
    palette = {}
    for i, (t, im) in enumerate(zip(times, frames)):
        x, y = i % 3 * thumb_w, i // 3 * (thumb_h + 26)
        sheet.paste(ImageOps.contain(im, (thumb_w, thumb_h)), (x, y + 26))
        draw.text((x + 8, y + 6), f'{t:.3f}s', fill='#151515')
        quant = im.resize((96, 54)).quantize(colors=8)
        pal = quant.getpalette()
        for count, index in sorted(quant.getcolors(), reverse=True)[:5]:
            color = '#%02x%02x%02x' % tuple(pal[index * 3:index * 3 + 3])
            palette[color] = palette.get(color, 0) + count
    sheet.save(out / 'contact-sheet.jpg', quality=90)
    for i in (0, len(frames) // 2, len(frames) - 1):
        frames[i].save(out / f'still-{i:02d}.png')
    edges = [0] + cuts + [duration]
    lengths = np.diff(edges)
    result = {'schema_version': 1, 'target': {'name': Path(path).name, 'sha256': sha(path)}, 'duration': duration, 'dimensions': [v['width'], v['height']], 'crop_xywh': crop, 'sample_fps': sample_fps, 'cut_candidates': cuts, 'shot_length_candidates': {'median': float(np.median(lengths)), 'min': float(lengths.min()), 'max': float(lengths.max())}, 'palette_candidates': sorted(palette, key=palette.get, reverse=True)[:12], 'findings': findings, 'motion_series': [{'t': round(i / sample_fps, 4), 'difference': round(float(x), 6), 'luma': round(luma[i], 6)} for i, x in enumerate(d)], 'manual_analysis': {'line_weight': None, 'subject_scale': None, 'layering': None, 'camera': None, 'transition_mechanisms': [], 'lyric_object_meaning': None}, 'scope': 'Measured candidates at reduced resolution. Slow dissolves, small text and subtle acting require targeted full-resolution review. No automatic beauty, story, natural-motion or beat verdict.'}
    save(out / 'media-audit.json', result)
    return result


def compare_images(reference, rendered, out):
    images = [Image.open(p).convert('RGB') for p in (reference, rendered)]
    canvas = Image.new('RGB', (1280, 480), '#e8e8e8')
    d = ImageDraw.Draw(canvas)
    for i, im in enumerate(images):
        fit = ImageOps.contain(im, (624, 380))
        x = i * 640 + (640 - fit.width) // 2
        y = 50 + (380 - fit.height) // 2
        canvas.paste(fit, (x, y))
        d.text((i * 640 + 12, 15), ('REFERENCE' if i == 0 else 'RENDER') + f' | {im.width} x {im.height}', fill='#111111')
        for j in range(1, 10):
            d.line((x + fit.width * j / 10, y, x + fit.width * j / 10, y + fit.height), fill='#aaaaaa', width=1)
            d.line((x, y + fit.height * j / 10, x + fit.width, y + fit.height * j / 10), fill='#aaaaaa', width=1)
    d.text((12, 451), 'Compare subject scale, margins, palette, line and texture. Different aspects are fitted, never stretched.', fill='#111111')
    canvas.save(out / 'compare.png')
    result = {'schema_version': 1, 'reference_sha256': sha(reference), 'render_sha256': sha(rendered), 'comparison': 'compare.png', 'differences_to_review': [], 'scope': 'Visual comparison aid; no similarity score. Contains reference pixels: keep in the project private reference area.'}
    save(out / 'compare.json', result)
    return result


def pcm(path, start=0, duration=None, rate=8000):
    args = ['ffmpeg', '-v', 'error', '-ss', str(start), '-i', str(path), '-vn']
    if duration is not None:
        args += ['-t', str(duration)]
    data = command(args + ['-ac', '1', '-ar', str(rate), '-f', 'f32le', '-'])
    return np.frombuffer(data, dtype='<f4').copy()


def loudness(path, start=0, duration=None):
    args = ['ffmpeg', '-hide_banner', '-nostats', '-ss', str(start), '-i', str(path)]
    if duration is not None:
        args += ['-t', str(duration)]
    r = subprocess.run(args + ['-vn', '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True)
    if r.returncode:
        raise ValueError(r.stderr[-2000:])
    integrated = re.findall(r'I:\s*(-?[\d.]+) LUFS', r.stderr)
    peaks = re.findall(r'Peak:\s*(-?[\d.]+) dBFS', r.stderr)
    return {'integrated_lufs': float(integrated[-1]) if integrated else None, 'true_peak_dbfs': float(peaks[-1]) if peaks else None}


def audio_audit(reference, encoded, out, audio_start=0):
    inf = probe(encoded)
    if not any(s['codec_type'] == 'audio' for s in inf['streams']):
        raise ValueError('encoded file has no audio')
    duration = float(inf['format']['duration'])
    if not math.isfinite(audio_start) or audio_start < 0:
        raise ValueError('audio start must be nonnegative')
    rate, hop = 8000, 80
    a, b = pcm(reference, audio_start, duration), pcm(encoded, 0, duration)
    n = min(len(a), len(b)) // hop
    if n < 50:
        raise ValueError('audio is too short for the envelope audit')
    def env(x):
        return np.sqrt(np.mean(x[:n * hop].reshape(n, hop) ** 2, axis=1))
    ea, eb = env(a), env(b)
    anchors = []
    for center in np.linspace(min(3, duration / 2), max(min(3, duration / 2), duration - 3), 3):
        lo, hi = max(0, int((center - 2) * 100)), min(n, int((center + 2) * 100))
        scores = []
        for lag in range(-50, 51):
            l, h = max(lo, -lag), min(hi, n - lag)
            x, y = ea[l:h], eb[l + lag:h + lag]
            x, y = x - x.mean(), y - y.mean()
            den = float(np.linalg.norm(x) * np.linalg.norm(y))
            scores.append(float(np.dot(x, y) / den) if den > 1e-9 else -1)
        best = int(np.argmax(scores))
        peak = scores[best]
        alternatives = [s for i, s in enumerate(scores) if abs(i - best) > 5]
        ambiguity = peak - max(alternatives) if alternatives else 0
        informative = peak > .75 and ambiguity > .015 and best not in (0, 100)
        anchors.append({'at': round(float(center), 3), 'encoded_delay_seconds': round((best - 50) / 100, 3) if informative else None, 'correlation': round(peak, 4), 'peak_margin': round(ambiguity, 4), 'status': 'measured_candidate' if informative else 'ambiguous'})
    lr, le = loudness(reference, audio_start, duration), loudness(encoded)
    result = {'schema_version': 1, 'reference_sha256': sha(reference), 'encoded_sha256': sha(encoded), 'reference_start': audio_start, 'duration': duration, 'anchors': anchors, 'reference_loudness': lr, 'encoded_loudness': le, 'lufs_difference': round(le['integrated_lufs'] - lr['integrated_lufs'], 3) if le['integrated_lufs'] is not None and lr['integrated_lufs'] is not None else None, 'scope': 'Decoded mono RMS-envelope correlation at 10ms steps, search +/-0.5s; ambiguous periodic/silent audio is not certified. Checks mux alignment, not sung-word/caption timing. Loudness is measured, never normalized automatically.'}
    save(out / 'audio-audit.json', result)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='mode', required=True)
    for mode in ('reference', 'inspect'):
        s = sub.add_parser(mode)
        s.add_argument('video', type=Path)
        s.add_argument('--out', type=Path, required=True)
        s.add_argument('--crop', help='x,y,width,height')
        s.add_argument('--sample-fps', type=float, default=12)
        s.add_argument('--shot-map', type=Path)
        s.add_argument('--policy', type=Path)
    s = sub.add_parser('compare')
    s.add_argument('reference', type=Path)
    s.add_argument('rendered', type=Path)
    s.add_argument('--out', type=Path, required=True)
    s = sub.add_parser('audio')
    s.add_argument('reference', type=Path)
    s.add_argument('encoded', type=Path)
    s.add_argument('--out', type=Path, required=True)
    s.add_argument('--audio-start', type=float, default=0)
    a = p.parse_args()
    try:
        out = output_dir(a.out)
        if a.mode in ('reference', 'inspect'):
            result = video_audit(a.video.resolve(), out, a.crop, a.sample_fps, json.loads(a.shot_map.read_text()) if a.shot_map else None, json.loads(a.policy.read_text()) if a.policy else None)
        elif a.mode == 'compare':
            result = compare_images(a.reference, a.rendered, out)
        else:
            result = audio_audit(a.reference, a.encoded, out, a.audio_start)
        print(json.dumps({'out': str(out), 'mode': a.mode, 'findings': len(result.get('findings', [])), 'scope': result['scope']}, ensure_ascii=False))
    except (ValueError, OSError, KeyError) as exc:
        p.error(str(exc))


if __name__ == '__main__':
    main()

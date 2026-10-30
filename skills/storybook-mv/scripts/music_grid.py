#!/usr/bin/env python3
"""Propose a constant-tempo beat grid from transients; never infer meter, lyrics or emotion."""
import argparse
import json
import math
from pathlib import Path

import numpy as np
from media_audit import pcm, sha


def fit_grid(signal, rate=8000, bpm=None, offset=None):
    hop, size = 160, 512
    if len(signal) < rate * 2:
        raise ValueError('at least two seconds of audio are needed')
    count = (len(signal) - size) // hop + 1
    spectrum = np.empty((count, size // 2 + 1), dtype=np.float32)
    window = np.hanning(size)
    for i in range(count):
        spectrum[i] = np.log1p(np.abs(np.fft.rfft(signal[i * hop:i * hop + size] * window)))
    onset = np.r_[0., np.maximum(0, np.diff(spectrum, axis=0)).mean(axis=1)]
    onset = np.maximum(0, onset - np.median(onset))
    scale = float(np.percentile(onset, 95))
    if scale <= 1e-7:
        return {'status': 'insufficient_transients', 'candidates': [], 'beats': [], 'review_needed': True}
    onset = np.minimum(onset / scale, 4)
    step = hop / rate
    times = np.arange(len(onset)) * step + size / rate / 2
    duration = len(signal) / rate
    if bpm is not None and (not math.isfinite(bpm) or not 30 <= bpm <= 300):
        raise ValueError('bpm must be 30..300')
    if offset is not None and (not math.isfinite(offset) or not 0 <= offset < duration):
        raise ValueError('first beat must be within the audio')
    if bpm is None:
        options = []
        centered = onset - onset.mean()
        for tempo in np.arange(60, 181, .5):
            lag = round(60 / tempo / step)
            score = float(np.dot(centered[:-lag], centered[lag:]) / max(1, len(centered) - lag)) if lag < len(centered) else 0
            options.append((score, float(tempo)))
        options.sort(reverse=True)
        tempos = []
        for score, tempo in options:
            if all(abs(tempo - t) > 4 for t in tempos):
                tempos.append(tempo)
            if len(tempos) == 4:
                break
    else:
        tempos = [bpm]
    candidates = []
    for seed in tempos:
        best = None
        tempo_values = [bpm] if bpm is not None else np.arange(max(30, seed - 1.5), min(300, seed + 1.5) + .01, .1)
        for tempo in tempo_values:
            beat = 60 / tempo
            phases = [offset] if offset is not None else np.arange(0, beat, step)
            for phase in phases:
                grid = np.arange(phase, duration, beat)
                values = np.interp(grid, times, onset, left=0, right=0)
                # A window around each beat tolerates the FFT analysis resolution.
                values = np.maximum(values, np.maximum(np.interp(grid - step, times, onset, left=0, right=0), np.interp(grid + step, times, onset, left=0, right=0)))
                score = float(values.mean()) if len(values) else 0
                if best is None or score > best[0]:
                    best = (score, float(tempo), float(phase), grid)
        if best:
            score, tempo, phase, grid = best
            candidates.append({'bpm': round(tempo, 4), 'first_beat': round(phase, 4), 'onset_agreement': round(score, 4), 'beats': [round(float(t), 4) for t in grid]})
    candidates.sort(key=lambda c: c['onset_agreement'], reverse=True)
    selected = candidates[0]
    peaks = [i for i in range(1, len(onset) - 1) if onset[i] >= onset[i - 1] and onset[i] > onset[i + 1] and onset[i] > .25]
    residuals = []
    peak_times = times[peaks]
    for q in (.1, .5, .9):
        at = duration * q
        local_beats = [t for t in selected['beats'] if abs(t - at) < 2]
        offsets = [float(peak_times[np.argmin(np.abs(peak_times - t))] - t) for t in local_beats] if len(peak_times) else []
        residuals.append({'region': q, 'nearest_transient_residual_median': round(float(np.median(offsets)), 4) if offsets else None})
    return {'status': 'proposed', 'selected': {k: v for k, v in selected.items() if k != 'beats'}, 'beats': selected['beats'], 'candidates': [{k: v for k, v in c.items() if k != 'beats'} for c in candidates], 'anchor_residuals': residuals, 'review_needed': True, 'meter': None, 'downbeats': [], 'sections_status': 'unreviewed', 'supplied_hints': {'bpm': bpm, 'first_beat': offset}, 'limits': ['Constant-tempo model; half/double tempo and syncopation remain ambiguous.', 'Check the beginning, middle and end by listening; variable tempo needs a piecewise grid.', 'Nearest transients are not proof of beats, downbeats or musical meaning.']}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('audio', type=Path)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--bpm', type=float)
    p.add_argument('--first-beat', type=float)
    a = p.parse_args()
    try:
        if a.out.exists():
            raise ValueError('output exists; previous analysis was preserved')
        result = fit_grid(pcm(a.audio), bpm=a.bpm, offset=a.first_beat)
        result.update(schema_version=1, audio_sha256=sha(a.audio), scope='Transient-based timing proposal. Music, words and emotion require review; no automatic beat certification.')
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'out': str(a.out), 'status': result['status'], 'selected': result.get('selected'), 'review_needed': True}))
    except (ValueError, OSError) as exc:
        p.error(str(exc))


if __name__ == '__main__':
    import sys
    for _stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(_stream, 'reconfigure'):
            _stream.reconfigure(encoding='utf-8')
    main()

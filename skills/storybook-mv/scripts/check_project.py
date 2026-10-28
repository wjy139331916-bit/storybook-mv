#!/usr/bin/env python3
"""Validate numerical shot/cue structure; do not certify aesthetic or sync quality."""
import argparse
import json
import math
from pathlib import Path


def finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def check(shots, lyrics, duration):
    errors, warnings = [], []
    if not finite(duration) or duration <= 0:
        return ['invalid duration'], warnings
    eps = 0.001
    if shots is not None:
        items = shots.get('shots') if isinstance(shots, dict) else None
        if not isinstance(items, list) or not items:
            errors.append('timeline must contain nonempty shots')
        else:
            cursor, ids = 0, set()
            for i, shot in enumerate(items):
                if not isinstance(shot, dict):
                    errors.append(f'shot {i}: not an object')
                    continue
                a, b = shot.get('start'), shot.get('end')
                if not finite(a) or not finite(b) or a < 0 or b <= a or b > duration + eps:
                    errors.append(f'shot {i}: invalid bounds')
                    continue
                if abs(a - cursor) > eps:
                    errors.append(f'shot {i}: gap or overlap near {cursor:g}')
                cursor = b
                ident = shot.get('id')
                if not isinstance(ident, str) or not ident or ident in ids:
                    errors.append(f'shot {i}: missing/duplicate id')
                if isinstance(ident, str) and ident:
                    ids.add(ident)
                if not shot.get('action'):
                    warnings.append(f'shot {ident}: no action recorded')
            if abs(cursor - duration) > eps:
                errors.append('shots do not cover the final duration')
        if finite(shots.get('duration')) and abs(shots['duration'] - duration) > eps:
            errors.append('shot file duration differs from master duration')
    if lyrics is not None:
        cues = lyrics.get('cues') if isinstance(lyrics, dict) else None
        if not isinstance(cues, list):
            errors.append('lyrics must contain a cues array')
        else:
            cursor = -1
            for i, cue in enumerate(cues):
                if not isinstance(cue, dict):
                    errors.append(f'cue {i}: not an object')
                    continue
                a, b = cue.get('start'), cue.get('end')
                if not finite(a) or not finite(b) or a < 0 or b <= a or b > duration + eps:
                    errors.append(f'cue {i}: invalid bounds')
                    continue
                if a < cursor - eps:
                    errors.append(f'cue {i}: out of order or overlapping')
                cursor = b
                if not isinstance(cue.get('text'), str) or not cue['text'].strip():
                    errors.append(f'cue {i}: empty/missing text')
        if cues and lyrics.get('alignment_status') != 'ear_checked':
            warnings.append('Lyric timing is not marked ear_checked; numerical validity is not verified singing sync.')
        if finite(lyrics.get('duration')) and abs(lyrics['duration'] - duration) > eps:
            errors.append('lyric file duration differs from master duration')
    return errors, warnings


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--shots', type=Path)
    p.add_argument('--lyrics', type=Path)
    p.add_argument('--duration', type=float, required=True)
    a = p.parse_args()
    if not a.shots and not a.lyrics:
        p.error('provide --shots and/or --lyrics')
    try:
        shots = json.loads(a.shots.read_text(encoding='utf-8')) if a.shots else None
        lyrics = json.loads(a.lyrics.read_text(encoding='utf-8')) if a.lyrics else None
        if shots is not None and not isinstance(shots, dict):
            raise ValueError('shots root must be an object')
        if lyrics is not None and not isinstance(lyrics, dict):
            raise ValueError('lyrics root must be an object')
        errors, warnings = check(shots, lyrics, a.duration)
    except (OSError, ValueError) as exc:
        p.error(str(exc))
    print(json.dumps({'ok': not errors, 'errors': errors, 'warnings': warnings, 'scope': 'numerical timeline and cue checks only'}, ensure_ascii=False, indent=2))
    return 2 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())

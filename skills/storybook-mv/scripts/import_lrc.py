#!/usr/bin/env python3
"""Import full lyric lines. Imported timing remains explicitly unverified."""
import argparse
import json
import math
import re
from pathlib import Path

STAMP = re.compile(r'\[(\d+):([0-5]?\d)(?:[.:](\d{1,3}))?\]')
META = re.compile(r'^\[([A-Za-z]+):(.*)\]\s*$')


def parse_lrc(text, duration, offset=0):
    if not math.isfinite(duration) or duration <= 0 or not math.isfinite(offset):
        raise ValueError('duration must be positive and all times finite')
    events, metadata = [], {}
    for number, raw in enumerate(text.lstrip('\ufeff').splitlines(), 1):
        stamps = list(STAMP.finditer(raw))
        if not stamps:
            if re.search(r'\[\d+:[^]]*\]', raw):
                raise ValueError(f'line {number}: malformed timestamp')
            meta = META.match(raw.strip())
            if meta:
                metadata[meta[1].lower()] = meta[2].strip()
            continue
        line = STAMP.sub('', raw).strip()
        if re.search(r'\[\d+:[^]]*\]', line):
            raise ValueError(f'line {number}: malformed timestamp')
        for match in stamps:
            fraction = float('0.' + match[3]) if match[3] else 0
            start = int(match[1]) * 60 + int(match[2]) + fraction + offset
            if start < -1e-6 or start >= duration:
                raise ValueError(f'line {number}: timestamp {start:g} outside audio duration')
            events.append((max(0, start), line))
    events.sort(key=lambda event: event[0])
    unique = []
    for event in events:
        if unique and abs(unique[-1][0] - event[0]) < 1e-7:
            if unique[-1][1] != event[1]:
                raise ValueError('different lines share one timestamp; choose canonical text explicitly')
            continue
        unique.append(event)
    cues = []
    for i, (start, line) in enumerate(unique):
        end = unique[i + 1][0] if i + 1 < len(unique) else duration
        if line:
            cues.append({'start': round(start, 6), 'end': round(end, 6), 'text': line})
    if not cues:
        raise ValueError('no timestamped nonempty lyric lines found')
    warnings = ['Cue ends are provisional; check silence, holds and final release by ear.']
    if metadata.get('offset', '0') not in ('0', '+0', '-0', ''):
        warnings.append('Embedded LRC offset tag was not applied; use explicit --offset after checking the recording.')
    return {'duration': duration, 'alignment_status': 'lrc_unverified', 'display_offset_seconds': offset, 'source_metadata': metadata, 'warnings': warnings, 'cues': cues}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('input', type=Path)
    p.add_argument('--duration', type=float, required=True)
    p.add_argument('--offset', type=float, default=0)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--js-out', type=Path)
    a = p.parse_args()
    try:
        result = parse_lrc(a.input.read_text(encoding='utf-8-sig'), a.duration, a.offset)
    except (OSError, ValueError) as exc:
        p.error(str(exc))
    encoded = json.dumps(result, ensure_ascii=False, indent=2)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(encoded + '\n', encoding='utf-8')
    if a.js_out:
        a.js_out.parent.mkdir(parents=True, exist_ok=True)
        a.js_out.write_text('globalThis.STORY_LYRICS = ' + encoded + ';\n', encoding='utf-8')
    print(json.dumps({'lines': len(result['cues']), 'alignment_status': result['alignment_status'], 'out': str(a.out)}, ensure_ascii=False))


if __name__ == '__main__':
    main()

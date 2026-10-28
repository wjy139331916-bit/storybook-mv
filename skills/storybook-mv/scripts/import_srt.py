#!/usr/bin/env python3
"""Import supplied SRT cues without inventing word timings or canonical lyric text."""
import argparse
import hashlib
import json
from pathlib import Path
import re


def seconds(value):
    m = re.fullmatch(r'(\d+):(\d{2}):(\d{2})[,.](\d{3})', value.strip())
    if not m or int(m[2]) >= 60 or int(m[3]) >= 60:
        raise ValueError('invalid SRT timestamp: ' + value)
    return int(m[1]) * 3600 + int(m[2]) * 60 + int(m[3]) + int(m[4]) / 1000


def parse(text):
    cues = []
    for block in re.split(r'\n\s*\n', text.lstrip('\ufeff').replace('\r\n', '\n').strip()):
        lines = block.splitlines()
        if not lines:
            continue
        if lines[0].strip().isdigit():
            lines.pop(0)
        if not lines or '-->' not in lines[0]:
            raise ValueError('SRT block has no timestamp line')
        a, b = lines.pop(0).split('-->', 1)
        start, end = seconds(a), seconds(b.strip().split()[0])
        content = '\n'.join(lines).strip()
        if not content or end <= start:
            raise ValueError('SRT cue needs text and positive duration')
        if cues and start < cues[-1]['end'] - .001:
            raise ValueError('overlapping or unsorted cues need explicit review before import')
        cues.append({'id': f'line-{len(cues) + 1:03d}', 'start': start, 'end': end, 'text': content})
    if not cues:
        raise ValueError('SRT has no cues')
    return cues


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('srt', type=Path)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--audio', type=Path)
    a = p.parse_args()
    try:
        if a.out.exists():
            raise ValueError('output exists; prior lyrics were preserved')
        raw = a.srt.read_bytes()
        data = {'schema_version': 1, 'source_sha256': hashlib.sha256(raw).hexdigest(), 'audio_sha256': hashlib.sha256(a.audio.read_bytes()).hexdigest() if a.audio else None, 'text_status': 'supplied_unreviewed', 'timing_status': 'supplied_unreviewed', 'word_timing_status': 'not_supplied', 'cues': parse(raw.decode('utf-8-sig'))}
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'out': str(a.out), 'lines': len(data['cues']), 'review_needed': True}))
    except (ValueError, OSError) as exc:
        p.error(str(exc))


if __name__ == '__main__':
    main()

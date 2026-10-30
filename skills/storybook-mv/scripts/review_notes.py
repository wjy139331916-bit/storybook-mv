#!/usr/bin/env python3
"""Merge timestamped viewer observations into a NEW review record, preserving the original."""
import argparse
import copy
import json
import math
from pathlib import Path
import subprocess
from project_contracts import contained, digest, load, write


def merge(project, notes):
    if notes.get('schema_version') != 1 or not isinstance(notes.get('notes'), list):
        raise ValueError('expected versioned viewer notes')
    review = copy.deepcopy(load(project / 'review.json'))
    target = contained(project, review['target']['path'])
    actual = digest(target)
    if actual != review['target'].get('sha256') or actual != notes.get('target', {}).get('sha256'):
        raise ValueError('viewer notes do not match the exact current reviewed video')
    duration = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', str(target)], text=True, encoding='utf-8'))
    seen = {i.get('id') for i in review.get('issues', [])}
    added = 0
    for note in notes.get('notes', []):
        ident, bounds = note.get('id'), note.get('range')
        if not isinstance(ident,str) or not ident or not isinstance(bounds, list) or len(bounds) != 2 or not all(isinstance(x, (int, float)) and not isinstance(x,bool) and math.isfinite(x) for x in bounds) or not 0 <= bounds[0] < bounds[1] <= duration+.001 or not isinstance(note.get('observation'),str) or not note['observation'].strip() or note.get('severity') not in ('minor', 'major', 'blocker'):
            raise ValueError('invalid viewer observation')
        if ident in seen:
            continue
        review.setdefault('issues', []).append({'id': ident, 'severity': note['severity'], 'status': 'open', 'category': 'viewer_feedback', 'range': bounds, 'observation': note['observation'], 'hypothesis': None, 'resolution': None, 'evidence': [review['target']['path']], 'origin': 'viewer'})
        seen.add(ident)
        added += 1
    # New notes never auto-resolve old issues or turn a failing check into a pass.
    return review, added


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('notes', type=Path)
    p.add_argument('--project', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    try:
        result, added = merge(a.project.resolve(), load(a.notes))
        write(a.out, result)
        print(json.dumps({'out': str(a.out), 'added_issues': added, 'original_preserved': True}))
    except (ValueError, OSError, KeyError) as exc:
        p.error(str(exc))


if __name__ == '__main__':
    import sys
    for _stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(_stream, 'reconfigure'):
            _stream.reconfigure(encoding='utf-8')
    main()

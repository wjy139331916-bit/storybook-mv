#!/usr/bin/env python3
"""Check structural proposal completeness without selecting a style for the user."""
import argparse
import json
from pathlib import Path


def check(brief):
    missing = []
    def value(path):
        node = brief
        for key in path.split('.'):
            if not isinstance(node, dict):
                return None
            node = node.get(key)
        return node
    def filled(path):
        v = value(path)
        return (isinstance(v, str) and bool(v.strip())) or (isinstance(v, list) and bool(v))
    for key in ('goal', 'style.direction', 'emotion', 'structure.mode', 'structure.outline', 'asset_policy', 'output.aspect_ratio', 'music.source', 'music.scope', 'lyrics.mode', 'execution.engine'):
        if not filled(key):
            missing.append(key)
    required = value('characters.required')
    if not isinstance(required, bool):
        missing.append('characters.required')
    elif required and not filled('characters.roles'):
        missing.append('characters.roles')
    if value('structure.mode') == 'narrative' and not filled('structure.ending'):
        missing.append('structure.ending')
    questions = value('open_questions') or []
    if not isinstance(questions, list):
        missing.append('open_questions must be an array')
    else:
        for q in questions:
            if isinstance(q, dict) and q.get('blocking') and not q.get('resolved'):
                missing.append('unresolved: ' + str(q.get('question', q.get('field', 'material question'))))
    production = list(missing)
    if value('execution.production_authorized') is not True:
        production.append('production is not authorized')
    source = value('music.source')
    if source and source != 'none':
        audio = value('music.audio')
        if not isinstance(audio, str) or not audio.strip():
            production.append('final audio is not provided')
        elif not Path(audio).expanduser().is_file():
            production.append('final audio path is not locally available; resolve it before full production')
    return {'ready_to_propose': not missing, 'missing_for_proposal': missing, 'ready_for_full_production': not production, 'missing_for_full_production': production, 'scope': 'structural brief check only; does not certify taste, feasibility, runtime, or rendered quality'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('brief', type=Path)
    p.add_argument('--for', dest='purpose', choices=('proposal', 'production'), default='proposal')
    a = p.parse_args()
    try:
        data = json.loads(a.brief.read_text(encoding='utf-8'))
        if not isinstance(data, dict):
            raise ValueError('brief must be an object')
        result = check(data)
    except (OSError, ValueError) as exc:
        p.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    key = 'ready_to_propose' if a.purpose == 'proposal' else 'ready_for_full_production'
    return 0 if result[key] else 2


if __name__ == '__main__':
    raise SystemExit(main())

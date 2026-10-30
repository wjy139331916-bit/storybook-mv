#!/usr/bin/env python3
"""Export the complete host-neutral skill as a normal folder, never an archive."""
import argparse
import hashlib
import json
import re
from pathlib import Path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--dest', type=Path, required=True, help='parent of the portable storybook-mv directory')
    p.add_argument('--include-project-profile', action='store_true')
    p.add_argument('--include-host-metadata', action='store_true')
    a = p.parse_args()
    source = Path(__file__).resolve().parents[1]
    text = (source / 'SKILL.md').read_text(encoding='utf-8')
    match = re.search(r'^name:\s*([a-z0-9-]+)\s*$', text, re.M)
    if not match:
        p.error('cannot resolve the skill name')
    target = a.dest.expanduser().resolve() / match[1]
    if target == source or source in target.parents:
        p.error('destination must be outside the source skill')
    if target.exists():
        p.error('destination already exists; no files were overwritten')
    entries = []
    for file in sorted(source.rglob('*')):
        if not file.is_file():
            continue
        resolved = file.resolve()
        if source not in resolved.parents:
            p.error('an external symlink resource cannot be exported automatically')
        rel = file.relative_to(source)
        # Re-exporting a portable copy must create a fresh manifest, not hash
        # the previous manifest and then overwrite the file it describes.
        if rel.as_posix() == 'PORTABLE_MANIFEST.json':
            continue
        if any(x in rel.parts for x in ('.git', '__pycache__', 'node_modules', 'out')) or file.suffix == '.pyc':
            continue
        if not a.include_host_metadata and rel.parts[0] == 'agents':
            continue
        if not a.include_project_profile and rel.as_posix() == 'references/tebie-de-ren.md':
            continue
        payload = file.read_bytes()
        if rel.as_posix() == 'SKILL.md' and not a.include_project_profile:
            public = re.sub(r'<!-- PERSONAL_PROJECT_PROFILE_START -->.*?<!-- PERSONAL_PROJECT_PROFILE_END -->\s*', '', text, flags=re.S)
            payload = public.encode('utf-8')
        entries.append((rel, payload))
    target.mkdir(parents=True)
    info = json.loads((source / 'assets/toolkit.json').read_text(encoding='utf-8')) if (source / 'assets/toolkit.json').is_file() else {}
    manifest = {'name': match[1], 'version': info.get('version', 'unversioned'), 'entry': 'SKILL.md', 'personal_project_profile': a.include_project_profile, 'host_metadata': a.include_host_metadata, 'runtime_dependencies_bundled': False, 'files': []}
    for rel, payload in entries:
        output = target / rel
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(payload)
        manifest['files'].append({'path': rel.as_posix(), 'bytes': len(payload), 'sha256': hashlib.sha256(payload).hexdigest()})
    (target / 'PORTABLE_MANIFEST.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'directory': str(target), 'files': len(entries), 'profile_included': a.include_project_profile, 'archive': False}, ensure_ascii=False))


if __name__ == '__main__':
    import sys
    for _stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(_stream, 'reconfigure'):
            _stream.reconfigure(encoding='utf-8')
    main()

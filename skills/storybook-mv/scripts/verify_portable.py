#!/usr/bin/env python3
"""Verify a complete exported skill without claiming a working render runtime."""
import argparse
import hashlib
import json
from pathlib import Path
import re


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('directory', type=Path)
    a = p.parse_args()
    root = a.directory.expanduser().resolve()
    errors, seen = [], set()
    try:
        manifest = json.loads((root/'PORTABLE_MANIFEST.json').read_text())
        if not isinstance(manifest.get('files'), list) or not manifest['files']:
            raise ValueError('manifest has no files')
        for item in manifest['files']:
            rel = item['path']
            if not isinstance(rel,str) or Path(rel).is_absolute() or '..' in Path(rel).parts:
                errors.append('unsafe manifest path: '+str(rel))
                continue
            f = (root/rel).resolve()
            if root not in f.parents or rel in seen:
                errors.append('unsafe/duplicate manifest path: '+str(rel))
                continue
            seen.add(rel)
            if not f.is_file() or f.stat().st_size != item['bytes'] or hashlib.sha256(f.read_bytes()).hexdigest() != item['sha256']:
                errors.append('missing/changed: '+rel)
        for required in ('SKILL.md', 'assets/toolkit.json', 'scripts/runtime_smoke.py', 'references/production-contracts.md'):
            if required not in seen:
                errors.append('required resource absent: '+required)
        main = (root/'SKILL.md').read_text()
        found = re.search(r'^name:\s*([a-z0-9-]+)\s*$', main, re.M)
        if not found or found[1] != manifest.get('name'):
            errors.append('manifest/skill name mismatch')
        info = json.loads((root/'assets/toolkit.json').read_text())
        if info['version'] != manifest.get('version'):
            errors.append('toolkit/manifest version mismatch')
        if not manifest.get('personal_project_profile') and ('references/tebie-de-ren.md' in seen or 'PERSONAL_PROJECT_PROFILE_START' in main):
            errors.append('personal profile unexpectedly included')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(str(exc))
    print(json.dumps({'ok':not errors,'errors':errors,'verified_files':len(seen),'scope':'Export integrity only. Run the selected runtime self-test on the destination machine; dependencies and project inputs are separate.'}, ensure_ascii=False, indent=2))
    return 0 if not errors else 2


if __name__ == '__main__':
    raise SystemExit(main())

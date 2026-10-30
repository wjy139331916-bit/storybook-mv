#!/usr/bin/env python3
"""Give supplied plain-text lyrics stable line IDs; do not invent text or timing."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('input',type=Path)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    if a.out.exists():p.error('output exists; previous canonical text was preserved')
    try:
        raw=a.input.read_bytes()
        lines=[x.strip() for x in raw.decode('utf-8-sig').splitlines() if x.strip()]
        if not lines:raise ValueError('supplied lyrics contain no nonempty lines')
        d={'schema_version':1,'text_status':'provided_unverified','source_sha256':hashlib.sha256(raw).hexdigest(),'lines':[{'id':f'line-{i+1:03d}','text':x} for i,x in enumerate(lines)]}
        a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n', encoding='utf-8')
        print(json.dumps({'path':str(a.out),'sha256':hashlib.sha256(a.out.read_bytes()).hexdigest(),'lines':len(lines),'timing_invented':False}))
    except (OSError,ValueError) as exc:p.error(str(exc))


if __name__ == '__main__':
    import sys
    for _stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(_stream, 'reconfigure'):
            _stream.reconfigure(encoding='utf-8')
    main()

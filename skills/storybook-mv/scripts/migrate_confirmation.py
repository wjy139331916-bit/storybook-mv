#!/usr/bin/env python3
"""Migrate a verifiable 3.1 digest format without inventing missing acceptance."""
import argparse
import hashlib
import json
from pathlib import Path
from input_contracts import content_digest


def legacy_digest(b):
    value={k:b.get(k) for k in ('content','structure','characters')}
    value['lyrics_mode']=(b.get('lyrics') or {}).get('mode')
    value['song_basis']={k:(b.get('music') or {}).get(k) for k in ('title','artist','version','kind')}
    value['song_meaning']={k:(b.get('song_reading') or {}).get(k) for k in ('central_meaning','intent_basis','selected_direction','lyrics_source')}
    return hashlib.sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('brief',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    if a.out.exists():p.error('output exists; prior brief was preserved')
    try:
        b=json.loads(a.brief.read_text());c=b.get('content_confirmation') or {}
        if c.get('status')!='confirmed' or not c.get('user_evidence') or c.get('content_sha256')!=legacy_digest(b):
            raise ValueError('legacy acceptance is absent/stale; recover actual decisions instead of auto-approving')
        old=c['content_sha256'];c.update(content_sha256=content_digest(b),digest_version=2)
        b['schema_version']=4;b['format_migration']={'from_digest':old,'scope':'Format only. Missing evidence, stage and input records remain unresolved; this grants no production approval.'}
        a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(b,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({'migrated':True,'production_approved':False,'output':str(a.out)}))
    except (OSError,ValueError,TypeError) as exc:p.error(str(exc))


if __name__=='__main__':main()

"""Evidence receipt for expansion; review judgments remain the reviewer's responsibility."""
import json
from pathlib import Path
from input_contracts import bound_file, content_digest, sha


def pilot_errors(project, brief):
    pointer=(brief.get('execution') or {}).get('pilot_receipt')
    record=project/'prototype-pass.json'
    if pointer:
        errors=[];record=bound_file(project,pointer,'pilot receipt',errors)
        if not record:return errors
    if not record.is_file():
        return ['PILOT_REQUIRED: inspect the representative clip and run project_contracts.py promote before full rendering']
    errors=[]
    try:
        d=json.loads(record.read_text(encoding='utf-8'))
        if d.get('content_sha256')!=content_digest(brief):
            errors.append('pilot receipt describes another content revision')
        from project_contracts import fingerprint
        if d.get('input_digest')!=fingerprint(project):
            errors.append('pilot source/design changed; review a representative clip of the current revision')
        for key in ('review','artifact','runtime'):
            bound_file(project,d.get(key),'pilot '+key,errors)
        if not d.get('reviewer') or d.get('status')!='observed_pass':
            errors.append('pilot needs a named observed review')
    except (OSError,ValueError,TypeError,KeyError) as exc:
        errors.append('invalid pilot receipt: '+str(exc))
    return errors


def promote(project):
    from project_contracts import inspect, fingerprint
    from check_brief import production_gate
    brief=json.loads((project/'brief.json').read_text(encoding='utf-8'))
    if (brief.get('execution') or {}).get('context')=='tool-self-test':
        raise ValueError('a tool self-test cannot authorize user-video expansion')
    result=inspect(project,'prototype')
    if not result['ok']:
        raise ValueError('prototype review is incomplete: '+'; '.join(result['errors']))
    review=json.loads((project/'review.json').read_text(encoding='utf-8'))
    out=project/'prototype-pass.json'
    revision=1
    while out.exists():
        revision+=1;out=project/('prototype-pass-r'+str(revision)+'.json')
    evidence=project/'out/pilot-gate-evidence'/('r'+str(revision))
    evidence.mkdir(parents=True,exist_ok=False)
    records={}
    for name in ('review','runtime-report'):
        source=project/(name+'.json');target=evidence/(name+'.json');target.write_bytes(source.read_bytes())
        records['review' if name=='review' else 'runtime']={'path':target.relative_to(project).as_posix(),'sha256':sha(target)}
    records['artifact']={'path':review['target']['path'],'sha256':review['target']['sha256']}
    d={'schema_version':1,'status':'observed_pass','reviewer':review['reviewer'],'content_sha256':content_digest(brief),'input_digest':fingerprint(project),**records,'scope':'Recorded representative review only; no automatic beauty, natural acting or user-taste certification.'}
    out.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n', encoding='utf-8')
    brief['execution']['pilot_receipt']={'path':out.relative_to(project).as_posix(),'sha256':sha(out)}
    (project/'brief.json').write_text(json.dumps(brief,ensure_ascii=False,indent=2)+'\n', encoding='utf-8')
    return d

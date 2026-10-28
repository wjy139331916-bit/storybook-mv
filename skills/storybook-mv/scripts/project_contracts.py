#!/usr/bin/env python3
"""Initialize neutral production records, inspect recorded evidence, or plan bounded repairs."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

from check_brief import check as check_brief


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def fingerprint(project):
    files = []
    for name in ('src', 'data', 'assets', 'visual-spec.json', 'package.json', 'package-lock.json', 'render_canvas.mjs', 'render.mjs', 'studio.html', 'production_gate.mjs'):
        p = project/name
        if p.is_symlink():
            raise ValueError('resolve input symlinks explicitly')
        for f in sorted(p.rglob('*')) if p.is_dir() else ([p] if p.is_file() else []):
            if f.is_symlink():
                raise ValueError('resolve input symlinks explicitly')
            if f.is_file():
                files.append({'path': f.relative_to(project).as_posix(), 'sha256': digest(f)})
    files.sort(key=lambda f: f['path'])
    return hashlib.sha256(''.join(f['path']+'\0'+f['sha256']+'\n' for f in files).encode()).hexdigest()


def load(path):
    result = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(result, dict):
        raise ValueError(str(path.name)+' must be an object')
    return result


def write(path, value):
    if path.exists():
        raise ValueError('output exists: '+str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def field(data, dotted):
    for key in dotted.split('.'):
        if not isinstance(data, dict):
            return None
        data = data.get(key)
    return data


def finite(n):
    return isinstance(n, (int, float)) and not isinstance(n, bool) and math.isfinite(n)


def contained(project, rel):
    if not isinstance(rel, str) or not rel.strip():
        raise ValueError('missing artifact path')
    p = (project/rel).resolve()
    if project not in p.parents:
        raise ValueError('artifact paths must stay inside project; copy authorized inputs explicitly')
    return p


def initialize(project, root):
    brief = load(project/'brief.json')
    made, kept = [], []
    for stem in ('visual-spec', 'shot-map', 'review'):
        dest = project/(stem+'.json')
        if dest.exists():
            kept.append(dest.name)
            continue
        obj = load(root/'assets/contracts'/(stem+'.template.json'))
        if stem == 'visual-spec':
            obj['brief_sha256'] = digest(project/'brief.json')
            obj['characters_required'] = field(brief, 'characters.required')
            obj['design']['medium'] = field(brief, 'style.medium')
            obj['design']['motion'] = field(brief, 'style.motion')
            obj['design']['typography']['mode'] = field(brief, 'lyrics.mode')
            obj['locked_choices'] = [{'path': x, 'value': field(brief, x)} for x in brief.get('confirmed_fields', []) if isinstance(x, str)]
            if field(brief, 'lyrics.mode') not in (None, 'none'):
                obj['required_checks'].append('text')
        write(dest, obj)
        made.append(dest.name)
    return {'created': made, 'preserved': kept, 'note': 'Templates contain unresolved fields; fill from agreed decisions and actual evidence, without re-interviewing routine details.'}


def timeline(mapping, errors, full):
    duration = mapping.get('duration')
    if not finite(duration) or duration <= 0:
        errors.append('shot-map.duration must be positive')
        return {}
    sections, shots = {}, {}
    for name, store in [('sections', sections), ('shots', shots)]:
        items = mapping.get(name)
        if not isinstance(items, list) or not items:
            errors.append('shot-map.'+name+' is empty')
            continue
        cursor = 0
        for item in items:
            if not isinstance(item, dict):
                errors.append(name+': expected object')
                continue
            ident = item.get('id')
            if not isinstance(ident, str) or not ident or ident in store:
                errors.append(name+': missing/duplicate id')
                continue
            store[ident] = item
            start, end = item.get('start'), item.get('end')
            if not finite(start) or not finite(end) or not 0 <= start < end <= duration+.001:
                errors.append(ident+': invalid bounds')
                continue
            if abs(start-cursor) > .001:
                errors.append(ident+': timeline gap/overlap')
            cursor = end
            if item.get('repeat_of') and not item.get('variation'):
                errors.append(ident+': repeated material needs a stated variation')
        if abs(cursor-duration) > .001:
            errors.append(name+': incomplete duration coverage')
        for ident, item in store.items():
            if item.get('repeat_of') and item['repeat_of'] not in store:
                errors.append(ident+': unknown repeat_of')
    for ident, shot in shots.items():
        section = sections.get(shot.get('section_id'))
        if not section:
            errors.append(ident+': missing/unknown section_id')
        elif all(finite(v) for v in (shot.get('start'), shot.get('end'), section.get('start'), section.get('end'))) and not (shot['start']>=section['start']-.001 and shot['end']<=section['end']+.001):
            errors.append(ident+': split shot at section boundary or record the correct section')
        for key in ('objective', 'visible_change'):
            if not isinstance(shot.get(key), str) or not shot[key].strip():
                errors.append(ident+': missing '+key)
        if not isinstance(shot.get('assets', []), list):
            errors.append(ident+': assets must be an array of logical asset ids')
    if full and mapping.get('duration_status') != 'recording_measured':
        errors.append('full timeline duration must be marked recording_measured')
    return shots


def inspect(project, stage):
    errors, warnings = [], []
    brief = load(project/'brief.json')
    spec = load(project/'visual-spec.json')
    base = check_brief(brief,project)
    errors += base['missing_for_full_production' if stage == 'full' else 'missing_for_prototype']
    for key in ('revision', 'design.medium', 'design.shape_language', 'design.composition', 'design.motion'):
        if field(spec, key) in (None, '', []):
            errors.append('visual-spec missing '+key)
    if not isinstance(field(spec, 'design.palette'), list) or not field(spec, 'design.palette'):
        errors.append('visual-spec requires the selected palette/color rule')
    if spec.get('characters_required') is not field(brief, 'characters.required'):
        errors.append('visual-spec characters_required differs from brief')
    if spec.get('characters_required') and not spec.get('cast'):
        errors.append('visual-spec requires cast identity/model entries')
    if stage == 'full' and spec.get('status') != 'locked':
        errors.append('reconcile the selected design and mark visual-spec locked before expansion')
    for lock in spec.get('locked_choices', []):
        if not isinstance(lock, dict) or field(brief, lock.get('path', '')) != lock.get('value'):
            errors.append('locked decision differs from current brief; resolve the decision explicitly')
    if spec.get('brief_sha256') != digest(project/'brief.json'):
        warnings.append('brief changed since visual-spec creation; reconcile affected choices and refresh its digest')
    evidence = spec.get('evidence')
    if not isinstance(evidence, list) or not evidence:
        errors.append('visual-spec needs actual rendered evidence')
    else:
        for e in evidence:
            f = contained(project, e.get('path') if isinstance(e, dict) else None)
            if not f.is_file() or not f.stat().st_size:
                errors.append('missing/empty visual evidence: '+str(f.name))
            elif e.get('sha256') != digest(f):
                errors.append('stale visual evidence: '+f.name)
    if stage == 'design':
        return {'ok': not errors, 'errors': errors, 'warnings': warnings, 'scope': 'Recorded design completeness only; no taste or motion certification.'}
    mapping = load(project/'shot-map.json')
    shots = timeline(mapping, errors, stage == 'full' and field(brief,'music.source') != 'none')
    if stage == 'full' and field(brief,'music.source') == 'none' and mapping.get('duration_status') != 'agreed_scope':
        errors.append('silent full output needs an agreed_scope duration')
    if stage == 'full' and field(brief, 'music.source') != 'none':
        audio = Path(field(brief, 'music.audio') or '').expanduser()
        if not audio.is_absolute():
            audio = project/audio
        if not audio.is_file() or mapping.get('audio_sha256') != digest(audio):
            errors.append('shot-map must identify the actual final audio by SHA-256')
        else:
            import subprocess
            measured = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', str(audio)], text=True))
            if not finite(mapping.get('duration')) or abs(mapping['duration']-measured)>.12:
                errors.append('full shot-map duration differs from the final recording')
    review = load(project/'review.json')
    if review.get('scope') != ('full' if stage == 'full' else 'prototype'):
        errors.append('review scope does not match the requested stage')
    target = review.get('target') or {}
    clip = contained(project, target.get('path'))
    if not clip.is_file() or target.get('sha256') != digest(clip):
        errors.append('review target missing or changed since review')
    else:
        import subprocess
        try:
            media = json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(clip)],stderr=subprocess.PIPE))
            video = next((s for s in media.get('streams',[]) if s.get('codec_type')=='video'),None)
            if not video:
                errors.append('review target has no encoded video stream')
            if stage == 'full':
                if abs(float(media['format']['duration'])-mapping['duration'])>.12:
                    errors.append('full encoded duration differs from shot map')
                resolution = field(brief,'output.resolution')
                if isinstance(resolution,list) and len(resolution)==2 and video and [video.get('width'),video.get('height')]!=resolution:
                    errors.append('full encoded dimensions differ from selected output')
                if field(brief,'music.source') != 'none' and not any(s.get('codec_type')=='audio' for s in media.get('streams',[])):
                    errors.append('full encoded file has no required audio')
                decoded = subprocess.run(['ffmpeg','-v','error','-i',str(clip),'-f','null','-'],capture_output=True)
                if decoded.returncode:
                    errors.append('full encoded file failed complete decode')
        except (OSError,ValueError,KeyError,subprocess.SubprocessError):
            errors.append('review target is not an inspectable encoded video')
    if target.get('input_digest') != fingerprint(project):
        errors.append('source/design changed after render review; render affected ranges and renew evidence')
    for diagnostic in review.get('diagnostics', []):
        if not isinstance(diagnostic, dict):
            errors.append('invalid diagnostic record')
            continue
        report_path = contained(project, diagnostic.get('path'))
        if not report_path.is_file() or diagnostic.get('sha256') != digest(report_path):
            errors.append('diagnostic report missing or changed')
            continue
        report = load(report_path)
        measured_target = (report.get('target') or {}).get('sha256') or report.get('encoded_sha256')
        if measured_target != target.get('sha256'):
            errors.append('diagnostic report describes another encoded target')
        input_digest = (report.get('target') or {}).get('input_digest')
        if input_digest is not None and input_digest != target.get('input_digest'):
            errors.append('diagnostic report describes stale source/design')
    checks = review.get('checks')
    by_id = {}
    for item in checks if isinstance(checks, list) else []:
        if not isinstance(item, dict) or not item.get('id') or item['id'] in by_id:
            errors.append('missing/duplicate review check id')
            continue
        by_id[item['id']] = item
    required = set(spec.get('required_checks') or []) | {'composition', 'style', 'motion', 'continuity', 'music'}
    for key in sorted(required):
        item = by_id.get(key, {})
        if item.get('status') not in ('pass', 'not_applicable') or not isinstance(item.get('notes'),str) or not item['notes'].strip():
            errors.append('review not satisfied: '+key)
        if item.get('status') == 'not_applicable' and (key in ('composition','style','continuity') or (key == 'text' and field(brief,'lyrics.mode') not in (None,'none')) or (key == 'music' and field(brief,'music.source') != 'none')):
            errors.append('required criterion cannot be marked not_applicable: '+key)
        if item.get('status') == 'pass' and not item.get('evidence'):
            errors.append('review pass lacks observed evidence: '+key)
        for rel in item.get('evidence', []):
            if not contained(project, rel).is_file():
                errors.append('review evidence missing: '+str(rel))
    if not review.get('reviewer'):
        errors.append('record who/what inspected the rendered artifact')
    issue_ids = set()
    for item in review.get('issues', []):
        if not isinstance(item, dict):
            errors.append('invalid issue record')
            continue
        ident = item.get('id')
        if not isinstance(ident,str) or not ident or ident in issue_ids or item.get('severity') not in ('blocker','major','minor') or item.get('status') not in ('open','resolved'):
            errors.append('invalid/duplicate issue id, severity or status')
        issue_ids.add(ident)
        if item.get('status') != 'resolved' and item.get('severity') in ('blocker', 'major'):
            errors.append('unresolved '+item['severity']+': '+str(item.get('id')))
        if item.get('status') == 'resolved' and (not item.get('resolution') or not item.get('evidence')):
            errors.append('resolved issue needs resolution and replacement evidence')
        for rel in item.get('evidence', []):
            if not contained(project,rel).is_file():
                errors.append('issue replacement evidence missing: '+str(rel))
    runtime = load(project/'runtime-report.json')
    if runtime.get('status') != 'passed' or not runtime.get('encoded', {}).get('full_decode'):
        errors.append('runtime self-test did not verify a playable encoded clip')
    if runtime.get('runtime_backend') != field(brief, 'execution.runtime'):
        errors.append('runtime self-test backend differs from selected runtime; test the selected adapter')
    if runtime.get('engine') != field(brief,'execution.engine'):
        errors.append('runtime self-test engine differs from selected engine')
    runtime_artifact = contained(project, runtime.get('artifact', {}).get('path'))
    if not runtime_artifact.is_file() or runtime.get('artifact', {}).get('sha256') != digest(runtime_artifact):
        errors.append('runtime self-test artifact missing/changed')
    return {'ok': not errors, 'errors': errors, 'warnings': warnings, 'shots': len(shots), 'scope': 'Structural checks and freshness of recorded reviews/runtime evidence. Visual judgments are the named reviewer\'s, not computed aesthetic scores.'}


def repair(project, margin):
    mapping, review = load(project/'shot-map.json'), load(project/'review.json')
    errors = []
    shots = timeline(mapping, errors, False)
    if errors:
        raise ValueError('; '.join(errors))
    duration, intervals, affected = mapping['duration'], [], set()
    for issue in review.get('issues', []):
        if issue.get('status') == 'resolved':
            continue
        ids = set(issue.get('shot_ids') or [])
        shared = set(issue.get('shared_assets') or [])
        if ids-set(shots):
            raise ValueError('issue references unknown shots')
        bounds = issue.get('range')
        if bounds is not None:
            if not isinstance(bounds, list) or len(bounds)!=2 or not all(finite(x) for x in bounds) or not 0 <= bounds[0] <= bounds[1] <= duration:
                raise ValueError('issue has invalid time range')
            ids |= {k for k,s in shots.items() if s['start']<=bounds[1] and s['end']>=bounds[0]}
        ids |= {k for k,s in shots.items() if shared & set(s.get('assets') or [])}
        if not ids:
            raise ValueError('open issue needs shot_ids, a range or shared_assets; do not guess')
        for ident in ids:
            affected.add(ident)
            s = shots[ident]
            intervals.append([max(0,s['start']-margin),min(duration,s['end']+margin)])
    merged = []
    for a,b in sorted(intervals):
        if merged and a<=merged[-1][1]:
            merged[-1][1]=max(b,merged[-1][1])
        else:
            merged.append([a,b])
    return {'schema_version':1,'affected_shots':sorted(affected),'preserve_shots':sorted(set(shots)-affected),'render_ranges':merged,'join_margin_seconds':margin,'source_digest':fingerprint(project),'instructions':'Fix common causes once; preserve accepted unrelated shots. Re-render ranges including joins, compare before/after, update review target hashes. Do not reuse stale frames or silently alter locked style.'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=('init', 'check', 'repair', 'fingerprint'))
    p.add_argument('--project', type=Path, required=True)
    p.add_argument('--stage', choices=('design', 'prototype', 'full'), default='prototype')
    p.add_argument('--margin', type=float, default=.25)
    p.add_argument('--out', type=Path)
    a = p.parse_args()
    output_path = a.out.expanduser().resolve() if a.out else None
    project = a.project.expanduser().resolve()
    root = Path(__file__).resolve().parents[1]
    if project == root or root in project.parents:
        p.error('project records belong outside the installed skill')
    if not finite(a.margin) or a.margin < 0:
        p.error('margin must be nonnegative')
    try:
        if a.action == 'init':
            result = initialize(project, root)
        elif a.action == 'check':
            # Resolve project-relative audio paths without changing the caller's brief.
            import os
            os.chdir(project)
            result = inspect(project, a.stage)
        elif a.action == 'repair':
            result = repair(project, a.margin)
        else:
            result = {'input_digest': fingerprint(project)}
        if output_path:
            write(output_path, result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result.get('ok', True) else 2
    except (OSError, ValueError, TypeError, KeyError, AttributeError, subprocess.SubprocessError) as exc:
        p.error(str(exc))


if __name__ == '__main__':
    sys.exit(main())

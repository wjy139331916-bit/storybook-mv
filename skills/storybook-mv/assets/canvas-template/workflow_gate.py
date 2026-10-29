"""Stage-specific user review of actual artifacts. Records are evidence, not authentication."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess

from input_contracts import content_digest, sha, text, typed

NEXT = {'design': 'prototype', 'prototype': 'animatic', 'animatic': 'full'}
NEEDED = {'design': (), 'prototype': ('design',), 'animatic': ('design', 'prototype'),
          'production': ('design', 'prototype', 'animatic')}


def design_digest(brief):
    """Bind visible decisions separately from the content/meaning confirmation."""
    lyric = brief.get('lyrics') or {}
    value = {'content': content_digest(brief), 'style': brief.get('style'),
             'emotion': brief.get('emotion'), 'asset_policy': brief.get('asset_policy'),
             'aspect_ratio': (brief.get('output') or {}).get('aspect_ratio'),
             'text': {k: lyric.get(k) for k in ('mode', 'language')},
             'font_sha256': (lyric.get('font') or {}).get('sha256')}
    return hashlib.sha256(json.dumps(typed(value), ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


def default_workflow():
    return {'schema_version': 1, 'policy': 'user-stage-review', 'packages': {}, 'approvals': {}}


def target_duration(brief, project):
    execution, music = brief.get('execution') or {}, brief.get('music') or {}
    if execution.get('authorized_scope') == 'full':
        if project is not None and music.get('audio'):
            audio=Path(music['audio']);audio=audio if audio.is_absolute() else Path(project)/audio
            if audio.is_file():
                return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(audio)],stderr=subprocess.PIPE,text=True))
        return music.get('duration') or execution.get('authorized_duration')
    return execution.get('authorized_duration')


def pilot_plan(brief, project):
    if project is None:
        return None
    errors=[]
    f=local_file(project,((brief.get('workflow') or {}).get('packages') or {}).get('design'),'design pilot plan',errors)
    if not f:return None
    try:
        plan=read_json(f).get('pilot') or {}
        a,b=plan.get('start'),plan.get('end')
        if all(isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x) for x in (a,b)) and 0<=a<b and text(plan.get('objectives')):
            return plan
    except (OSError,ValueError,TypeError,AttributeError):
        pass
    return None


def local_file(project, record, label, errors):
    if not isinstance(record, dict) or not text(record.get('path')) or not text(record.get('sha256')):
        errors.append(label + ': missing actual artifact path/SHA-256')
        return None
    if project is None:
        return None
    root = Path(project).resolve()
    rel = Path(record['path'])
    if rel.is_absolute() or '..' in rel.parts:
        errors.append(label + ': review artifacts must use project-relative paths')
        return None
    target = root / rel
    if any(p.is_symlink() for p in [target, *target.parents] if p == root or root in p.parents):
        errors.append(label + ': resolve review artifact symlinks explicitly')
        return None
    if not target.is_file() or not target.stat().st_size or sha(target) != record['sha256']:
        errors.append(label + ': artifact missing, empty or changed since presentation')
        return None
    return target


def read_json(path):
    result = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(result, dict):
        raise ValueError(path.name + ' must be an object')
    return result


def inspect_package(brief, project, stage, record, errors):
    path = local_file(project, record, stage + ' package', errors)
    if not path:
        return None
    try:
        data = read_json(path)
        if data.get('stage') != stage or not text(data.get('revision')):
            errors.append(stage + ': package needs its own stage and revision')
        if data.get('content_sha256') != content_digest(brief) or data.get('design_sha256') != design_digest(brief):
            errors.append(stage + ': presented content/design revision is stale')
        packages = (brief.get('workflow') or {}).get('packages') or {}
        if stage != 'design' and data.get('design_package_sha256') != (packages.get('design') or {}).get('sha256'):
            errors.append(stage + ': sample is not bound to the presented design/script package')
        if stage == 'animatic' and data.get('prototype_package_sha256') != (packages.get('prototype') or {}).get('sha256'):
            errors.append('animatic: sample revision changed after the rough-cut presentation')
        artifacts = data.get('artifacts')
        if not isinstance(artifacts, list) or not artifacts:
            errors.append(stage + ': no presented artifacts')
            return data
        roles = {}
        for item in artifacts:
            if not isinstance(item, dict) or not text(item.get('role')):
                errors.append(stage + ': artifact needs a role')
                continue
            f = local_file(project, item, stage + ' ' + item['role'], errors)
            if f:
                roles.setdefault(item['role'], []).append(f)
        required = ('proposal', 'script', 'visual_spec', 'design_frame') if stage == 'design' else ('video', 'render_report', 'review')
        for role in required:
            if not roles.get(role):
                errors.append(stage + ': missing presented ' + role)
        if stage == 'design':
            plan=pilot_plan(brief,project)
            target=data.get('target_duration')
            if not plan or not isinstance(target,(int,float)) or plan['end']>target+.125:
                errors.append('design: needs an explicit bounded pilot interval and test objectives in the accepted package')
            for f in roles.get('design_frame', []):
                # Decode pixels; source code, prompts and renamed text are not design images.
                from PIL import Image
                with Image.open(f) as im:
                    im.verify()
                with Image.open(f) as im:
                    if min(im.size) < 32:
                        errors.append('design: frame too small to inspect')
            for f in roles.get('script', []):
                script = read_json(f)
                from project_contracts import timeline
                shots = timeline(script, errors, False)
                duration = script.get('duration')
                target = data.get('target_duration')
                if not isinstance(target, (int, float)) or isinstance(target, bool) or not math.isfinite(target) or target <= 0 or duration != target:
                    errors.append('design: script must cover its entire declared target duration')
                expected = target_duration(brief, project)
                if expected and isinstance(target,(int,float)) and abs(target-expected)>.125:
                    errors.append('design: script covers a sample instead of the requested full scope')
                for ident, shot in shots.items():
                    if not text(shot.get('visual')) or not text(shot.get('lyric_treatment')) or not isinstance(shot.get('transition'), dict) or not text(shot['transition'].get('type')):
                        errors.append('design: ' + ident + ' needs visual, lyric treatment and transition')
            for f in roles.get('visual_spec', []):
                spec = read_json(f)
                design = spec.get('design') or {}
                if not all(design.get(k) for k in ('medium', 'palette', 'shape_language', 'composition', 'motion')):
                    errors.append('design: actual visual specification is incomplete')
                if (brief.get('characters') or {}).get('required') and not spec.get('cast'):
                    errors.append('design: selected characters need a presented cast/model specification')
        elif roles.get('video'):
            video = roles['video'][0]
            media = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(video)], stderr=subprocess.PIPE))
            stream = next((s for s in media.get('streams', []) if s.get('codec_type') == 'video'), None)
            if not stream:
                raise ValueError('presented sample has no encoded video')
            measured = float(stream.get('duration') or media['format']['duration'])
            if not math.isfinite(measured) or measured <= 0:
                raise ValueError('presented sample has an invalid duration')
            from check_brief import aspect_parts
            ra, rb = aspect_parts((brief.get('output') or {}).get('aspect_ratio'))
            if stream['width'] * rb != stream['height'] * ra:
                errors.append(stage + ': presented video changes the selected aspect ratio')
            expected_range = None
            if stage == 'prototype':
                plan = pilot_plan(brief, project)
                if plan:
                    expected_range = [plan['start'], plan['end']]
                    if abs(measured - (plan['end'] - plan['start'])) > .125:
                        errors.append('prototype: presented video must cover the complete accepted pilot interval')
            else:
                expected_range = [0, target_duration(brief, project)]
            if (brief.get('music') or {}).get('audio') and not any(s.get('codec_type') == 'audio' for s in media['streams']):
                errors.append(stage + ': presented video lacks the selected soundtrack')
            for f in roles.get('render_report', []):
                report = read_json(f)
                targets = report.get('artifacts') or []
                if not any(x.get('sha256') == sha(video) for x in targets) or not (report.get('encoded') or {}).get('full_decode'):
                    errors.append(stage + ': render report does not verify this encoded artifact')
                if report.get('production_stage') != stage:
                    errors.append(stage + ': render report belongs to another production stage')
                bounds = report.get('range')
                valid_range = isinstance(bounds, list) and len(bounds) == 2 and all(isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) for x in bounds)
                if not valid_range or not expected_range or any(not isinstance(x, (int, float)) for x in expected_range) or any(abs(a-b) > .001 for a,b in zip(bounds, expected_range)):
                    errors.append(stage + ': render report must identify the accepted source timeline interval')
                elif abs((bounds[1]-bounds[0]) - measured) > .125:
                    errors.append(stage + ': reported source interval differs from the actual encoded duration')
                music = brief.get('music') or {}
                if music.get('audio') and (report.get('audio') or {}).get('sha256') != music.get('audio_sha256'):
                    errors.append(stage + ': render report must identify the selected soundtrack by SHA-256')
            for f in roles.get('review', []):
                review = read_json(f)
                if review.get('scope') != stage or not text(review.get('reviewer')) or review.get('target_sha256') != sha(video) or review.get('status') != 'observed_pass' or not text(review.get('observations')):
                    errors.append(stage + ': needs an actual observed review of this video, separate from user acceptance')
            if stage == 'animatic':
                target = data.get('target_duration')
                expected = target_duration(brief, project)
                if not isinstance(target, (int, float)) or isinstance(target,bool) or not math.isfinite(target) or abs(float(media['format']['duration']) - target) > .125 or (expected and abs(target-expected)>.125):
                    errors.append('animatic: encoded rough cut must cover the complete requested timeline')
                rate = stream.get('avg_frame_rate', '0/1').split('/')
                if data.get('fidelity') != 'rough' or max(stream['width'], stream['height']) > 960 or float(rate[0]) / max(float(rate[-1]), 1) > 15:
                    errors.append('animatic: require a declared rough cut, at most 960px and 15fps')
        return data
    except (OSError, ValueError, TypeError, KeyError, AttributeError, subprocess.SubprocessError) as exc:
        errors.append(stage + ': invalid presentation: ' + str(exc))
        return None


def workflow_errors(brief, project, purpose):
    if purpose not in NEEDED or (brief.get('execution') or {}).get('context') == 'tool-self-test':
        return []
    flow = brief.get('workflow') or {}
    if flow.get('schema_version') != 1 or flow.get('policy') != 'user-stage-review':
        return ['USER_STAGE_REVIEW_REQUIRED: recover real stage decisions; whole-MV authorization is not design/sample acceptance']
    errors, messages = [], set()
    # Reusing an intake acceptance message cannot approve artifacts made later.
    c = (brief.get('content_confirmation') or {}).get('record')
    if project is not None and isinstance(c, dict) and text(c.get('path')):
        f = Path(c['path']);f = f if f.is_absolute() else Path(project)/f
        if f.is_file():
            try:
                messages.add(read_json(f).get('message_id'))
            except (OSError, ValueError):
                pass
    for stage in NEEDED[purpose]:
        record = (flow.get('packages') or {}).get(stage)
        package = inspect_package(brief, project, stage, record, errors)
        approval = local_file(project, (flow.get('approvals') or {}).get(stage), stage.upper() + '_USER_APPROVAL_REQUIRED', errors)
        if not approval:
            continue
        try:
            d = read_json(approval)
            waived=d.get('decision')=='waived'
            if d.get('origin') != 'user-message' or not all(text(d.get(k)) for k in ('message_id', 'user_reply')) or (not waived and not text(d.get('presented_message_id'))):
                errors.append(stage + ': retain the actual user reply and presentation message references')
            if not waived and (d.get('message_id') in messages or d.get('message_id') == d.get('presented_message_id')):
                errors.append(stage + ': an intake/earlier reply cannot accept a later presentation')
            if not waived:messages.add(d.get('message_id'))
            if d.get('stage') != stage or d.get('next_stage') != NEXT[stage] or not package or d.get('package_sha256') != (record or {}).get('sha256') or d.get('revision') != package.get('revision') or d.get('content_sha256') != content_digest(brief):
                errors.append(stage + ': user acceptance does not identify this exact package/revision and immediate next stage')
            if d.get('decision') not in ('approved', 'waived'):
                errors.append(stage + ': waiting/rejected/agent self-review does not authorize advancement')
            if waived:
                if d.get('explicit_skip') is not True or d.get('waived_stage') != stage or d.get('scope') != 'this_stage_only':
                    errors.append(stage + ': waiver needs explicit user delegation naming this stage only')
                review=d.get('self_review') or {}
                if not text(review.get('reviewer')) or not text(review.get('observations')):
                    errors.append(stage + ': waived review still needs a named self-review of the actual package')
        except (OSError, ValueError, TypeError, AttributeError) as exc:
            errors.append(stage + ': invalid user acceptance: ' + str(exc))
    return errors


def relocate(brief, source, target):
    """Preserve relative presentation identities when an accepted design is scaffolded."""
    flow = brief.get('workflow') or {}
    records = list((flow.get('packages') or {}).values()) + list((flow.get('approvals') or {}).values())
    for record in (flow.get('packages') or {}).values():
        errors = [];f = local_file(source, record, 'handoff package', errors)
        if errors:
            raise ValueError('; '.join(errors))
        if f:
            records.extend(read_json(f).get('artifacts') or [])
    for record in records:
        errors = [];f = local_file(source, record, 'handoff artifact', errors)
        if errors:
            raise ValueError('; '.join(errors))
        if f:
            dest = Path(target)/record['path'];dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists() and sha(dest) != sha(f):
                raise ValueError('handoff would overwrite a different artifact: ' + record['path'])
            if not dest.exists():
                shutil.copy2(f, dest)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('brief', type=Path)
    p.add_argument('--for', dest='purpose', choices=tuple(NEEDED), default='prototype')
    p.add_argument('--design-digest', action='store_true')
    a = p.parse_args();brief = read_json(a.brief)
    if a.design_digest:
        print(design_digest(brief));return 0
    errors = workflow_errors(brief, a.brief.resolve().parent, a.purpose)
    print(json.dumps({'ok': not errors, 'errors': errors, 'scope': 'Actual artifact/revision and recorded stage-user decisions; no authentication or automatic taste judgment.'}, ensure_ascii=False, indent=2))
    return 2 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())

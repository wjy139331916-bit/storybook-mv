#!/usr/bin/env python3
"""Check structural proposal completeness without selecting a style for the user."""
import argparse
import hashlib
import json
import math
from pathlib import Path
from fractions import Fraction
from input_contracts import content_digest, reading_evidence_errors, confirmation_errors, media_errors, subtitle_errors, bound_file
from workflow_gate import workflow_errors, pilot_plan


def aspect_parts(value):
    try:
        a,b = str(value).split(':')
        ratio = Fraction(a)/Fraction(b)
        if ratio <= 0 or max(ratio.numerator, ratio.denominator)>1000:
            raise ValueError()
        return ratio.numerator, ratio.denominator
    except (ValueError, ZeroDivisionError):
        raise ValueError('aspect_ratio must be a positive numeric ratio such as 16:9, 1:1 or 4:3')


def song_reading_errors(brief, project=None):
    music, reading = brief.get('music') or {}, brief.get('song_reading') or {}
    errors = []
    kind = music.get('kind')
    if kind not in ('lyrical','instrumental','none'):
        return ['song kind/lyric applicability is not established; no visible lyrics does not mean an instrumental']
    if kind != 'lyrical':
        if reading.get('status') != 'not_applicable' or not isinstance(reading.get('reason'),str) or not reading['reason'].strip():
            errors.append('record why lyric interpretation is not applicable')
        return errors
    if reading.get('status') != 'clarified':
        errors.append('SONG_MEANING_UNRESOLVED: verify lyrics, explain evidence and let the user select material ambiguities')
    for key in ('recording_basis','lyrics_source','central_meaning'):
        if not isinstance(reading.get(key),str) or not reading[key].strip():
            errors.append('song reading needs '+key+'; do not reconstruct missing lyrics or intent from memory')
    if reading.get('lyrics_status') not in ('provided','verified'):
        errors.append('lyrics are missing/unverified; do not guess their words or meaning')
    if not isinstance(reading.get('evidence'),list) or not reading['evidence']:
        errors.append('song meaning needs actual lyric/recording evidence, using cue IDs and paraphrases')
    basis = reading.get('intent_basis')
    if basis not in ('documented_artist_intent','text_interpretation','user_adaptation'):
        errors.append('separate documented artist intent, textual interpretation and user adaptation')
    if basis == 'documented_artist_intent' and not reading.get('sources'):
        errors.append('an artist-intent claim requires a checked attributable source')
    options = reading.get('options') or []
    needs_selection = reading.get('needs_user_selection') is True or len(options)>1
    if needs_selection:
        if not reading.get('selected_direction') or not isinstance(reading.get('user_selection_evidence'),str) or not reading['user_selection_evidence'].strip():
            errors.append('materially different song interpretations require the user selection, not an agent guess')
        elif options and reading['selected_direction'] not in [x.get('id') for x in options if isinstance(x,dict)]:
            errors.append('selected song interpretation is not among the recorded options')
    if any(isinstance(x,dict) and x.get('selection_required') and not x.get('resolved') for x in reading.get('uncertainties') or []):
        errors.append('material song-meaning uncertainty is still unresolved')
    errors += reading_evidence_errors(brief, project)
    return errors


def production_gate(brief, purpose='prototype', duration=None, project=None, audio=None):
    """Check recorded confirmation, not whether the alleged user evidence is truthful."""
    execution = brief.get('execution') or {}
    if execution.get('context') == 'tool-self-test':
        marker = brief.get('tool_self_test') or {}
        errors = []
        if marker.get('source') != 'storybook-mv' or marker.get('purpose') != 'isolated-tool-verification':
            errors.append('invalid isolated tool self-test marker')
        if (brief.get('music') or {}).get('source') not in (None, 'none', 'original-code'):
            errors.append('tool self-tests cannot use a user recording or impersonate a commissioned MV')
        if purpose == 'production':
            errors.append('tool self-test is not authorization for a full user MV')
        if duration is not None and (not isinstance(duration,(int,float)) or isinstance(duration,bool) or not math.isfinite(duration) or not 0 < duration <= 60):
            errors.append('isolated tool self-tests are limited to 60 seconds')
        return errors
    errors = song_reading_errors(brief, project)
    if (brief.get('request_mode') in ('plan-only','explore') and purpose!='design') or brief.get('phase') in (None,'discover','proposal','awaiting-confirmation'):
        errors.append('STAGE_BLOCKED: discovery/planning must not run production')
    if purpose == 'production' and brief.get('phase') not in ('full','repair','deliver'):
        errors.append('full production requires the explicit full/repair stage')
    if purpose == 'design' and brief.get('phase') != 'design':
        errors.append('design work requires the explicit design stage')
    if purpose == 'animatic' and brief.get('phase') != 'animatic':
        errors.append('rough-cut work requires the explicit animatic stage')
    if purpose == 'prototype' and brief.get('phase') not in ('study','prototype','animatic','full','repair','deliver'):
        errors.append('select the authorized study/prototype stage before rendering')
    content = brief.get('content') or {}
    for key in ('subject', 'core_idea'):
        if not isinstance(content.get(key),str) or not content[key].strip():
            errors.append('content.'+key+' is not established through discovery')
    moments = content.get('key_moments')
    if not isinstance(moments,list) or len(moments)<2 or any(not isinstance(x,dict) or not isinstance(x.get('description'),str) or not x['description'].strip() or not isinstance(x.get('purpose'),str) or not x['purpose'].strip() for x in moments):
        errors.append('content.key_moments needs concrete visible moments and their purpose')
    confirmation = brief.get('content_confirmation') or {}
    if confirmation.get('status') != 'confirmed':
        errors.append('CONTENT_NOT_CONFIRMED: ask content questions, recap the intended video and wait for user confirmation')
    for key in ('summary', 'user_evidence'):
        if not isinstance(confirmation.get(key),str) or not confirmation[key].strip():
            errors.append('content confirmation needs '+key+'; the agent cannot invent user acceptance')
    if confirmation.get('content_sha256') != content_digest(brief):
        errors.append('content confirmation is missing/stale after a content change')
    if execution.get('production_authorized') is not True:
        errors.append('production is not authorized')
    allowed = execution.get('authorized_scope')
    if allowed not in ('design', 'study', 'prototype', 'full') or (purpose in ('production','animatic') and allowed != 'full') or (purpose == 'prototype' and allowed == 'design'):
        errors.append('requested production exceeds the explicitly authorized scope')
    if not isinstance(execution.get('authorization_evidence'),str) or not execution['authorization_evidence'].strip():
        errors.append('record the user authorization for this production scope')
    cap = execution.get('authorized_duration')
    if not isinstance(cap,(int,float)) or isinstance(cap,bool) or not math.isfinite(cap) or cap<=0:
        errors.append('record the authorized prototype/full duration bound')
    elif duration is not None and (not isinstance(duration,(int,float)) or isinstance(duration,bool) or not math.isfinite(duration) or duration<=0 or duration>cap+.125):
        errors.append('render duration exceeds the authorized duration')
    if purpose == 'production' and isinstance(moments,list) and len(moments)<3:
        errors.append('full video needs an established beginning, development and ending/loop behavior')
    if purpose == 'prototype':
        plan=pilot_plan(brief,project)
        pilot_cap=(plan['end']-plan['start']) if plan else ((brief.get('prototype') or {}).get('duration') if project is None else None)
        if not isinstance(pilot_cap,(int,float)) or isinstance(pilot_cap,bool) or not math.isfinite(pilot_cap) or pilot_cap<=0:
            errors.append('PILOT_PLAN_REQUIRED: prototype duration must be explicitly bounded in the user-accepted design package')
        if duration is not None and isinstance(pilot_cap,(int,float)) and duration > pilot_cap+.125:
            errors.append('render exceeds the separately bounded prototype duration')
        requested=(brief.get('prototype') or {}).get('duration')
        if duration is not None and isinstance(requested,(int,float)) and duration>requested+.125:
            errors.append('render exceeds the separately bounded prototype duration')
    errors += confirmation_errors(brief, project)
    errors += media_errors(brief, project, purpose, audio)
    if purpose!='design':errors += subtitle_errors(brief, project, purpose)
    for key in ('font','glyph_review'):
        record=(brief.get('lyrics') or {}).get(key)
        if record is not None:bound_file(project,record,'selected text '+key,errors)
    errors += workflow_errors(brief, project, purpose)
    return errors


def check(brief, project=None):
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
    if value('output.aspect_ratio'):
        try:
            a,b=aspect_parts(value('output.aspect_ratio'))
            resolution=value('output.resolution')
            if resolution is not None and (not isinstance(resolution,list) or len(resolution)!=2 or not all(isinstance(x,int) and not isinstance(x,bool) and x>0 and x%2==0 for x in resolution) or resolution[0]*b!=resolution[1]*a):
                missing.append('resolution conflicts with the selected aspect ratio')
        except ValueError as exc:
            missing.append(str(exc))
    prototype = list(missing) + production_gate(brief, 'prototype', project=project)
    production = list(missing) + production_gate(brief, 'production', project=project)
    source = value('music.source')
    if source and source != 'none':
        audio = value('music.audio')
        if not isinstance(audio, str) or not audio.strip():
            production.append('final audio is not provided')
        else:
            audio_path=Path(audio).expanduser()
            if project is not None and not audio_path.is_absolute():
                audio_path=Path(project)/audio_path
            if not audio_path.is_file():
                production.append('final audio path is not locally available; resolve it before full production')
    return {'ready_to_propose': not missing, 'missing_for_proposal': missing, 'ready_for_prototype': not prototype, 'missing_for_prototype': prototype, 'ready_for_full_production': not production, 'missing_for_full_production': production, 'content_sha256': content_digest(brief), 'scope': 'Recorded content confirmation and scoped authorization plus structural checks. User evidence must be truthful; no aesthetic/runtime certification.'}


def entry_errors(brief, project, purpose=None, duration=None, audio=None, resolution=None, fps=None, timeline_duration=None, operation=None, still_count=None, timeline_range=None):
    """One authority shared by the CLI and both JavaScript rendering adapters."""
    phase=brief.get('phase')
    actual='production' if phase in ('full','repair','deliver') else ('design' if phase=='design' else ('animatic' if phase=='animatic' else 'prototype'))
    purpose=purpose or actual
    result=check(brief,project)
    director_errors=[]
    if project is not None and (Path(project)/'director-active.json').exists():
        from director_contract import check_active
        director_errors=check_active(project,brief)
    if (brief.get('execution') or {}).get('context')=='tool-self-test':
        return production_gate(brief,purpose,duration,project,audio)+director_errors
    errors=list(result['missing_for_proposal'])+production_gate(brief,purpose,duration,project,audio)+director_errors
    if purpose!=actual:
        errors.append('STAGE_MISMATCH: changing a command purpose cannot bypass the current phase')
    if purpose=='prototype' and timeline_range is not None:
        plan=pilot_plan(brief,project)
        if not isinstance(timeline_range,list) or len(timeline_range)!=2 or not all(isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x) for x in timeline_range) or not plan or not plan['start']-.001<=timeline_range[0]<timeline_range[1]<=plan['end']+.001:
            errors.append('PILOT_INTERVAL: render must stay inside the user-accepted pilot interval')
    if purpose=='design':
        if operation not in ('scaffold','stills','estimate','check'):
            errors.append('DESIGN_STILLS_ONLY: design approval is pending; no animation, frame sequence or video export')
        if still_count is not None and (not isinstance(still_count,int) or isinstance(still_count,bool) or not 1<=still_count<=12):
            errors.append('design preview is limited to 1..12 static frames per render')
    selected=brief.get('output') or {}
    if purpose=='animatic':
        if resolution is not None and (len(resolution)!=2 or not all(isinstance(x,int) and x>0 for x in resolution) or max(resolution)>960):
            errors.append('ANIMATIC_LIMIT: rough-cut dimensions must be positive and at most 960px')
        elif resolution is not None:
            ra,rb=aspect_parts(selected.get('aspect_ratio'))
            if resolution[0]*rb!=resolution[1]*ra:errors.append('animatic must preserve the selected aspect ratio')
        if fps is not None and (not isinstance(fps,(int,float)) or not math.isfinite(fps) or not 0<fps<=15):
            errors.append('ANIMATIC_LIMIT: rough-cut frame rate must be at most 15fps')
    if purpose!='animatic' and resolution is not None and selected.get('resolution') is not None and resolution!=selected['resolution']:
        errors.append('render dimensions differ from the approved output')
    if purpose!='animatic' and fps is not None and selected.get('fps') is not None and fps!=selected['fps']:
        errors.append('render fps differs from the approved output')
    if purpose=='production':
        from pilot_gate import pilot_errors
        errors += pilot_errors(Path(project),brief)
        if timeline_duration is not None and (brief.get('music') or {}).get('audio'):
            import subprocess
            path=Path(brief['music']['audio']);path=path if path.is_absolute() else Path(project)/path
            try:
                measured=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(path)],stderr=subprocess.PIPE,text=True, encoding='utf-8'))
                if abs(measured-timeline_duration)>.125:errors.append('full timeline duration differs from the selected recording')
            except (OSError,ValueError,subprocess.SubprocessError):errors.append('selected recording cannot be measured')
    return list(dict.fromkeys(errors))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('brief', type=Path, nargs='?')
    p.add_argument('--bridge', choices=('digest','song','gate','entry'))
    p.add_argument('--for', dest='purpose', choices=('proposal', 'design', 'prototype', 'animatic', 'production'), default='proposal')
    p.add_argument('--content-digest', action='store_true', help='print current content digest; does NOT confirm content or grant authorization')
    a = p.parse_args()
    try:
        if a.bridge:
            import sys
            envelope=json.load(sys.stdin);data=envelope['brief'];o=envelope.get('options') or {}
            if a.bridge=='digest':result=content_digest(data)
            elif a.bridge=='song':result=song_reading_errors(data,o.get('project'))
            elif a.bridge=='entry':result=entry_errors(data,o['project'],o.get('purpose'),o.get('duration'),o.get('audio'),o.get('resolution'),o.get('fps'),o.get('timeline_duration'),o.get('operation'),o.get('still_count'),o.get('timeline_range'))
            else:result=production_gate(data,o.get('purpose','prototype'),o.get('duration'),o.get('project'),o.get('audio'))
            print(json.dumps(result,ensure_ascii=False));return 0
        if a.brief is None:
            p.error('provide a brief file')
        data = json.loads(a.brief.read_text(encoding='utf-8'))
        if not isinstance(data, dict):
            raise ValueError('brief must be an object')
        if a.content_digest:
            print(content_digest(data))
            return 0
        result = check(data, a.brief.resolve().parent)
        if a.purpose!='proposal':
            blocked=entry_errors(data,a.brief.resolve().parent,a.purpose,operation='check')
            k='full_production' if a.purpose=='production' else a.purpose
            result['ready_for_'+k]=not blocked;result['missing_for_'+k]=blocked
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        p.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    key = {'proposal':'ready_to_propose','design':'ready_for_design','prototype':'ready_for_prototype','animatic':'ready_for_animatic','production':'ready_for_full_production'}[a.purpose]
    return 0 if result[key] else 2


if __name__ == '__main__':
    import sys
    for _stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(_stream, 'reconfigure'):
            _stream.reconfigure(encoding='utf-8')
    raise SystemExit(main())

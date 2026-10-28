#!/usr/bin/env python3
"""Check structural proposal completeness without selecting a style for the user."""
import argparse
import hashlib
import json
import math
from pathlib import Path


def content_digest(brief):
    payload = {k: brief.get(k) for k in ('content', 'structure', 'characters')}
    payload['lyrics_mode'] = (brief.get('lyrics') or {}).get('mode')
    music, reading = brief.get('music') or {}, brief.get('song_reading') or {}
    payload['song_basis'] = {k: music.get(k) for k in ('title','artist','version','kind')}
    payload['song_meaning'] = {k: reading.get(k) for k in ('central_meaning','intent_basis','selected_direction','lyrics_source')}
    return hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def song_reading_errors(brief):
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
    return errors


def production_gate(brief, purpose='prototype', duration=None):
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
    errors = song_reading_errors(brief)
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
    if allowed not in ('study', 'prototype', 'full') or (purpose == 'production' and allowed != 'full'):
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
    prototype = list(missing) + production_gate(brief, 'prototype')
    production = list(missing) + production_gate(brief, 'production')
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


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('brief', type=Path)
    p.add_argument('--for', dest='purpose', choices=('proposal', 'prototype', 'production'), default='proposal')
    p.add_argument('--content-digest', action='store_true', help='print current content digest; does NOT confirm content or grant authorization')
    a = p.parse_args()
    try:
        data = json.loads(a.brief.read_text(encoding='utf-8'))
        if not isinstance(data, dict):
            raise ValueError('brief must be an object')
        if a.content_digest:
            print(content_digest(data))
            return 0
        result = check(data, a.brief.resolve().parent)
    except (OSError, ValueError) as exc:
        p.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    key = {'proposal':'ready_to_propose','prototype':'ready_for_prototype','production':'ready_for_full_production'}[a.purpose]
    return 0 if result[key] else 2


if __name__ == '__main__':
    raise SystemExit(main())

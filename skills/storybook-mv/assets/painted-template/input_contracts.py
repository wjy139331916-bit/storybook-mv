"""Bound, local evidence for a brief. No network calls or automatic artistic approval."""
import hashlib
import json
import math
import struct
from pathlib import Path
from urllib.parse import urlparse


def text(value):
    return isinstance(value, str) and bool(value.strip())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def typed(value):
    """Stable across JSON runtimes, including 160/160.0, exponents and negative zero."""
    if value is None:
        return ['null']
    if isinstance(value, bool):
        return ['bool', value]
    if isinstance(value, (int, float)):
        if not math.isfinite(value) or (isinstance(value, int) and int(float(value)) != value):
            raise ValueError('content numbers must be finite and exactly representable as JSON binary64; use strings for large identifiers')
        return ['number', struct.pack('>d', float(value) if value else 0.0).hex()]
    if isinstance(value, str):
        return ['string', value]
    if isinstance(value, list):
        return ['array', [typed(x) for x in value]]
    if isinstance(value, dict) and all(isinstance(k, str) for k in value):
        return ['object', [[k, typed(value[k])] for k in sorted(value)]]
    raise ValueError('unsupported content value')


def content_payload(brief):
    payload = {k: brief.get(k) for k in ('content', 'structure', 'characters')}
    payload['lyrics_mode'] = (brief.get('lyrics') or {}).get('mode')
    music, reading = brief.get('music') or {}, brief.get('song_reading') or {}
    payload['song_basis'] = {k: music.get(k) for k in ('title', 'artist', 'version', 'kind')}
    payload['song_basis']['audio_sha256'] = music.get('audio_sha256')
    payload['song_meaning'] = {k: reading.get(k) for k in ('central_meaning', 'intent_basis', 'selected_direction', 'lyrics_source')}
    payload['song_meaning']['lyrics_sha256'] = (reading.get('lyrics_document') or {}).get('sha256')
    return payload


def content_digest(brief):
    return hashlib.sha256(json.dumps(typed(content_payload(brief)), ensure_ascii=False, separators=(',', ':')).encode('utf-8')).hexdigest()


def bound_file(project, record, label, errors):
    if not isinstance(record, dict) or not text(record.get('path')) or not text(record.get('sha256')):
        errors.append(label+': needs a path and SHA-256')
        return None
    if project is None:
        return None
    root = Path(project).resolve()
    candidate = Path(record['path']).expanduser()
    if not candidate.is_absolute():
        candidate = root/candidate
    # Inputs can be supplied outside the project before scaffolding; their
    # explicit path and digest are retained, then copied into the new project.
    candidate = candidate.resolve()
    if not candidate.is_file() or sha(candidate) != record['sha256']:
        errors.append(label+': local evidence is missing or changed')
        return None
    return candidate


def lyric_lines(document):
    lines = document.get('lines', document.get('cues'))
    if not isinstance(lines, list) or not lines:
        raise ValueError('canonical lyrics need nonempty lines/cues')
    ids = set()
    for line in lines:
        if not isinstance(line, dict) or not text(line.get('id')) or line['id'] in ids or not text(line.get('text')):
            raise ValueError('canonical lyric lines need unique IDs and actual text')
        ids.add(line['id'])
    return lines


def reading_evidence_errors(brief, project=None):
    r = brief.get('song_reading') or {}
    if (brief.get('music') or {}).get('kind') != 'lyrical':
        return []
    errors = []
    document = bound_file(project, r.get('lyrics_document'), 'lyrics_document', errors)
    ids = None
    if document:
        try:
            ids = {x['id'] for x in lyric_lines(json.loads(document.read_text(encoding='utf-8')))}
        except (OSError, ValueError, TypeError) as exc:
            errors.append('lyrics_document: '+str(exc))
    evidence = r.get('evidence')
    if not isinstance(evidence, list) or not evidence:
        errors.append('song meaning needs actual lyric/recording evidence')
    else:
        for e in evidence:
            if not isinstance(e, dict) or not text(e.get('observation')) or not isinstance(e.get('cue_ids'), list) or not e['cue_ids'] or any(not text(x) for x in e['cue_ids']):
                errors.append('lyric evidence needs nonempty cue IDs and an observed basis')
            elif ids is not None and any(x not in ids for x in e['cue_ids']):
                errors.append('lyric evidence cites a nonexistent canonical line')
    sources = r.get('sources') or []
    if not isinstance(sources, list):
        errors.append('song sources must be structured records')
        sources = []
    for source in sources:
        if not isinstance(source, dict) or not all(text(source.get(k)) for k in ('id', 'attribution', 'checked_at', 'summary')):
            errors.append('source needs identity, attribution, checked date and supporting summary')
            continue
        parsed = urlparse(source.get('url', ''))
        if parsed.scheme not in ('https', 'http') or not parsed.netloc:
            errors.append('source needs an attributable HTTP(S) URL')
        if r.get('intent_basis') == 'documented_artist_intent' and source.get('kind') != 'artist_primary':
            errors.append('artist-intent evidence must identify a primary artist source')
        bound_file(project, source.get('snapshot'), 'source snapshot', errors)
    if r.get('intent_basis') == 'documented_artist_intent' and not sources:
        errors.append('artist-intent claim needs a checked primary source snapshot')
    if r.get('lyrics_status') == 'verified' and not sources:
        errors.append('verified lyrics need a checked source; supplied text can be marked provided')
    return errors


def confirmation_errors(brief, project):
    if project is None:
        return []
    errors = []
    c = brief.get('content_confirmation') or {}
    path = bound_file(project, c.get('record'), 'user confirmation record', errors)
    if path:
        try:
            d = json.loads(path.read_text(encoding='utf-8'))
            if not all(text(d.get(k)) for k in ('message_id', 'user_reply', 'recap_id')) or d.get('origin') != 'user-message':
                errors.append('confirmation record needs the actual user reply, message reference and recap revision')
            if d.get('accepted_content_sha256') != content_digest(brief):
                errors.append('user confirmation record describes another content revision')
        except (OSError, ValueError, TypeError, AttributeError) as exc:
            errors.append('invalid confirmation record: '+str(exc))
    return errors


def media_errors(brief, project, purpose, audio=None):
    if project is None or (brief.get('execution') or {}).get('context') == 'tool-self-test':
        return []
    errors = []
    m = brief.get('music') or {}
    source = m.get('source')
    declared = m.get('audio')
    if source not in ('none', None) and (purpose == 'production' or declared or audio):
        p = bound_file(project, {'path': declared, 'sha256': m.get('audio_sha256')}, 'selected recording', errors)
        if audio and p:
            other = Path(audio)
            if not other.is_absolute():
                other = Path(project)/other
            if not other.is_file() or sha(other) != m.get('audio_sha256'):
                errors.append('render audio differs from the confirmed recording')
    elif source == 'none' and audio:
        errors.append('a silent approved concept cannot silently acquire another soundtrack')
    return errors


def subtitle_errors(brief, project, purpose):
    if project is None or (brief.get('music') or {}).get('kind') != 'lyrical' or (brief.get('lyrics') or {}).get('mode') not in ('full', 'full-lines'):
        return []
    errors = []
    record = (brief.get('lyrics') or {}).get('display_document')
    display = bound_file(project, record, 'full-line display document', errors)
    canonical = bound_file(project, (brief.get('song_reading') or {}).get('lyrics_document'), 'canonical lyrics', errors)
    if not display or not canonical:
        return errors
    try:
        originals = lyric_lines(json.loads(canonical.read_text(encoding='utf-8')))
        data = json.loads(display.read_text(encoding='utf-8'))
        cues = data.get('cues')
        if not isinstance(cues, list) or not cues:
            raise ValueError('full subtitles cannot contain an empty cue list')
        expected = [x['id'] for x in originals]
        actual = [x.get('line_id', x.get('id')) for x in cues]
        if actual != expected:
            errors.append('full subtitles omit, duplicate or reorder canonical lyric lines')
        texts = {x['id']: x['text'] for x in originals}
        previous = 0
        for cue, ident in zip(cues, actual):
            start, end = cue.get('start'), cue.get('end')
            if not all(isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x) for x in (start, end)) or not 0 <= previous <= start < end:
                errors.append('subtitle cues need ordered nonoverlapping finite intervals')
                break
            previous = end
            if cue.get('text') != texts.get(ident):
                errors.append('displayed lyric text differs from its canonical line')
        if purpose == 'production' and (data.get('alignment_status') != 'ear_checked' or not text(data.get('alignment_evidence'))):
            errors.append('full singing alignment needs a listening review with evidence')
        # This verifies measured line coverage/timing records, not glyph appearance.
        if purpose == 'production' and previous > (brief.get('execution') or {}).get('authorized_duration', 0)+.125:
            errors.append('subtitle timing exceeds the authorized recording duration')
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        errors.append('subtitle coverage: '+str(exc))
    if purpose=='production' and str((brief.get('lyrics') or {}).get('language','')).lower().startswith(('zh','chinese')):
        font=bound_file(project,brief['lyrics'].get('font'),'selected lyric font',errors)
        proof=bound_file(project,brief['lyrics'].get('glyph_review'),'glyph coverage report',errors)
        if font and proof:
            try:
                d=json.loads(proof.read_text())
                if d.get('ok') is not True or d.get('missing')!=[] or d.get('font_sha256')!=sha(font) or d.get('text_document_sha256')!=sha(canonical):
                    errors.append('glyph report does not prove coverage of the current font and canonical text')
            except (OSError,ValueError,AttributeError):errors.append('invalid glyph coverage report')
    return errors

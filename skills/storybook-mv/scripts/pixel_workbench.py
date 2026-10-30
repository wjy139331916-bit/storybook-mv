#!/usr/bin/env python3
"""Create an offline pixel editor and reproducible, stage-scoped character assets."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 2 * 1024 * 1024


def integer(value, lo, hi):
    return isinstance(value, int) and not isinstance(value, bool) and lo <= value <= hi


def identifier(value):
    return isinstance(value, str) and re.fullmatch(r'[A-Za-z0-9_-]{1,48}', value) and value not in ('__proto__', 'constructor', 'prototype')


def validate(data):
    if not isinstance(data, dict) or data.get('schema_version') != 1 or data.get('kind') != 'pixel-character':
        raise ValueError('expected a schema 1 pixel-character model')
    size = data.get('canvas', {})
    if not isinstance(size, dict) or not all(integer(size.get(k), 8, 128) for k in ('width', 'height')):
        raise ValueError('canvas width/height must be integers in 8..128')
    w, h = size['width'], size['height']
    palette = data.get('palette')
    if not isinstance(palette, dict) or not 1 <= len(palette) <= 32 or any(not isinstance(k, str) or not re.fullmatch('[A-Za-z0-9]', k) or not isinstance(v, str) or not re.fullmatch('#[0-9a-fA-F]{6}', v) for k, v in palette.items()):
        raise ValueError('palette needs 1..32 single letter/digit keys and #RRGGBB colors; . is transparent')

    def rows_check(rows):
        if not isinstance(rows, list) or not 1 <= len(rows) <= h or not isinstance(rows[0], str) or not 1 <= len(rows[0]) <= w or any(not isinstance(r, str) or len(r) != len(rows[0]) or any(c != '.' and c not in palette for c in r) for r in rows):
            raise ValueError('layer rows must be a rectangular, canvas-sized pixel matrix using the palette')

    layers, frames = data.get('layers'), data.get('frames')
    if not isinstance(layers, list) or not 1 <= len(layers) <= 24 or not isinstance(frames, list) or not 1 <= len(frames) <= 64:
        raise ValueError('use 1..24 layers and 1..64 poses')
    ids = set()
    for layer in layers:
        if not isinstance(layer, dict) or not identifier(layer.get('id')) or layer['id'] in ids:
            raise ValueError('layer IDs must be safe and unique')
        ids.add(layer['id'])
        if not isinstance(layer.get('origin'), list) or len(layer['origin']) != 2 or not all(integer(n, -128, 128) for n in layer['origin']):
            raise ValueError('layer origin must contain two integer pixels')
        rows_check(layer.get('rows'))
        if 'visible' in layer and not isinstance(layer['visible'], bool):
            raise ValueError('layer visibility must be boolean')
    frame_ids = set()
    for frame in frames:
        if not isinstance(frame, dict) or not identifier(frame.get('id')) or frame['id'] in frame_ids or not integer(frame.get('duration_ms'), 40, 2000):
            raise ValueError('pose IDs must be safe/unique and durations must be 40..2000ms')
        frame_ids.add(frame['id'])
        offsets = frame.get('layers', {})
        if not isinstance(offsets, dict) or set(offsets) - ids:
            raise ValueError('pose refers to an unknown layer')
        for part in offsets.values():
            if not isinstance(part, dict) or any(not integer(part.get(k, 0), -128, 128) for k in ('dx', 'dy')) or any(k in part and not isinstance(part[k], bool) for k in ('visible', 'flip_x')):
                raise ValueError('pose offsets must be integer pixels; visibility/flip must be boolean')
            if 'rows' in part:
                rows_check(part['rows'])
        anchors = frame.get('anchors', {})
        if not isinstance(anchors, dict) or not {'foot', 'grip'} <= anchors.keys() or any(not identifier(k) or not isinstance(v, list) or len(v) != 2 or not all(integer(n, -128, 256) for n in v) for k, v in anchors.items()):
            raise ValueError('each pose needs integer foot/grip anchors')
    actions = data.get('actions', {})
    if not isinstance(actions, dict) or len(actions) > 24 or any(not identifier(k) or not isinstance(v, list) or not 1 <= len(v) <= 64 or any(f not in frame_ids for f in v) for k, v in actions.items()):
        raise ValueError('actions must name existing poses in order')
    return data


def seed():
    # Original neutral construction example, not an approved project character.
    data = {'schema_version': 1, 'kind': 'pixel-character', 'name': '原创角色草稿', 'revision': 'draft-r1',
            'canvas': {'width': 48, 'height': 64},
            'palette': {'I': '#293945', 'H': '#413f47', 'S': '#e7b698', 'D': '#c98e79', 'C': '#548b95', 'L': '#82b2b4', 'P': '#3a4b61', 'W': '#f4e7cc'},
            'layers': [], 'frames': [], 'actions': {'stand': ['front'], 'walk': ['step-a', 'step-b'], 'sit': ['sit'], 'turn': ['front', 'side']}}

    def layer(key, name, x, y, rows):
        data['layers'].append({'id': key, 'name': name, 'origin': [x, y], 'visible': True, 'rows': rows})

    layer('back-arm', '后臂', 11, 29, ['.CCCC.'] * 12 + ['.SSSS.'] * 4)
    layer('left-leg', '左腿', 16, 44, ['PPPPPP'] * 15 + ['IIIIII', 'WWWWWW'])
    layer('right-leg', '右腿', 26, 44, ['PPPPPP'] * 15 + ['IIIIII', 'WWWWWW'])
    layer('body', '上衣', 15, 28, ['..CCCCCCCCCCCC..', '.CCCCCCCCCCCCCC.', 'CCCCCCSSSSCCCCCC'] + ['CCCCCCCLLCCCCCCC'] * 4 + ['CCCCCCCCCCCCCCCC'] * 10 + ['.CCCCCCCCCCCCCC.'])
    layer('neck', '颈部', 21, 24, ['SSSSSS'] * 6)
    layer('head', '头部', 16, 9, ['...HHHHHHHHHH...', '.HHHHHHHHHHHHHH.', 'HHHHHHHHHHHHHHHH'] + ['HSSSSSSSSSSSSSSH'] * 9 + ['.SSSSSSSSSSSSSS.', '..SSSSSSSSSSSS..', '...DDDDDDDDDD...'])
    layer('hair', '头发', 15, 7, ['....HHHHHHHH....', '..HHHHHHHHHHHH..', '.HHHHHHHHHHHHHH.', 'HHHHHHHHHHHHHHHH', 'HHHHHHHHHHHHHHHH', '.HHHHHHH..HHHHH.', '.HHHHH......HHH.'])
    layer('face', '眼睛与表情', 18, 18, ['.II......II.', '.IW......IW.', '............', '.....D......', '............', '....DDDD....'])
    layer('front-arm', '前臂', 32, 29, ['.CCCC.'] * 12 + ['.SSSS.'] * 4)
    for key, label, parts, foot, grip in [
        ('front', '正面', {}, [24, 62], [35, 44]),
        ('side', '侧面草稿', {'head': {'dx': 2}, 'hair': {'dx': 2}, 'face': {'dx': 5}, 'back-arm': {'visible': False}, 'front-arm': {'dx': -3}}, [24, 62], [32, 44]),
        ('smile', '微笑', {'face': {'rows': ['.II......II.', '.IW......IW.', '............', '.....D......', '...D....D...', '....DDDD....']}}, [24, 62], [35, 44]),
        ('step-a', '步态 A', {'left-leg': {'dx': -3, 'dy': -1}, 'right-leg': {'dx': 3}, 'front-arm': {'dx': -2, 'dy': -2}, 'back-arm': {'dx': 2}}, [24, 62], [33, 42]),
        ('step-b', '步态 B', {'left-leg': {'dx': 3}, 'right-leg': {'dx': -3, 'dy': -1}, 'front-arm': {'dx': 2}, 'back-arm': {'dx': -2, 'dy': -2}}, [24, 62], [37, 44]),
        ('sit', '坐姿草稿', {'left-leg': {'rows': ['PPPPPPPPPPPP', 'PPPPPPPPPPPP', 'PPPPPPPPPPPP', '......PPPPPP', '......PPPPPP', '......WWWWWW'], 'dy': 1}, 'right-leg': {'visible': False}}, [28, 51], [35, 44])]:
        data['frames'].append({'id': key, 'label': label, 'duration_ms': 160, 'layers': parts, 'anchors': {'foot': foot, 'grip': grip}})
    return validate(data)


def raster(data, frame):
    try:
        from PIL import Image
    except ImportError as exc:
        raise ValueError('Pillow is required; install scripts/requirements-media.txt in this Python interpreter') from exc
    w, h = data['canvas']['width'], data['canvas']['height']
    result = Image.new('RGBA', (w, h))
    for layer in data['layers']:
        part = frame.get('layers', {}).get(layer['id'], {})
        if not part.get('visible', layer.get('visible', True)):
            continue
        rows = part.get('rows', layer['rows'])
        ox, oy = layer['origin']
        ox += part.get('dx', 0)
        oy += part.get('dy', 0)
        for y, row in enumerate(rows):
            for x, char in enumerate(row):
                xx = ox + (len(row) - 1 - x if part.get('flip_x') else x)
                yy = oy + y
                if char != '.' and 0 <= xx < w and 0 <= yy < h:
                    c = data['palette'][char]
                    result.putpixel((xx, yy), tuple(int(c[i:i+2], 16) for i in (1, 3, 5)) + (255,))
    return result


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def authorized(project, mode, data=None):
    from check_brief import entry_errors
    from workflow_gate import pilot_plan
    brief = json.loads((project / 'brief.json').read_text(encoding='utf-8'))
    if (brief.get('execution') or {}).get('context') == 'tool-self-test':
        raise ValueError('a user project cannot be relabelled tool-self-test; use an isolated workbench self-test instead')
    frames = (data or seed())['frames']
    options = {'operation': 'stills', 'still_count': len(frames)}
    if mode == 'motion':
        if brief.get('phase') not in ('prototype', 'animatic', 'full', 'repair', 'deliver'):
            raise ValueError('DESIGN_STILLS_ONLY: motion needs the accepted design/script and a permitted project stage')
        by_id = {f['id']: f for f in frames}
        duration = max([sum(by_id[x]['duration_ms'] for x in action) / 1000 for action in (data or seed()).get('actions', {}).values()] or [0])
        if not 0 < duration <= 8:
            raise ValueError('workbench motion previews must have an action lasting at most eight seconds')
        start = (pilot_plan(brief, project) or {}).get('start', 0)
        options = {'operation': 'video', 'duration': duration, 'timeline_range': [start, start + duration]}
    errors = entry_errors(brief, project, **options)
    if errors:
        raise ValueError('Production blocked: ' + '; '.join(errors))
    return brief


def safe_output(path, project=None, new_revision=False):
    path = path.expanduser()
    if project and not path.is_absolute():
        path = project / path
    path = path.resolve()
    if path == ROOT or ROOT in path.parents:
        raise ValueError('project assets belong outside the installed skill')
    if project and (path == project or project not in path.parents):
        raise ValueError('output must be inside the selected project, without replacing its root')
    if path.exists() and new_revision:
        base = path
        i = 2
        while path.exists():
            path = base.with_name(base.name + '-r' + str(i))
            i += 1
    if path.exists():
        raise ValueError('existing work preserved; choose another --out or use --new-revision')
    return path


def read_model(path):
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError('model must be a local JSON file no larger than 2 MiB')
    return validate(json.loads(path.read_text(encoding='utf-8')))


def build(data, target, mode, source=None):
    from PIL import Image, ImageDraw
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix='.pixel-build-', dir=target.parent))
    try:
        assets = ROOT / 'assets/pixel-workbench'
        config = json.dumps({'model': data, 'motion': mode == 'motion'}, ensure_ascii=False).replace('<', '\\u003c')
        html = (assets / 'editor.html').read_text(encoding='utf-8')
        html = html.replace('/*__PIXEL_CONFIG__*/', 'const PIXEL_CONFIG=' + config + ';').replace('/*__PIXEL_CORE__*/', (assets / 'core.js').read_text(encoding='utf-8')).replace('/*__PIXEL_UI__*/', (assets / 'editor.js').read_text(encoding='utf-8'))
        (temp / 'workbench.html').write_text(html, encoding='utf-8')
        (temp / 'character.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        images = [raster(data, f) for f in data['frames']]
        w, h = data['canvas']['width'], data['canvas']['height']
        scale = max(1, min(6, 256 // max(w, h)))
        cols = min(4, len(images))
        cellw, cellh = w * scale + 24, h * scale + 40
        board = Image.new('RGB', (cols * cellw, ((len(images) + cols - 1) // cols) * cellh), '#f4f1e9')
        drawing = ImageDraw.Draw(board)
        frame_records = []
        for i, (f, im) in enumerate(zip(data['frames'], images)):
            filename = 'pose-' + f['id'] + '.png'
            im.save(temp / filename)
            x, y = (i % cols) * cellw + 12, (i // cols) * cellh + 12
            board.paste(im.resize((w * scale, h * scale), Image.Resampling.NEAREST), (x, y), im.resize((w * scale, h * scale), Image.Resampling.NEAREST))
            drawing.text((x, y + h * scale + 5), f['id'], fill='#293945')
            frame_records.append({'id': f['id'], 'path': filename, 'sha256': digest(temp / filename), 'duration_ms': f['duration_ms'], 'anchors': f['anchors'], 'rect': {'x': i * w, 'y': 0, 'w': w, 'h': h}})
        board.save(temp / 'design-board.png')
        metadata = {'schema_version': 1, 'kind': 'pixel-assets', 'mode': mode, 'acceptance': 'not_reviewed', 'canvas': data['canvas'], 'frames': frame_records, 'actions': data.get('actions', {}) if mode == 'motion' else {}, 'sheet': None, 'source_sha256': digest(temp / 'character.json')}
        if mode == 'motion':
            sheet = Image.new('RGBA', (w * len(images), h))
            for i, im in enumerate(images):
                sheet.paste(im, (i * w, 0))
            sheet.save(temp / 'sprites.png')
            metadata['sheet'] = {'path': 'sprites.png', 'sha256': digest(temp / 'sprites.png')}
            shutil.copy2(assets / 'player.js', temp / 'sprite-player.js')
        (temp / 'assets.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        receipt = {'tool': 'storybook-mv.pixel-workbench', 'mode': mode, 'source': str(source) if source else 'original-neutral-construction-example', 'source_sha256': digest(source) if source else None, 'model_sha256': digest(temp / 'character.json'), 'motion_enabled': mode == 'motion', 'pose_count': len(images), 'acceptance': 'not_reviewed', 'limitations': ['Neutral example poses are construction aids, not verified natural acting.', 'No user approval, audio sync, finished MV or destination-platform result is supplied.']}
        (temp / 'workbench-report.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        os.rename(temp, target)
        return receipt
    finally:
        if temp.exists():
            shutil.rmtree(temp)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=('init', 'build'))
    p.add_argument('--project', type=Path)
    p.add_argument('--model', type=Path)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--mode', choices=('design', 'motion'), default='design')
    p.add_argument('--new-revision', action='store_true')
    p.add_argument('--tool-self-test', action='store_true', help='isolated original example only, never a user MV or approval bypass')
    a = p.parse_args()
    try:
        project = a.project.expanduser().resolve() if a.project else None
        if a.tool_self_test and project:
            raise ValueError('isolated self-tests cannot select a user project')
        if not a.tool_self_test and not project:
            raise ValueError('provide --project with its truthful brief and workflow, or use an isolated --tool-self-test')
        if a.command == 'init' and (a.model or a.mode != 'design'):
            raise ValueError('init creates the neutral static design workspace; use build for an edited model or approved motion')
        model_path = None
        if a.model:
            model_path = a.model.expanduser()
            model_path = (project / model_path if project and not model_path.is_absolute() else model_path).resolve()
            if project and project not in model_path.parents:
                raise ValueError('model must belong to the selected project')
            if a.tool_self_test:
                marker = model_path.parent / 'SELF_TEST.json'
                if not marker.is_file() or json.loads(marker.read_text(encoding='utf-8')).get('purpose') != 'isolated-pixel-workbench-example':
                    raise ValueError('self-test input must come from an isolated workbench example')
        if a.command == 'build' and not model_path:
            raise ValueError('build needs --model; edited data is never guessed')
        data = read_model(model_path) if model_path else seed()
        if a.mode == 'design' and len(data['frames']) > 12:
            raise ValueError('design exports allow at most twelve separate static poses')
        if not a.tool_self_test:
            authorized(project, a.mode, data)
        target = safe_output(a.out, project, a.new_revision)
        report = build(data, target, a.mode, model_path)
        if a.tool_self_test:
            (target / 'SELF_TEST.json').write_text('{"purpose":"isolated-pixel-workbench-example","not_a_user_mv":true}\n', encoding='utf-8')
        print(json.dumps({'directory': str(target), 'editor': str(target / 'workbench.html'), 'board': str(target / 'design-board.png'), **report}, ensure_ascii=False))
        return 0
    except (OSError, ValueError, KeyError, TypeError, ImportError) as exc:
        p.error(str(exc))


if __name__ == '__main__':
    raise SystemExit(main())

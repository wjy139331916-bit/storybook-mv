#!/usr/bin/env python3
"""Create an explicitly selected bundled engine without choosing a visual style."""
import argparse
import copy
import json
import math
import shutil
import subprocess
from pathlib import Path
from check_brief import entry_errors, aspect_parts
from input_contracts import sha


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('project', type=Path)
    p.add_argument('--engine', choices=('painted-p5', 'canvas2d', 'remotion'))
    p.add_argument('--brief', type=Path)
    p.add_argument('--duration', type=float, default=8)
    p.add_argument('--fps', type=int, default=30)
    p.add_argument('--width', type=int)
    p.add_argument('--height', type=int)
    p.add_argument('--install', action='store_true')
    p.add_argument('--tool-self-test', action='store_true', help='isolated toolkit verification only; never a bypass for a requested user MV')
    p.add_argument('--phase', choices=('design','prototype'), help='design creates only a static-design workspace; default preserves the brief stage')
    a = p.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        brief = json.loads((a.brief or root / 'assets/brief.template.json').read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        p.error(str(exc))
    if not isinstance(brief, dict):
        p.error('brief must be an object')
    if a.tool_self_test:
        if a.brief:
            p.error('do not relabel a user brief as a tool self-test')
        if a.duration>60:
            p.error('isolated tool self-tests are limited to 60 seconds')
    else:
        if not a.brief:
            p.error('confirmed user content and scoped authorization are required: provide --brief; three basic answers are not production approval')
        selected_phase=a.phase or brief.get('phase')
        if selected_phase not in ('design','study','prototype'):
            p.error('scaffold only design/prototype work; preserve and continue later project stages')
        brief['phase']=selected_phase
        blocked = entry_errors(brief, a.brief.resolve().parent, 'design' if selected_phase=='design' else 'prototype', a.duration, operation='scaffold')
        if blocked:
            p.error('Production blocked: '+'; '.join(blocked))
    for section in ('execution', 'output', 'style', 'lyrics'):
        if brief.get(section) is not None and not isinstance(brief[section], dict):
            p.error(section + ' must be an object or null')
    selected = (brief.get('execution') or {}).get('engine')
    engine = a.engine or selected
    if not engine:
        p.error('select --engine after the style/route is decided; there is no default style or engine')
    if selected and a.engine and selected != a.engine:
        p.error('engine conflicts with the brief; update the agreed route first')
    registry = json.loads((root / 'assets/engines.json').read_text(encoding='utf-8'))
    if engine not in registry or registry[engine]['status'] != 'bundled':
        p.error('this route is guide-only here; set it up from appropriate documentation instead of silently using another engine')
    if not math.isfinite(a.duration) or a.duration <= 0 or not 1 <= a.fps <= 120:
        p.error('duration must be positive and fps must be 1..120')
    if bool(a.width) != bool(a.height):
        p.error('provide both --width and --height')
    output = brief.get('output') or {}
    resolution = output.get('resolution')
    if a.width and a.height:
        width, height = a.width, a.height
    elif isinstance(resolution, list) and len(resolution) == 2:
        width, height = resolution
    else:
        ra,rb=aspect_parts(output.get('aspect_ratio') or ('16:9' if a.tool_self_test else None))
        unit=max(2,math.ceil((1920 if ra<rb else 1080)/rb/2)*2)
        width,height=ra*unit,rb*unit
    if not all(isinstance(x, int) and x > 0 and x % 2 == 0 for x in (width, height)):
        p.error('prototype dimensions must be positive even integers')
    if not a.tool_self_test:
        ra,rb=aspect_parts(output.get('aspect_ratio'))
        if width*rb!=height*ra:
            p.error('resolution conflicts with the approved aspect ratio')
    target = a.project.expanduser().resolve()
    if target == root or root in target.parents:
        p.error('project output must be outside the installed skill')
    if target.exists() and (not target.is_dir() or any(target.iterdir())):
        p.error('destination is not empty; existing work was preserved')
    shutil.copytree(root / 'assets' / registry[engine]['template'], target, dirs_exist_ok=True)
    if engine == 'canvas2d' and (root / 'scripts/render_canvas.mjs').is_file():
        shutil.copy2(root / 'scripts/render_canvas.mjs', target / 'render_canvas.mjs')
    for name in ('assets', 'data', 'out/check', 'src/data'):
        (target / name).mkdir(parents=True, exist_ok=True)
    if engine == 'remotion':
        (target/'src/project.json').write_text(json.dumps({'duration':a.duration,'width':width,'height':height,'fps':a.fps,'fidelity':'design' if not a.tool_self_test else 'original-probe'}),encoding='utf-8')
    shutil.copytree(root/'assets/contracts',target/'assets/contracts',dirs_exist_ok=True)
    brief = copy.deepcopy(brief)
    brief.update(project=target.name, phase='prototype' if a.tool_self_test else selected_phase)
    brief['execution'] = dict(brief.get('execution') or {})
    brief['output'] = dict(brief.get('output') or {})
    brief.setdefault('execution', {}).update(engine=engine, template_status='bundled')
    if a.tool_self_test:
        brief['execution'].update(context='tool-self-test',production_authorized=False,authorized_scope=None,authorized_duration=None,authorization_evidence=None)
        brief['tool_self_test']={'source':'storybook-mv','purpose':'isolated-tool-verification','not_a_user_mv':True}
        brief['music']['source']='none'
    brief.setdefault('output', {}).update(resolution=[width, height], fps=a.fps)
    brief['prototype'] = {'duration': a.duration, 'song_duration_verified': False}
    (target / 'brief.json').write_text(json.dumps(brief, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    config = {'duration': a.duration, 'width': width, 'height': height, 'fps': a.fps, 'bpm': 120, 'offset': 0, 'boil': 0, 'prototype': True, 'bpmMeasured': False}
    (target / 'src/config.js').write_text('// Prototype dimensions/timing are not a verified song plan.\nconst PROJECT = ' + json.dumps(config) + ';\nglobalThis.STORY_LYRICS_MODE = ' + json.dumps((brief.get('lyrics') or {}).get('mode') or 'unset') + ';\n', encoding='utf-8')
    for name in ('production_gate.mjs','check_brief.py','input_contracts.py','pilot_gate.py','project_contracts.py','workflow_gate.py','review_workspace.py','media_audit.py','preflight.py','runtime_environment.py','director_contract.py'):
        shutil.copy2(root/'scripts'/name,target/name)
    if not a.tool_self_test:
        from workflow_gate import relocate
        relocate(brief,a.brief.resolve().parent,target)
        # Relocate only explicitly referenced, digest-checked inputs; preserve
        # source attribution strings and content hashes across project handoff.
        base=a.brief.resolve().parent
        records=[brief['content_confirmation'].get('record'),brief.get('song_reading',{}).get('lyrics_document'),brief.get('lyrics',{}).get('display_document'),brief.get('lyrics',{}).get('font'),brief.get('lyrics',{}).get('glyph_review')]
        records += [x.get('snapshot') for x in brief.get('song_reading',{}).get('sources',[]) if isinstance(x,dict)]
        if brief.get('music',{}).get('audio'):
            records.append({'path':brief['music']['audio'],'sha256':brief['music'].get('audio_sha256'),'_audio':True})
        for i,record in enumerate(records):
            if not isinstance(record,dict) or not record.get('path'):continue
            source=Path(record['path']).expanduser()
            if not source.is_absolute():source=base/source
            dest=target/'assets'/('input-'+str(i)+source.suffix)
            shutil.copy2(source,dest)
            rel=dest.relative_to(target).as_posix()
            if record.get('_audio'):brief['music']['audio']=rel
            else:record['path']=rel
        (target/'brief.json').write_text(json.dumps(brief,ensure_ascii=False,indent=2)+'\n', encoding='utf-8')
    renderer = target / 'render.mjs'
    renderer.write_text(renderer.read_text(encoding='utf-8').replace('args.fps || 30', 'args.fps || ' + str(a.fps)), encoding='utf-8')
    html = target / 'studio.html'
    text = html.read_text(encoding='utf-8').replace('width="1920" height="1080"', f'width="{width}" height="{height}"')
    text = text.replace('aspect-ratio: 16 / 9', f'aspect-ratio: {width} / {height}')
    html.write_text(text, encoding='utf-8')
    (target / 'PROGRESS.md').write_text('# Progress\n\nExplicit engine scaffold only. Visual design, production authorization, actual song timing and rendered quality are separate checks.\n', encoding='utf-8')
    if (root / 'assets/UPSTREAM_LICENSE').exists():
        shutil.copy2(root / 'assets/UPSTREAM_LICENSE', target / 'UPSTREAM_LICENSE')
    if a.install:
        npm = shutil.which('npm')
        if not npm:
            p.error('project was created but npm is unavailable')
        subprocess.run([npm, 'ci' if (target / 'package-lock.json').exists() else 'install'], cwd=target, check=True)
    print(json.dumps({'project': str(target), 'engine': engine, 'prototype': True, 'style_selected': bool((brief.get('style') or {}).get('direction')), 'npm_install_run': a.install}, ensure_ascii=False))


if __name__ == '__main__':
    import sys
    for _stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(_stream, 'reconfigure'):
            _stream.reconfigure(encoding='utf-8')
    main()

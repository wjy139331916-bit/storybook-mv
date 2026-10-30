#!/usr/bin/env python3
"""Check prerequisites for the selected engine; never silently assume p5."""
import argparse
import glob
import importlib.util
import json
import os
import shutil
import subprocess
from pathlib import Path
from runtime_environment import browser_candidates, python_diagnostics, platform_facts


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project', type=Path)
    p.add_argument('--engine', choices=('painted-p5', 'canvas2d', 'remotion', 'threejs', 'blender', 'custom'))
    p.add_argument('--chrome')
    p.add_argument('--runtime', choices=('browser', 'node-canvas'))
    p.add_argument('--canvas-module', type=Path)
    p.add_argument('--json', action='store_true')
    p.add_argument('--strict', action='store_true')
    p.add_argument('--require-cjk', action='store_true')
    p.add_argument('--font', type=Path, help='selected local Chinese font; checked against the project text when available')
    p.add_argument('--media-tools', action='store_true', help='also check optional Python media-analysis dependencies')
    a = p.parse_args()
    engine = a.engine
    brief = {}
    if a.project and (a.project / 'brief.json').is_file():
        try:
            brief = json.loads((a.project / 'brief.json').read_text(encoding='utf-8'))
            selected_engine = (brief.get('execution') or {}).get('engine')
            if engine and selected_engine and engine != selected_engine:
                p.error('engine conflicts with the selected project route')
            engine = engine or selected_engine
        except (OSError, ValueError, AttributeError):
            pass
    runtime = a.runtime or (brief.get('execution') or {}).get('runtime') or 'browser'
    if runtime == 'node-canvas' and engine != 'canvas2d':
        p.error('node-canvas is an optional canvas2d runtime only; it does not test p5, WebGL or another engine')
    required = ['ffmpeg', 'ffprobe']
    dependencies_python = {'interpreter': __import__('sys').executable, 'major': __import__('sys').version_info.major}
    if engine in ('painted-p5', 'canvas2d', 'remotion', 'threejs'):
        required += ['node', 'npm']
    if engine == 'blender':
        required += ['blender']
    tools = {k: shutil.which(k) for k in required}
    missing = [k for k, v in tools.items() if not v]
    # User-stage design evidence is decoded even without optional diagnostics.
    contract_dependencies = {'PIL': importlib.util.find_spec('PIL') is not None} if brief and (brief.get('execution') or {}).get('context') != 'tool-self-test' else {}
    dependencies_python['dependencies'] = contract_dependencies
    if contract_dependencies.get('PIL') is False:
        missing.append('Pillow for actual design-image evidence (install scripts/requirements-media.txt)')
    python_media = {name: importlib.util.find_spec(name) is not None for name in ('numpy', 'PIL')} if a.media_tools else {}
    missing += [name+' for the selected media tools (see scripts/requirements-media.txt)' for name, present in python_media.items() if not present]
    if not engine:
        missing.append('rendering engine has not been selected')
    browser_engine = engine in ('painted-p5', 'canvas2d', 'remotion', 'threejs') and runtime != 'node-canvas'
    chrome = None
    if browser_engine:
        candidates = [a.chrome, os.environ.get('CHROME_PATH'), shutil.which('google-chrome'), shutil.which('chromium'), shutil.which('chromium-browser'), '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']
        candidates += [str(Path(os.environ.get(k, 'C:/Program Files')) / 'Google/Chrome/Application/chrome.exe') for k in ('PROGRAMFILES', 'PROGRAMFILES(X86)')]
        candidates += sorted(glob.glob(str(Path.home() / '.cache/ms-playwright/chromium-*/chrome-linux64/chrome')), reverse=True)
        chrome = next(iter(browser_candidates(a.chrome)), None)
        if not chrome:
            missing.append('Chrome/Chromium (or backend-specific managed browser)')
    maps = {'painted-p5': {'p5': 'p5/lib/p5.min.js', 'p5.brush': 'p5.brush/dist/p5.brush.js', 'puppeteer-core': 'puppeteer-core/package.json'}, 'canvas2d': {'puppeteer-core': 'puppeteer-core/package.json'}, 'remotion': {'remotion': 'remotion/package.json', '@remotion/renderer':'@remotion/renderer/package.json', '@remotion/bundler':'@remotion/bundler/package.json', '@remotion/cli':'@remotion/cli/package.json', 'react':'react/package.json', 'react-dom':'react-dom/package.json'}, 'threejs': {'three': 'three/package.json'}}
    dependencies = {}
    if runtime == 'node-canvas':
        try:
            module = str(a.canvas_module.expanduser().resolve()) if a.canvas_module else '@napi-rs/canvas'
            probe = subprocess.run(['node', '-e', 'const m=require(process.argv[1]);console.log(m.createCanvas(2,2).toBuffer("image/png").length)', module], cwd=a.project or Path.cwd(), capture_output=True, text=True, timeout=10, encoding='utf-8')
            dependencies['@napi-rs/canvas'] = probe.returncode == 0
        except (OSError, subprocess.SubprocessError):
            dependencies['@napi-rs/canvas'] = False
        if not dependencies['@napi-rs/canvas']:
            missing.append('@napi-rs/canvas for the explicitly selected CPU runtime')
    elif a.project:
        dependencies = {k: (a.project / 'node_modules' / v).is_file() for k, v in maps.get(engine, {}).items()}
        missing += [k for k, v in dependencies.items() if not v]
    elif engine in ('painted-p5', 'canvas2d', 'remotion', 'threejs'):
        missing.append('project dependencies not checked; provide --project')
    font = {'status': 'unverified', 'families': []}
    fc = shutil.which('fc-list')
    if fc:
        try:
            r = subprocess.run([fc, ':lang=zh', 'family'], capture_output=True, text=True, timeout=5, check=True, encoding='utf-8')
            families = sorted(set(x.strip() for x in r.stdout.splitlines() if x.strip()))
            font = {'status': 'found' if families else 'missing', 'families': families[:6]}
        except (OSError, subprocess.SubprocessError):
            pass
    else:
        paths = [Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts/msyh.ttc', Path('/System/Library/Fonts/PingFang.ttc'), Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')]
        found = [str(x) for x in paths if x.is_file()]
        if found:
            font = {'status': 'found', 'families': found}
    need_cjk = a.require_cjk or str((brief.get('lyrics') or {}).get('language') or '').lower().startswith(('zh', 'chinese', '中文'))
    selected_font = a.font or (brief.get('lyrics') or {}).get('font', {}).get('path') if isinstance((brief.get('lyrics') or {}).get('font'), dict) else a.font
    if selected_font:
        selected_font = Path(selected_font).expanduser()
        if a.project and not selected_font.is_absolute(): selected_font = a.project / selected_font
        font['selected'] = str(selected_font)
        font['status'] = 'found' if selected_font.is_file() else 'missing'
    if need_cjk and font['status'] != 'found' and not any('Chinese-capable font' in x for x in missing): missing.append('Chinese-capable font (' + font['status'] + ')')
    needed_python = (['PIL'] if contract_dependencies else []) + (['numpy', 'PIL'] if a.media_tools else []) + (['fontTools'] if need_cjk else [])
    interpreter_diagnostics = python_diagnostics(tuple(dict.fromkeys(needed_python)))
    bridge = interpreter_diagnostics['bridge']
    if not bridge or not all(bridge['modules'].values()): missing.append('selected MV_PYTHON/bridge interpreter is unavailable or lacks required packages; inspect interpreter_diagnostics')
    dependency_versions = {}
    if a.project:
        for name in dependencies:
            package = a.project / 'node_modules' / name / 'package.json'
            try: dependency_versions[name] = json.loads(package.read_text(encoding='utf-8')).get('version')
            except (OSError, ValueError): dependency_versions[name] = None
    guide_only = engine in ('threejs', 'blender', 'custom')
    if guide_only:
        missing.append('backend-specific executable probe is not bundled; verify the chosen adapter separately')
    if engine == 'remotion':
        try:
            network = subprocess.run(['node','-e','require("node:os").networkInterfaces();console.log("ok")'],capture_output=True,text=True,timeout=5)
            if network.returncode:missing.append('Remotion local server needs network-interface/loopback access; this host denies os.networkInterfaces(). Use a normal permitted render host; do not patch around host restrictions.')
        except (OSError,subprocess.SubprocessError):missing.append('Remotion local-server environment probe could not run')
    result = {'ready': not missing, 'engine': engine, 'runtime': runtime, 'template_support': 'guide-only' if guide_only else ('bundled' if engine else 'unselected'), 'tools': tools, 'chrome': chrome, 'project_dependencies': dependencies, 'dependency_versions': dependency_versions, 'shared_contract_python':dependencies_python, 'interpreter_diagnostics': interpreter_diagnostics, 'platform_facts': platform_facts(), 'python_media': python_media, 'chinese_font': font, 'missing': missing, 'next_steps': ['Install only the selected project dependencies with npm ci (lockfile) or npm install; runtime_smoke.py --install can prepare its own isolated project.', 'For Chinese projects use --require-cjk --font <local-font>, then run runtime_smoke.py --cjk --font <local-font>.'], 'scope': 'Prerequisites and optional 2x2 CPU-canvas probe only; run runtime_smoke.py for an encoded sample. No project aesthetics or real-song sync was verified'}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if a.strict and missing else 0


if __name__ == '__main__':
    import sys
    for _stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(_stream, 'reconfigure'):
            _stream.reconfigure(encoding='utf-8')
    raise SystemExit(main())

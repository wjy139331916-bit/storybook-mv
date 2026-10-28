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
    if engine in ('painted-p5', 'canvas2d', 'remotion', 'threejs'):
        required += ['node', 'npm']
    if engine == 'blender':
        required += ['blender']
    tools = {k: shutil.which(k) for k in required}
    missing = [k for k, v in tools.items() if not v]
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
        chrome = next((str(Path(x).expanduser()) for x in candidates if x and Path(x).expanduser().is_file()), None)
        if not chrome:
            missing.append('Chrome/Chromium (or backend-specific managed browser)')
    maps = {'painted-p5': {'p5': 'p5/lib/p5.min.js', 'p5.brush': 'p5.brush/dist/p5.brush.js', 'puppeteer-core': 'puppeteer-core/package.json'}, 'canvas2d': {'puppeteer-core': 'puppeteer-core/package.json'}, 'remotion': {'remotion': 'remotion/package.json'}, 'threejs': {'three': 'three/package.json'}}
    dependencies = {}
    if runtime == 'node-canvas':
        try:
            module = str(a.canvas_module.expanduser().resolve()) if a.canvas_module else '@napi-rs/canvas'
            probe = subprocess.run(['node', '-e', 'const m=require(process.argv[1]);console.log(m.createCanvas(2,2).toBuffer("image/png").length)', module], cwd=a.project or Path.cwd(), capture_output=True, text=True, timeout=10)
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
            r = subprocess.run([fc, ':lang=zh', 'family'], capture_output=True, text=True, timeout=5, check=True)
            families = sorted(set(x.strip() for x in r.stdout.splitlines() if x.strip()))
            font = {'status': 'found' if families else 'missing', 'families': families[:6]}
        except (OSError, subprocess.SubprocessError):
            pass
    else:
        paths = [Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts/msyh.ttc', Path('/System/Library/Fonts/PingFang.ttc'), Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')]
        found = [str(x) for x in paths if x.is_file()]
        if found:
            font = {'status': 'found', 'families': found}
    if a.require_cjk and font['status'] != 'found':
        missing.append('Chinese-capable font (' + font['status'] + ')')
    guide_only = engine in ('remotion', 'threejs', 'blender', 'custom')
    if guide_only:
        missing.append('backend-specific executable probe is not bundled; verify the chosen adapter separately')
    result = {'ready': not missing, 'engine': engine, 'runtime': runtime, 'template_support': 'guide-only' if guide_only else ('bundled' if engine else 'unselected'), 'tools': tools, 'chrome': chrome, 'project_dependencies': dependencies, 'python_media': python_media, 'chinese_font': font, 'missing': missing, 'scope': 'prerequisites and optional 2x2 CPU-canvas probe only; run runtime_smoke.py for an encoded sample. No project aesthetics or real-song sync was verified'}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if a.strict and missing else 0


if __name__ == '__main__':
    raise SystemExit(main())

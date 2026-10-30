"""Small, explicit destination diagnostics; no automatic interpreter substitution."""
import glob
import importlib.metadata
import importlib.util
import json
import os
from pathlib import Path
import platform
import shlex
import shutil
import subprocess
import sys

MODULES = {'numpy': 'numpy', 'PIL': 'Pillow', 'fontTools': 'fonttools'}


def python_facts(required=()):
    packages = {}
    for module, distribution in MODULES.items():
        try:
            version = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            version = None
        packages[module] = {'available': importlib.util.find_spec(module) is not None, 'version': version}
    return {'interpreter': sys.executable, 'version': platform.python_version(), 'major': sys.version_info.major,
            'packages': packages, 'missing': [m for m in required if not packages.get(m, {}).get('available')]}


def python_diagnostics(required=()):
    current = python_facts(required)
    bridge = os.environ.get('MV_PYTHON') or shutil.which('python3') or shutil.which('python')
    candidates = list(dict.fromkeys([bridge, sys.executable, shutil.which('python3'), shutil.which('python'), '/usr/bin/python3', '/usr/local/bin/python3']))
    alternatives = []
    code = 'import sys,json,importlib.util;print(json.dumps({"interpreter":sys.executable,"version":sys.version.split()[0],"major":sys.version_info.major,"modules":{m:importlib.util.find_spec(m) is not None for m in sys.argv[1:]}}))'
    for candidate in candidates:
        if not candidate:
            continue
        try:
            r = subprocess.run([candidate, '-c', code, *required], capture_output=True, text=True, encoding='utf-8', timeout=5)
            if r.returncode == 0:
                facts = json.loads(r.stdout)
                if facts['major'] == 3:
                    facts['command'] = candidate
                    alternatives.append(facts)
        except (OSError, ValueError, subprocess.SubprocessError):
            continue
        # Probe other interpreters only when the selected one has a problem.
        if len(alternatives) == 1 and all(alternatives[0]['modules'].values()) and not current['missing']:
            break
    selected = next((f for f in alternatives if f['command'] == bridge), None)
    working = next((f for f in alternatives if all(f['modules'].values())), None)
    command = None
    if working:
        command = ('$env:MV_PYTHON=' + json.dumps(working['interpreter'])) if os.name == 'nt' else 'export MV_PYTHON=' + shlex.quote(working['interpreter'])
    return {'current': current, 'bridge_command': bridge, 'bridge': selected, 'checked_interpreters': alternatives,
            'suggestion': command, 'scope': 'Version/package diagnostics only; no environment variable was changed.'}


def version(command):
    if not command:
        return None
    try:
        r = subprocess.run([str(command), '--version' if Path(command).name not in ('ffmpeg', 'ffprobe') else '-version'], capture_output=True, text=True, encoding='utf-8', timeout=5)
        return (r.stdout or r.stderr).splitlines()[0] if r.returncode == 0 and (r.stdout or r.stderr) else None
    except (OSError, subprocess.SubprocessError):
        return None


def browser_candidates(explicit=None):
    bases = [Path(os.environ['PLAYWRIGHT_BROWSERS_PATH'])] if os.environ.get('PLAYWRIGHT_BROWSERS_PATH') else []
    bases += [Path.home() / '.cache/ms-playwright', Path(os.environ.get('LOCALAPPDATA', 'C:/Users/Default/AppData/Local')) / 'ms-playwright', Path.home() / 'Library/Caches/ms-playwright']
    result = [explicit, os.environ.get('CHROME_PATH'), shutil.which('google-chrome'), shutil.which('chromium'), shutil.which('chromium-browser'), '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome']
    result += [str(Path(os.environ.get(k, 'C:/Program Files')) / 'Google/Chrome/Application/chrome.exe') for k in ('PROGRAMFILES', 'PROGRAMFILES(X86)')]
    for base in bases:
        for pattern in ('chromium-*/chrome-linux64/chrome', 'chromium-*/chrome-linux/chrome', 'chromium-*/chrome-win/chrome.exe', 'chromium-*/chrome-win64/chrome.exe', 'chromium_headless_shell-*/chrome-linux/headless_shell', 'chromium_headless_shell-*/chrome-linux64/headless_shell'):
            result += sorted(glob.glob(str(base / pattern)), reverse=True)
    return [str(Path(x).expanduser()) for x in result if x and Path(x).expanduser().is_file()]


def platform_facts():
    return {'system': platform.system(), 'platform': sys.platform, 'arch': platform.machine(), 'release': platform.release(), 'python': python_facts(), 'node': version(shutil.which('node')), 'ffmpeg': version(shutil.which('ffmpeg')), 'ffprobe': version(shutil.which('ffprobe'))}

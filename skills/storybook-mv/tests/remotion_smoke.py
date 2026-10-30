#!/usr/bin/env python3
"""Actual normal-host Remotion nonzero-range exercise; all approvals are synthetic fixtures."""
import argparse
from array import array
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import wave

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
from test_content_gate import agreed_fixture,bind_confirmation
from workflow_fixtures import approval
from input_contracts import sha,content_digest
from runtime_smoke import pulses


def prepare_project(out,deps_from=None):
    """Build the real bounded fixture before requiring a browser/rendering host."""
    out=Path(out).expanduser().resolve()
    if out.exists():raise ValueError('choose a new isolated output directory')
    out.mkdir(parents=True);audio=out/'original.wav';pulses(audio)
    with wave.open(str(audio),'rb') as f:params=f.getparams();data=f.readframes(f.getnframes())
    with wave.open(str(audio),'wb') as f:f.setparams(params);f.writeframes(data+data)
    brief=agreed_fixture();brief['phase']='prototype';brief['execution'].update(engine='remotion',runtime='browser',authorized_scope='full',authorized_duration=4,authorization_evidence='Synthetic fixture requests a four-second original timeline and a two-second pilot at [2,4]; not real user consent')
    brief['prototype']['duration']=2;brief['output'].update(resolution=[640,360],fps=30)
    brief['music'].update(source='provided',kind='instrumental',scope='four-second original soundtrack with a bounded two-second pilot',audio='original.wav',audio_sha256=sha(audio),duration=4)
    brief['content_confirmation']['content_sha256']=content_digest(brief)
    bind_confirmation(brief,out)
    pkg=brief['workflow']['packages']['design'];file=out/pkg['path'];obj=json.loads(file.read_text());obj['pilot'].update(start=2,end=4);file.write_text(json.dumps(obj));pkg['sha256']=sha(file);approval(brief,out,'design')
    file=out/'brief.json';file.write_text(json.dumps(brief))
    project=out/'project';prepared=subprocess.run([sys.executable,str(ROOT/'scripts/scaffold.py'),str(project),'--engine','remotion','--brief',str(file),'--duration','2','--width','640','--height','360','--fps','30'],capture_output=True,text=True,encoding='utf-8')
    if prepared.returncode:raise RuntimeError('Nonzero Remotion fixture could not be prepared: '+prepared.stderr)
    if deps_from is not None:(project/'node_modules').symlink_to(Path(deps_from).resolve(),target_is_directory=True)
    source=project/'src/index.jsx';source.write_text(source.read_text().replace('{probe?<div','{true?<div'))
    return project,audio


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);p.add_argument('--deps-from',type=Path,required=True);p.add_argument('--chrome',type=Path);a=p.parse_args()
    out=a.output.expanduser().resolve()
    try:project,audio=prepare_project(out,a.deps_from)
    except (ValueError,RuntimeError) as exc:p.error(str(exc))
    cmd=['node','render.mjs','--clip','--out=out/nonzero/clip.mp4']+(['--chrome='+str(a.chrome.resolve())] if a.chrome else [])
    result=subprocess.run(cmd,cwd=project,capture_output=True,text=True)
    if result.returncode:raise RuntimeError(result.stderr)
    report=json.loads((project/'out/nonzero/render-report.json').read_text())
    if report['range']!=[2,4] or report['audio']['sha256']!=sha(audio) or not report['encoded']['full_decode']:raise ValueError('nonzero source/range/audio report failed')
    video=project/'out/nonzero/clip.mp4';pcm=array('h',subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-map','0:a:0','-ar','8000','-ac','1','-f','s16le','-']))
    if sys.byteorder!='little':pcm.byteswap()
    starts=[];active=False
    for i in range(0,len(pcm),160):
        block=pcm[i:i+160];loud=math.sqrt(sum(x*x for x in block)/max(1,len(block)))/32768>.03
        if loud and not active:starts.append(i/8000)
        active=loud
    if len(starts)!=2 or any(abs(x-y)>.06 for x,y in zip(starts,[.5,1.5])):raise ValueError('nonzero encoded soundtrack pulses are shifted: '+str(starts))
    receipt={'status':'passed','source_range':[2,4],'encoded_pulse_offsets':starts,'runtime':report['runtime'],'scope':'Original actual normal-host Remotion nonzero source/audio exercise, with synthetic fixture approvals only. No real user acceptance or art claim.'}
    (out/'nonzero-remotion-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))


if __name__=='__main__':main()

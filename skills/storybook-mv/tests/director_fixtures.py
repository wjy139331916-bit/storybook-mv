"""Original synthetic director projects. These records never represent real user approval."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import wave

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
from test_content_gate import agreed_fixture,bind_confirmation
from workflow_fixtures import approval
from input_contracts import sha,content_digest
from director_workbench import seed,write


def make_project(folder,engine='canvas2d',phase='prototype',accepted=True,audio=False):
    folder=Path(folder);folder.mkdir(parents=True)
    model=seed(6,640,360,30,True);model['caption']['enabled']=False
    source=folder/'director-approved.json';write(source,model)
    brief=agreed_fixture();brief['phase']=phase
    brief['execution'].update(engine=engine,runtime='node-canvas' if engine=='canvas2d' else 'browser',authorized_scope='full',authorized_duration=6,
        authorization_evidence='Synthetic fixture authorizes its original six-second construction study, with a two-second pilot; not real consent')
    brief['prototype']['duration']=2;brief['output'].update(resolution=[640,360],fps=30)
    brief['characters'].update(required=True,roles=['original construction figure'])
    brief['content'].update(subject='original construction figure and letter',core_idea='notice the letter, approach and hold',exclusions=['no real user or real song'])
    if audio:
        from runtime_smoke import pulses
        track=folder/'original.wav';pulses(track)
        with wave.open(str(track),'rb') as f:params=f.getparams();data=f.readframes(f.getnframes())
        with wave.open(str(track),'wb') as f:f.setparams(params);f.writeframes(data*3)
        brief['music'].update(source='provided',kind='instrumental',audio='original.wav',audio_sha256=sha(track),duration=6,scope='original six-second synthetic pulse recording')
    brief['content_confirmation']['content_sha256']=content_digest(brief)
    bind_confirmation(brief,folder)
    package=brief['workflow']['packages']['design'];path=folder/package['path'];obj=json.loads(path.read_text(encoding='utf-8'));obj['pilot'].update(start=2,end=4)
    obj['artifacts'].append({'role':'design_source','path':source.name,'sha256':sha(source)})
    write(path,obj);package['sha256']=sha(path);approval(brief,folder,'design')
    if not accepted:brief['workflow']['approvals'].clear()
    write(folder/'brief.json',brief)
    project=folder/'project'
    r=subprocess.run([sys.executable,str(ROOT/'scripts/scaffold.py'),str(project),'--engine',engine,'--brief',str(folder/'brief.json'),'--duration','2','--width','640','--height','360'],capture_output=True,text=True,encoding='utf-8')
    if r.returncode:raise ValueError(r.stderr)
    write(project/'director-current.json',model)
    return project,model

#!/usr/bin/env python3
"""Render the actual original director model through the chosen existing host."""
import argparse
from array import array
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
from director_fixtures import make_project
import director_workbench as D


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);p.add_argument('--engine',choices=('canvas2d','remotion'),default='canvas2d');p.add_argument('--canvas-module');p.add_argument('--deps-from',type=Path);p.add_argument('--chrome',type=Path);a=p.parse_args()
    out=a.output.expanduser().resolve()
    if out.exists():p.error('use a new isolated output directory')
    out.mkdir(parents=True)
    project,model=make_project(out/'fixture',engine=a.engine,audio=True)
    caps,brief=D.context(project,True,False);workspace=project/'plan/workspace'
    D.build_editor(workspace,model,caps,brief,project,project/'director-current.json')
    package=project/'plan/director-r1';D.export_package(package,model,project,caps,workspace);D.activate(project,package)
    if a.engine=='remotion':
        if not a.deps_from:p.error('Remotion exercise needs its selected --deps-from')
        (project/'node_modules').symlink_to(a.deps_from.resolve(),target_is_directory=True)
        cmd=['node','render.mjs','--clip','--range=2:4','--out=out/director/clip.mp4']
        if a.chrome:cmd.append('--chrome='+str(a.chrome.resolve()))
        cmd.append('--soft-gl')
    else:
        cmd=['node','render_canvas.mjs','--project='+str(project),'--out=out/director','--range=2:4','--times=2,2.75,3.5']
        module=a.canvas_module or os.environ.get('MV_CANVAS_MODULE')
        if module:cmd.append('--canvas-module='+module)
    result=subprocess.run(cmd,cwd=project,capture_output=True,text=True,encoding='utf-8')
    if result.returncode:raise RuntimeError(result.stderr)
    movie=project/'out/director/clip.mp4';report=D.load(movie.parent/'render-report.json')
    subprocess.run(['ffmpeg','-v','error','-i',str(movie),'-f','null','-'],check=True,capture_output=True)
    pcm=array('h',subprocess.check_output(['ffmpeg','-v','error','-i',str(movie),'-map','0:a:0','-ar','8000','-ac','1','-f','s16le','-']))
    if sys.byteorder!='little':pcm.byteswap()
    starts=[];active=False
    for i in range(0,len(pcm),160):
        block=pcm[i:i+160];loud=math.sqrt(sum(x*x for x in block)/max(1,len(block)))/32768>.03
        if loud and not active:starts.append(i/8000)
        active=loud
    if report['range']!=[2,4] or len(starts)!=2 or any(abs(x-y)>.06 for x,y in zip(starts,[.5,1.5])):raise ValueError('actual director source interval/audio differs: '+str(starts))
    stills=[]
    for t in [.25,1.25]:
        frame=out/('decoded-'+str(t)+'.png')
        subprocess.run(['ffmpeg','-v','error','-ss',str(t),'-i',str(movie),'-frames:v','1',str(frame)],check=True,capture_output=True)
        stills.append(hashlib.sha256(frame.read_bytes()).hexdigest())
    if stills[0]==stills[1]:raise ValueError('actual director video showed no frame change')
    proof={'status':'passed','engine':a.engine,'source_range':[2,4],'encoded_pulse_offsets':starts,'model_sha256':D.digest(package/'director.json'),'video_sha256':D.digest(movie),'runtime':report['runtime'],'encoded_full_decode':True,'decoded_frame_hashes':stills,'user_approvals_written':False,'scope':'Original synthetic director scene via selected actual host; not a user MV, natural acting, real singing or all-platform certification.'}
    D.write(out/'director-render-receipt.json',proof);print(json.dumps(proof))


if __name__=='__main__':main()


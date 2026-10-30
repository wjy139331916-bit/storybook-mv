"""Optional source binding for the director workbench; never authenticates consent."""
import copy
import hashlib
import json
from pathlib import Path
from input_contracts import sha,typed


def signature(model):
    value=copy.deepcopy(model)
    value.pop('fps',None)
    import math
    canvas=value.get('canvas',{});w,h=canvas.get('width',1),canvas.get('height',1);g=math.gcd(w,h);value['canvas']={'aspect':[w//g,h//g]}
    scene_ids={x['scene_id'] for x in value.get('shots',[])}
    value['scenes']=[x for x in value.get('scenes',[]) if x['id'] in scene_ids]
    asset_ids={l['asset_id'] for x in value['scenes'] for l in x.get('layers',[])}
    value['assets']=[x for x in value.get('assets',[]) if x['id'] in asset_ids]
    value.pop('notes',None);value.pop('revision',None);value.pop('review',None)
    for scene in value.get('scenes',[]):
        scene.pop('name',None)
        for layer in scene.get('layers',[]):
            for key in ('keys','pin_left','pin_right','easing'):layer.pop(key,None)
        scene.get('camera',{}).pop('keys',None)
        scene.get('camera',{}).pop('easing',None)
        # Contact observations/mechanics can be refined inside a bounded sample.
        scene.pop('contacts',None)
    for cue in value.get('cues',[]):
        for key in ('start','end','words','timing_status'):cue.pop(key,None)
    for asset in value.get('assets',[]):asset.pop('name',None)
    return hashlib.sha256(json.dumps(typed(value),ensure_ascii=False,separators=(',',':')).encode('utf-8')).hexdigest()


def local(root,name):
    path=(Path(root)/name).resolve()
    if not path.is_relative_to(Path(root).resolve()) or not path.is_file():raise ValueError('director source must be an existing project file')
    return path


def approved_model(brief,project,model):
    """A bound shown source plus existing workflow acceptance supplies design scope."""
    package=brief.get('workflow',{}).get('packages',{}).get('design') or {}
    path=local(project,package.get('path',''))
    if sha(path)!=package.get('sha256'):raise ValueError('director design package changed')
    data=json.loads(path.read_text(encoding='utf-8'))
    for item in data.get('artifacts',[]):
        if item.get('role')!='design_source':continue
        source=local(project,item.get('path',''))
        if sha(source)!=item.get('sha256'):raise ValueError('director design source changed after presentation')
        try:old=json.loads(source.read_text(encoding='utf-8'))
        except (ValueError,UnicodeError):continue
        if old.get('kind')=='mv-director' and signature(old)==signature(model):return
    raise ValueError('DIRECTOR_DESIGN_SOURCE: present this model with --source and actual design frames; the accepted asset/layout/shot design must match')


def check_active(project,brief):
    root=Path(project).resolve();record=root/'director-active.json'
    if not record.exists():return []
    try:
        data=json.loads(record.read_text(encoding='utf-8'))
        if data.get('schema_version')!=1:raise ValueError('unknown director activation')
        model_file=local(root,data['model']['path'])
        if sha(model_file)!=data['model']['sha256']:raise ValueError('active director model changed; export a new revision')
        model=json.loads(model_file.read_text(encoding='utf-8'))
        for source in data.get('scripts',[]):
            if sha(local(root,source['path']))!=source['sha256']:raise ValueError('active director drawing source changed; export a new revision')
        if brief.get('execution',{}).get('context')!='tool-self-test' and brief.get('phase')!='design':approved_model(brief,root,model)
        return []
    except (ValueError,KeyError,TypeError,OSError) as exc:return ['DIRECTOR_SOURCE: '+str(exc)]

"""Original synthetic approval/artifact fixtures. Never records real user consent."""
import json
from pathlib import Path
import shutil
from input_contracts import content_digest, sha
from workflow_gate import default_workflow, design_digest, target_duration, NEXT

ROOT = Path(__file__).resolve().parents[1]


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')
    return {'path': path.name, 'sha256': sha(path)}


def record(project, path, value=None, role=None):
    target = project/path
    if value is not None:
        save(target, value)
    result = {'path': path, 'sha256': sha(target)}
    if role:result['role'] = role
    return result


def approval(brief, project, stage):
    package = brief['workflow']['packages'][stage]
    data = json.loads((project/package['path']).read_text())
    value = {'origin':'user-message', 'message_id':'synthetic-'+stage+'-reply',
             'user_reply':'Synthetic fixture accepts the displayed '+stage+' package; not real consent',
             'presented_message_id':'synthetic-'+stage+'-presentation', 'stage':stage,
             'next_stage':NEXT[stage], 'decision':'approved', 'revision':data['revision'],
             'content_sha256':content_digest(brief), 'package_sha256':package['sha256']}
    brief['workflow']['approvals'][stage] = record(project, 'plan/'+stage+'-user.json', value)
    return value


def design(brief, project):
    project=Path(project);(project/'plan').mkdir(parents=True,exist_ok=True)
    brief['workflow'] = default_workflow()
    duration = target_duration(brief, project)
    proposal = project/'plan/proposal.md';proposal.write_text('Synthetic complete proposal: source shape, change, return. No real artistic acceptance.\n')
    image = project/'plan/design.png';shutil.copy2(ROOT/'assets/studies/evidence/style-board.png',image)
    script={'duration':duration,'duration_status':'agreed_scope','sections':[{'id':'a','start':0,'end':duration}],
            'shots':[{'id':'s01','start':0,'end':duration,'section_id':'a','objective':'synthetic source and return',
                      'visible_change':'shape changes and returns','visual':'one geometric shape in space',
                      'lyric_treatment':'none for this synthetic fixture', 'transition':{'type':'loop'},'assets':[]}]}
    spec={'design':{'medium':'Canvas','palette':['#fff','#222'],'shape_language':'geometry','composition':'center','motion':'time-based'},
          'cast':[{'id':'synthetic-cast'}] if brief['characters']['required'] else []}
    artifacts=[record(project,'plan/proposal.md',role='proposal'),record(project,'plan/script.json',script,'script'),
               record(project,'plan/visual-spec.json',spec,'visual_spec'),record(project,'plan/design.png',role='design_frame')]
    value={'stage':'design','revision':'synthetic-design-r1','content_sha256':content_digest(brief),
           'design_sha256':design_digest(brief),'target_duration':duration,'pilot':{'start':0,'end':min(duration,(brief.get('prototype') or {}).get('duration',8)),'objectives':'Synthetic interval checks source, transformation and settle'},'artifacts':artifacts}
    brief['workflow']['packages']['design']=record(project,'plan/design-package.json',value)
    approval(brief,project,'design')


def video_stage(brief, project, stage, clip, report):
    # Compatibility fixture metadata is explicit; production reports must be
    # written from the actual renderer/inspection, never inferred this way.
    report_data=json.loads((project/report).read_text())
    plan=json.loads((project/brief['workflow']['packages']['design']['path']).read_text())['pilot']
    report_data.setdefault('range',[plan['start'],plan['end']] if stage=='prototype' else [0,target_duration(brief,project)])
    if brief.get('music',{}).get('audio'):
        report_data.setdefault('audio',{'sha256':brief['music']['audio_sha256']})
    save(project/report,report_data)
    review={'scope':stage,'status':'observed_pass','reviewer':'synthetic review fixture',
            'target_sha256':sha(project/clip),'observations':'Synthetic fixture exercises recorded review checks; no real taste claim.'}
    artifacts=[record(project,clip,role='video'),record(project,report,role='render_report'),
               record(project,'plan/'+stage+'-review.json',review,'review')]
    value={'stage':stage,'revision':'synthetic-'+stage+'-r1','content_sha256':content_digest(brief),
           'design_sha256':design_digest(brief),'design_package_sha256':brief['workflow']['packages']['design']['sha256'],
           'target_duration':target_duration(brief,project), 'artifacts':artifacts}
    if stage=='animatic':
        value.update(fidelity='rough',prototype_package_sha256=brief['workflow']['packages']['prototype']['sha256'])
    brief['workflow']['packages'][stage]=record(project,'plan/'+stage+'-package.json',value)
    approval(brief,project,stage)

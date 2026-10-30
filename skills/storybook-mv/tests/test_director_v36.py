"""Shared director editing, source-bound stage safety and actual adapter regressions."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import director_workbench as D
from director_contract import signature,check_active,approved_model
from director_fixtures import make_project
from check_brief import entry_errors
from input_contracts import sha


class ModelTests(unittest.TestCase):
    def setUp(self):
        self.model=D.seed(example=True)
        self.tmp=tempfile.TemporaryDirectory(prefix='mv-director-model-');self.p=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def test_original_model_validates(self):self.assertEqual(D.validate(self.model),self.model)
    def test_unknown_asset_is_rejected(self):
        self.model['scenes'][0]['layers'][0]['asset_id']='missing'
        with self.assertRaisesRegex(ValueError,'引用'):D.validate(self.model)
    def test_incomplete_or_overlapping_shot_timeline_is_rejected(self):
        for start in [1.5,2.5]:
            m=copy.deepcopy(self.model);m['shots'][1]['start']=start
            with self.assertRaises(ValueError):D.validate(m)
    def test_unsafe_ids_and_properties_are_rejected(self):
        for payload in [lambda m:m['assets'][0].update(id='__proto__'),lambda m:m.update(__proto__={'motion':True})]:
            m=copy.deepcopy(self.model);payload(m)
            with self.assertRaises(ValueError):D.validate(m)
    def test_word_timing_must_stay_inside_cue_and_preserve_order(self):
        self.model['cues'][0]['words'][0]['start']=-1
        with self.assertRaisesRegex(ValueError,'词段'):D.validate(self.model)
    def test_transition_window_cannot_exceed_shot(self):
        self.model['shots'][0]['transition']['duration']=3
        with self.assertRaisesRegex(ValueError,'转场'):D.validate(self.model)
    def test_pixel_model_uses_existing_real_validator(self):
        from pixel_workbench import seed
        self.model['assets'].append({'id':'pixel','name':'original pixel','kind':'pixel','model':seed(),'unit':.3})
        D.validate(self.model)
        self.model['assets'][-1]['model']['layers'][0]['rows']=['??']
        with self.assertRaises(ValueError):D.validate(self.model)
    def test_signature_preserves_bounded_mechanics_but_detects_design_change(self):
        old=signature(self.model);m=copy.deepcopy(self.model);m['notes']=[{'id':'n','range':[0,.5],'severity':'minor','observation':'original observation'}]
        m['scenes'][0]['layers'][1]['keys'][0]['headTilt']=10;m['cues'][0]['start']=.3
        self.assertEqual(signature(m),old)
        m['assets'][0]['colors']['shirt']='#ff0000';self.assertNotEqual(signature(m),old)
    def test_fresh_selftest_is_static_and_contains_all_seven_controls(self):
        out=self.p/'design';caps,_=D.context(None,False,True);r=D.build_editor(out,self.model,caps,None,None)
        html=(out/'workbench.html').read_text(encoding='utf-8')
        self.assertFalse(r['motion']);self.assertEqual(len(r['modules']),7);self.assertIn('directorWorkbench',html)
        self.assertEqual(D.load(out/'workbench-report.json')['acceptance'],'not_reviewed')
    def test_html_escapes_user_text_and_has_no_external_dependency(self):
        self.model['assets'][2]['name']='</script><script>alert(1)</script>'
        out=self.p/'design';caps,_=D.context(None,False,True);D.build_editor(out,self.model,caps,None,None)
        html=(out/'workbench.html').read_text(encoding='utf-8')
        self.assertIn('\\u003c/script>',html);self.assertNotIn('</script><script>alert(1)',html);self.assertNotIn('<script src=',html)
    def test_selftest_build_cannot_relabel_arbitrary_project_model(self):
        p=self.p/'model.json';D.write(p,self.model);caps,_=D.context(None,True,True)
        with self.assertRaisesRegex(ValueError,'marker'):D.build_editor(self.p/'motion',self.model,caps,None,None,p)
    def test_new_revision_preserves_existing_work(self):
        out=self.p/'work';out.mkdir();(out/'keep').write_text('keep',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'preserved'):D.output_path(None,out)
        self.assertEqual(D.output_path(None,out,True).name,'work-r2');self.assertEqual((out/'keep').read_text(encoding='utf-8'),'keep')
    def test_embedding_budget_is_explicit(self):
        caps,_=D.context(None,False,True)
        with self.assertRaisesRegex(ValueError,'budget'):D.build_editor(self.p/'x',self.model,caps,None,None,max_mb=0)


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='mv-director-project-');self.p=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def workspace(self,phase='prototype',motion=True):
        project,model=make_project(self.p/'fixture',phase=phase)
        caps,brief=D.context(project,motion,False);out=project/'plan/workspace'
        D.build_editor(out,model,caps,brief,project,project/'director-current.json')
        return project,model,caps,out
    def package(self,project,model,caps,workspace):
        return D.export_package(project/'plan/director-r1',model,project,caps,workspace)
    def test_design_rejects_motion_before_writing_a_workspace(self):
        project,_=make_project(self.p/'fixture',phase='design',accepted=False)
        with self.assertRaisesRegex(ValueError,'DESIGN_STILLS_ONLY'):D.context(project,True,False)
        self.assertFalse((project/'plan/workspace').exists())
    def test_motion_range_is_accepted_global_pilot(self):
        project,model,caps,workspace=self.workspace()
        self.assertEqual(caps['range'],[2,4]);self.assertTrue(caps['motion'])
    def test_project_root_alias_is_normalized_without_weakening_containment(self):
        project,model=make_project(self.p/'fixture');alias=project/'src/..'
        self.assertEqual(D.project_file(alias,'brief.json'),(project/'brief.json').resolve())
        with self.assertRaisesRegex(ValueError,'existing project file'):D.project_file(alias,'../brief.json')
    def test_changed_asset_design_is_blocked_even_with_old_acceptance(self):
        project,model=make_project(self.p/'fixture')
        model['assets'][0]['colors']['shirt']='#ff0000'
        with self.assertRaisesRegex(ValueError,'DIRECTOR_DESIGN_SOURCE'):approved_model(D.load(project/'brief.json'),project,model)
    def test_workbench_cannot_create_user_consent(self):
        project,model,caps,workspace=self.workspace();before=(project/'brief.json').read_bytes()
        self.package(project,model,caps,workspace)
        self.assertEqual((project/'brief.json').read_bytes(),before)
        self.assertEqual(D.load(project/'plan/director-r1/package.json')['acceptance'],'not_reviewed')
    def test_application_rejects_stale_project_sources(self):
        project,model,caps,workspace=self.workspace();brief=D.load(project/'brief.json');brief['phase']='animatic';D.write(project/'brief.json',brief)
        with self.assertRaisesRegex(ValueError,'inputs changed'):D.check_workspace(project,workspace)
    def test_workspace_rejects_replaced_baseline_without_discarding_saved_edits(self):
        project,model,caps,workspace=self.workspace();edited=workspace/'director-edited.json';D.write(edited,model)
        altered=copy.deepcopy(model);altered['notes']=[{'id':'n','range':[2,3],'severity':'minor','observation':'saved observation'}];D.write(workspace/'director.json',altered)
        with self.assertRaisesRegex(ValueError,'baseline changed'):D.check_workspace(project,workspace)
        self.assertEqual(D.load(edited),model)
    def test_workspace_rejects_a_different_full_recording_duration(self):
        project,model=make_project(self.p/'fixture');caps,brief=D.context(project,False,False)
        model['duration']=7;model['shots'][-1]['end']=7
        with self.assertRaisesRegex(ValueError,'timeline differs'):D.build_editor(project/'plan/wrong',model,caps,brief,project)
        self.assertFalse((project/'plan/wrong').exists())
    def test_exported_package_contains_actual_data_for_all_modules(self):
        project,model,caps,workspace=self.workspace();self.package(project,model,caps,workspace)
        expected=['director.json','impact.json','lyrics-draft.json','shot-map-draft.json','performance-draft.json','repair-plan.json','package.json']
        self.assertTrue(all((project/'plan/director-r1'/n).is_file() for n in expected))
        self.assertEqual(D.load(project/'plan/director-r1/lyrics-draft.json')['timing_status'],'unverified')
    def test_activation_installs_actual_selected_canvas_entry_and_preserves_old_files(self):
        project,model,caps,workspace=self.workspace();old=(project/'studio.html').read_bytes();brief=(project/'brief.json').read_bytes();self.package(project,model,caps,workspace)
        result=D.activate(project,project/'plan/director-r1')
        self.assertEqual(result['engine'],'canvas2d');self.assertEqual((project/'brief.json').read_bytes(),brief)
        self.assertEqual((project/result['backup']/'studio.html').read_bytes(),old)
        self.assertTrue(D.load(project/'src/render-entry.json')['scripts']);self.assertEqual(check_active(project,D.load(project/'brief.json')),[])
    def test_active_source_tampering_is_rejected_by_shared_gate(self):
        project,model,caps,workspace=self.workspace();self.package(project,model,caps,workspace);D.activate(project,project/'plan/director-r1')
        file=project/'src/director/director-r1/director.json';file.write_text('{}',encoding='utf-8')
        errors=entry_errors(D.load(project/'brief.json'),project,'prototype',2,operation='video',timeline_range=[2,4])
        self.assertTrue(any('DIRECTOR_SOURCE' in e for e in errors),errors)
    def test_failed_partial_write_restores_original_entry_and_helpers(self):
        project,model,caps,workspace=self.workspace();self.package(project,model,caps,workspace)
        targets=[project/'studio.html',project/'src/render-entry.json',project/'check_brief.py']
        before={p:p.read_bytes() if p.exists() else None for p in targets};write=Path.write_bytes;failed=[]
        def interrupt(path,data):
            if path.resolve()==(project/'studio.html').resolve() and not failed:
                failed.append(True);write(path,b'partial write');raise OSError('synthetic interrupted write')
            return write(path,data)
        with patch.object(Path,'write_bytes',interrupt),self.assertRaisesRegex(OSError,'interrupted write'):D.activate(project,project/'plan/director-r1')
        self.assertEqual({p:p.read_bytes() if p.exists() else None for p in targets},before)
        self.assertFalse((project/'director-active.json').exists());self.assertFalse((project/'src/director/director-r1').exists())
        self.assertEqual(D.load(project/'plan/director-activation/director-r1/activation.json')['status'],'rolled_back')
    def test_other_host_is_not_silently_replaced(self):
        project,model,caps,workspace=self.workspace();self.package(project,model,caps,workspace)
        b=D.load(project/'brief.json');b['execution']['engine']='painted-p5';D.write(project/'brief.json',b)
        with self.assertRaises(ValueError):D.activate(project,project/'plan/director-r1')
        self.assertFalse((project/'director-active.json').exists())
    def test_cue_draft_cannot_silently_enable_forbidden_lyrics(self):
        project,model,caps,workspace=self.workspace();model['caption']['enabled']=True;self.package(project,model,caps,workspace)
        with self.assertRaises(ValueError):D.activate(project,project/'plan/director-r1')
        self.assertFalse((project/'director-active.json').exists())
    def test_remotion_adapter_preserves_main_host_and_binds_canvas_source(self):
        project,model=make_project(self.p/'fixture',engine='remotion');caps,brief=D.context(project,True,False);workspace=project/'plan/workspace'
        D.build_editor(workspace,model,caps,brief,project,project/'director-current.json');self.package(project,model,caps,workspace)
        old=(project/'src/index.jsx').read_bytes();result=D.activate(project,project/'plan/director-r1')
        self.assertEqual(result['engine'],'remotion');self.assertIn('useLayoutEffect',(project/'src/index.jsx').read_text(encoding='utf-8'))
        self.assertEqual((project/result['backup']/'src/index.jsx').read_bytes(),old);self.assertEqual(check_active(project,D.load(project/'brief.json')),[])


@unittest.skipUnless(os.environ.get('MV_CANVAS_MODULE'),'selected native Canvas needed')
class GeometryTests(unittest.TestCase):
    def test_rough_drawing_retains_motion_geometry_and_changes_actual_pixels(self):
        js="require(process.argv[1]);const C=require(process.argv[2]),{createCanvas}=require(process.argv[3]),hash=x=>require('crypto').createHash('sha256').update(x).digest('hex');let s='';process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>{const d=JSON.parse(s),c=createCanvas(960,540),x=c.getContext('2d'),a=C.render(x,d,.8),full=hash(c.toBuffer('image/png')),b=C.render(x,d,.8,{rough:true});console.log(JSON.stringify({full,rough:hash(c.toBuffer('image/png')),a:a.positions.lead.hand,b:b.positions.lead.hand}))});"
        r=subprocess.run(['node','-e',js,str(ROOT/'assets/pixel-workbench/core.js'),str(ROOT/'assets/director-workbench/core.js'),os.environ['MV_CANVAS_MODULE']],input=json.dumps(D.seed(example=True)),text=True,capture_output=True,encoding='utf-8')
        self.assertEqual(r.returncode,0,r.stderr);v=json.loads(r.stdout);self.assertEqual(v['a'],v['b']);self.assertNotEqual(v['full'],v['rough'])
    def test_actual_drawing_proves_pinned_foot_and_contact_gap(self):
        data=D.seed(example=True);scene=data['scenes'][0];lead=scene['layers'][1];lead['keys']=[{'time':0,'x':.3},{'time':1,'x':.325}];scene['contacts'][0].update(start=0,end=2)
        js="require(process.argv[1]);const C=require(process.argv[2]),{createCanvas}=require(process.argv[3]);let s='';process.stdin.on('data',x=>s+=x);process.stdin.on('end',()=>{const d=JSON.parse(s),c=createCanvas(960,540),x=c.getContext('2d');const a=C.render(x,d,0),b=C.render(x,d,1);console.log(JSON.stringify({a:a.positions.lead.left,b:b.positions.lead.left,gap:b.contacts[0].distance,bytes:c.toBuffer('image/png').length}))});"
        r=subprocess.run(['node','-e',js,str(ROOT/'assets/pixel-workbench/core.js'),str(ROOT/'assets/director-workbench/core.js'),os.environ['MV_CANVAS_MODULE']],input=json.dumps(data),text=True,capture_output=True,encoding='utf-8')
        self.assertEqual(r.returncode,0,r.stderr);v=json.loads(r.stdout);self.assertAlmostEqual(v['a'][0],v['b'][0],places=4);self.assertAlmostEqual(v['a'][1],v['b'][1],places=4);self.assertGreater(v['gap'],0);self.assertGreater(v['bytes'],1000)


if __name__=='__main__':unittest.main()

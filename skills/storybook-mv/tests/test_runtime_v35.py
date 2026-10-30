"""Destination recovery, selected backends and asset helpers; no real user approvals."""
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
import runtime_environment as E
import runtime_probe as R
import project_contracts as C
from pixel_font import export_atlas
from test_content_gate import agreed_fixture,bind_confirmation


class DestinationTests(unittest.TestCase):
    def setUp(self):self.folder=tempfile.TemporaryDirectory(prefix='mv-v35-');self.p=Path(self.folder.name)
    def tearDown(self):self.folder.cleanup()
    def command(self,*args):return subprocess.run([sys.executable,str(ROOT/'scripts/runtime_smoke.py'),*map(str,args)],capture_output=True,text=True,encoding='utf-8')

    def test_fresh_browser_missing_dependencies_is_actionable_and_retryable(self):
        target=self.p/'probe'
        for extra in ([],['--retry']):
            r=self.command(target,'--runtime','browser',*extra)
            self.assertNotEqual(r.returncode,0);self.assertIn('prerequisites incomplete',r.stderr);self.assertIn('puppeteer-core',r.stderr);self.assertIn('--install',r.stderr)
            self.assertNotIn('destination is not empty',r.stderr)

    def test_retry_preserves_an_unrecognized_directory(self):
        target=self.p/'mine';target.mkdir();(target/'keep.txt').write_text('important')
        r=self.command(target,'--runtime','browser','--retry')
        self.assertNotEqual(r.returncode,0);self.assertEqual((target/'keep.txt').read_text(),'important')

    def test_retry_rejects_changed_source(self):
        target=self.p/'probe';R.prepare(target,'canvas2d','browser',False,None,False)
        (target/'src/scene.js').write_text('changed source')
        with self.assertRaisesRegex(ValueError,'source/options changed'):R.prepare(target,'canvas2d','browser',False,None,True)

    def test_new_revision_does_not_reuse_old_failed_project(self):
        target=self.p/'probe';target.mkdir();(target/'keep').write_text('keep')
        r=self.command(target,'--runtime','browser','--new-revision')
        self.assertNotEqual(r.returncode,0);self.assertTrue((self.p/'probe-r2/RUNTIME_SELF_TEST.json').exists());self.assertEqual((target/'keep').read_text(),'keep')

    def test_destination_facts_include_platform_arch_and_selected_python_versions(self):
        d=E.platform_facts();self.assertTrue(d['arch']);self.assertTrue(d['platform']);self.assertEqual(d['python']['interpreter'],sys.executable);self.assertTrue(d['python']['version']);self.assertIn('version',d['python']['packages']['PIL'])

    def test_broken_explicit_bridge_interpreter_is_reported_not_silently_replaced(self):
        with patch.dict(os.environ,{'MV_PYTHON':str(self.p/'absent-python')}):d=E.python_diagnostics(('PIL',))
        self.assertIsNone(d['bridge']);self.assertIn('MV_PYTHON',d['suggestion']);self.assertNotEqual(d['suggestion'],d['bridge_command'])

    def test_chinese_probe_requires_a_real_explicit_font(self):
        r=self.command(self.p/'probe','--runtime','node-canvas','--cjk')
        self.assertNotEqual(r.returncode,0);self.assertIn('explicit local --font',r.stderr);self.assertFalse((self.p/'probe').exists())

    def test_wrong_engine_cannot_claim_native_canvas_success(self):
        r=self.command(self.p/'probe','--runtime','node-canvas','--engine','painted-p5')
        self.assertNotEqual(r.returncode,0);self.assertIn('actual browser backend',r.stderr)


class RemotionTests(unittest.TestCase):
    def setUp(self):self.folder=tempfile.TemporaryDirectory(prefix='mv-remotion-gate-');self.p=Path(self.folder.name)
    def tearDown(self):self.folder.cleanup()

    def scaffold(self,phase='design',accepted=False):
        b=agreed_fixture();b['execution']['engine']='remotion';b['phase']=phase;bind_confirmation(b,self.p)
        if not accepted:b['workflow']['approvals'].clear();b['workflow']['packages'].clear()
        f=self.p/'brief.json';f.write_text(json.dumps(b));project=self.p/'project'
        r=subprocess.run([sys.executable,str(ROOT/'scripts/scaffold.py'),str(project),'--brief',str(f),'--engine','remotion','--duration','2'],capture_output=True,text=True)
        return r,project

    def test_remotion_is_explicitly_bundled_and_uses_exact_dependency_versions(self):
        registry=json.loads((ROOT/'assets/engines.json').read_text());self.assertEqual(registry['remotion']['status'],'bundled')
        deps=json.loads((ROOT/'assets/remotion-template/package.json').read_text())['dependencies'];self.assertTrue(all(not v.startswith(('^','~')) for v in deps.values()));self.assertEqual(len({v for k,v in deps.items() if k=='remotion' or k.startswith('@remotion/')}),1)

    def test_confirmed_direction_can_scaffold_remotion_static_workspace(self):
        r,p=self.scaffold();self.assertEqual(r.returncode,0,r.stderr);self.assertTrue((p/'src/index.jsx').exists());self.assertEqual(json.loads((p/'src/project.json').read_text())['duration'],2)

    def test_design_video_is_blocked_before_loading_missing_remotion_packages(self):
        r,p=self.scaffold();self.assertEqual(r.returncode,0,r.stderr)
        r=subprocess.run(['node','render.mjs','--clip'],cwd=p,capture_output=True,text=True)
        self.assertNotEqual(r.returncode,0);self.assertIn('DESIGN_STILLS_ONLY',r.stderr);self.assertNotIn('dependencies are missing',r.stderr);self.assertFalse((p/'out/remotion').exists())

    def test_unaccepted_design_cannot_scaffold_remotion_prototype(self):
        r,p=self.scaffold('prototype');self.assertNotEqual(r.returncode,0);self.assertIn('DESIGN_USER_APPROVAL_REQUIRED',r.stderr);self.assertFalse(p.exists())

    def test_accepted_stage_has_actionable_dependency_error(self):
        r,p=self.scaffold('prototype',True);self.assertEqual(r.returncode,0,r.stderr)
        r=subprocess.run(['node','render.mjs','--clip'],cwd=p,capture_output=True,text=True)
        self.assertNotEqual(r.returncode,0);self.assertIn('Remotion dependencies are missing',r.stderr);self.assertIn('npm ci',r.stderr)

    def test_actual_nonzero_fixture_passes_shared_gate_before_browser_loading(self):
        from remotion_smoke import prepare_project
        from check_brief import entry_errors
        project,audio=prepare_project(self.p/'nonzero')
        brief=json.loads((project/'brief.json').read_text(encoding='utf-8'))
        self.assertEqual(brief['prototype']['duration'],2)
        errors=entry_errors(brief,project,'prototype',2,resolution=[640,360],fps=30,timeline_duration=4,operation='video',timeline_range=[2,4])
        self.assertEqual(errors,[])
        outside=entry_errors(brief,project,'prototype',2,resolution=[640,360],fps=30,timeline_duration=4,operation='video',timeline_range=[0,2])
        self.assertTrue(any('pilot' in e for e in outside),outside)


class AssetTests(unittest.TestCase):
    def setUp(self):self.folder=tempfile.TemporaryDirectory(prefix='mv-asset-v35-');self.p=Path(self.folder.name)
    def tearDown(self):self.folder.cleanup()

    def test_bitmap_atlas_is_source_bound_and_has_actual_nonempty_glyphs(self):
        from PIL import Image
        font=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
        if not font.is_file():self.skipTest('destination has no selected Latin font')
        doc=self.p/'text.json';doc.write_text(json.dumps({'lines':[{'id':'a','text':'DAY 412'}]}));target=self.p/'atlas';r=export_atlas(font,doc,16,target)
        self.assertTrue({'D','A','Y','4','1','2'}<=r['glyphs'].keys());self.assertEqual(r['font_sha256'],C.digest(font));self.assertEqual(r['acceptance'],'not_reviewed')
        image=Image.open(target/'glyphs.png');self.assertTrue(image.getbbox());self.assertEqual(set(image.getchannel('A').getdata()),{0,255})

    def test_performance_plan_requires_specific_mechanisms_and_real_shot_intervals(self):
        plan={'schema_version':1,'revision':'original-test','shots':[{'shot_id':'s','actor_id':'a','start':0,'end':2,'intent':'noticing a light','gaze_target':'light at screen right','head_orientation':'turn right then settle','support_and_weight':'left foot remains planted','contact_and_release':'hands remain free; inspect no object contact','breathing_or_intentional_hold':'still hold after the turn','key_poses':[{'time':0,'description':'look down'},{'time':1,'description':'look right'}]}]}
        file=self.p/'acting.json';file.write_text(json.dumps(plan));spec={'cast':[{'id':'a'}],'performance_plan':{'path':'acting.json','sha256':C.digest(file)}};shots={'s':{'start':0,'end':2}}
        errors=[];C.performance_plan(self.p,spec,shots,errors);self.assertEqual(errors,[])
        plan['shots'][0]['gaze_target']='';file.write_text(json.dumps(plan));spec['performance_plan']['sha256']=C.digest(file);errors=[];C.performance_plan(self.p,spec,shots,errors);self.assertTrue(any('gaze_target' in e for e in errors))

    def test_changed_acting_plan_is_not_accepted_under_old_hash(self):
        f=self.p/'plan.json';f.write_text('{}');s={'performance_plan':{'path':'plan.json','sha256':'0'*64}};errors=[];C.performance_plan(self.p,s,{},errors);self.assertIn('performance plan missing or changed',errors)

    @unittest.skipUnless(os.environ.get('MV_CANVAS_MODULE'),'selected native canvas needed for original UI drawing')
    def test_narrative_cards_draw_real_pixels_and_report_text_boxes(self):
        module=os.environ['MV_CANVAS_MODULE'];file=ROOT/'assets/modules/narrative-ui.js'
        code="const {createCanvas}=require(process.argv[1]);const u=require(process.argv[2]);const c=createCanvas(640,360),x=c.getContext('2d');const a=u.rows(x,{x:5,y:5,w:310,h:210,title:'Calls',items:[{label:'Original caller',time:'08:40',status:'missed'}]});u.stamp(x,{x:330,y:5,label:'TIME',value:'DAY 412'});u.route(x,{x:330,y:110,w:270,h:220,points:[[0,0],[.5,.5],[1,1]],labels:['A','B','C']});console.log(JSON.stringify({bytes:c.toBuffer('image/png').length,boxes:a.length}));"
        r=subprocess.run(['node','-e',code,module,str(file)],capture_output=True,text=True);self.assertEqual(r.returncode,0,r.stderr);result=json.loads(r.stdout);self.assertGreater(result['bytes'],2000);self.assertGreater(result['boxes'],1)


if __name__=='__main__':unittest.main()

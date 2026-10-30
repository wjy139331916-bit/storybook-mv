"""Actual media/record regressions; synthetic replies assert no real user consent."""
import argparse
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
from input_contracts import sha
from workflow_gate import workflow_errors
from workflow_fixtures import approval, record, video_stage
from test_content_gate import agreed_fixture, bind_confirmation
import test_contracts as fixtures
import project_contracts as contracts
import review_workspace as workspace


class MediaBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.media=Path(tempfile.mkdtemp(prefix='mv-v34-media-'))
        for name,size in [('wide','320x180'),('square','180x180')]:
            subprocess.run(['ffmpeg','-y','-v','error','-i',str(ROOT/'assets/studies/evidence/runtime.mp4'),'-t','2','-vf','scale='+size,'-r','12','-an',str(cls.media/(name+'.mp4'))],check=True)

    @classmethod
    def tearDownClass(cls):shutil.rmtree(cls.media)

    def setUp(self):
        self.folder=tempfile.TemporaryDirectory(prefix='mv-v34-boundary-');self.p=Path(self.folder.name)
        self.b=agreed_fixture();self.b['execution'].update(authorized_scope='full',authorized_duration=6)
        bind_confirmation(self.b,self.p);(self.p/'out').mkdir()

    def tearDown(self):self.folder.cleanup()

    def sample(self,name='wide'):
        shutil.copy2(self.media/(name+'.mp4'),self.p/'out/pilot.mp4')
        record(self.p,'out/report.json',{'production_stage':'prototype','encoded':{'full_decode':True},'artifacts':[{'sha256':sha(self.p/'out/pilot.mp4')}]})
        video_stage(self.b,self.p,'prototype','out/pilot.mp4','out/report.json')

    def pilot(self,start,end):
        pkg=self.b['workflow']['packages']['design'];f=self.p/pkg['path'];d=json.loads(f.read_text(encoding='utf-8'));d['pilot'].update(start=start,end=end)
        f.write_text(json.dumps(d), encoding='utf-8');pkg['sha256']=sha(f);approval(self.b,self.p,'design')

    def edit_report(self,fn):
        p=self.p/'out/report.json';d=json.loads(p.read_text(encoding='utf-8'));fn(d);p.write_text(json.dumps(d), encoding='utf-8')
        pkg=self.b['workflow']['packages']['prototype'];f=self.p/pkg['path'];d=json.loads(f.read_text(encoding='utf-8'))
        next(x for x in d['artifacts'] if x['role']=='render_report')['sha256']=sha(p)
        f.write_text(json.dumps(d), encoding='utf-8');pkg['sha256']=sha(f);approval(self.b,self.p,'prototype')

    def test_two_second_video_cannot_accept_six_second_pilot(self):
        self.sample();errors=workflow_errors(self.b,self.p,'animatic')
        self.assertTrue(any('complete accepted pilot' in e for e in errors),errors)

    def test_actual_nonzero_two_second_pilot_report_is_valid(self):
        self.pilot(2,4);self.sample();self.assertEqual(workflow_errors(self.b,self.p,'animatic'),[])

    def test_same_duration_wrong_source_interval_is_rejected(self):
        self.pilot(2,4);self.sample();self.edit_report(lambda d:d.update(range=[0,2]))
        self.assertTrue(any('source timeline' in e for e in workflow_errors(self.b,self.p,'animatic')))

    def test_missing_source_interval_cannot_be_guessed_from_duration(self):
        self.pilot(2,4);self.sample();self.edit_report(lambda d:d.pop('range'))
        self.assertTrue(any('source timeline' in e for e in workflow_errors(self.b,self.p,'animatic')))

    def test_actual_sample_aspect_is_checked(self):
        self.pilot(0,2);self.sample('square')
        self.assertTrue(any('aspect ratio' in e for e in workflow_errors(self.b,self.p,'animatic')))

    def test_video_inspection_rejects_false_interval(self):
        self.sample()
        with self.assertRaisesRegex(ValueError,'actual video duration'):
            workspace.inspect_video(self.p,self.b,'out/pilot.mp4','prototype',[0,6],self.p/'out/new-report.json')

    def test_video_inspection_decodes_and_retains_real_range(self):
        self.sample();r=workspace.inspect_video(self.p,self.b,'out/pilot.mp4','prototype',[2,4],self.p/'out/new-report.json')
        self.assertEqual(r['range'],[2,4]);self.assertTrue(r['encoded']['full_decode'])

    def test_preview_preserves_master_and_identifies_its_source(self):
        self.sample();master=sha(self.p/'out/pilot.mp4')
        r=workspace.create_preview(self.p,'out/pilot.mp4',self.p/'out/preview.webm')
        self.assertEqual(master,sha(self.p/'out/pilot.mp4'));self.assertEqual(r['source_sha256'],master)
        self.assertEqual(r['role'],'video_preview');self.assertTrue((self.p/r['path']).is_file())

    def test_wrong_soundtrack_record_cannot_accept_sample(self):
        subprocess.run(['ffmpeg','-y','-v','error','-f','lavfi','-i','sine=frequency=440:duration=6',str(self.p/'audio.wav')],check=True)
        self.b['music'].update(source='provided',kind='instrumental',audio='audio.wav',audio_sha256=sha(self.p/'audio.wav'))
        bind_confirmation(self.b,self.p);self.pilot(0,2)
        subprocess.run(['ffmpeg','-y','-v','error','-i',str(self.media/'wide.mp4'),'-i',str(self.p/'audio.wav'),'-t','2','-c:v','copy','-c:a','aac',str(self.p/'out/pilot.mp4')],check=True)
        record(self.p,'out/report.json',{'production_stage':'prototype','encoded':{'full_decode':True},'artifacts':[{'sha256':sha(self.p/'out/pilot.mp4')}]})
        video_stage(self.b,self.p,'prototype','out/pilot.mp4','out/report.json')
        self.assertEqual(workflow_errors(self.b,self.p,'animatic'),[])
        self.edit_report(lambda d:d.update(audio={'sha256':'0'*64}))
        self.assertTrue(any('selected soundtrack' in e for e in workflow_errors(self.b,self.p,'animatic')))


class TemporalReviewTests(unittest.TestCase):
    def setUp(self):self.tool=fixtures.ToolkitTests();self.tool.setUp();self.p=self.tool.fixture()
    def tearDown(self):self.tool.tearDown()
    def edit(self,name,fn):
        p=self.p/name;v=json.loads(p.read_text(encoding='utf-8'));fn(v);p.write_text(json.dumps(v), encoding='utf-8')
    def refresh(self):self.edit('review.json',lambda d:d['target'].update(input_digest=contracts.fingerprint(self.p)))

    def test_project_alias_is_canonicalized_without_weakening_boundary(self):
        alias=self.p/'..'/self.p.name
        self.assertEqual(contracts.contained(alias,'out/reference.png'),(self.p/'out/reference.png').resolve())
        with self.assertRaises(ValueError):contracts.contained(alias,'../outside.png')

    def test_explicit_contact_check_cannot_be_not_applicable(self):
        self.edit('visual-spec.json',lambda d:d['required_checks'].append('contact'))
        self.edit('review.json',lambda d:d['checks'].append({'id':'contact','status':'not_applicable','notes':'synthetic bypass attempt','evidence':[]}));self.refresh()
        self.assertTrue(any('not_applicable: contact' in e for e in contracts.inspect(self.p,'prototype')['errors']))

    def test_a_purposeful_hold_is_reviewed_not_exempted(self):
        self.edit('review.json',lambda d:next(c for c in d['checks'] if c['id']=='motion').update(status='not_applicable'))
        self.assertTrue(any('not_applicable: motion' in e for e in contracts.inspect(self.p,'prototype')['errors']))

    def test_a_single_still_cannot_prove_motion(self):
        self.edit('review.json',lambda d:next(c for c in d['checks'] if c['id']=='motion').update(evidence=['out/reference.png']))
        self.assertTrue(any('temporal review needs playable' in e for e in contracts.inspect(self.p,'prototype')['errors']))

    def test_motion_needs_an_inspected_time_range(self):
        self.edit('review.json',lambda d:next(c for c in d['checks'] if c['id']=='motion').pop('range'))
        self.assertTrue(any('output-time range' in e for e in contracts.inspect(self.p,'prototype')['errors']))

    def test_inspected_range_must_fit_the_actual_video(self):
        self.edit('review.json',lambda d:next(c for c in d['checks'] if c['id']=='motion').update(range=[0,999]))
        self.assertTrue(any('output-time range' in e for e in contracts.inspect(self.p,'prototype')['errors']))

    def test_source_bound_strip_can_support_motion(self):
        self.edit('review.json',lambda d:d.update(sequences=[{'path':'out/reference.png','sha256':sha(self.p/'out/reference.png'),'source_sha256':d['target']['sha256'],'times':[0,.1,.2]}]))
        self.edit('review.json',lambda d:next(c for c in d['checks'] if c['id']=='motion').update(evidence=['out/reference.png']))
        self.assertTrue(contracts.inspect(self.p,'prototype')['ok'])

    def test_a_strip_from_another_video_is_rejected(self):
        self.edit('review.json',lambda d:d.update(sequences=[{'path':'out/reference.png','sha256':sha(self.p/'out/reference.png'),'source_sha256':'0'*64,'times':[0,.1,.2]}]))
        self.edit('review.json',lambda d:next(c for c in d['checks'] if c['id']=='motion').update(evidence=['out/reference.png']))
        self.assertTrue(any('source-bound consecutive' in e for e in contracts.inspect(self.p,'prototype')['errors']))


class ReviewWorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.folder=tempfile.TemporaryDirectory(prefix='mv-v34-workspace-');self.p=Path(self.folder.name)
        self.b=agreed_fixture();bind_confirmation(self.b,self.p)
        self.b['workflow']['packages'].clear();self.b['workflow']['approvals'].clear();self.b['phase']='design'
        self.save();self.args=argparse.Namespace(stage='design',revision='design-r1',proposal='plan/proposal.md',script='plan/script.json',visual_spec='plan/visual-spec.json',frame=['plan/design.png'],pilot_range='0:6',objective='Original geometric transformation',limit=['Synthetic validation, no real taste acceptance'],max_embed_mb=64,webm_preview=False)
    def tearDown(self):self.folder.cleanup()
    def save(self):workspace.write_json(self.p/'brief.json',self.b)
    def present(self):
        result=workspace.present(self.p,self.b,self.args);self.b=json.loads((self.p/'brief.json').read_text(encoding='utf-8'));return result
    def acceptance(self,**updates):
        (self.p/'reply.txt').write_text('Synthetic test reply accepts this complete shown revision; not real consent.', encoding='utf-8')
        v=dict(stage='design',reply_file=str(self.p/'reply.txt'),message_id='synthetic-new-design-reply',presented_message_id='synthetic-presentation',decision='approved',waiver_review=None,advance=True);v.update(updates)
        return argparse.Namespace(**v)

    def test_present_builds_self_contained_page_and_does_not_approve(self):
        r=self.present();page=(self.p/r['page']).read_text(encoding='utf-8');b=json.loads((self.p/'brief.json').read_text(encoding='utf-8'))
        self.assertIn('data:image/png;base64,',page);self.assertIn('完整分镜脚本',page)
        self.assertEqual(b['phase'],'design');self.assertEqual(b['workflow']['approvals'],{})
        self.assertNotIn('https://',page);self.assertTrue((self.p/'plan/STATUS.md').is_file())

    def test_present_preserves_prior_revision(self):
        self.present();before=(self.p/'brief.json').read_bytes()
        with self.assertRaisesRegex(ValueError,'already exists'):workspace.present(self.p,self.b,self.args)
        self.assertEqual(before,(self.p/'brief.json').read_bytes())

    def test_present_binds_exact_editable_design_source_without_approval(self):
        source=self.p/'plan/director.json';source.write_text('{"kind":"mv-director","revision":"original-draft"}',encoding='utf-8');self.args.source=['plan/director.json']
        result=self.present();package=workspace.read_json(self.p/result['package']['path'])
        bound=next(x for x in package['artifacts'] if x['role']=='design_source')
        self.assertEqual(bound['path'],'plan/director.json');self.assertEqual(bound['sha256'],sha(source))
        self.assertEqual(self.b['workflow']['approvals'],{})

    def test_text_is_escaped_in_review_page(self):
        (self.p/'plan/proposal.md').write_text('<script>BAD()</script>', encoding='utf-8')
        r=self.present();page=(self.p/r['page']).read_text(encoding='utf-8');self.assertIn('&lt;script&gt;BAD()',page);self.assertNotIn('<script>BAD()',page)

    def test_status_derives_the_next_allowed_stage(self):
        self.present();s=workspace.status(self.p);self.assertEqual(s['user_authorized_stage'],'design')
        s=workspace.accept(self.p,self.b,self.acceptance());self.assertEqual(s['user_authorized_stage'],'prototype')
        self.assertEqual(s['phase'],'prototype');self.assertFalse(s['stages'][1]['accepted']);self.assertFalse(s['stages'][2]['accepted'])

    def test_an_empty_user_reply_does_not_change_the_brief(self):
        self.present();a=self.acceptance();(self.p/'reply.txt').write_text('', encoding='utf-8');before=(self.p/'brief.json').read_bytes()
        with self.assertRaises(ValueError):workspace.accept(self.p,self.b,a)
        self.assertEqual(before,(self.p/'brief.json').read_bytes())

    def test_old_intake_reply_cannot_approve_new_artifacts(self):
        self.present();before=(self.p/'brief.json').read_bytes()
        with self.assertRaisesRegex(ValueError,'earlier reply'):workspace.accept(self.p,self.b,self.acceptance(message_id='synthetic-fixture-message'))
        self.assertEqual(before,(self.p/'brief.json').read_bytes())

    def test_handoff_keeps_limits_and_is_not_acceptance(self):
        self.present();s=workspace.save_status(self.p)
        self.assertIn(self.args.limit[0],(self.p/'plan/STATUS.md').read_text(encoding='utf-8'));self.assertFalse(s['stages'][0]['accepted'])

    def test_changed_presented_frame_invalidates_old_acceptance(self):
        self.present();workspace.accept(self.p,self.b,self.acceptance())
        (self.p/'plan/design.png').write_bytes(b'changed')
        self.assertEqual(workspace.status(self.p)['user_authorized_stage'],'design')

    def test_embedding_budget_failure_preserves_brief(self):
        self.args.max_embed_mb=0;before=(self.p/'brief.json').read_bytes()
        with self.assertRaisesRegex(ValueError,'byte budget'):workspace.present(self.p,self.b,self.args)
        self.assertEqual(before,(self.p/'brief.json').read_bytes());self.assertFalse((self.p/'plan/reviews/design/design-r1').exists())

    def test_status_cli_handles_legacy_pipe_encoding(self):
        import os
        self.present();env={**os.environ,'PYTHONIOENCODING':'cp1252','PYTHONUTF8':'0'}
        result=subprocess.run([sys.executable,'-X','utf8=0',str(ROOT/'scripts/review_workspace.py'),'--project',str(self.p),'status'],capture_output=True,encoding='utf-8',env=env)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout)['stages'][0]['label'],'设计与完整脚本')

    def test_javascript_bridge_preserves_unicode_under_legacy_encoding(self):
        import os
        from input_contracts import content_digest
        self.b['content']['subject']='原创圆环 Ω 与中文'
        code="const fs=require('fs');const{pathToFileURL}=require('url');(async()=>{const m=await import(pathToFileURL(process.argv[1]).href);console.log(JSON.stringify(m.contentDigest(JSON.parse(fs.readFileSync(0,'utf8')))));})();"
        result=subprocess.run(['node','-e',code,str(ROOT/'scripts/production_gate.mjs')],input=json.dumps(self.b,ensure_ascii=False),capture_output=True,encoding='utf-8',env={**os.environ,'PYTHONIOENCODING':'cp1252','PYTHONUTF8':'0'})
        self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(json.loads(result.stdout),content_digest(self.b))


if __name__=='__main__':unittest.main()

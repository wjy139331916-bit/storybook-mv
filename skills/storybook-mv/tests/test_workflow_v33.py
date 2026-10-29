"""Stage bypass regressions use synthetic messages, never real user acceptance."""
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
from check_brief import entry_errors
from input_contracts import sha
from workflow_gate import workflow_errors, design_digest
from test_content_gate import agreed_fixture, bind_confirmation
from workflow_fixtures import record, video_stage, approval


class WorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shared=Path(tempfile.mkdtemp(prefix='mv-workflow-media-'))
        cls.clip=cls.shared/'rough.mp4'
        subprocess.run(['ffmpeg','-y','-v','error','-i',str(ROOT/'assets/studies/evidence/runtime.mp4'),'-t','2','-vf','scale=320:180','-r','12','-an',str(cls.clip)],check=True)

    @classmethod
    def tearDownClass(cls):shutil.rmtree(cls.shared)

    def setUp(self):
        self.temp=Path(tempfile.mkdtemp(prefix='mv-workflow-v33-'))
        self.brief=agreed_fixture();self.brief['execution'].update(authorized_scope='full',authorized_duration=2)
        bind_confirmation(self.brief,self.temp)

    def tearDown(self):shutil.rmtree(self.temp)

    def edit(self, record, change):
        p=self.temp/record['path'];d=json.loads(p.read_text());change(d);p.write_text(json.dumps(d));record['sha256']=sha(p)

    def stage(self, stage, accept=True):
        out=self.temp/'out';out.mkdir(exist_ok=True)
        clip='out/'+stage+'.mp4';shutil.copy2(self.clip,self.temp/clip)
        report='out/'+stage+'-render.json'
        record(self.temp,report,{'production_stage':stage,'encoded':{'full_decode':True},'artifacts':[{'path':clip,'sha256':sha(self.temp/clip)}]})
        video_stage(self.brief,self.temp,stage,clip,report)
        if not accept:self.brief['workflow']['approvals'].pop(stage)

    def test_direction_only_can_enter_design_but_not_prototype(self):
        self.brief['workflow']['packages'].clear();self.brief['workflow']['approvals'].clear();self.brief['phase']='design'
        self.assertEqual(entry_errors(self.brief,self.temp,operation='stills',still_count=3),[])
        self.brief['phase']='prototype'
        self.assertTrue(any('DESIGN_USER_APPROVAL_REQUIRED' in x for x in entry_errors(self.brief,self.temp)))

    def test_whole_song_request_does_not_skip_design(self):
        self.brief['workflow']['approvals'].clear()
        self.assertTrue(workflow_errors(self.brief,self.temp,'prototype'))

    def test_design_cannot_export_video_or_frame_sequence(self):
        self.brief['phase']='design'
        for operation in ('video','frames','encode',None):
            self.assertTrue(any('DESIGN_STILLS_ONLY' in x for x in entry_errors(self.brief,self.temp,operation=operation)))

    def test_design_has_a_bounded_static_preview(self):
        self.brief['phase']='design'
        self.assertTrue(entry_errors(self.brief,self.temp,operation='stills',still_count=13))
        self.assertEqual(entry_errors(self.brief,self.temp,operation='stills',still_count=2),[])

    def test_source_code_is_not_a_design_frame(self):
        pkg=self.brief['workflow']['packages']['design'];data=json.loads((self.temp/pkg['path']).read_text())
        (self.temp/'plan/design.png').write_text('source code masquerading as art')
        self.edit(pkg,lambda d:next(x for x in d['artifacts'] if x['role']=='design_frame').update(sha256=sha(self.temp/'plan/design.png')))
        approval(self.brief,self.temp,'design')
        self.assertTrue(workflow_errors(self.brief,self.temp,'prototype'))

    def test_no_full_script_cannot_start_sample(self):
        pkg=self.brief['workflow']['packages']['design']
        self.edit(pkg,lambda d:d.update(artifacts=[x for x in d['artifacts'] if x['role']!='script']))
        approval(self.brief,self.temp,'design')
        self.assertTrue(any('script' in x for x in workflow_errors(self.brief,self.temp,'prototype')))

    def test_script_must_cover_complete_scope(self):
        pkg=self.brief['workflow']['packages']['design'];p=self.temp/'plan/script.json'
        d=json.loads(p.read_text());d['duration']=1;d['sections'][0]['end']=1;d['shots'][0]['end']=1;p.write_text(json.dumps(d))
        self.edit(pkg,lambda d:next(x for x in d['artifacts'] if x['role']=='script').update(sha256=sha(p)))
        approval(self.brief,self.temp,'design')
        self.assertTrue(any('entire' in x for x in workflow_errors(self.brief,self.temp,'prototype')))

    def test_package_and_script_cannot_be_changed_under_old_approval(self):
        self.edit(self.brief['workflow']['packages']['design'],lambda d:d.update(revision='unapproved-r2'))
        self.assertTrue(any('exact package' in x for x in workflow_errors(self.brief,self.temp,'prototype')))

    def test_new_palette_requires_design_acceptance_not_content_interview(self):
        original=self.brief['content_confirmation']['content_sha256'];self.brief['style']['palette']=['#f00']
        self.assertEqual(original,self.brief['content_confirmation']['content_sha256'])
        self.assertTrue(any('stale' in x for x in workflow_errors(self.brief,self.temp,'prototype')))

    def test_technical_resolution_does_not_erase_design_acceptance(self):
        original=design_digest(self.brief);self.brief['output']['resolution']=[320,180]
        self.assertEqual(original,design_digest(self.brief));self.assertEqual(workflow_errors(self.brief,self.temp,'prototype'),[])

    def test_initial_direction_reply_cannot_approve_later_art(self):
        self.edit(self.brief['workflow']['approvals']['design'],lambda d:d.update(message_id='synthetic-fixture-message'))
        self.assertTrue(any('earlier reply' in x for x in workflow_errors(self.brief,self.temp,'prototype')))

    def test_approval_of_one_stage_cannot_approve_another(self):
        self.stage('prototype')
        self.brief['workflow']['approvals']['prototype']=copy.deepcopy(self.brief['workflow']['approvals']['design'])
        self.assertTrue(workflow_errors(self.brief,self.temp,'animatic'))

    def test_pilot_self_review_is_not_user_acceptance(self):
        self.stage('prototype',accept=False)
        self.assertTrue(any('PROTOTYPE_USER_APPROVAL_REQUIRED' in x for x in workflow_errors(self.brief,self.temp,'animatic')))

    def test_pilot_user_acceptance_advances_only_to_rough_cut(self):
        self.stage('prototype')
        self.assertEqual(workflow_errors(self.brief,self.temp,'animatic'),[])
        self.assertTrue(any('ANIMATIC_USER_APPROVAL_REQUIRED' in x for x in workflow_errors(self.brief,self.temp,'production')))

    def test_changed_accepted_pilot_file_is_rejected(self):
        self.stage('prototype');(self.temp/'out/prototype.mp4').write_bytes(b'changed')
        self.assertTrue(workflow_errors(self.brief,self.temp,'animatic'))

    def test_auto_or_a_bare_skip_flag_is_not_a_user_waiver(self):
        self.brief['workflow']['skip_all']=True
        self.edit(self.brief['workflow']['approvals']['design'],lambda d:d.update(decision='waived',explicit_skip=True))
        self.assertTrue(any('waiver' in x for x in workflow_errors(self.brief,self.temp,'prototype')))

    def test_explicit_named_waiver_preserves_design_work(self):
        self.edit(self.brief['workflow']['approvals']['design'],lambda d:d.update(decision='waived',explicit_skip=True,waived_stage='design',scope='this_stage_only',self_review={'reviewer':'synthetic agent','observations':'Actual fixture design and full script inspected'}))
        self.assertEqual(workflow_errors(self.brief,self.temp,'prototype'),[])
        self.assertTrue(workflow_errors(self.brief,self.temp,'production'))

    def test_specific_intake_waiver_does_not_fabricate_later_acceptance(self):
        self.edit(self.brief['workflow']['approvals']['design'],lambda d:d.update(decision='waived',message_id='synthetic-fixture-message',presented_message_id=None,explicit_skip=True,waived_stage='design',scope='this_stage_only',self_review={'reviewer':'synthetic reviewer','observations':'Full fixture package self-reviewed under explicit delegation'}))
        self.assertEqual(workflow_errors(self.brief,self.temp,'prototype'),[])

    def test_one_reply_can_accept_shown_pilot_and_explicitly_waive_animatic_stop(self):
        self.stage('prototype');self.stage('animatic')
        self.edit(self.brief['workflow']['approvals']['animatic'],lambda d:d.update(decision='waived',message_id='synthetic-prototype-reply',presented_message_id=None,explicit_skip=True,waived_stage='animatic',scope='this_stage_only',self_review={'reviewer':'synthetic reviewer','observations':'Combined whole-scope clip inspected as rough-cut fixture'}))
        self.assertEqual(workflow_errors(self.brief,self.temp,'production'),[])

    def test_missing_recording_cannot_produce_a_silent_whole_song_animatic(self):
        self.stage('prototype');self.brief.update(phase='animatic');self.brief['music'].update(source='provided',audio=None)
        self.assertTrue(any('selected recording' in x for x in entry_errors(self.brief,self.temp)))

    def test_whole_scope_does_not_supply_a_missing_pilot_bound(self):
        self.brief['execution']['authorized_duration']=6;self.brief.pop('prototype',None);bind_confirmation(self.brief,self.temp)
        self.edit(self.brief['workflow']['packages']['design'],lambda d:d['pilot'].update(end=2))
        approval(self.brief,self.temp,'design')
        self.assertTrue(any('prototype duration' in x for x in entry_errors(self.brief,self.temp,duration=6)))
        self.assertEqual(entry_errors(self.brief,self.temp,duration=2),[])

    def test_render_cannot_substitute_an_unapproved_sample_interval(self):
        self.edit(self.brief['workflow']['packages']['design'],lambda d:d['pilot'].update(start=1,end=2))
        approval(self.brief,self.temp,'design')
        self.assertTrue(any('PILOT_INTERVAL' in x for x in entry_errors(self.brief,self.temp,duration=.5,timeline_range=[0,.5])))
        self.assertEqual(entry_errors(self.brief,self.temp,duration=.5,timeline_range=[1,1.5]),[])

    def test_draft_design_check_does_not_require_its_own_prior_approval(self):
        from test_contracts import ToolkitTests
        import project_contracts as C
        t=ToolkitTests();t.setUp()
        try:
            p=t.fixture();b=C.load(p/'brief.json');b['workflow']['approvals'].clear();b['phase']='design';(p/'brief.json').write_text(json.dumps(b))
            result=C.inspect(p,'design');self.assertTrue(result['ok'],result)
        finally:t.tearDown()

    def test_stage_mismatch_cannot_force_a_lesser_gate(self):
        self.brief['phase']='full'
        self.assertTrue(any('STAGE_MISMATCH' in x for x in entry_errors(self.brief,self.temp,purpose='prototype')))

    def test_rough_cut_is_limited_before_render(self):
        self.stage('prototype');self.brief['phase']='animatic'
        self.assertTrue(any('ANIMATIC_LIMIT' in x for x in entry_errors(self.brief,self.temp,resolution=[1920,1080],fps=30)))
        self.assertEqual(entry_errors(self.brief,self.temp,resolution=[320,180],fps=12),[])

    def test_rough_cut_must_cover_whole_requested_duration(self):
        self.stage('prototype');self.stage('animatic')
        self.edit(self.brief['workflow']['packages']['animatic'],lambda d:d.update(target_duration=1))
        approval(self.brief,self.temp,'animatic')
        self.assertTrue(any('complete' in x for x in workflow_errors(self.brief,self.temp,'production')))

    def test_all_user_reviews_are_required_and_revision_bound(self):
        self.stage('prototype');self.stage('animatic')
        self.assertEqual(workflow_errors(self.brief,self.temp,'production'),[])
        self.edit(self.brief['workflow']['approvals']['animatic'],lambda d:d.update(decision='waiting'))
        self.assertTrue(workflow_errors(self.brief,self.temp,'production'))

    def test_legacy_confirmed_content_does_not_invent_stage_approvals(self):
        self.brief.pop('workflow')
        self.assertTrue(any('USER_STAGE_REVIEW_REQUIRED' in x for x in entry_errors(self.brief,self.temp)))

    def test_template_contracts_match_authoritative_gate(self):
        for folder in ('canvas-template','painted-template'):
            self.assertEqual((ROOT/'scripts/workflow_gate.py').read_bytes(),(ROOT/'assets'/folder/'workflow_gate.py').read_bytes())


@unittest.skipUnless(os.environ.get('MV_CANVAS_MODULE'),'optional native Canvas dependency not selected')
class NativeDesignTests(unittest.TestCase):
    def test_design_stills_render_but_video_does_not_start(self):
        with tempfile.TemporaryDirectory(prefix='mv-design-native-') as folder:
            p=Path(folder);b=agreed_fixture();bind_confirmation(b,p);b['workflow']['packages'].clear();b['workflow']['approvals'].clear();b['phase']='design'
            (p/'brief.json').write_text(json.dumps(b));target=p/'project'
            scaffold=subprocess.run([sys.executable,str(ROOT/'scripts/scaffold.py'),str(target),'--brief',str(p/'brief.json'),'--duration','2','--width','1280','--height','720'],capture_output=True,text=True)
            self.assertEqual(scaffold.returncode,0,scaffold.stderr)
            cmd=['node',str(target/'render_canvas.mjs'),'--project='+str(target),'--canvas-module='+os.environ['MV_CANVAS_MODULE']]
            video=subprocess.run(cmd+['--out=out/blocked'],capture_output=True,text=True)
            self.assertNotEqual(video.returncode,0);self.assertIn('DESIGN_STILLS_ONLY',video.stderr);self.assertFalse((target/'out/blocked').exists())
            stills=subprocess.run(cmd+['--out=out/design','--stills-only','--times=0,1'],capture_output=True,text=True)
            self.assertEqual(stills.returncode,0,stills.stderr);self.assertTrue((target/'out/design/sheet.png').is_file());self.assertFalse((target/'out/design/clip.mp4').exists())
            local=subprocess.run([sys.executable,str(target/'project_contracts.py'),'init','--project',str(target)],capture_output=True,text=True)
            self.assertEqual(local.returncode,0,local.stderr);self.assertTrue((target/'visual-spec.json').is_file())


class BrowserAdapterEncodeTests(unittest.TestCase):
    """Actual FFmpeg-only branch; does not launch or certify a browser."""
    def setUp(self):
        import wave,array,math
        self.temp=Path(tempfile.mkdtemp(prefix='mv-browser-encode-v33-'))
        audio=self.temp/'song.wav'
        with wave.open(str(audio),'wb') as f:
            f.setparams((1,2,8000,0,'NONE','not compressed'))
            f.writeframes(array.array('h',(int(5000*math.sin(i*2*math.pi*440/8000)) if 16000<=i<18400 else 0 for i in range(48000))).tobytes())
        self.brief=agreed_fixture();self.brief['execution'].update(authorized_scope='full',authorized_duration=6);self.brief['output'].update(resolution=[320,180],fps=12)
        self.brief['music'].update(source='provided',kind='instrumental',audio='song.wav',audio_sha256=sha(audio))
        from input_contracts import content_digest
        self.brief['content_confirmation']['content_sha256']=content_digest(self.brief)
        bind_confirmation(self.brief,self.temp)
        pkg=self.brief['workflow']['packages']['design'];p=self.temp/pkg['path'];d=json.loads(p.read_text());d['pilot'].update(start=2,end=4);p.write_text(json.dumps(d));pkg['sha256']=sha(p);approval(self.brief,self.temp,'design')
        (self.temp/'brief.json').write_text(json.dumps(self.brief));(self.temp/'out/frames').mkdir(parents=True)

    def tearDown(self):shutil.rmtree(self.temp)

    def frames(self,first):
        subprocess.run(['ffmpeg','-y','-v','error','-f','lavfi','-i','color=c=navy:s=320x180:r=12','-frames:v','24','-start_number',str(first),str(self.temp/'out/frames/f%05d.jpg')],check=True)

    def encode(self,folder,out):
        return subprocess.run(['node',str(ROOT/'assets'/folder/'render.mjs'),'--encode','--fps=12','--out='+out],cwd=self.temp,capture_output=True,text=True)

    def test_nonzero_approved_frames_encode_with_matching_audio_seek(self):
        import array
        self.frames(24)
        for folder in ('canvas-template','painted-template'):
            name='out/'+folder+'.mp4';r=self.encode(folder,name);self.assertEqual(r.returncode,0,r.stderr)
            media=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-of','json',str(self.temp/name)]))
            video=next(x for x in media['streams'] if x['codec_type']=='video');self.assertEqual(int(video['nb_read_frames']),24)
            pcm=array.array('h',subprocess.check_output(['ffmpeg','-v','error','-i',str(self.temp/name),'-ar','8000','-ac','1','-f','s16le','-']))
            self.assertGreater(max(abs(x) for x in pcm[:1600]),2000,'source pulse at 2s must appear at the output start')

    def test_numbered_frames_from_an_unapproved_interval_are_blocked(self):
        self.frames(0)
        for folder in ('canvas-template','painted-template'):
            r=self.encode(folder,'out/blocked.mp4');self.assertNotEqual(r.returncode,0);self.assertIn('PILOT_INTERVAL',r.stderr);self.assertFalse((self.temp/'out/blocked.mp4').exists())


if __name__=='__main__':unittest.main()

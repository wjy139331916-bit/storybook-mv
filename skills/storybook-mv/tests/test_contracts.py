import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT/'assets/studies/evidence'
sys.path.insert(0, str(ROOT/'scripts'))
import project_contracts as C


def run(script, *args, code=0):
    result = subprocess.run([sys.executable, str(ROOT/'scripts'/script), *map(str,args)], capture_output=True, text=True, encoding='utf-8')
    if result.returncode != code:
        raise AssertionError((result.returncode, result.stdout, result.stderr))
    return result


class ToolkitTests(unittest.TestCase):
    def setUp(self):
        self.temp = Path(tempfile.mkdtemp(prefix='mv-contract-test-'))
        import wave, array, math
        samples=array.array('h',(int(4000*math.sin(i*2*math.pi*440/8000)) for i in range(16000)))
        with wave.open(str(self.temp/'runtime-tones.wav'),'wb') as f:
            f.setnchannels(1);f.setsampwidth(2);f.setframerate(8000);f.writeframes(samples.tobytes())

    def tearDown(self):
        shutil.rmtree(self.temp)

    def fixture(self):
        p = self.temp/'project'
        p.mkdir()
        brief = json.loads((ROOT/'assets/brief.template.json').read_text(encoding='utf-8'))
        brief.update(goal='original abstract test',emotion='curiosity',asset_policy='all-code',phase='prototype',request_mode='production')
        brief['style'].update(direction='geometric',medium='Canvas',motion='time-based')
        brief['structure'].update(mode='abstract',outline=['circle translates'])
        brief['characters']['required']=False
        brief['music'].update(source='none',scope='2-second silent scope')
        brief['output']['aspect_ratio']='16:9'
        brief['lyrics']['mode']='none'
        brief['execution'].update(engine='canvas2d',runtime='node-canvas',production_authorized=True)
        brief['confirmed_fields']=['style.direction','characters.required','asset_policy']
        brief['content']={'subject':'synthetic geometric fixture','core_idea':'follow a circle through three declared states','key_moments':[{'description':d,'purpose':'exercise the structural validator only'} for d in ('circle appears','circle moves','circle settles')],'exclusions':['no real user or artistic acceptance is asserted']}
        brief['music']['kind']='none'
        brief['song_reading'].update(status='not_applicable',reason='silent synthetic validator fixture')
        brief['execution'].update(context='user-project',authorized_scope='full',authorized_duration=6,authorization_evidence='synthetic test-user authorization; not a real user acceptance claim')
        from check_brief import content_digest
        brief['content_confirmation']={'status':'confirmed','summary':'Synthetic fixture: circle appears, moves and settles','user_evidence':'synthetic test-user message inside this unit fixture','content_sha256':content_digest(brief)}
        from test_content_gate import bind_confirmation
        bind_confirmation(brief,p)
        (p/'brief.json').write_text(json.dumps(brief), encoding='utf-8')
        C.initialize(p,ROOT)
        spec=C.load(p/'visual-spec.json')
        spec.update(revision='test-1',status='locked')
        spec['design'].update(palette=['#000000','#ffffff'],shape_language='circle',composition='center',motion='linear')
        (p/'out').mkdir();(p/'src').mkdir()
        shutil.copy2(BASE/'style-board.png',p/'out/reference.png')
        shutil.copy2(BASE/'runtime.mp4',p/'out/prototype.mp4')
        (p/'src/scene.js').write_text('// synthetic structural-validator fixture, not a claimed art acceptance\n', encoding='utf-8')
        spec['evidence']=[{'path':'out/reference.png','sha256':C.digest(p/'out/reference.png')}]
        (p/'visual-spec.json').write_text(json.dumps(spec), encoding='utf-8')
        mapping={'schema_version':1,'duration':2,'duration_status':'prototype','audio_sha256':None,'sections':[{'id':'a','start':0,'end':2}], 'shots':[{'id':'s01','start':0,'end':2,'section_id':'a','objective':'observe change','visible_change':'circle moves','assets':['circle']} ]}
        (p/'shot-map.json').write_text(json.dumps(mapping), encoding='utf-8')
        # Deliberately synthetic review records exercise record validation, not visual truth.
        review={'schema_version':1,'scope':'prototype','reviewer':'synthetic validator fixture','target':{'path':'out/prototype.mp4','sha256':C.digest(p/'out/prototype.mp4'),'input_digest':C.fingerprint(p)},'checks':[{'id':k,'status':'not_applicable' if k=='music' else 'pass','notes':'fixture only; no aesthetic claim','range':[0,2],'evidence':[] if k=='music' else ['out/prototype.mp4'] if k in ('motion','continuity') else ['out/reference.png']} for k in spec['required_checks']],'issues':[]}
        (p/'review.json').write_text(json.dumps(review), encoding='utf-8')
        runtime={'status':'passed','engine':'canvas2d','runtime_backend':'node-canvas','encoded':{'full_decode':True},'artifact':{'path':'out/prototype.mp4','sha256':C.digest(p/'out/prototype.mp4')}}
        (p/'runtime-report.json').write_text(json.dumps(runtime), encoding='utf-8')
        return p

    def check(self,p):
        result = C.inspect(p,'prototype')
        return result

    def edit(self,p,name,fn):
        f=p/name;data=json.loads(f.read_text(encoding='utf-8'));fn(data);f.write_text(json.dumps(data), encoding='utf-8')

    def test_neutral_and_preserving_init(self):
        p=self.fixture();original=(p/'visual-spec.json').read_bytes();result=C.initialize(p,ROOT)
        self.assertEqual(original,(p/'visual-spec.json').read_bytes());self.assertEqual(len(result['preserved']),3)
        self.assertFalse(C.load(p/'visual-spec.json')['characters_required'])

    def test_valid_review_record(self):
        r=self.check(self.fixture());self.assertTrue(r['ok'],r)

    def test_art_review_history_preserves_bound_design_and_render_identity(self):
        p=self.fixture();before=(p/'visual-spec.json').read_bytes();identity=C.fingerprint(p)
        notes=C.load(ROOT/'assets/contracts/art-direction.template.json')
        notes['taste_notes']=[{'scope':'synthetic-project-only','source_statement':'Synthetic preference observation, no approval','observation':'keep the existing quiet palette'}]
        notes['review_rounds']=[{'revision':'test-1','focus_issue_ids':[],'observation':'Synthetic bookkeeping only; drawing is unchanged'}]
        (p/'plan/art-direction.json').write_text(json.dumps(notes),encoding='utf-8')
        self.assertEqual((p/'visual-spec.json').read_bytes(),before)
        self.assertEqual(C.fingerprint(p),identity);self.assertTrue(self.check(p)['ok'])
        self.edit(p,'visual-spec.json',lambda x:x['design'].update(shape_language='changed visible design'))
        self.assertNotEqual(C.fingerprint(p),identity)
        self.assertTrue(any('source/design changed' in x for x in self.check(p)['errors']))

    def test_source_change_invalidates_record(self):
        p=self.fixture();(p/'src/scene.js').write_text('changed', encoding='utf-8')
        self.assertTrue(any('source/design changed' in x for x in self.check(p)['errors']))

    def test_clip_change_invalidates_record(self):
        p=self.fixture();(p/'out/prototype.mp4').write_bytes(b'changed')
        self.assertTrue(any('target missing or changed' in x for x in self.check(p)['errors']))

    def test_unresolved_major_blocks_expansion(self):
        p=self.fixture();self.edit(p,'review.json',lambda x:x['issues'].append({'id':'i1','severity':'major','status':'open'}))
        self.assertTrue(any('unresolved major' in x for x in self.check(p)['errors']))

    def test_na_style_is_rejected(self):
        p=self.fixture();self.edit(p,'review.json',lambda x:next(k for k in x['checks'] if k['id']=='style').update(status='not_applicable'))
        self.assertFalse(self.check(p)['ok'])

    def test_false_resolution_evidence_rejected(self):
        p=self.fixture();self.edit(p,'review.json',lambda x:x['issues'].append({'id':'i1','severity':'major','status':'resolved','resolution':'changed','evidence':['out/missing.png']}))
        self.assertTrue(any('replacement evidence missing' in x for x in self.check(p)['errors']))

    def test_wrong_runtime_rejected(self):
        p=self.fixture();self.edit(p,'runtime-report.json',lambda x:x.update(runtime_backend='browser'))
        self.assertTrue(any('backend differs' in x for x in self.check(p)['errors']))

    def test_diagnostic_is_bound_to_current_encoded_target(self):
        p=self.fixture();report={'target':{'sha256':C.digest(p/'out/prototype.mp4')}}
        (p/'out/diagnostic.json').write_text(json.dumps(report), encoding='utf-8')
        self.edit(p,'review.json',lambda x:x.update(diagnostics=[{'path':'out/diagnostic.json','sha256':C.digest(p/'out/diagnostic.json')}]))
        self.assertTrue(self.check(p)['ok'])
        report['target']['sha256']='another-video';(p/'out/diagnostic.json').write_text(json.dumps(report), encoding='utf-8')
        self.edit(p,'review.json',lambda x:x['diagnostics'][0].update(sha256=C.digest(p/'out/diagnostic.json')))
        self.assertTrue(any('another encoded target' in x for x in self.check(p)['errors']))

    def test_changed_diagnostic_cannot_be_reused(self):
        p=self.fixture();(p/'out/diagnostic.json').write_text(json.dumps({'target':{'sha256':C.digest(p/'out/prototype.mp4')}}), encoding='utf-8')
        self.edit(p,'review.json',lambda x:x.update(diagnostics=[{'path':'out/diagnostic.json','sha256':C.digest(p/'out/diagnostic.json')}]))
        (p/'out/diagnostic.json').write_text('{}', encoding='utf-8')
        self.assertTrue(any('diagnostic report missing or changed' in x for x in self.check(p)['errors']))

    def test_locked_choice_change_rejected(self):
        p=self.fixture();self.edit(p,'brief.json',lambda x:x['style'].update(direction='paper'))
        self.assertTrue(any('locked decision differs' in x for x in self.check(p)['errors']))

    def test_full_recording_and_decode(self):
        p=self.fixture();shutil.copy2(self.temp/'runtime-tones.wav',p/'assets.wav')
        self.edit(p,'brief.json',lambda x:(x['music'].update(source='provided',audio=str(p/'assets.wav'),audio_sha256=C.digest(p/'assets.wav')),x['output'].update(resolution=[640,360],fps=30)))
        self.edit(p,'brief.json',lambda x:x['music'].update(kind='instrumental'))
        from check_brief import content_digest
        self.edit(p,'brief.json',lambda x:(x.update(phase='full'),x['content_confirmation'].update(content_sha256=content_digest(x))))
        from test_content_gate import bind_confirmation
        b=C.load(p/'brief.json');bind_confirmation(b,p);(p/'brief.json').write_text(json.dumps(b), encoding='utf-8')
        self.edit(p,'shot-map.json',lambda x:x.update(duration_status='recording_measured',audio_sha256=C.digest(p/'assets.wav')))
        self.edit(p,'review.json',lambda x:(x.update(scope='full'),next(c for c in x['checks'] if c['id']=='music').update(status='pass',evidence=['out/prototype.mp4'])))
        # Synthetic fixture now explicitly includes artifact-specific user stage
        # records. Internal runtime review alone must not satisfy the new gates.
        from workflow_fixtures import record, video_stage
        b=C.load(p/'brief.json')
        for stage in ('prototype','animatic'):
            clip='out/'+stage+'-stage.mp4'
            subprocess.run(['ffmpeg','-y','-v','error','-i',str(p/'out/prototype.mp4'),'-r','12','-vf','scale=320:180','-t','2',str(p/clip)],check=True)
            report='out/'+stage+'-report.json'
            record(p,report,{'production_stage':stage,'encoded':{'full_decode':True},'artifacts':[{'path':clip,'sha256':C.digest(p/clip)}]})
            video_stage(b,p,stage,clip,report)
        (p/'brief.json').write_text(json.dumps(b), encoding='utf-8')
        result=C.inspect(p,'full');self.assertTrue(result['ok'],result)
        self.edit(p,'shot-map.json',lambda x:x.update(audio_sha256='wrong'))
        self.assertFalse(C.inspect(p,'full')['ok'])

    def test_shared_asset_repair_and_join_margin(self):
        p=self.fixture();mapping=C.load(p/'shot-map.json');mapping.update(duration=6,sections=[{'id':'a','start':0,'end':6}]);mapping['shots']=[{'id':'s0'+str(i+1),'start':i*2,'end':(i+1)*2,'section_id':'a','objective':'observe','visible_change':'move','assets':['shared'] if i!=1 else ['other']} for i in range(3)]
        (p/'shot-map.json').write_text(json.dumps(mapping), encoding='utf-8')
        self.edit(p,'review.json',lambda x:x['issues'].append({'id':'i1','status':'open','severity':'major','shared_assets':['shared']}))
        result=C.repair(p,.25)
        self.assertEqual(result['affected_shots'],['s01','s03']);self.assertEqual(result['preserve_shots'],['s02']);self.assertEqual(result['render_ranges'],[[0,2.25],[3.75,6]])

    def test_repeated_section_requires_variation(self):
        errors=[];C.timeline({'duration':4,'sections':[{'id':'a','start':0,'end':2},{'id':'b','start':2,'end':4,'repeat_of':'a'}],'shots':[]},errors,False)
        self.assertIn('b: repeated material needs a stated variation',errors)

    def test_export_integrity_and_tamper(self):
        dest=self.temp/'export';run('export_skill.py','--dest',dest)
        folder=dest/'storybook-mv';run('verify_portable.py',folder)
        self.assertFalse((folder/'references/tebie-de-ren.md').exists());self.assertFalse((folder/'agents').exists())
        (folder/'assets/modules/motion.js').write_text('changed', encoding='utf-8')
        run('verify_portable.py',folder,code=2)

    def test_unsafe_manifest_rejected(self):
        dest=self.temp/'export';run('export_skill.py','--dest',dest);folder=dest/'storybook-mv'
        self.edit(folder,'PORTABLE_MANIFEST.json',lambda x:x['files'].append({'path':'../outside','bytes':0,'sha256':''}))
        run('verify_portable.py',folder,code=2)

    def test_portable_copy_can_be_exported_again(self):
        first=self.temp/'first';run('export_skill.py','--dest',first)
        source=first/'storybook-mv';second=self.temp/'second'
        result=subprocess.run([sys.executable,str(source/'scripts/export_skill.py'),'--dest',str(second)],capture_output=True,text=True, encoding='utf-8')
        self.assertEqual(result.returncode,0,result.stderr)
        folder=second/'storybook-mv';run('verify_portable.py',folder)
        self.assertEqual((source/'PORTABLE_MANIFEST.json').read_bytes(),(folder/'PORTABLE_MANIFEST.json').read_bytes())
        self.assertFalse((folder/'references/tebie-de-ren.md').exists())
        self.assertFalse((folder/'agents').exists())

    def test_music_metadata_keeps_candidates_unverified(self):
        f=self.temp/'audio.json';run('analyze_music.py',self.temp/'runtime-tones.wav','--out',f,'--window','0.1')
        data=json.loads(f.read_text(encoding='utf-8'));self.assertAlmostEqual(data['duration'],2);self.assertEqual(len(data['windows']),20);self.assertEqual(data['beats_status'],'not_measured');self.assertEqual(data['sections_status'],'unreviewed')

    def test_study_no_subject_and_no_overwrite(self):
        run('build_study.py',self.temp/'missing','--kind','style','--style','flat',code=2)
        run('scaffold.py',self.temp/'missing',code=2)
        run('build_study.py',self.temp/'study','--kind','style','--style','pixel','--subject','abstract','--tool-self-test')
        r=subprocess.run([sys.executable,str(ROOT/'scripts/build_study.py'),str(self.temp/'study'),'--kind','style','--style','pixel','--subject','abstract','--tool-self-test'],capture_output=True)
        self.assertNotEqual(r.returncode,0)

    def test_cpu_preflight_does_not_require_browser(self):
        import os
        configured=os.environ.get('MV_CANVAS_MODULE')
        if not configured:
            self.skipTest('optional native Canvas dependency not selected')
        module=Path(configured)
        result=json.loads(run('preflight.py','--engine','canvas2d','--runtime','node-canvas','--canvas-module',module,'--strict','--json').stdout)
        self.assertTrue(result['ready']);self.assertIsNone(result['chrome'])
        media=json.loads(run('preflight.py','--engine','canvas2d','--runtime','node-canvas','--canvas-module',module,'--media-tools','--json').stdout)
        self.assertTrue(media['python_media']['numpy'])
        self.assertTrue(media['python_media']['PIL'])
        run('preflight.py','--engine','painted-p5','--runtime','node-canvas',code=2)


if __name__=='__main__':
    unittest.main(verbosity=2)

"""Synthetic records exercise hard content/meaning/scope gates; they assert no real consent."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
from check_brief import content_digest, production_gate, song_reading_errors


def agreed_fixture():
    b=json.loads((ROOT/'assets/brief.template.json').read_text())
    b.update(goal='synthetic original time study',emotion='curiosity',asset_policy='all-code',phase='prototype',request_mode='production')
    b['music'].update(source='none',kind='none',scope='six-second silent fixture')
    b['style'].update(direction='flat',medium='Canvas',motion='reusable strokes')
    b['characters'].update(required=False,roles=[])
    b['lyrics']['mode']='none'
    b['structure'].update(mode='type',outline=['TIME','clock','TIME'],ending='return to initial word')
    b['content']={'subject':'word TIME and clock','core_idea':'the same letter parts become a clock and return','key_moments':[{'description':d,'purpose':p} for d,p in [('TIME is readable','establish source parts'),('parts form a working clock','visualize time'),('parts return to TIME','close the loop')]],'exclusions':['no cast']}
    b['song_reading'].update(status='not_applicable',reason='no song in this synthetic fixture')
    b['output'].update(aspect_ratio='16:9',resolution=[1280,720],fps=30)
    b['execution'].update(context='user-project',engine='canvas2d',runtime='node-canvas',production_authorized=True,authorized_scope='prototype',authorized_duration=6,authorization_evidence='Synthetic test user explicitly requests only this six-second prototype')
    b['content_confirmation']={'status':'confirmed','summary':'TIME becomes a clock and returns, no characters','user_evidence':'Synthetic test user explicitly requested this exact concept; fixture only','content_sha256':content_digest(b)}
    b['prototype']={'duration':6}
    b['workflow']={'schema_version':1,'policy':'user-stage-review','packages':{'design':{'path':'plan/design-package.json','sha256':'0'*64}},'approvals':{'design':{'path':'plan/design-user.json','sha256':'0'*64}}}
    return b


def lyrical_fixture():
    b=agreed_fixture();b['music'].update(kind='lyrical',title='Original unit-test song',artist='Synthetic fixture',version='test mix')
    b['song_reading']['lyrics_document']={'path':str(ROOT/'tests/fixtures/original-lyrics.json'),'sha256':hashlib.sha256((ROOT/'tests/fixtures/original-lyrics.json').read_bytes()).hexdigest()}
    b['song_reading'].update(status='clarified',recording_basis='synthetic unit-test source',lyrics_status='provided',lyrics_source='original fixture cue file',central_meaning='a speaker notices hope after difficulty',intent_basis='text_interpretation',evidence=[{'cue_ids':['line-1','line-2'],'observation':'original fixture contrasts darkness and a visible light'}],needs_user_selection=True,options=[{'id':'hope','reading':'renewed hope'},{'id':'memory','reading':'remembered comfort'}],selected_direction='hope',user_selection_evidence='Synthetic test user selected hope')
    b['content_confirmation']['content_sha256']=content_digest(b)
    return b


def bind_confirmation(brief,folder):
    """Synthetic test messages only; never asserts real user acceptance."""
    from workflow_fixtures import design
    design(brief, Path(folder))
    record=Path(folder)/'synthetic-confirmation.json'
    record.write_text(json.dumps({'origin':'user-message','message_id':'synthetic-fixture-message','user_reply':'Synthetic unit fixture accepts this exact concept','recap_id':'fixture-recap','accepted_content_sha256':content_digest(brief)}))
    brief['content_confirmation']['record']={'path':str(record),'sha256':hashlib.sha256(record.read_bytes()).hexdigest()}
    return record


class ContentGateTests(unittest.TestCase):
    def test_three_basic_answers_are_not_content_confirmation(self):
        b=json.loads((ROOT/'assets/brief.template.json').read_text());b['music'].update(title='named song',scope='whole song');b['output']['aspect_ratio']='16:9';b['style']['direction']='warm'
        errors=production_gate(b,'production',240)
        self.assertTrue(any('CONTENT_NOT_CONFIRMED' in e for e in errors))
        self.assertTrue(any('content.key_moments' in e for e in errors))

    def test_old_production_boolean_does_not_auto_approve(self):
        b=agreed_fixture();b.pop('content_confirmation');b['execution']['production_authorized']=True
        self.assertTrue(production_gate(b,'production',6))

    def test_exact_user_content_and_bounded_prototype_can_proceed(self):
        self.assertEqual(production_gate(agreed_fixture(),'prototype',6),[])

    def test_prototype_does_not_authorize_full_video(self):
        self.assertTrue(any('scope' in e for e in production_gate(agreed_fixture(),'production',6)))

    def test_prototype_duration_cannot_expand_to_whole_song(self):
        self.assertTrue(any('duration' in e for e in production_gate(agreed_fixture(),'prototype',240)))

    def test_content_approval_is_not_production_authorization(self):
        b=agreed_fixture();b['execution']['production_authorized']=False
        self.assertIn('production is not authorized',production_gate(b,'prototype',6))

    def test_changed_story_invalidates_old_confirmation(self):
        b=agreed_fixture();b['content']['key_moments'][1]['description']='invented unrelated romance'
        self.assertTrue(any('stale' in e for e in production_gate(b,'prototype',6)))

    def test_routine_palette_change_does_not_reinterview_content(self):
        b=agreed_fixture();b['style']['palette']=['#111111','#eeeeee']
        self.assertEqual(production_gate(b,'prototype',6),[])

    def test_missing_lyrics_cannot_be_replaced_with_guesses(self):
        b=lyrical_fixture();b['song_reading']['lyrics_status']='missing'
        self.assertTrue(any('lyrics are missing' in e for e in production_gate(b,'prototype',6)))

    def test_no_subtitles_does_not_skip_lyrical_song_reading(self):
        b=lyrical_fixture();b['lyrics']['mode']='none';b['song_reading']['status']='pending'
        self.assertTrue(any('SONG_MEANING_UNRESOLVED' in e for e in production_gate(b,'prototype',6)))

    def test_multiple_readings_need_actual_user_selection_record(self):
        b=lyrical_fixture();b['song_reading']['user_selection_evidence']=None
        self.assertTrue(any('user selection' in e for e in production_gate(b,'prototype',6)))

    def test_artist_intent_without_source_is_not_a_fact(self):
        b=lyrical_fixture();b['song_reading'].update(intent_basis='documented_artist_intent',sources=[])
        self.assertTrue(any('artist-intent' in e for e in song_reading_errors(b)))

    def test_song_meaning_change_invalidates_content_confirmation(self):
        b=lyrical_fixture();b['song_reading']['central_meaning']='another unconfirmed reading'
        self.assertTrue(any('stale' in e for e in production_gate(b,'prototype',6)))

    def test_instrumental_needs_a_reason(self):
        b=agreed_fixture();b['music']['kind']='instrumental';b['song_reading']['reason']=None
        self.assertTrue(song_reading_errors(b))

    def test_self_test_cannot_use_user_recording_or_pass_full_contract(self):
        b=agreed_fixture();b['execution']['context']='tool-self-test';b['tool_self_test']={'source':'storybook-mv','purpose':'isolated-tool-verification'};b['music']['source']='provided'
        self.assertTrue(production_gate(b,'prototype',6));b['music']['source']='original-code'
        self.assertTrue(production_gate(b,'production',6));self.assertTrue(production_gate(b,'prototype',240))

    def test_scaffold_refuses_unconfirmed_content_without_creating_project(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder);b=agreed_fixture();b['content_confirmation']['status']='pending';(p/'brief.json').write_text(json.dumps(b));target=p/'project'
            result=subprocess.run([sys.executable,str(ROOT/'scripts/scaffold.py'),str(target),'--engine','canvas2d','--brief',str(p/'brief.json')],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0);self.assertIn('CONTENT_NOT_CONFIRMED',result.stderr);self.assertFalse(target.exists())

    def test_native_renderer_blocks_before_loading_runtime_or_creating_output(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder);b=agreed_fixture();b['content_confirmation']['status']='pending';(p/'brief.json').write_text(json.dumps(b))
            result=subprocess.run(['node',str(ROOT/'scripts/render_canvas.mjs'),'--project='+str(p),'--out=out/blocked'],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0);self.assertIn('CONTENT_NOT_CONFIRMED',result.stderr);self.assertFalse((p/'out').exists())

    def test_python_and_js_gate_agree_on_content_meaning_and_scope(self):
        cases=[agreed_fixture(),lyrical_fixture()]
        for mutate in (lambda b:b['content_confirmation'].update(status='pending'),lambda b:b['content'].update(core_idea='changed'),lambda b:b['execution'].update(authorized_duration=2),lambda b:b['song_reading'].update(user_selection_evidence=None)):
            b=lyrical_fixture();mutate(b);cases.append(b)
        code="import {contentDigest,gateErrors} from "+json.dumps((ROOT/'scripts/production_gate.mjs').as_uri())+";let data='';for await(const part of process.stdin)data+=part;console.log(JSON.stringify(JSON.parse(data).map(b=>({digest:contentDigest(b),errors:gateErrors(b,{duration:6})}))));"
        result=subprocess.run(['node','--input-type=module','-e',code],input=json.dumps(cases,ensure_ascii=False),capture_output=True,text=True,check=True)
        for b,j in zip(cases,json.loads(result.stdout)):
            self.assertEqual(content_digest(b),j['digest']);self.assertEqual(production_gate(b,'prototype',6),j['errors'])

    def test_bundled_browser_adapters_have_the_same_gate(self):
        original=(ROOT/'scripts/production_gate.mjs').read_bytes()
        for name in ('canvas-template','painted-template'):
            self.assertEqual(original,(ROOT/'assets'/name/'production_gate.mjs').read_bytes())
            code=(ROOT/'assets'/name/'render.mjs').read_text()
            self.assertIn('assertProduction(process.cwd(),',code)
            self.assertIn('const stageAssert=options=>assertProduction(',code)
            self.assertGreaterEqual(code.count('stageAssert('),5)

    @unittest.skipUnless(os.environ.get('MV_CANVAS_MODULE'),'optional native Canvas dependency not selected')
    def test_confirmed_bounded_user_prototype_reaches_a_real_encode(self):
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder);brief=agreed_fixture();bind_confirmation(brief,p);(p/'brief.json').write_text(json.dumps(brief))
            project=p/'project'
            subprocess.run([sys.executable,str(ROOT/'scripts/scaffold.py'),str(project),'--engine','canvas2d','--brief',str(p/'brief.json'),'--duration','2','--width','1280','--height','720','--fps','12'],check=True,capture_output=True,text=True)
            (project/'src/scene.js').write_bytes((ROOT/'assets/style-packs/time-clock.js').read_bytes())
            result=subprocess.run(['node',str(ROOT/'scripts/render_canvas.mjs'),'--project='+str(project),'--out=out/prototype','--canvas-module='+os.environ['MV_CANVAS_MODULE']],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            report=json.loads((project/'out/prototype/render-report.json').read_text())
            self.assertEqual(report['frames'],24);self.assertTrue(report['encoded']['full_decode'])


if __name__=='__main__':
    unittest.main(verbosity=2)

"""Original/synthetic fixtures verify contracts; no real consent or art approval is asserted."""
import copy
import hashlib
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
from check_brief import content_digest,production_gate,entry_errors,song_reading_errors
from input_contracts import sha,subtitle_errors
from test_content_gate import agreed_fixture,lyrical_fixture,bind_confirmation
import test_contracts as contract_fixtures
import project_contracts as C


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temp=Path(tempfile.mkdtemp(prefix='mv-v32-test-'))

    def tearDown(self):
        shutil.rmtree(self.temp)

    def scaffold(self,b,**options):
        bind_confirmation(b,self.temp)
        f=self.temp/'brief.json';f.write_text(json.dumps(b), encoding='utf-8')
        target=self.temp/'project'
        cmd=[sys.executable,str(ROOT/'scripts/scaffold.py'),str(target),'--brief',str(f),'--engine','canvas2d','--duration','2']
        for k,v in options.items():cmd.extend(['--'+k.replace('_','-'),str(v)])
        return subprocess.run(cmd,capture_output=True,text=True, encoding='utf-8'),target

    def test_empty_and_null_lyric_evidence_rejected(self):
        for evidence in ([None],[{}],[{'cue_ids':[''],'observation':'x'}],[{'cue_ids':['line-1'],'observation':' '}],[]):
            b=lyrical_fixture();b['song_reading']['evidence']=evidence
            self.assertTrue(song_reading_errors(b))

    def test_artist_claim_needs_structured_primary_snapshot(self):
        for sources in ([''],[None],[{'id':'post','attribution':'Fan','checked_at':'2026-10-29','summary':'a fan guess','url':'https://example.test','kind':'fan'}]):
            b=lyrical_fixture();b['song_reading'].update(intent_basis='documented_artist_intent',sources=sources)
            self.assertTrue(song_reading_errors(b))

    def test_nonexistent_lyric_cue_rejected(self):
        b=lyrical_fixture();b['song_reading']['evidence'][0]['cue_ids']=['invented-line']
        self.assertTrue(any('nonexistent' in x for x in song_reading_errors(b,self.temp)))

    def test_changed_canonical_file_rejected(self):
        b=lyrical_fixture();p=self.temp/'lyrics.json';p.write_bytes((ROOT/'tests/fixtures/original-lyrics.json').read_bytes())
        b['song_reading']['lyrics_document']={'path':str(p),'sha256':sha(p)}
        p.write_text('{"lines":[]}', encoding='utf-8')
        self.assertTrue(any('changed' in x for x in song_reading_errors(b,self.temp)))

    def test_discovery_and_plan_only_flags_rejected(self):
        for update in ({'phase':'discover'},{'request_mode':'plan-only'},{'phase':'awaiting-confirmation'}):
            b=agreed_fixture();b.update(update)
            self.assertTrue(any('STAGE_BLOCKED' in x for x in production_gate(b)))

    def test_authorized_full_scope_still_obeys_pilot_duration(self):
        b=agreed_fixture();b['execution'].update(authorized_scope='full',authorized_duration=240);b['prototype']={'duration':8}
        self.assertTrue(any('prototype duration' in x for x in production_gate(b,duration=240)))

    def test_missing_confirmation_record_blocks_scaffold(self):
        b=agreed_fixture();f=self.temp/'brief.json';f.write_text(json.dumps(b), encoding='utf-8');target=self.temp/'absent'
        r=subprocess.run([sys.executable,str(ROOT/'scripts/scaffold.py'),str(target),'--brief',str(f),'--engine','canvas2d'],capture_output=True,text=True, encoding='utf-8')
        self.assertNotEqual(r.returncode,0);self.assertIn('confirmation record',r.stderr);self.assertFalse(target.exists())

    def test_confirmation_record_is_bound_to_content(self):
        b=agreed_fixture();p=bind_confirmation(b,self.temp)
        record=json.loads(p.read_text(encoding='utf-8'));record['accepted_content_sha256']='another-recap';p.write_text(json.dumps(record), encoding='utf-8');b['content_confirmation']['record']['sha256']=sha(p)
        self.assertTrue(any('another content' in x for x in entry_errors(b,self.temp)))

    def test_float_exponents_negative_zero_and_unicode_hash_parity(self):
        cases=[]
        for value in (160.0,1e-7,1e20,-0.0,1.2345678901234567):
            b=agreed_fixture();b['characters']['roles']=[{'height':value,'中文':'边缘','😀':True}];b['content_confirmation']['content_sha256']=content_digest(b);cases.append(b)
        code="import {contentDigest} from "+json.dumps((ROOT/'scripts/production_gate.mjs').as_uri())+";let d='';for await(const c of process.stdin)d+=c;console.log(JSON.stringify(JSON.parse(d).map(contentDigest)));"
        r=subprocess.run(['node','--input-type=module','-e',code],input=json.dumps(cases),capture_output=True,text=True,check=True, encoding='utf-8')
        self.assertEqual(json.loads(r.stdout),[content_digest(b) for b in cases])

    def test_unsafe_large_integer_rejected(self):
        b=agreed_fixture();b['characters']['roles']=[{'height':2**54+1}]
        with self.assertRaises(ValueError):content_digest(b)

    def test_square_and_four_three_do_not_fall_back_to_widescreen(self):
        b=agreed_fixture();b['output'].update(aspect_ratio='1:1',resolution=None)
        r,p=self.scaffold(b);self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(json.loads((p/'brief.json').read_text(encoding='utf-8'))['output']['resolution'],[1080,1080])
        shutil.rmtree(p);b['output']['aspect_ratio']='4:3';r,p=self.scaffold(b)
        self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(json.loads((p/'brief.json').read_text(encoding='utf-8'))['output']['resolution'],[1440,1080])

    def test_explicit_resolution_cannot_change_approved_aspect(self):
        r,p=self.scaffold(agreed_fixture(),width=100,height=100)
        self.assertNotEqual(r.returncode,0);self.assertFalse(p.exists())

    def test_missing_full_recording_and_pilot_block_entry(self):
        b=agreed_fixture();b.update(phase='full');b['execution']['authorized_scope']='full';b['music'].update(source='provided',audio='missing.wav',audio_sha256='0'*64)
        bind_confirmation(b,self.temp);e=entry_errors(b,self.temp,duration=2)
        self.assertTrue(any('recording' in x for x in e));self.assertTrue(any('PILOT_REQUIRED' in x for x in e))

    def test_different_audio_cannot_replace_confirmed_recording(self):
        b=agreed_fixture();song=self.temp/'song.wav';song.write_bytes(b'synthetic input A');other=self.temp/'other.wav';other.write_bytes(b'synthetic input B')
        b['music'].update(source='provided',audio=str(song),audio_sha256=sha(song));b['content_confirmation']['content_sha256']=content_digest(b);bind_confirmation(b,self.temp)
        self.assertTrue(any('differs' in x for x in entry_errors(b,self.temp,audio=str(other))))

    def test_cli_audio_requires_a_bound_recording_even_in_a_provisional_study(self):
        b=agreed_fixture();b['music'].update(source='pending',audio=None);bind_confirmation(b,self.temp)
        self.assertTrue(any('selected recording' in x for x in entry_errors(b,self.temp,audio='unselected.wav')))

    def test_blocking_question_blocks_actual_scaffold(self):
        b=agreed_fixture();b['open_questions']=[{'question':'Which ending?','blocking':True,'resolved':False}]
        r,p=self.scaffold(b);self.assertNotEqual(r.returncode,0);self.assertIn('Which ending',r.stderr);self.assertFalse(p.exists())

    def test_selected_output_fps_is_not_silently_overridden(self):
        b=agreed_fixture();bind_confirmation(b,self.temp)
        self.assertTrue(any('fps' in x for x in entry_errors(b,self.temp,fps=12)))
        self.assertTrue(any('dimensions' in x for x in entry_errors(b,self.temp,resolution=[100,100])))

    def test_full_timeline_is_measured_against_actual_recording(self):
        t=contract_fixtures.ToolkitTests();t.setUp()
        try:
            b=agreed_fixture();b['phase']='full';b['execution']['authorized_scope']='full';audio=t.temp/'runtime-tones.wav';b['music'].update(source='provided',audio=str(audio),audio_sha256=sha(audio));b['content_confirmation']['content_sha256']=content_digest(b);bind_confirmation(b,self.temp)
            self.assertTrue(any('timeline duration differs' in x for x in entry_errors(b,self.temp,timeline_duration=3)))
        finally:t.tearDown()

    def display_fixture(self):
        b=lyrical_fixture();b['lyrics']['mode']='full-lines'
        cues=[{'line_id':'line-1','start':0,'end':2,'text':'The corridor grows dark.'},{'line_id':'line-2','start':2,'end':4,'text':'A small light waits by the window.'}]
        p=self.temp/'display.json';p.write_text(json.dumps({'alignment_status':'ear_checked','alignment_evidence':'Synthetic known cue exercise, not an actual sung recording','cues':cues}), encoding='utf-8')
        b['lyrics']['display_document']={'path':str(p),'sha256':sha(p)}
        return b,p

    def test_full_subtitles_need_all_canonical_lines(self):
        b,p=self.display_fixture();self.assertEqual(subtitle_errors(b,self.temp,'production'),[])
        for cues in ([],json.loads(p.read_text(encoding='utf-8'))['cues'][:1]):
            p.write_text(json.dumps({'cues':cues}), encoding='utf-8');b['lyrics']['display_document']['sha256']=sha(p)
            self.assertTrue(subtitle_errors(b,self.temp,'production'))

    def test_display_text_order_and_alignment_cannot_drift(self):
        for mode in ('wrong-text','reorder','unreviewed'):
            b,p=self.display_fixture();data=json.loads(p.read_text(encoding='utf-8'))
            if mode=='wrong-text':data['cues'][0]['text']='invented other lyric'
            if mode=='reorder':data['cues'].reverse()
            if mode=='unreviewed':data['alignment_status']='estimated'
            p.write_text(json.dumps(data), encoding='utf-8');b['lyrics']['display_document']['sha256']=sha(p)
            self.assertTrue(subtitle_errors(b,self.temp,'production'))

    def test_new_text_requirement_cannot_reuse_nontext_review(self):
        t=contract_fixtures.ToolkitTests();t.setUp()
        try:
            p=t.fixture();b=json.loads((p/'brief.json').read_text(encoding='utf-8'));b['lyrics']['mode']='in-world';b['content_confirmation']['content_sha256']=content_digest(b);bind_confirmation(b,p);(p/'brief.json').write_text(json.dumps(b), encoding='utf-8')
            self.assertTrue(any('text' in x for x in C.inspect(p,'prototype')['errors']))
        finally:t.tearDown()

    def test_selected_font_is_measured_not_assumed_from_name(self):
        from font_check import inspect_font
        font=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
        if not font.exists():self.skipTest('portable negative font fixture unavailable on this host')
        text=self.temp/'original-cjk.json';text.write_text(json.dumps({'lines':[{'id':'a','text':'窗边还有一盏灯。'}]},ensure_ascii=False), encoding='utf-8')
        result=inspect_font(font,text);self.assertFalse(result['ok']);self.assertTrue(result['missing'])
        text.write_text(json.dumps({'lines':[{'id':'a','text':'TIME'}]}), encoding='utf-8');self.assertTrue(inspect_font(font,text)['ok'])

    def test_real_cjk_font_covers_original_chinese_lines(self):
        from font_check import inspect_font
        font=Path(os.environ.get('MV_CJK_FONT','/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'))
        if not font.is_file():self.skipTest('selected CJK font is not installed on this destination')
        doc=self.temp/'original-cjk.json';doc.write_text(json.dumps({'lines':[{'id':'a','text':'窗边还有一盏灯。'},{'id':'b','text':'我沿着微光慢慢往前走。'}]},ensure_ascii=False), encoding='utf-8')
        d=inspect_font(font,doc);self.assertTrue(d['ok']);self.assertEqual(d['missing'],[])

    def test_legacy_digest_migration_does_not_grant_new_authorization(self):
        from migrate_confirmation import legacy_digest
        b=agreed_fixture();b['content_confirmation']['content_sha256']=legacy_digest(b);b['execution']['production_authorized']=False
        source=self.temp/'old.json';source.write_text(json.dumps(b), encoding='utf-8');out=self.temp/'new.json'
        r=subprocess.run([sys.executable,str(ROOT/'scripts/migrate_confirmation.py'),str(source),'--out',str(out)],capture_output=True,text=True, encoding='utf-8')
        self.assertEqual(r.returncode,0,r.stderr);d=json.loads(out.read_text(encoding='utf-8'));self.assertFalse(d['execution']['production_authorized']);self.assertEqual(d['content_confirmation']['content_sha256'],content_digest(d))
        b['content']['core_idea']='unaccepted change';source.write_text(json.dumps(b), encoding='utf-8');r=subprocess.run([sys.executable,str(ROOT/'scripts/migrate_confirmation.py'),str(source),'--out',str(self.temp/'blocked.json')],capture_output=True,text=True, encoding='utf-8');self.assertNotEqual(r.returncode,0)

    def test_plain_lyrics_keep_repeated_lines_without_inventing_timing(self):
        source=self.temp/'original.txt';source.write_text('窗边的灯\n\n窗边的灯\n我沿着光往前走\n', encoding='utf-8');out=self.temp/'canonical.json'
        subprocess.run([sys.executable,str(ROOT/'scripts/prepare_lyrics.py'),str(source),'--out',str(out)],check=True,capture_output=True)
        d=json.loads(out.read_text(encoding='utf-8'));self.assertEqual(len(d['lines']),3);self.assertEqual(d['lines'][0]['text'],d['lines'][1]['text']);self.assertNotEqual(d['lines'][0]['id'],d['lines'][1]['id']);self.assertNotIn('cues',d)


@unittest.skipUnless(os.environ.get('MV_CANVAS_MODULE'),'optional native Canvas dependency not selected')
class NativeExecutionTests(unittest.TestCase):
    setUp=ExecutionTests.setUp
    tearDown=ExecutionTests.tearDown
    scaffold=ExecutionTests.scaffold
    def render(self,project,*extra):
        return subprocess.run(['node',str(ROOT/'scripts/render_canvas.mjs'),'--project='+str(project),'--canvas-module='+os.environ['MV_CANVAS_MODULE'],*extra],capture_output=True,text=True, encoding='utf-8')

    def test_range_estimate_resume_and_changed_source(self):
        project=self.temp/'native'
        subprocess.run([sys.executable,str(ROOT/'scripts/scaffold.py'),str(project),'--tool-self-test','--engine','canvas2d','--duration','2','--fps','12','--width','64','--height','64'],capture_output=True,check=True)
        (project/'src/scene.js').write_text("globalThis.drawFrame=(c,t)=>{c.fillStyle='#ddd';c.fillRect(0,0,64,64);c.fillStyle='#222';c.fillRect(t*10,20,10,10);};", encoding='utf-8')
        r=self.render(project,'--out=out/partial','--range=0.5:1.5','--resume');self.assertEqual(r.returncode,0,r.stderr)
        report=json.loads((project/'out/partial/render-report.json').read_text(encoding='utf-8'));self.assertEqual(report['frames'],12);self.assertEqual(report['range'],[.5,1.5])
        r=self.render(project,'--out=out/partial','--range=0.5:1.5','--resume');self.assertEqual(r.returncode,0,r.stderr)
        report=json.loads((project/'out/partial/render-report.json').read_text(encoding='utf-8'));self.assertEqual(report['reused_frames'],12)
        frame=next((project/'out/partial/frames').glob('*.png'));frame.write_bytes(b'corrupt')
        r=self.render(project,'--out=out/partial','--range=0.5:1.5','--resume');self.assertEqual(r.returncode,0,r.stderr)
        self.assertEqual(json.loads((project/'out/partial/render-report.json').read_text(encoding='utf-8'))['reused_frames'],11)
        r=self.render(project,'--estimate','--range=0:1','--out=out/estimate');self.assertEqual(r.returncode,0,r.stderr);self.assertEqual(json.loads(r.stdout)['frames'],12);self.assertFalse((project/'out/estimate').exists())
        r=self.render(project,'--range=0:1','--out=out/budget','--max-cache-bytes=1');self.assertNotEqual(r.returncode,0);self.assertIn('budget',r.stderr);self.assertFalse((project/'out/budget').exists())
        (project/'src/scene.js').write_text((project/'src/scene.js').read_text(encoding='utf-8')+'\n// changed', encoding='utf-8')
        r=self.render(project,'--out=out/partial','--range=0.5:1.5','--resume');self.assertNotEqual(r.returncode,0);self.assertIn('changed',r.stderr)

    def test_unknown_render_option_is_not_silently_ignored(self):
        r=self.render(self.temp,'--ragne=0:1');self.assertNotEqual(r.returncode,0);self.assertIn('unsupported',r.stderr)

    def test_range_audio_uses_the_same_source_interval(self):
        import array
        from runtime_smoke import pulses
        project=self.temp/'range-audio'
        subprocess.run([sys.executable,str(ROOT/'scripts/scaffold.py'),str(project),'--tool-self-test','--engine','canvas2d','--duration','2','--fps','12','--width','64','--height','64'],check=True,capture_output=True)
        pulses(project/'assets/pulses.wav')
        r=self.render(project,'--out=out/trim','--range=0.5:1','--audio=assets/pulses.wav');self.assertEqual(r.returncode,0,r.stderr)
        pcm=array.array('h',subprocess.check_output(['ffmpeg','-v','error','-i',str(project/'out/trim/clip.mp4'),'-ar','8000','-ac','1','-f','s16le','-']))
        self.assertGreater(max(abs(x) for x in pcm[:1600]),3000,'pulse at source 0.5s must be at the start of the trimmed output')

    def test_observed_pilot_allows_full_render_with_selected_audio_automatically(self):
        import wave,array,math
        audio=self.temp/'original-test.wav'
        with wave.open(str(audio),'wb') as w:
            w.setparams((1,2,8000,0,'NONE','not compressed'));w.writeframes(array.array('h',(int(2000*math.sin(i*2*math.pi*440/8000)) for i in range(16000))).tobytes())
        b=agreed_fixture();b['execution'].update(authorized_scope='full',authorized_duration=2);b['music'].update(source='provided',kind='instrumental',audio=str(audio),audio_sha256=sha(audio));b['content_confirmation']['content_sha256']=content_digest(b)
        r,p=self.scaffold(b,width=320,height=180,fps=12);self.assertEqual(r.returncode,0,r.stderr)
        C.initialize(p,ROOT);spec=C.load(p/'visual-spec.json');spec.update(status='locked',revision='synthetic-fixture');spec['design'].update(palette=['#fff','#222'],shape_language='square',composition='center',motion='static synthetic fixture');spec['evidence']=[{'path':'src/scene.js','sha256':sha(p/'src/scene.js')}];(p/'visual-spec.json').write_text(json.dumps(spec), encoding='utf-8')
        r=self.render(p,'--out=out/pilot');self.assertEqual(r.returncode,0,r.stderr);report=C.load(p/'out/pilot/render-report.json')
        mapping={'duration':2,'duration_status':'prototype','sections':[{'id':'a','start':0,'end':2}],'shots':[{'id':'s','start':0,'end':2,'section_id':'a','objective':'synthetic test','visible_change':'fixture only','assets':[]}]};(p/'shot-map.json').write_text(json.dumps(mapping), encoding='utf-8')
        review={'scope':'prototype','reviewer':'synthetic validator fixture, not a real aesthetic acceptance','target':{'path':'out/pilot/clip.mp4','sha256':sha(p/'out/pilot/clip.mp4'),'input_digest':report['input_digest']},'checks':[{'id':key,'status':'pass','notes':'Synthetic record validates the workflow only','range':[0,2],'evidence':['out/pilot/clip.mp4']} for key in spec['required_checks']],'issues':[]};(p/'review.json').write_text(json.dumps(review), encoding='utf-8')
        (p/'runtime-report.json').write_text(json.dumps({'status':'passed','engine':'canvas2d','runtime_backend':'node-canvas','encoded':report['encoded'],'artifact':{'path':'out/pilot/clip.mp4','sha256':sha(p/'out/pilot/clip.mp4')}}), encoding='utf-8')
        from pilot_gate import promote
        promote(p);new=C.load(p/'brief.json')
        from workflow_fixtures import video_stage
        video_stage(new,p,'prototype','out/pilot/clip.mp4','out/pilot/render-report.json')
        new['phase']='animatic';(p/'brief.json').write_text(json.dumps(new), encoding='utf-8')
        r=self.render(p,'--out=out/rough');self.assertEqual(r.returncode,0,r.stderr)
        video_stage(new,p,'animatic','out/rough/clip.mp4','out/rough/render-report.json')
        new['phase']='full';(p/'brief.json').write_text(json.dumps(new), encoding='utf-8')
        r=self.render(p,'--out=out/full');self.assertEqual(r.returncode,0,r.stderr)
        full=C.load(p/'out/full/render-report.json');self.assertTrue(full['encoded']['audio']);self.assertEqual(full['audio']['sha256'],sha(audio));self.assertEqual(full['project_acceptance'],'not_assessed')

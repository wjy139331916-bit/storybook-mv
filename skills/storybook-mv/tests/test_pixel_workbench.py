"""Pixel tools are exercised with original assets and synthetic workflow records only."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'tests')]
import pixel_workbench as W
from test_content_gate import agreed_fixture, bind_confirmation


class PixelWorkbenchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='mv-pixel-')
        self.path = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def command(self, *args):
        return subprocess.run([sys.executable, str(ROOT / 'scripts/pixel_workbench.py'), *map(str, args)], capture_output=True, text=True, encoding='utf-8')

    def project(self, phase='design', approved=False):
        b = agreed_fixture()
        bind_confirmation(b, self.path)
        b['phase'] = phase
        if not approved:
            b['workflow']['packages'].clear()
            b['workflow']['approvals'].clear()
        (self.path / 'brief.json').write_text(json.dumps(b), encoding='utf-8')
        return b

    def test_original_seed_is_valid_and_renders_distinct_static_poses(self):
        d = W.seed()
        images = [W.raster(d, f) for f in d['frames']]
        self.assertEqual(images[0].size, (48, 64))
        self.assertGreater(len(set(im.tobytes() for im in images)), 3)

    def test_unknown_palette_entry_and_ragged_rows_rejected(self):
        for rows in (['?'], ['III', 'II']):
            d = W.seed(); d['layers'][0]['rows'] = rows
            with self.assertRaises(ValueError): W.validate(d)

    def test_safe_unique_ids_and_known_action_references_required(self):
        for bad in ('../outside', '__proto__', 'constructor'):
            d = W.seed(); d['frames'][0]['id'] = bad
            with self.assertRaises(ValueError): W.validate(d)
        d = W.seed(); d['actions']['walk'] = ['absent']
        with self.assertRaises(ValueError): W.validate(d)

    def test_noninteger_offsets_and_missing_contact_anchors_rejected(self):
        d = W.seed(); d['frames'][0]['layers'] = {'head': {'dx': 0.5}}
        with self.assertRaises(ValueError): W.validate(d)
        d = W.seed(); del d['frames'][0]['anchors']['grip']
        with self.assertRaises(ValueError): W.validate(d)

    def test_js_and_python_render_the_same_pixels_including_flips(self):
        d = W.seed(); d['frames'][0]['layers'] = {'face': {'flip_x': True, 'dx': 1, 'dy': -1}}
        code = 'const m=require(process.argv[2]);let s="";for await(const c of process.stdin)s+=c;const d=m.validate(JSON.parse(s));process.stdout.write(Buffer.from(m.pixels(d,d.frames[0])));'
        # A .cjs entry supports top-level async without any optional canvas package.
        script = self.path / 'compare.cjs'
        script.write_text('(async()=>{' + code + '})();', encoding='utf-8')
        r = subprocess.run(['node', str(script), str(ROOT / 'assets/pixel-workbench/core.js')], input=json.dumps(d).encode(), capture_output=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, W.raster(d, d['frames'][0]).tobytes())

    def test_direction_acceptance_generates_static_workspace_only(self):
        self.project()
        before = (self.path / 'brief.json').read_bytes()
        r = self.command('init', '--project', self.path, '--out', 'assets/actor-r1')
        self.assertEqual(r.returncode, 0, r.stderr)
        target = self.path / 'assets/actor-r1'
        self.assertTrue((target / 'design-board.png').is_file())
        self.assertFalse((target / 'sprites.png').exists())
        self.assertFalse(json.loads((target / 'workbench-report.json').read_text())['motion_enabled'])
        self.assertEqual(before, (self.path / 'brief.json').read_bytes())

    def test_motion_cannot_be_requested_in_design_phase(self):
        self.project(); (self.path / 'character.json').write_text(json.dumps(W.seed()))
        r = self.command('build', '--project', self.path, '--model', 'character.json', '--out', 'forbidden', '--mode', 'motion')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('DESIGN_STILLS_ONLY', r.stderr)
        self.assertFalse((self.path / 'forbidden').exists())

    def test_prototype_without_design_acceptance_is_blocked(self):
        self.project('prototype'); (self.path / 'character.json').write_text(json.dumps(W.seed()))
        r = self.command('build', '--project', self.path, '--model', 'character.json', '--out', 'forbidden', '--mode', 'motion')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('DESIGN_USER_APPROVAL_REQUIRED', r.stderr)

    def test_accepted_synthetic_design_enables_asset_motion_not_user_consent(self):
        self.project('prototype', approved=True); (self.path / 'character.json').write_text(json.dumps(W.seed()))
        before = (self.path / 'brief.json').read_bytes()
        r = self.command('build', '--project', self.path, '--model', 'character.json', '--out', 'motion-r1', '--mode', 'motion')
        self.assertEqual(r.returncode, 0, r.stderr)
        target = self.path / 'motion-r1'
        self.assertTrue((target / 'sprites.png').exists())
        meta = json.loads((target / 'assets.json').read_text())
        self.assertEqual(meta['acceptance'], 'not_reviewed')
        self.assertEqual(meta['frames'][0]['anchors']['foot'], [24, 62])
        self.assertEqual(before, (self.path / 'brief.json').read_bytes())

    def test_changed_design_approval_cannot_enable_motion(self):
        b = self.project('prototype', approved=True)
        b['style']['palette'] = ['#123456']
        (self.path / 'brief.json').write_text(json.dumps(b))
        with self.assertRaisesRegex(ValueError, 'Production blocked'): W.authorized(self.path, 'motion', W.seed())

    def test_action_preview_must_fit_pilot_and_eight_second_limit(self):
        self.project('prototype', approved=True)
        d = W.seed(); d['actions']['walk'] = ['front'] * 64
        with self.assertRaisesRegex(ValueError, 'eight'): W.authorized(self.path, 'motion', d)
        d['actions']['walk'] = ['front'] * 40  # 6.4s exceeds the fixture's 6s pilot.
        with self.assertRaisesRegex(ValueError, 'Production blocked'): W.authorized(self.path, 'motion', d)

    def test_existing_work_preserved_and_new_revision_available(self):
        target = self.path / 'existing'; target.mkdir(); (target / 'valuable.txt').write_text('keep')
        with self.assertRaisesRegex(ValueError, 'preserved'): W.safe_output(target)
        self.assertEqual(W.safe_output(target, new_revision=True).name, 'existing-r2')
        self.assertEqual((target / 'valuable.txt').read_text(), 'keep')

    def test_output_cannot_escape_project_or_enter_skill(self):
        for target in (self.path, self.path / '../escape', ROOT / 'assets/generated'):
            with self.assertRaises(ValueError): W.safe_output(target, self.path)

    def test_isolated_self_test_cannot_select_user_project(self):
        r = self.command('init', '--project', self.path, '--out', 'wrong', '--tool-self-test')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('cannot select a user project', r.stderr)

    def test_user_model_cannot_be_relabelled_an_isolated_example(self):
        model = self.path / 'real.json'; model.write_text(json.dumps(W.seed()))
        r = self.command('build', '--model', model, '--out', self.path / 'wrong', '--tool-self-test')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('isolated workbench example', r.stderr)

    def test_failed_build_cleans_its_own_temp_without_touching_existing_files(self):
        from unittest.mock import patch
        target = self.path / 'failed'
        with patch.object(W, 'raster', side_effect=ValueError('synthetic failure')):
            with self.assertRaises(ValueError): W.build(W.seed(), target, 'design')
        self.assertFalse(target.exists())
        self.assertFalse(list(self.path.glob('.pixel-build-*')))

    def test_browser_document_is_offline_and_script_injection_is_escaped(self):
        d = W.seed(); d['name'] = '</script><script>window.injection=true</script>'
        W.build(d, self.path / 'static', 'design')
        html = (self.path / 'static/workbench.html').read_text()
        self.assertNotIn('</script><script>window.injection', html)
        self.assertIn("connect-src 'none'", html)
        self.assertNotIn('src="http', html)

    def test_sprite_adapter_uses_timing_and_world_anchors(self):
        code = "const p=require(process.argv[1]);const m={sheet:{},frames:[{id:'a',duration_ms:100,rect:{x:0,y:0,w:4,h:4},anchors:{foot:[2,4],grip:[3,2]}},{id:'b',duration_ms:200,rect:{x:4,y:0,w:4,h:4},anchors:{foot:[2,4],grip:[3,2]}}],actions:{walk:['a','b']}};const calls=[];const c={save(){},restore(){},drawImage(...a){calls.push(a)}};const result=p.draw(c,{},m,'a',100,200,2);console.log(JSON.stringify([p.frameAt(m,'walk',.12).id,p.frameAt(m,'walk',.31).id,result,calls[0].slice(-4)]));"
        r = subprocess.run(['node', '-e', code, str(ROOT / 'assets/pixel-workbench/player.js')], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout), ['b', 'a', {'foot': [100, 200], 'grip': [102, 196]}, [96, 192, 8, 8]])


if __name__ == '__main__':
    unittest.main()

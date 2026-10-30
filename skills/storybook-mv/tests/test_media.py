"""Generated media fixtures test measurement behavior, never aesthetic verdicts."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import wave

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import media_audit as A
import music_grid as G
import import_srt as S
import review_notes as N
import project_contracts as C


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'FFmpeg/FFprobe required')
class MediaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = Path(tempfile.mkdtemp(prefix='mv-media-fixture-'))
        cls.video = cls.base / 'cuts.mp4'
        A.command(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'color=c=red:s=320x180:r=12:d=4', '-f', 'lavfi', '-i', 'color=c=black:s=320x180:r=12:d=2', '-f', 'lavfi', '-i', 'color=c=blue:s=320x180:r=12:d=4', '-filter_complex', '[0:v][1:v][2:v]concat=n=3:v=1:a=0[v]', '-map', '[v]', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', str(cls.video)])
        rate, duration = 8000, 12
        rng = np.random.default_rng(123)
        levels = rng.uniform(.03, .8, duration * 10)
        t = np.arange(rate * duration) / rate
        env = np.interp(t, np.arange(len(levels)) / 10, levels)
        samples = (env * np.sin(2 * np.pi * 433 * t) * 25000).astype('<i2')
        cls.audio = cls.base / 'original.wav'
        with wave.open(str(cls.audio), 'wb') as f:
            f.setnchannels(1); f.setsampwidth(2); f.setframerate(rate); f.writeframes(samples.tobytes())
        cls.shifted = cls.base / 'delayed.m4a'
        A.command(['ffmpeg', '-v', 'error', '-i', str(cls.audio), '-af', 'adelay=130', '-t', '12', '-c:a', 'aac', str(cls.shifted)])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.base)

    def setUp(self):
        self.temp = Path(tempfile.mkdtemp(prefix='mv-media-test-'))

    def tearDown(self):
        shutil.rmtree(self.temp)

    def test_reference_candidates_and_intentional_hold(self):
        out = A.output_dir(self.temp / 'review')
        result = A.video_audit(self.video, out, sample_fps=12, policy={'intentional_ranges': [{'range': [0, 4], 'categories': ['low_change'], 'reason': 'fixture intentionally held'}]})
        self.assertTrue(any(abs(x - 4) < .2 for x in result['cut_candidates']))
        self.assertTrue(any(x['category'] == 'near_black' for x in result['findings']))
        self.assertTrue(any(x['disposition'] == 'declared_intent' for x in result['findings']))
        self.assertIsNone(result['manual_analysis']['camera'])
        self.assertTrue((out / 'contact-sheet.jpg').is_file())

    def test_crop_is_validated_and_existing_evidence_preserved(self):
        out = A.output_dir(self.temp / 'review')
        (out / 'evidence.txt').write_text('accepted', encoding='utf-8')
        with self.assertRaises(ValueError):
            A.output_dir(out)
        with self.assertRaises(ValueError):
            A.crop_filter('300,0,100,100', {'width': 320, 'height': 180})
        self.assertEqual((out / 'evidence.txt').read_text(encoding='utf-8'), 'accepted')

    def test_comparison_fits_aspects_without_replacing_sources(self):
        r, v = self.temp / 'ref.png', self.temp / 'render.png'
        Image.new('RGB', (200, 400), 'red').save(r)
        Image.new('RGB', (400, 200), 'blue').save(v)
        result = A.compare_images(r, v, A.output_dir(self.temp / 'cmp'))
        self.assertEqual(result['reference_sha256'], A.sha(r))
        with Image.open(self.temp / 'cmp/compare.png') as image:
            self.assertEqual(image.size, (1280, 480))

    def test_audio_delay_and_loudness_are_measured(self):
        result = A.audio_audit(self.audio, self.shifted, A.output_dir(self.temp / 'audio'))
        informative = [x['encoded_delay_seconds'] for x in result['anchors'] if x['encoded_delay_seconds'] is not None]
        self.assertGreaterEqual(len(informative), 2, result)
        self.assertTrue(all(abs(x - .13) <= .025 for x in informative), result)
        self.assertIsNotNone(result['lufs_difference'])

    def test_nonzero_audio_excerpt_keeps_its_selected_timeline(self):
        excerpt=self.temp/'excerpt.m4a'
        A.command(['ffmpeg','-v','error','-i',str(self.audio),'-af','atrim=start=4:duration=3,asetpts=PTS-STARTPTS','-c:a','aac',str(excerpt)])
        result=A.audio_audit(self.audio,excerpt,A.output_dir(self.temp/'excerpt-audit'),audio_start=4)
        informative=[x['encoded_delay_seconds'] for x in result['anchors'] if x['encoded_delay_seconds'] is not None]
        self.assertTrue(informative,result);self.assertTrue(all(abs(x)<=.025 for x in informative),result)

    def test_silence_does_not_produce_a_confident_grid(self):
        result = G.fit_grid(np.zeros(8000 * 3))
        self.assertEqual(result['status'], 'insufficient_transients')
        self.assertEqual(result['beats'], [])

    def test_hinted_grid_keeps_review_and_no_invented_downbeats(self):
        samples = np.zeros(8000 * 8)
        for t in np.arange(.2, 8, .625):
            i = int(t * 8000)
            n = min(100, len(samples) - i)
            samples[i:i + n] = np.hanning(n)
        result = G.fit_grid(samples, bpm=96, offset=.2)
        self.assertAlmostEqual(result['selected']['bpm'], 96)
        self.assertAlmostEqual(result['beats'][0], .2)
        self.assertTrue(result['review_needed'])
        self.assertEqual(result['downbeats'], [])

    def test_srt_preserves_lines_and_rejects_overlap(self):
        cues = S.parse('\ufeff1\n00:00:00,200 --> 00:00:01,500\n原创一句\nsecond line\n\n2\n00:00:02.000 --> 00:00:03.000\nEND\n')
        self.assertEqual(cues[0]['text'], '原创一句\nsecond line')
        self.assertEqual(cues[1]['start'], 2)
        with self.assertRaises(ValueError):
            S.parse('1\n00:00:00,000 --> 00:00:02,000\nA\n\n2\n00:00:01,000 --> 00:00:03,000\nB')
        with self.assertRaises(ValueError):
            S.seconds('00:70:00,000')

    def test_viewer_notes_bind_exact_video_and_preserve_old_record(self):
        p = self.temp / 'project'
        p.mkdir()
        shutil.copy2(self.video, p / 'video.mp4')
        review = {'target': {'path': 'video.mp4', 'sha256': A.sha(self.video)}, 'checks': [{'id': 'motion', 'status': 'fail'}], 'issues': [{'id': 'old', 'status': 'open'}]}
        (p / 'review.json').write_text(json.dumps(review), encoding='utf-8')
        notes = {'schema_version': 1, 'target': {'sha256': A.sha(self.video)}, 'notes': [{'id': 'viewer-1', 'range': [1, 2], 'severity': 'major', 'observation': 'fixture note'}]}
        merged, count = N.merge(p, notes)
        self.assertEqual(count, 1)
        self.assertEqual(merged['checks'][0]['status'], 'fail')
        self.assertEqual(len(C.load(p / 'review.json')['issues']), 1)
        notes['target']['sha256'] = 'another-version'
        with self.assertRaises(ValueError):
            N.merge(p, notes)

    def test_viewer_note_outside_video_is_rejected(self):
        p = self.temp
        shutil.copy2(self.video, p / 'video.mp4')
        (p / 'review.json').write_text(json.dumps({'target': {'path': 'video.mp4', 'sha256': A.sha(self.video)}}), encoding='utf-8')
        notes = {'schema_version': 1, 'target': {'sha256': A.sha(self.video)}, 'notes': [{'id': 'x', 'range': [8, 30], 'severity': 'major', 'observation': 'invalid'}]}
        with self.assertRaises(ValueError):
            N.merge(p, notes)


if __name__ == '__main__':
    unittest.main(verbosity=2)

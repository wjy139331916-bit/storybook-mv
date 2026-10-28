# Song, lyric and timeline timing

Use the actual final recording as master timebase. Measure it with FFprobe. Mark tempo/sections measured or provisional; cast work and labelled silent tests may precede the audio.

Use `scripts/analyze_music.py` for optional metadata/RMS/change guides, and map reviewed sections to visual development in `shot-map.json`. Energy rises are candidates, not measured musical beats. Follow the main skill's music-direction reference for repetition, motifs and instrumental progression.

When useful, run `scripts/music_grid.py <audio> --out <new-grid.json> [--bpm 96 --first-beat 0.2]`. This proposes a constant-tempo grid from transients, retains alternatives and checks residual candidates at three regions. Half/double tempo and variable-tempo recordings need listening and possibly a piecewise grid; do not infer meter/downbeats from this tool. Supplied hints remain labelled. Do not make every cut land on every beat.

For supplied SRT use `scripts/import_srt.py <lyrics.srt> --out <new-cues.json> [--audio <chosen-recording>]`. It preserves line text/timestamps, rejects overlaps for review and marks text/timing unverified. It never invents word timing. Keep recognition/forced alignment optional and compare with canonical text and the actual recording before claiming accuracy.

When aligning against a vocal stem, verify its offset from the mix. Automated recognition is a draft; compare with canonical lyrics and the recording.

```bash
python3 <skill-dir>/scripts/import_lrc.py song.lrc --duration 240 --out data/lyrics.json --js-out src/data/lyrics.js
```

Replace 240 with measured duration. `--offset 0.2` delays display by 0.2 seconds; negative values advance it. Embedded LRC offset tags are reported, not silently applied, because conventions/prior corrections vary. Choose an explicit offset after checking the recording.

Import multiple timestamps per line, repeats and UTF-8 Chinese. Ends are provisional next-cue/final-duration boundaries; review silence, long holds and final release. `alignment_status=lrc_unverified` must not be described as ear-checked.

```json
{"duration":24,"alignment_status":"lrc_unverified","cues":[{"start":1,"end":4,"text":"原创测试文字"}]}
```

Follow the selected lyric policy: full lines, key lines, environmental text, or no visible lyrics. When full lines are selected, wrap and flag overflow; never truncate to hide a layout issue. Require measured word/syllable timing for accurate karaoke; character counts do not measure singing.

Heavy forced alignment is optional; consult the attributed upstream `ai-music-video` alignment reference when line cues are insufficient. Do not add Torch, model downloads or paid APIs to a simple LRC workflow by default.

Timeline schema:

```json
{"duration":24,"shots":[{"id":"s01","start":0,"end":8,"action":"arrive"},{"id":"s02","start":8,"end":24,"action":"respond"}]}
```

```bash
python3 <skill-dir>/scripts/check_project.py --shots data/shots.json --lyrics data/lyrics.json --duration 24
```

Use consecutive nonoverlapping shot intervals covering the duration; describe transition windows explicitly. Instrumental time may have no lyric cue. The validator checks numerical structure, not musical rhythm/meaning.

Render timeline changes in an animatic. Check exact transitions/captions at target resolution. Compare every lyric line and retain known-issue timestamps for full-song delivery.

# Inspect actual output and collect useful repair evidence

Load at prototype/full review. Keep artist observations, viewer acceptance and numerical measurements separate. Existing `review.json` records remain authoritative for issues; a new diagnostic report does not automatically make checks pass.

Optional Python tools need `scripts/requirements-media.txt` (NumPy and Pillow), FFmpeg and FFprobe. Check the selected environment and install only required packages within existing authorization. Planning and the basic schema tools do not require every media dependency.

Add `--media-tools` to the selected route's `preflight.py` command to probe these optional imports. Presence checks do not replace the actual diagnostic/render tests.

```bash
python3 <skill>/scripts/media_audit.py inspect <render.mp4> --out <project>/out/review-r1 --shot-map <project>/shot-map.json
python3 <skill>/scripts/media_audit.py audio <final-audio> <render.mp4> --out <project>/out/audio-r1
```

The video report flags low-change ranges, near-black frames and isolated large differences away from planned boundaries. It samples reduced-resolution decoded frames: inspect full-size details and consecutive frames around findings. Darkness, a long hold or a hard cut can be intentional. Do not enforce a universal one-second stillness limit, continuous camera motion, one cut per lyric, fixed scenery count or mandatory beat cuts.

Use an optional `--policy <file.json>` with explicit local exceptions:

```json
{"low_change_seconds":3,"intentional_ranges":[{"range":[12,14.5],"categories":["low_change"],"reason":"held reaction after the final word"}]}
```

Declared intent labels a finding; it does not remove it or certify artistic success. Inspect that range with the real soundtrack. Keep diagnostic thresholds and exception reasons in the project so another agent can reproduce the assessment.

The CPU renderer also writes `frame-audit.json` when the scene exposes `MV_FRAME_CHECKS`: actual drawing boxes, local pose signatures, reachability and contact points. Local-pose checks exclude root/camera motion. Missing metadata reports missing coverage; it never passes unseen layout/acting. Box overlap is a candidate, not semantic face/hand recognition. The existing full-line overlay detects overflow; CJK glyph shape and text/face relationships still need rendered inspection.

Audio review decodes the original and delivered audio, compares loudness, and estimates offset in early/middle/late windows using RMS envelopes. Periodic/silent audio can be ambiguous; preserve that result. A source/output match does not verify lyric onsets. Do not normalize every song to an arbitrary LUFS target or alter the original mix without the project's sound decision. For clips pass `--audio-start` so the source segment matches.

Open `assets/review-player.html` (copied into new demonstrations) for local playback, frame-step assistance, a loop range, optional synchronized comparison and timestamped notes. It uploads nothing. Browser frame steps can be approximate with compressed video; use the renderer for exact evidence. Feedback export includes the video's content hash and never edits project code.

Use only a preview environment permitted by the destination host. If browser/file policies block the player, record that interaction as unverified; do not bypass the restriction. `tests/player_browser.mjs` is an optional destination test, separate from the Python/CPU checks.

```bash
python3 <skill>/scripts/review_notes.py <review-notes.json> --project <project> --out <project>/review-with-notes.json
```

This creates a new review record only when feedback matches the exact reviewed video. It preserves earlier issues/checks and imports observations without inventing a diagnosis or marking a repair complete. Inspect the result before adopting it as the next project review.

Attach actual diagnostic reports with hashes to review evidence. When `review.json.diagnostics` is supplied, the contract checker verifies report freshness against the current target. Fix common causes, render affected intervals with joins, compare old/new output and renew evidence. A validator or metric pass never certifies beauty or natural acting.

# From recording to visible progression

Measure the chosen recording and preserve its digest. The original lightweight analyzer needs only Python, FFprobe and FFmpeg:

```bash
python3 <skill-dir>/scripts/analyze_music.py <final-audio> --out <project-dir>/data/music-analysis.json --plot <project-dir>/out/check/energy.svg
```

It records duration, stream facts, mono RMS energy windows and candidate rises. It does not recognize lyrics, find reliable beats, name sections or derive a story. Listen to confirm phrase entrances, breath/holds, instrumental changes and section boundaries. Keep provisional and reviewed markers distinct. Silence and low energy can carry emotional weight; RMS is not an emotion score.

Use `shot-map.json` to connect each measured/proposed section with its intended viewer response, visual development, motif, shot IDs and text treatment. For each important lyric/musical phrase decide whether it advances action, changes perspective, recalls an object, transforms a word, or deliberately holds. Do not cut every line or animate every beat automatically.

For repeated sections, state the intended variation or deliberate repetition. A recurring location may change occupancy, viewpoint or meaning; an abstract pattern may change topology/density; typography may change hierarchy or spatial behavior. Preserve a comprehensible progression through instrumental sections and an intentional ending or loop boundary.

Keep a line's complete subtitle separate from a selected word participating in the scene when the concept requires both. Do not produce contradictory duplicate text. Use measured word/syllable cues for precise word highlights; imported LRC and RMS candidates cannot provide them.

Review an animatic against the actual recording before filling the whole film with detailed art. Record known timing defects with timestamps. For a missing final recording, character/behavior studies may proceed when authorized, with provisional timing labelled; do not certify whole-song duration or sync.

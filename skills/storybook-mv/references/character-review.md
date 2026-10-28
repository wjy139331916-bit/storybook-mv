# Character design and visual review

## Cast design

Use the approved character proportion, anatomy and age cues. The bundled stylized humanoid helper is optional and is not a default for all styles. Establish front, three-quarter, side and back views as needed, plus a small readable set of emotional poses. Preserve hair, glasses, silhouette and costume identity.

For each cast member preserve only the project-approved identifiers. If glasses or accessories are part of that design, keep their shapes distinct and attach them, ears and hair to the head hierarchy; preserve eye readability when required. Render model sheets and a complete scene at final resolution; a correct head-count number alone does not establish a good design.

## Local geometry

Use head-height units and a foot/ground origin. `StoryRig.restPose(4.5)` is one optional stylized-human scaffold for a deliberately selected 4.5-head design, not finished art or a universal proportion. Map all points with `StoryRig.mapPoints`, or draw under one translate/rotate/uniform-scale parent.

Do not put screen y-values into local knees/ankles. Do not scale arms/trousers to reach props. Test poses before and after camera transforms. If the two-bone solver returns `reachable:false`, change blocking or the target instead of stretching.

For walking, stage support and swing phases. Plant the support foot in world space while weight moves, then transfer support. Add deliberate start/stop poses. Oscillating legs with a separately sliding root are insufficient evidence of walking.

Turn through key views and correct overlaps. Give hand transfer a preparation, contact, exchange and release. Attach the prop to its holding hand. Avoid transparent blends between full-body poses.

## Export actual pose evidence

```json
{"frames":[{"t":0,"characters":[{"id":"actor","head_px":80,"height_px":360,"heads":4.5,"limbs":[{"name":"forearm","a":[10,20],"b":[10,80],"length_px":60}]}]}]}
```

Run `node <skill-dir>/scripts/check_rig.mjs poses.json`, optionally passing `--min-heads` and `--max-heads` from the approved model. Export the coordinates actually used for drawing. This checks supplied ratios/lengths, not art quality or a drawing that ignores the metadata.

## Visual review

- Check silhouette, neck, shoulders and head/body ratio at wide and close scales.
- Inspect wrists, elbows, knees, ankles, contacts and feet shadows in strips.
- Check faces, eye targets, lens positions and hair across views.
- Make quiet acting purposeful; use eyes, breathing and pauses instead of universal idle wiggle.
- Keep paper/line noise mild and deterministic; compare repeated timestamps.
- Check subtitle wrapping, safety and scene keywords in the encoded file.

Fix a failed static pose in the drawing. Fix failed movement in key poses, timing or constraints. Higher fps, blur or camera motion cannot certify the fix.

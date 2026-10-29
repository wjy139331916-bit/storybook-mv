# Review, acceptance and bounded repairs

Review actual output at the relevant scale. Use full frames for composition, consecutive strips/playable clips for motion, full-resolution crops for contact/text, and the encoded file for delivery. A named reviewing agent may record visual judgments; do not mark checks observed if it only read code. User taste acceptance remains distinct from technical and artistic observations.

In `review.json`, record scope (`prototype`/`full`), reviewer and target `{path,sha256,input_digest}`. Get the current source/design digest with `project_contracts.py fingerprint --project <project>`. Match it to the render receipt; copying a new digest onto an old render is not a repair. Inspect source changes and render affected ranges before renewing the review.

Record checks as `{id,status,notes,evidence}` with status `pass`, `fail`, `unreviewed` or `not_applicable`. Explain non-applicability. Always review composition, style, motion, continuity and music as relevant; text is required when visible lyrics are selected. Add contact, pixel grid, glyphs, materials or another project-specific criterion. A purposeful hold can pass motion review if it supports the chosen language; do not require idle motion everywhere. No arbitrary numerical aesthetic score is a pass criterion.

For explicitly selected mandatory checks and automatically applicable acting/story/meaning/glyph checks, `not_applicable` cannot supply a pass. Remove an obsolete selected criterion only through the actual affected design decision; do not silently exempt it. Silent work may mark music inapplicable; absent visible text may mark text/glyph checks inapplicable.

Temporal passes (`motion`, `acting`, `contact`, `continuity`, `transition[s]`) include an inspected output-time `range:[start,end]` inside the actual encoded video, plus a playable video or a decoded strip. One still is insufficient. A strip uses `review.sequences` entries `{path,sha256,source_sha256,times:[...]}` with at least three increasing source-video output times; bind the actual image and current reviewed video's digest. Produce and inspect consecutive frames at the cadence needed for that action, not a montage of unrelated moments. This verifies record type/identity, not whether an agent actually looked or whether motion is natural.

```json
{"id":"contact","status":"fail","notes":"The prop leaves the giver before the receiver touches it.","evidence":["out/check/contact-strip.png","out/prototype.mp4"]}
```

Track defects without overwriting the history:

```json
{"id":"issue-01","severity":"major","status":"open","category":"contact","range":[3.4,3.9],"shot_ids":["s01"],"shared_assets":["prop-square"],"observation":"prop detaches during exchange","hypothesis":"ownership changes before contact","resolution":null,"evidence":["out/check/contact-strip.png"]}
```

Use stable issue IDs and retain pre/post revisions. `shared_assets` means the suspected reusable cause affects all shots using those logical asset IDs; omit it for a local timing defect. An observation and a code diagnosis are different claims. Resolve only with a concrete change, replacement evidence and re-inspection. Open blocker/major defects hold expansion of the affected work. Do not start a redundant user approval ritual for routine repairs already within scope.

```bash
python3 <skill-dir>/scripts/project_contracts.py repair --project <project> --out <new-repair-plan.json>
```

The repair plan includes affected shots, shared-asset propagation, adjacent cut margins and shots to preserve. Fix the common cause once, render affected ranges with joins, compare before/after and refresh the evidence. Use a new output directory/revision; stale cached frames cannot prove a fix. If repeated repair attempts cannot achieve the selected requirement, show the failed evidence and explain concrete scope/style/motion tradeoffs; do not silently change a locked decision.

After the representative agent checks, present the pilot and wait for its user acceptance; then make and present the whole-scope rough animatic and wait for that acceptance before fine full-timeline production. Follow user-stage-review.md. Technical checks alone cannot advance these stages. Whole-song delivery also requires measured final audio, full map coverage, applicable lyric review, join review and a playable encoded file. The validator checks records/freshness; it cannot make the film beautiful or certify unseen motion.

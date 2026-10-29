# Project visual and shot contracts

Create records in the project after the brief is useful; do not force a long technical form into the interview.

Before each user-video stage, follow user-stage-review.md and its actual artifact/user decision checks; the schema-5 content/song-understanding gates and scoped user authorization must be satisfied. A stored production boolean or a renderer passing its self-test is insufficient. `check --stage prototype|full` also checks the appropriate scope; an isolated tool self-test never passes a full commissioned-video contract. Recover real earlier acceptance during migration, or ask for the missing content confirmation.

```bash
python3 <skill-dir>/scripts/project_contracts.py init --project <project-dir>
```

This creates only missing `visual-spec.json`, `shot-map.json` and `review.json`. Existing files are preserved. Fill routine details as clearly labelled proposed implementation choices. Reuse accepted choices; ask only about material forks. Never keep private project inputs inside the reusable skill.

## Visual specification

Record a revision, draft/locked status, medium, selected palette or color rule, shape language, line/texture, composition, motion and text policy. `locked_choices` is an array of `{path,value}` entries copied from confirmed brief fields; it is not a source of new preferences. Update the decision record explicitly when a locked choice changes.

For characters, add stable cast IDs, distinguishing silhouettes/features/costumes, the selected proportion, model-sheet evidence and reusable asset IDs. For typography, abstract or spatial work use the corresponding type/grid/material/behavior rules instead; `characters_required:false` needs no cast. Add only relevant `required_checks`, e.g. `contact` for a prop transfer, `pixel_grid` for pixel work, or `glyphs` for CJK. Preserve font licenses; use approved local fonts and inspect actual glyphs.

Add rendered `evidence` entries `{path,sha256}` relative to the project. A source illustration or prompt alone is not proof of the selected renderer. Keep `brief_sha256` current after reconciling changes; do not silently relock a changed taste decision. Use `status:"locked"` for the established production design within existing authorization; reuse an actual acceptance of this same presented design/script package; a direction acceptance or an agent-written locked flag is not sufficient.

## Shot/music map

Set duration and `duration_status` to `prototype`, `recording_measured` or `agreed_scope` as appropriate. Record final `audio_sha256` for a real recording. `sections` and `shots` cover their declared scope in consecutive intervals. A prototype scope is not the full song.

```json
{"schema_version":1,"duration":6,"duration_status":"prototype","audio_sha256":null,
 "sections":[{"id":"part-a","start":0,"end":6,"music_read":"provisional build","emotion":"curiosity"}],
 "shots":[{"id":"s01","start":0,"end":6,"section_id":"part-a","objective":"make the exchange readable","visible_change":"approach, contact, transfer and release","lyric_ids":[],"motif":"square object","assets":["actor-a","actor-b","prop-square"],"transition":{"type":"cut","window":null}}]}
```

For non-narrative work replace the objective/event with the changing graphic state or a purposeful hold. A repeated section or shot uses `repeat_of` plus `variation`: new staging, perspective, relationship, graphic development or intended repetition. Do not invent variation just to avoid a repeated chorus; explain deliberate repetition. Add section/music evidence status and lyric links where used. For full production, validate the map against the actual final recording, not the reference or silent study.

```bash
python3 <skill-dir>/scripts/project_contracts.py check --project <project-dir> --stage design
python3 <skill-dir>/scripts/project_contracts.py check --project <project-dir> --stage prototype
python3 <skill-dir>/scripts/project_contracts.py check --project <project-dir> --stage full
```

These check structure and the freshness of recorded evidence. They cannot evaluate artistic quality. Missing/unreviewed fields do not pass. For legacy projects migrate incrementally, preserving code and accepted work; do not recreate or overwrite the project to get the new records.

For the schema-5 file/reply records and the source-bound `promote` checkpoint, follow the execution-gates reference linked directly from SKILL.md. Default stage changes never grant user approval.

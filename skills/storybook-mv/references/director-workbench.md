# Unified MV director workbench

Use this optional workbench after direction/content confirmation when structured scene editing fits the chosen visual approach. It extends the existing pixel editor, lyric tools and review workspace; it does not choose a style, invent a cast, convert arbitrary existing drawing code into editable layers, or authenticate acceptance. The agent prepares/imports the data and handles routine files. Users can inspect and adjust the result in an offline Chinese UI.

## Contents

- Seven modules and supported assets
- Build a static workspace
- Apply a saved revision and preview with the selected host
- Bind actual design sources before motion
- Recording, lyrics and source time
- Review notes and bounded repairs
- Portability and verification

## Seven modules and supported assets

| Module | Actual controls/data |
|---|---|
| Acting/contact | Keyed gaze/head/lean/hand/foot targets, hold/linear/smooth interpolation, simple ground pins, pixel pose selection, contact intervals and endpoint distances |
| Scene/camera | Reusable scenes, ordered layers, pointer placement, position/scale/rotation/visibility, pan/zoom keys, original primitive/character/text layers |
| Lyrics | Actual recording waveform, LRC/SRT/JSON line import, line dragging/retiming, manually timed word splits, reading layout and cue exports |
| Storyboard | Continuous shot timeline, duration exchange with adjacent shots, split/reorder, scene assignment and rough preview in the authorized stage |
| Transitions | A/B actual frames, crossfade/wipe/cut and a two-point position match; not arbitrary outline/CJK morphing |
| Assets/style | Shared rig/shape/text assets, existing pixel-character JSON, editable colors, duplicate/replace/export and affected-shot lookup |
| Review/repair | Exact-video hash binding, side-by-side playback, timestamped observations, source-relative note export and frame-aligned repair ranges with handles |

The schema is a deliberately scoped drawing interface. Original parameterized rigs are construction aids, not universal anatomy, automatic rigging, lip sync or natural acting. Pixel JSON reuses the pixel workbench's actual layers/poses/anchors. Integer placement/scaling and restrained transforms remain necessary for strict pixel rendering. A new project starts with empty scenes/assets or a bound existing director model; it never silently acquires the example cast/style.

Registered assets currently use simple parameterized rigs, rectangle/ellipse/line shapes, text and pixel-character models. An existing arbitrary Canvas/p5/3D asset needs an explicit adapter or data reconstruction with the agreed design preserved. The workbench is not a general SVG editor or a replacement for every artist tool.

## Build a static workspace

Continue the actual project/brief. Design requires the ordinary confirmed direction, but not a fabricated later acceptance.

    python3 <skill>/scripts/director_workbench.py init --project <project> --out plan/director-design-r1
    python3 <skill>/scripts/director_workbench.py build --project <project> --model plan/director-design-r1/director-edited.json --out plan/director-design-r2

Open the generated workbench.html through a host-accessible file/browser view. Save work as JSON; browser memory alone is not durable. The toolbar also exports a draft bundle and bounded still images. A JSON import cannot enable playback or change the page's generated stage scope. During design, audio listening and individual static frames remain available; character/rough-cut motion playback is disabled.

The browser app has no npm dependencies or external requests. The CLI uses Python 3 and Node to execute the same model validator as the actual drawing core. Audio waveform/recording/video inspection needs FFmpeg/FFprobe. Actual exports use the chosen existing renderer's dependencies. Chinese interface glyphs require a Chinese-capable browser font environment; a selected project font can be embedded privately. Do not bundle project audio/fonts/video inside the reusable skill.

For isolated technical validation only, init --tool-self-test creates the named original six-second example. A self-test build accepts only a saved model beside that owned marker, cannot select a user project, and remains labelled not_reviewed. It is not a way to avoid project questions or reviews.

## Apply a saved revision and preview with the selected host

    python3 <skill>/scripts/director_workbench.py apply --project <project> --workspace plan/director-design-r1 --model plan/director-design-r1/director-edited.json --out plan/director-r1
    python3 <skill>/scripts/director_workbench.py activate --project <project> --package plan/director-r1

Apply creates a NEW source package, model, impact report, shot-map/lyrics/performance drafts and repair data. It preserves the original project and does not write approvals. Workspace/source hashes prevent stale edits from silently replacing newer work. Existing destinations are preserved; use a new revision or --new-revision for build/apply.

Activation is an explicit adoption step for the selected Canvas2D or Remotion route. It backs up the previous entry/helper files under plan/director-activation/<revision>, installs a source-bound adapter, and retains the same host and soundtrack. It will not switch a painted/3D/custom project to Canvas. Other hosts may use the exported data with an explicit project adapter. Activation rejects conflicting cue policy, model/audio duration/aspect, missing accepted design sources and stale inputs. Partial writes restore the previous entry files; failed revision history is retained.

For a Canvas2D CPU project:

    node render_canvas.mjs --project=<project> --out=out/director-design-r1 --stills-only --times=0,2,4

For a Canvas2D browser project use the existing render.mjs still commands. For Remotion use its existing render.mjs --stills commands. The generated workbench and project adapter use the same director-core.js; save/edit/rebuild rather than treating an HTML mockup as the film.

After the appropriate acceptance, use the existing actual renderer with its allowed global range, soundtrack, selected font and encoded-output checks. Example only:

    node render_canvas.mjs --project=<project> --out=out/director-pilot-r1 --range=48:60
    node render.mjs --clip --range=48:60 --out=out/director-pilot-r1/clip.mp4

Use the project's actual accepted interval, not these numbers. For animatic the adapter generates a simplified rig/pixel blocking representation, preserves the aspect, caps dimensions at 960px and fps at 15. Inspect actual roughness; adding an engine or setting a label is not a substitute for a useful whole-song cut.

## Bind actual design sources before motion

Present actual design images AND the complete script/visual specification through the existing review workspace. Include the exact director model with its design source flag:

    python3 <skill>/scripts/review_workspace.py --project <project> present --stage design --revision design-r1 --proposal PROPOSAL.md --script plan/script.json --visual-spec visual-spec.json --frame out/design/key-01.png --source plan/director-r1/director.json --pilot-range 48:60 --objective "Inspect the actual hard action and transition" --limit "State real limitations."

The ordinary actual user reply accepts this specific package; the workbench never supplies it. Once accepted, build --mode motion from the current brief/model and a new workspace revision. Prototype playback stays inside the approved global pilot interval. Whole-scope moving rough preview becomes available only in the ordinary animatic/full stage, with its existing evidence.

The optional director-active.json is checked by the shared Python gate before all existing render entrypoints. It binds the model and drawing scripts, and compares the active static asset/layout/shot/lyric design with a real, hash-bound design_source artifact. Replacing colors/proportions/layout/story/order needs the appropriate design revision. Ordinary keyed mechanics, contact refinements and timestamped observations can be revised inside that accepted design and bounded sample. Those edits still do not approve the resulting pilot/animatic/full video. Technical resolution/fps, UI names and unused library entries are not aesthetic approval decisions.

The script's generated acceptance fields always remain not_reviewed. Keep real user review and observed agent findings in their existing records.

## Recording, lyrics and source time

Model duration and cue times use the selected recording's global seconds. Layer/camera keys use scene-local seconds from each shot plus its explicit scene_offset. Reordering video does not retime the song or canonical lyric text. The UI preserves total scope when exchanging neighboring shot lengths.

Imported line cues, dragged lines and manually split words remain unverified timing drafts. The workbench never derives real sung-character onsets from character count or waveform peaks. Word highlighting uses supplied word intervals; a multi-character word is a word-level unit, not certified character alignment. Compare early/middle/late anchors against the actual recording.

Before activation, adopt a checked cue revision through the ordinary canonical lyric workflow. Active captions must match that actual bound text/timing document and existing font/glyph checks. A saved flag alone does not verify singing. Keep original wording, cue IDs and real evidence; lyric text/meaning changes follow the content gate. No replacement song or universal beat-cut rule is introduced.

## Review notes and bounded repairs

For an exact project clip, build with --video <project-relative-file> and --video-range START:END. Its measured length must match the declared range. Whole-scope clips can infer [0, duration] only when their length matches. This is a source mapping, not independent sung-word/audio certification.

A project-bound video retains its declared global range in the editor; changing versions needs a new bound workspace. The review tab binds the actual video bytes, supports a second local comparison file and exports the existing review-notes schema. Notes are in global source time in the workbench; exported viewer notes subtract the clip start to match review_notes.py. Browser seeks are approximate with compressed video. Add --webm-preview when the browser cannot decode the MP4. The existing review helper creates/decodes a same-timeline WebM alternative, records its source hash, and embeds it while keeping feedback bound to the original master bytes.

    python3 <skill>/scripts/review_notes.py <viewer-notes.json> --project <project> --out review-with-director-notes.json

Import only notes for the exact current review target, preserve other findings, triage observations and render a new repair revision with adjacent handles. The repair plan does not overwrite the master, resolve old issues, approve a film, or certify repaired joins. Inspect the repaired clip and its integration with the original soundtrack.

## Portability and verification

Use the full exported skill and its manifest. Do not copy only this HTML template, omit the shared core/gate, or require the current chat's private paths. Production data live in each project. The reusable skill contains only original tool code, fixtures, contracts and named verification scope.

Run tests/test_director_v36.py for data/source/stage regressions, tests/director_browser.mjs for actual editor actions/save/import/playback/portrait layout, and tests/director_render.py for actual selected-host MP4/nonzero-source/audio verification. Browser and native passes are separate; Remotion needs its own real host exercise. A successful original fixture does not verify Android, arbitrary custom art, natural acting or an entire real sung MV.

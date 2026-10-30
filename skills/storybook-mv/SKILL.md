---
name: storybook-mv
description: "Direct music videos through adaptive questions, grounded song understanding and HARD user-review gates: direction → complete script plus actual design frames → pilot → whole-scope rough animatic → final production. Use for MV方案、视频风格选择、提问确认内容、理解歌词、代码MV、歌词视频、动画分镜, style comparisons, acting, diagnostics and cross-agent handoff. No fixed style/engine. Direction approval authorizes design only; AI self-review is never user approval. Basic song/length/aspect answers never authorize an invented full MV; resolve material meaning ambiguities with user choices and produce only confirmed content within explicit scope. Includes code packs, demos, contracts and tests."
---

# MV 创作导演

Start with the user's desired experience and constraints, not a rendering template. Discover and understand the song → confirm direction → present complete script and actual design → wait for user acceptance → pilot → wait → whole-scope rough animatic → wait → fine production and bounded repair.

Keep the handle `storybook-mv` for compatibility. It no longer implies storybook art or a default body proportion.

## 硬约束：使用者逐阶段验收，方向确认只放行设计

Read [user-stage review and artifact contracts](references/user-stage-review.md) before producing any project artifact. Use schema 5; preserve real earlier direction acceptance without inventing later approvals. Default workflow:

| Current work | Present to the user | Stop before advancing |
|---|---|---|
| Discovery and supported song reading | Exact content/theme/style candidates and scope recap | User confirms direction; this permits design only |
| Design | Complete target-scope script/shot table, proposal, actual rendered design frames, visual/text rules, difficult transitions and pilot plan | User accepts the entire identified design/script revision |
| Prototype | Bounded playable sample using the selected assets, hard effects/actions, transitions and soundtrack; actual agent review first | User watches and accepts this exact sample |
| Animatic for a complete MV | Whole-song rough cut with simplified assets/poses and the actual soundtrack; inspect repeats, pacing, progression and ending | User accepts this exact overall cut |
| Full production | Refine the accepted work, verify encoded output, deliver video/source/limitations and repair within scope | User feedback defines remaining revisions |

**认可大方向 ≠ 认可设计脚本 ≠ 认可样片 ≠ 认可全曲粗剪。AI 自检通过 ≠ 使用者验收通过。** For each review, show accessible artifacts, identify their revision, summarize remaining limits and the one next stage, then end the turn and wait. A reply about one image does not accept the whole package. A generic “continue” applies only to the currently presented immediate next stage, never unseen future work. A whole-MV request is an end goal, not a waiver of these stops.

While waiting, revise only the current stage or perform authorized technical checks; never batch later shots in the background. Separate `workflow.packages` and `workflow.approvals` from `content_confirmation` and overall production scope. Bind actual files and real user replies to their specific stage/revision. Other animation/generation/rendering skills are subordinate adapters and may not advance the phase. `project_contracts.py promote` records agent review only and never supplies a user decision.

Reuse previous accepted stages and resume at the earliest affected one. Material story/design/sample changes reopen that stage and dependent work; ordinary bug fixes within the accepted design need evidence rechecks, not another creative interview. A detailed direct request can eliminate redundant discovery, but does not silently accept later artifacts. A user may explicitly waive a named review or combine stages for a short work; retain that exact limited delegation, still create and inspect the required artifacts, and never infer `skip-all` from “make the full MV.” For a short combined pilot/animatic, its clip must cover the entire scope and be recorded in both packages with the explicit stage waiver.

Design scaffolds permit only bounded static frames, no video or frame sequences. Animatics use a genuinely simplified production (bundled limit: longest side 960px, ≤15fps), not a finished movie downscaled afterwards. Existing custom routes must apply the same checks. Unverified artistic or song claims remain unverified.

## 硬约束：先确认歌曲理解与具体内容，再制作

**基础题答完 ≠ 内容确认 ≠ 全长制作授权。** Song, duration, aspect, palette and style are logistical inputs. Do not treat one round of three basic questions as a completed creative interview. Continue adaptive content questions until the subject, core idea, visible progression and representative moments are clear; for a lyrical song establish a supported interpretation first. Then recap what the video will actually show and obtain the user's confirmation before advancing into user-video production.

Read [content confirmation and scope gate](references/content-confirmation.md). Until the gate is satisfied, only clarify, inspect inputs/references, verify facts and discuss proposed directions. Do not scaffold a production, draw its assets, render a pilot or start a whole-song build. Never invent a story/relationship/song meaning and mark it user-confirmed yourself. A generic “make a full MV,” a runtime check or a style choice is not acceptance of a proposed story. Production scripts also reject missing/stale content confirmation and out-of-scope durations.

Read [song and lyric understanding](references/song-understanding.md) before translating a lyrical song into visuals. Read the actual supplied/verified lyrics and check the chosen recording. Separate documented artist intent, evidence-based textual readings and the user's adaptation. Do not reconstruct missing words or author intent from memory. Offer 2–3 supported directions when meaning is materially ambiguous and let the user select; unknown facts stay unknown. Include that selected meaning in the content recap. No on-screen lyrics does not imply an instrumental.

Reuse a genuinely explicit, already accepted brief and its user evidence without repeating the interview. A direct, fully specified request can establish content when the user clearly instructs that exact concept; do not infer this exception from a generic “go ahead.” Local runtime/skill-maintenance self-tests are isolated verification, never a way to relabel and bypass a requested MV. Missing legacy confirmation must be recovered from actual prior decisions or requested; it is never auto-approved.

Read [execution evidence and stage gates](references/execution-gates.md) before scaffolding/rendering. Schema 5 retains those input/content bindings and additionally binds design, pilot and animatic user acceptance to actual presented artifacts. The CLI and JavaScript hosts use one local Python contract. Agent-generated records are not authenticated user consent; never fabricate them. Fill hashes and routine fields yourself from inspected inputs, not by asking technical questions of the user. Preserve genuine earlier acceptance through the documented migration path.

For full expansion require the representative technical prototype receipt AND the separate user approvals of design/script, sample and complete rough animatic. Inspect project-specific acting/story/meaning/text/glyph criteria and retain unresolved artistic defects. Full-line captions require complete canonical line coverage and reviewed timing; Chinese full captions require the selected font's actual glyph check. These records support review rather than certify taste. Check [capability status](assets/capability-matrix.json) before claiming an engine or real-song result has been verified.

Read [review workspace and handoff](references/review-workspace.md) when presenting or resuming work. Use its shared command to bind actual artifacts, create one accessible script/image/video review page, and derive `plan/STATUS.md` from the current evidence. Show the result through the host's accessible image/video/file views; a local filename alone is not a presentation. Keep routine records out of the user's questions. The helper never interprets a user reply or creates consent; record acceptance only after reading the real reply. Keep the existing stops, not extra interviews.

## Choose the mode and recover decisions

Read the current request, provided references, accepted decisions and project files. Reuse `brief.json`, `DECISIONS.md`, `PROPOSAL.md` and the latest render when available. Do not re-interview an already specified project or import another project's preferences.

- For an unclear new request, enter discovery. Ask a few useful questions, then adapt the next round to the answers.
- For a plan-only request, deliver only the requested plan/design material. Explicitly requested static design previews may use the design workspace, but no motion/video production.
- For a fully specified request to make the video, verify the content/song-meaning confirmation and the exact authorized scope, then proceed. Preserve real earlier acceptance; a general production request alone does not satisfy the hard content gate.
- For revisions, inspect the actual artifact and the changed requirement, update affected decisions, preserve accepted work and fix within scope.

## Discover through questions

Read [adaptive discovery](references/discovery.md). Analyze supplied reference frames/segments before discussing their visual mechanism. Distinguish observations, inferences, proposed changes and unavailable evidence.

When a reference drives the request, read [reference measurement and comparison](references/reference-analysis.md). Use actual sequences to extract staging, construction and rhythm, produce numerical candidates where useful and compare original rendered samples with the reference. Keep derived reference pixels private unless sharing them is authorized.

Ask at most 1–3 high-value questions per round, usually 2. Provide concrete, distinct choices and allow the user's own answer. Use the host's question widget if suitable; otherwise use plain numbered choices. For facts such as song name/version, ask a direct free-text question, alone if necessary.

Adapt to the content: a typography MV needs no question about romantic leads; an abstract visualizer needs no character portrait; an established song needs no songwriting interview. If the user selects every option, ask which quality must survive a tradeoff rather than treating all options as priorities.

Discuss feasibility early when requirements conflict: realistic acting plus all-code rendering, a full song plus a short deadline, or expensive generation plus no budget. Explain options without silently changing the user's constraint or steering every project into a cartoon.

Do not choose warmth, paper, realism, anime, pixels, 3D, head count, full lyrics, aspect ratio or pure-code assets by default. Maintain the user's confirmed constraints. Do not use image generation for style previews when the user requires all visuals to be code-drawn.

When a material choice benefits from visual comparison, read [controlled visual studies](references/visual-studies.md). Compare the same content across 2–3 viable treatments within the authorized scope. The optional flat/paper/pixel studies are implementation examples, not a fixed style menu. Use type/abstract subjects for no-character concepts. Separate code/runtime evidence, visual inspection and user taste acceptance.

For an executable drawing example or a reusable new look, read [style packs](references/style-packs.md). The optional flat/cut-paper/pixel/ink packs include construction rules and original scenic demos; they do not restrict style discovery. Use the selected design's actual assets in design frames and animation, and prove the hard effect before expanding it.

For a selected pixel-art project or a request to edit pixel characters, read [pixel character workbench](references/pixel-workbench.md). Use the bundled offline editor and Python exporter for editable layers, palettes, static poses and source-reproducible sprites. Start with static design only; enable motion previews/sprite sequences only through the shared stage gate after design/script acceptance. A saved model or exported sprite never supplies user approval. The neutral example is a construction aid, not an approved cast or a default style. No editor installation or network service is required; Pillow is the sole export dependency.

For a unified editing surface, read [MV director workbench](references/director-workbench.md). Its seven optional modules cover acting/contact, scene/camera, actual-recording lyric timing, storyboard/rough sequencing, transitions, assets/style and bound review/repair notes. Reuse the same model and drawing core through the selected Canvas2D or Remotion adapter; other art/hosts need explicit adapters. Initialize user projects from their actual decisions and sources, not the isolated example. Design stays static; moving previews and actual exports retain the shared stage/range/source gates. Save drafts, bind the shown design source with review_workspace.py --source, and keep real user acceptance separate.

## Converge and present the proposal

Track answers, assumptions and blocking questions with `assets/brief.template.json` or equivalent project files. Stop asking when the desired experience, visual direction, content progression, asset policy and output scope are specific enough to make a useful plan. Do not ask for trivial implementation details simply to fill fields.

Convergence means the intended content is understood and accepted, not that enough fields exist to invent a plausible film. Record `content`, `song_reading`, `content_confirmation` and scoped authorization truthfully. A content recap may be proposed while the gate is pending; production remains blocked until the user's response resolves it.

Present:
1. A concise description of the intended film, separating confirmed decisions from proposed assumptions.
2. Visual grammar: medium, shapes/proportions if relevant, palette, texture, composition, motion and text treatment.
3. Emotional progression/story or another progression mechanism, with 2–3 representative moments and an ending if relevant.
4. One proposed technical route, its fit, tradeoffs, required assets/tools, and what the bundled kit actually supports.
5. An execution order with visible checkpoints, realistic uncertainties and known missing inputs.

Use `scripts/check_brief.py <brief.json> --for proposal` for a structural completeness check when a brief file exists. It cannot decide whether the user likes the plan.

After a useful agreed direction, read [project contracts](references/production-contracts.md). Establish a project-specific `visual-spec.json` from the selected design, with stable cast/type/space rules, locked choices and actual rendered evidence as relevant. Use `scripts/project_contracts.py init --project <project-dir>` to create only missing neutral records. Also use the stage package/approval and full script templates linked in user-stage-review.md; never fill later-stage acceptance while the user has only confirmed direction. Let the agent fill routine technical details; do not turn templates into more interview questions.

If the user asked only to explore or plan, deliver the requested proposal/static design material and end that stage. For unresolved content/meaning/taste, ask the next specific question and wait. Once the content gate is satisfied, enter design only; advance through the user-stage reviews within the eventual requested scope. An approved short prototype never becomes full-song authorization by itself. Reuse actual acceptance of the same presented artifact revision; do not re-ask it. Required later artifact reviews are separate decisions, not redundant questions.

## Choose the route after the style

Read [style and engine routing](references/style-routing.md). Treat its examples as an open set, not a style menu imposed on the user.

- `painted-p5`: bundled p5.js/p5.brush renderer for painterly/ink/paper animation when selected.
- `canvas2d`: bundled minimal deterministic Canvas2D host for custom flat/vector/pixel/collage/typography work. It is a blank engine, not finished art.
- `remotion`: optional bundled original composition/preview/export adapter; read [Remotion adapter](references/remotion-adapter.md), install its selected dependencies, and retain the shared stage gate.
- three.js, Blender or custom tooling: plan and implement from suitable official documentation if selected. These remain guide-only routes here.

Use one main host per project. Consult `assets/engines.json` for the distinction between bundled templates and guide-only options. Preserve applicable licenses. General style coverage does not mean every style is equally cheap or achievable by the same agent/runtime.

For a selected Remotion route, use the bundled adapter and consult the official Remotion skills/documentation for composition, captions, preview and rendering as needed; do not install or combine another host merely because it is mentioned upstream. Measure representative frame cost and output size before making a long-film estimate.

After direction acceptance, select the engine and create a design workspace with `scaffold.py --phase design`. Render only static frames. After the complete design/script package has been shown and accepted, continue the same workspace in `phase:prototype`; a new authorized prototype can also be scaffolded from that bound design package:

```bash
python3 <skill-dir>/scripts/check_brief.py <confirmed-brief.json> --for prototype
python3 <skill-dir>/scripts/scaffold.py <project-dir> --brief <confirmed-brief.json> --engine canvas2d --duration 8 --fps 30
python3 <skill-dir>/scripts/preflight.py --project <project-dir> --json
```

The prototype duration is not the song length. Continue existing projects without overwriting them. For Chinese captions add `--require-cjk` and inspect glyphs. Follow the host's durable-saving rules; project outputs and private inputs do not belong inside this reusable skill.

`--tool-self-test` is reserved for isolated bundled examples/runtime regression checks (at most 60 seconds, no user recording). It does not grant content acceptance or authorize a requested MV. Guide-only engines must run the same brief/scope check before their custom production commands.

For Canvas2D, select `execution.runtime` as `browser` or the optional `node-canvas` CPU runner, then read [runtime verification](references/runtime-portability.md). A successful CPU test does not verify Chrome/p5/WebGL. The engine's dependencies, fonts and executable probe must match the selected route; the skill never installs every backend automatically.

## Reuse the integrated production method

Read [director method](references/directing.md), [timing](references/timing.md) and [rendering](references/rendering.md) at the relevant stages. For character-led scenes or story information cards read [project assets and performance mechanics](references/production-assets.md). Use the optional source-bound acting plan, generic UI cards and bitmap-font exporter where the selected project needs them; filled records never certify acting.

1. Establish the style with the right evidence: character sheets for characters, type/layout boards for typography, material/space frames for 3D, or a behavior sample for abstract graphics.
2. Prove the hardest relevant action or effect in a short representative clip. A human handoff needs contact evidence; a pixel loop or word transition needs a different test. Do not require a human rig in every style.
3. Measure the actual recording and build the full timeline/animatic when needed. Do not copy duration or lyrics from another reference. Imported LRC and automated recognition remain unverified until compared with the chosen recording.
4. Render and inspect shot by shot, then inspect important cuts and the encoded output. Keep accepted work, fix common causes and re-render affected ranges.
5. Deliver the actual requested artifacts, reproducible sources, checks and known limitations. A script/schema pass is not a certification of aesthetics, motion or sync.

Read [music-to-picture progression](references/music-direction.md) to build `shot-map.json`: recording/section facts, viewer response, visible development, motif and lyric links. Use `scripts/analyze_music.py` for measured metadata/RMS candidates only; listen to confirm sections and accents. Explain repeated sections' variation or deliberate repetition, including non-narrative patterns. RMS candidates are not verified beats or emotional meaning.

When beat precision matters, `scripts/music_grid.py` proposes a constant-tempo transient grid with candidate/ambiguity status and optional tempo/first-beat hints. Check early/middle/late regions; use a piecewise grid for tempo changes. `scripts/import_srt.py` preserves supplied line cues without inventing word timing. Neither tool establishes canonical lyrics, musical meter or the viewer's interpretation.

Respect the chosen asset and lyric policies. Do not add generation services, paid tools, stock art or a replacement song without authorization. Do not require all lyrics on screen when the chosen concept uses selected lines or no visible lyrics. Require measured word/syllable timing before claiming word-accurate highlights.

Use stable time-based state for procedural layers and reproducible local rendering. For character projects read [character review](references/character-review.md); use local units, parent attachments and uniform root transforms. Only apply a proportion-specific helper after its model has been selected. Keep purposeful holds or active motion according to the approved motion language.

Read [optional components](references/components.md) before reusing the original local motion/transition modules. Prove contact, foot support, views or the selected graphic effect in the actual project. A simple humanoid helper is not a complete acting system; a shape/word primitive does not invent a creative lyric transformation.

For relevant character or semantic work, read [performance and lyric meaning](references/performance-and-meaning.md). Prove gaze, reaction, preparation, action and settle in the chosen design. Track a lyric object's visible role and transition geometry instead of decorating every line with an unrelated symbol. Narrative and literal lyric illustration are optional, not global requirements.

Read [review and bounded repair](references/review-and-repair.md). Record actual observations, target/source hashes, relevant checks and timestamped issues in `review.json`. Satisfy the representative prototype's relevant checks before expanding affected work. Preserve accepted shots, propagate repairs only through declared shared assets, render affected intervals with adjacent joins and compare before/after. Do not silently weaken a locked requirement. These are AI quality checks in addition to the mandatory artifact-specific user reviews; they cannot replace them.

Read [native range, resume and cost controls](references/native-incremental.md) for bounded CPU rerenders, source-bound frame reuse and actual frame/disk estimates. Exported repair clips still need validated integration into the master.

Read [actual-output diagnostics and viewer feedback](references/output-diagnostics.md) for contact sheets, low-change/black/cut candidates, declared layout/local-pose checks, source/output audio comparison and the local timestamped review player. Missing metadata or ambiguous audio remains unverified. Treat metrics as repair evidence, retain intentional holds and never substitute continuous camera motion for acting.

```bash
python3 <skill-dir>/scripts/project_contracts.py check --project <project-dir> --stage prototype
python3 <skill-dir>/scripts/project_contracts.py repair --project <project-dir> --out <new-repair-plan.json>
```

Recorded review checks do not automatically judge beauty, natural motion or story. A reviewing agent must inspect the evidence before recording a pass. Keep user acceptance separate and retain unresolved limitations.

Use playable clips or source-bound consecutive strips and inspected time ranges for motion, acting, contact and transitions; one still cannot substantiate a temporal claim. Do not mark selected mandatory checks `not_applicable`. Review a deliberate hold as a deliberate hold. Compare actual production frames with the accepted design at the same content/time, explaining deliberate changes without a numerical beauty score. Read [representative creative validation](references/creative-validation.md) for scoped benchmark tasks, portable runtime checks and the distinction between original probes and a finished real sung MV.

Read [scoped lessons, cost and reproducible validation](references/learning-and-validation.md) when a repair reveals reusable knowledge or the skill itself changes. Keep lessons tied to evidence and applicability; never let them override user decisions. Run bundled regression tests and the selected destination's real render test, preserving the distinction between technical integrity and artistic success.

Use the original light tools as appropriate: LRC import, timeline/cue validation, actual-pose metadata checks and preflight. Read [trial failure case](references/failure-case.md) only as one observed regression example, not a universal diagnosis.

## Hand the work to another agent

Read [agent interoperability](references/agent-interop.md). Transfer the complete skill directory and relevant project decisions, not only the skill's name or the current chat. Resolve scripts/assets relative to this file; do not hardcode private workspace paths or require a particular question-tool name.

Use `scripts/export_skill.py --dest <export-parent>` to make a portable `storybook-mv` directory with checksums and licenses. By default omit the personal project profile and host-specific metadata; include the profile only when intentionally transferring that project.

Run `scripts/verify_portable.py <exported-skill-directory>` to verify the versioned complete export. Then run the selected destination runtime's actual self-test; do not reuse another host's success as compatibility evidence. See [runtime verification](references/runtime-portability.md) for the playable Canvas2D test and receipt scope.

For a delegated task, provide the agreed brief, decisions, current phase, presented package revisions and real user approvals/waivers, visual specification, shot map, latest review/issues, selected route/runtime, inputs, file ownership, deliverable and acceptance criteria. Follow the host's delegation policy. Another agent must not restart discovery, choose a different style or claim it inherits hidden chat memory.

Keep one coordinator responsible for seams and final verification when a team is authorized. Do not automatically publish or message third parties.

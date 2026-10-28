---
name: storybook-mv
description: Clarify, plan, prototype and review music videos through adaptive questions without fixing a style, proportion, palette or engine. Use for MV方案、视频风格选择、通过提问确认需求、代码MV、歌词视频、动画分镜, controlled style previews, music-to-shot mapping, visual consistency, timestamped repairs and cross-agent handoff. Includes optional code studies/components, project design/review contracts and a playable Canvas2D runtime self-test. Default to discovery and a concrete proposal before production; reuse existing answers and authorization.
---

# MV 创作导演

Start with the user's desired experience and constraints, not a rendering template. Discover → compare viable directions → converge through questions → present a concrete proposal → produce only within the user's authorized scope → review evidence and repair.

Keep the handle `storybook-mv` for compatibility. It no longer implies storybook art or a default body proportion.

## Choose the mode and recover decisions

Read the current request, provided references, accepted decisions and project files. Reuse `brief.json`, `DECISIONS.md`, `PROPOSAL.md` and the latest render when available. Do not re-interview an already specified project or import another project's preferences.

- For an unclear new request, enter discovery. Ask a few useful questions, then adapt the next round to the answers.
- For a plan-only request, finish with a concrete proposal and necessary execution information; do not scaffold a project or start rendering.
- For a fully specified request to make the video, honor that authorization, resolve only material gaps and proceed. Do not force the user through a redundant approval ritual.
- For revisions, inspect the actual artifact and the changed requirement, update affected decisions, preserve accepted work and fix within scope.

## Discover through questions

Read [adaptive discovery](references/discovery.md). Analyze supplied reference frames/segments before discussing their visual mechanism. Distinguish observations, inferences, proposed changes and unavailable evidence.

Ask at most 1–3 high-value questions per round, usually 2. Provide concrete, distinct choices and allow the user's own answer. Use the host's question widget if suitable; otherwise use plain numbered choices. For facts such as song name/version, ask a direct free-text question, alone if necessary.

Adapt to the content: a typography MV needs no question about romantic leads; an abstract visualizer needs no character portrait; an established song needs no songwriting interview. If the user selects every option, ask which quality must survive a tradeoff rather than treating all options as priorities.

Discuss feasibility early when requirements conflict: realistic acting plus all-code rendering, a full song plus a short deadline, or expensive generation plus no budget. Explain options without silently changing the user's constraint or steering every project into a cartoon.

Do not choose warmth, paper, realism, anime, pixels, 3D, head count, full lyrics, aspect ratio or pure-code assets by default. Maintain the user's confirmed constraints. Do not use image generation for style previews when the user requires all visuals to be code-drawn.

When a material choice benefits from visual comparison, read [controlled visual studies](references/visual-studies.md). Compare the same content across 2–3 viable treatments within the authorized scope. The optional flat/paper/pixel studies are implementation examples, not a fixed style menu. Use type/abstract subjects for no-character concepts. Separate code/runtime evidence, visual inspection and user taste acceptance.

## Converge and present the proposal

Track answers, assumptions and blocking questions with `assets/brief.template.json` or equivalent project files. Stop asking when the desired experience, visual direction, content progression, asset policy and output scope are specific enough to make a useful plan. Do not ask for trivial implementation details simply to fill fields.

Present:
1. A concise description of the intended film, separating confirmed decisions from proposed assumptions.
2. Visual grammar: medium, shapes/proportions if relevant, palette, texture, composition, motion and text treatment.
3. Emotional progression/story or another progression mechanism, with 2–3 representative moments and an ending if relevant.
4. One proposed technical route, its fit, tradeoffs, required assets/tools, and what the bundled kit actually supports.
5. An execution order with visible checkpoints, realistic uncertainties and known missing inputs.

Use `scripts/check_brief.py <brief.json> --for proposal` for a structural completeness check when a brief file exists. It cannot decide whether the user likes the plan.

After a useful agreed direction, read [project contracts](references/production-contracts.md). Establish a project-specific `visual-spec.json` from the selected design, with stable cast/type/space rules, locked choices and actual rendered evidence as relevant. Use `scripts/project_contracts.py init --project <project-dir>` to create only missing neutral records. Let the agent fill routine technical details; do not turn templates into more interview questions.

If the user asked only to explore or plan, deliver the proposal and end that stage. Continue into production only when authorized. For an unresolved material taste fork, ask one specific follow-up. If production was already requested and no material blockers remain, proceed without asking permission again.

## Choose the route after the style

Read [style and engine routing](references/style-routing.md). Treat its examples as an open set, not a style menu imposed on the user.

- `painted-p5`: bundled p5.js/p5.brush renderer for painterly/ink/paper animation when selected.
- `canvas2d`: bundled minimal deterministic Canvas2D host for custom flat/vector/pixel/collage/typography work. It is a blank engine, not finished art.
- Remotion, three.js, Blender or custom tooling: plan and implement from suitable official documentation if selected. These are guide-only routes here, not preinstalled engines.

Use one main host per project. Consult `assets/engines.json` for the distinction between bundled templates and guide-only options. Preserve applicable licenses. General style coverage does not mean every style is equally cheap or achievable by the same agent/runtime.

For a new authorized prototype, select the engine explicitly:

```bash
python3 <skill-dir>/scripts/scaffold.py <project-dir> --engine canvas2d --duration 8 --fps 30
python3 <skill-dir>/scripts/preflight.py --project <project-dir> --json
```

The prototype duration is not the song length. Continue existing projects without overwriting them. For Chinese captions add `--require-cjk` and inspect glyphs. Follow the host's durable-saving rules; project outputs and private inputs do not belong inside this reusable skill.

For Canvas2D, select `execution.runtime` as `browser` or the optional `node-canvas` CPU runner, then read [runtime verification](references/runtime-portability.md). A successful CPU test does not verify Chrome/p5/WebGL. The engine's dependencies, fonts and executable probe must match the selected route; the skill never installs every backend automatically.

## Reuse the integrated production method

Read [director method](references/directing.md), [timing](references/timing.md) and [rendering](references/rendering.md) at the relevant stages.

1. Establish the style with the right evidence: character sheets for characters, type/layout boards for typography, material/space frames for 3D, or a behavior sample for abstract graphics.
2. Prove the hardest relevant action or effect in a short representative clip. A human handoff needs contact evidence; a pixel loop or word transition needs a different test. Do not require a human rig in every style.
3. Measure the actual recording and build the full timeline/animatic when needed. Do not copy duration or lyrics from another reference. Imported LRC and automated recognition remain unverified until compared with the chosen recording.
4. Render and inspect shot by shot, then inspect important cuts and the encoded output. Keep accepted work, fix common causes and re-render affected ranges.
5. Deliver the actual requested artifacts, reproducible sources, checks and known limitations. A script/schema pass is not a certification of aesthetics, motion or sync.

Read [music-to-picture progression](references/music-direction.md) to build `shot-map.json`: recording/section facts, viewer response, visible development, motif and lyric links. Use `scripts/analyze_music.py` for measured metadata/RMS candidates only; listen to confirm sections and accents. Explain repeated sections' variation or deliberate repetition, including non-narrative patterns. RMS candidates are not verified beats or emotional meaning.

Respect the chosen asset and lyric policies. Do not add generation services, paid tools, stock art or a replacement song without authorization. Do not require all lyrics on screen when the chosen concept uses selected lines or no visible lyrics. Require measured word/syllable timing before claiming word-accurate highlights.

Use stable time-based state for procedural layers and reproducible local rendering. For character projects read [character review](references/character-review.md); use local units, parent attachments and uniform root transforms. Only apply a proportion-specific helper after its model has been selected. Keep purposeful holds or active motion according to the approved motion language.

Read [optional components](references/components.md) before reusing the original local motion/transition modules. Prove contact, foot support, views or the selected graphic effect in the actual project. A simple humanoid helper is not a complete acting system; a shape/word primitive does not invent a creative lyric transformation.

Read [review and bounded repair](references/review-and-repair.md). Record actual observations, target/source hashes, relevant checks and timestamped issues in `review.json`. Satisfy the representative prototype's relevant checks before expanding affected work. Preserve accepted shots, propagate repairs only through declared shared assets, render affected intervals with adjacent joins and compare before/after. Do not silently weaken a locked requirement. These are work-quality checkpoints, not repeated permission questions.

```bash
python3 <skill-dir>/scripts/project_contracts.py check --project <project-dir> --stage prototype
python3 <skill-dir>/scripts/project_contracts.py repair --project <project-dir> --out <new-repair-plan.json>
```

Recorded review checks do not automatically judge beauty, natural motion or story. A reviewing agent must inspect the evidence before recording a pass. Keep user acceptance separate and retain unresolved limitations.

Use the original light tools as appropriate: LRC import, timeline/cue validation, actual-pose metadata checks and preflight. Read [trial failure case](references/failure-case.md) only as one observed regression example, not a universal diagnosis.

## Hand the work to another agent

Read [agent interoperability](references/agent-interop.md). Transfer the complete skill directory and relevant project decisions, not only the skill's name or the current chat. Resolve scripts/assets relative to this file; do not hardcode private workspace paths or require a particular question-tool name.

Use `scripts/export_skill.py --dest <export-parent>` to make a portable `storybook-mv` directory with checksums and licenses. By default omit the personal project profile and host-specific metadata; include the profile only when intentionally transferring that project.

Run `scripts/verify_portable.py <exported-skill-directory>` to verify the versioned complete export. Then run the selected destination runtime's actual self-test; do not reuse another host's success as compatibility evidence. See [runtime verification](references/runtime-portability.md) for the playable Canvas2D test and receipt scope.

For a delegated task, provide the agreed brief, decisions, current phase, visual specification, shot map, latest review/issues, selected route/runtime, inputs, file ownership, deliverable and acceptance criteria. Follow the host's delegation policy. Another agent must not restart discovery, choose a different style or claim it inherits hidden chat memory.

Keep one coordinator responsible for seams and final verification when a team is authorized. Do not automatically publish or message third parties.

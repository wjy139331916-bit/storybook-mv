# User-stage review: direction, design, pilot, animatic, production

## Contents
1. Run the visible workflow
2. Keep user acceptance distinct from agent review
3. Bind the actual presentation
4. Execute the permitted stage
5. Resume, repair and delegate

## Run the visible workflow

Discover through adaptive questions and verify the supplied song/lyrics. Continue because material content remains unclear, not to meet a round count. Reuse genuine prior answers. Where meaning changes the film, present grounded alternatives and get the user's selection. A named song, length and aspect do not settle the content.

After an accurate direction recap is accepted, work on design only. The user must receive a complete package before sample animation:

- Overall idea, evidenced song reading, intended audience experience and limits.
- A target-scope script: all song sections and shots, their ranges, visible development, lyric treatment and transition. Cover the whole song, not only the pilot. Mark provisional timing honestly; finish timing against the selected recording before whole-song execution. Individual frames/micro-gestures need not be scripted yet.
- Actual design images made under the chosen asset policy: relevant cast/subject, scenic/layout, palette, text and representative key frames. No fixed style or character requirement. For all-code work draw these through the selected code renderer and reuse its actual assets in animation.
- Technical route, hardest requirements, cost/time uncertainties, and the bounded pilot interval and test objectives.

Present accessible images and readable script, not only internal JSON/source filenames. A review package means related reviewable artifacts, not an unsolicited ZIP; create an archive only when requested. Summarize the revision and ask for acceptance of the complete package; end the turn and wait. One liked image is not whole-package acceptance. Keep design amendments in that stage until reconciled.

Build the agreed pilot only after design acceptance. Include the difficult relevant acting/effect, at least the significant join when the plan uses one, actual selected assets/fonts and the soundtrack. An easy isolated shot cannot stand for an untested requirement. Inspect encoded output and fix observed faults first. Then present the actual playable sample and limitations; end the turn and wait for the user's response to this sample.

For a complete MV, build a whole-song rough animatic after pilot acceptance. Use simplified assets, key poses and actual timing/audio to expose repetition, changes between choruses, emotional/nonnarrative progression, callback and ending. The bundled rough route caps longest side at 960px and fps at 15. Reduced export size alone does not make production rough: do not finish detailed animation in advance and relabel/downscale it. A caption-mode choice remains binding, with provisional timing labelled when not yet ear-checked.

Show the complete rough cut; end the turn and wait. After acceptance refine it to full quality, inspect important actions/joins, full lyrics and encoded audio/video, deliver reproducible sources and limitations, and address feedback within the accepted scope. Final MP4 delivery does not authorize publishing it elsewhere.

## Keep user acceptance distinct from agent review

There are three separate records:

| Record | What it means | What it does not permit |
|---|---|---|
| `content_confirmation` | User accepted the content/meaning recap, or supplied that exact explicit concept | Does not accept later design or samples |
| Agent technical/visual review, including `prototype-pass.json` | Named reviewer inspected actual output and recorded observations | Does not represent user taste or waive a stop |
| `workflow.approvals.<stage>` | Real reply accepts/explicitly waives that identified presentation, permitting its immediate next stage | Does not accept unseen future stages |

Keep the real user's reply and its context. An ordinary “continue” can approve the currently presented complete package and the clearly stated next step; it cannot become a universal skip flag. An initial “make the whole MV” establishes the eventual goal only. Never copy its message into later approvals. Never write missing acceptance to appease a validator.

Default stops may be waived only by explicit user instructions identifying which review is delegated. Record one limited waiver per named stage, its actual reply, alternatives and self-review. Skipping a user stop does not omit the actual work or technical verification. For a short video, a user-authorized combined pilot/animatic may reuse the same whole-scope clip in two packages, retaining separate explicit stage records. Do not add your own skip because an agent thinks the result is good enough.

## Bind the actual presentation

Schema 5 adds `workflow:{schema_version:1,policy:"user-stage-review",packages:{},approvals:{}}`.
All stage package/approval/artifact paths are relative to the project and their SHA-256 must match. Keep them in a stable `plan/` directory and `out/` artifact revisions. Do not put private project data in this reusable skill.

Use [package template](../assets/contracts/stage-package.template.json), [approval template](../assets/contracts/stage-approval.template.json) and [complete script template](../assets/contracts/design-script.template.json). The agent fills routine records; do not ask the user for hashes, JSON or internal fields.

`workflow.packages.design` points to a package with `stage:"design"`, revision, `content_sha256`, `design_sha256`, `target_duration` and `artifacts`, plus `pilot:{start,end,objectives}` for the explicitly bounded sample. Actual sample renders must fit that accepted interval even when the eventual scope is a full song. Each artifact is `{role,path,sha256}`. Required roles:

- `proposal`: readable full proposal file.
- `script`: complete timeline JSON using the shot-map section/shot rules, plus each shot's `visual`, `lyric_treatment`, `transition:{type,...}`. Its duration equals the whole agreed target/recording duration, even though the prototype is shorter. For no lyrics explicitly say the treatment is none.
- `visual_spec`: concrete design object with medium, palette/rule, shape language, composition, motion and cast only when needed.
- `design_frame`: actual decodable raster design evidence from the selected renderer; source code, prompts or renamed text do not count. Preserve SVG/code originals as optional additional artifacts. The user sees the rendered image.

Compute the current design binding with:

```bash
python3 <skill>/scripts/workflow_gate.py <project>/brief.json --design-digest
```

It binds selected visible style/text/font/asset policy/aspect and content, independently of routine technical resolution. Do not silently refresh accepted design values after a visible change.

The `prototype` and `animatic` packages require `video`, `render_report`, `review` artifacts and the current `design_package_sha256`. `animatic` also references `prototype_package_sha256`, declares `fidelity:"rough"`, and covers the complete `target_duration`. Render report must identify this encoded video, `production_stage` and a successful decode. The native renderer writes this automatically. For another engine, inspect its actual output with FFprobe, completely decode with FFmpeg, and retain a truthful JSON report with `production_stage`, `encoded:{full_decode:true}` only after success, and `artifacts:[{path,sha256}]` identifying the video. This inspection never supplies user acceptance. Its separate stage review contains `scope`, `status:"observed_pass"`, `reviewer`, `target_sha256`, and concrete `observations`. Detailed acting/music/text reviews remain in project reviews; this short record cannot replace them.

An approval record has `origin:"user-message"`, actual `message_id`, actual `user_reply`, `presented_message_id`, stage, revision, content hash, `package_sha256`, `decision:"approved"`, and `next_stage`. Fixed immediate transitions are design→prototype, prototype→animatic, animatic→full. A waiver instead uses `decision:"waived"`, `explicit_skip:true`, `waived_stage:<same stage>`, `scope:"this_stage_only"` plus the actual limited instruction. Reusing an intake/earlier-stage reply as acceptance of a later presentation is rejected. An explicitly named waiver may use the actual earlier delegation reply; it needs no fictional later presentation message, and must retain `self_review:{reviewer,observations}` of the completed package. A user-authorized combined-stage reply can accept the shown pilot and explicitly waive the separate animatic stop with that same message, without turning it into two ordinary approvals. These fields make decisions inspectable; they cannot cryptographically authenticate an invented user message or judge its semantics. The agent must read the actual conversation.

## Execute the permitted stage

Direction acceptance can preserve the prior content hash/user record. Set phase `design`, overall authorized scope `design` or the actual eventual scope, and keep later packages/approvals empty. Explicitly requested static planning output may use `request_mode:"plan-only"` plus the design phase; this never authorizes animation. Do not change discover/proposal/awaiting-confirmation to evade missing acceptance.

```bash
python3 <skill>/scripts/scaffold.py <new-project> --brief <direction-brief> --phase design --engine canvas2d --duration 8
node <skill>/scripts/render_canvas.mjs --project=<new-project> --stills-only --times=0,2,5 --out=out/design-r1
```

Design runs allow at most 12 static frames per render and refuse video/frame-sequence export. After the user accepts the complete design/script, retain the same project, set `phase:"prototype"`, and render the agreed bounded interval. For a nonzero source interval keep the global scene timeline long enough and use `--range=START:END`; do not substitute a different excerpt of the same length. A newly scaffolded prototype carries the bound design files with their relative identities.

```bash
python3 <skill>/scripts/check_brief.py <project>/brief.json --for prototype
python3 <skill>/scripts/project_contracts.py check --project <project> --stage prototype
python3 <skill>/scripts/project_contracts.py promote --project <project>
```

`promote` records technical evidence only, without changing the phase. Create the sample presentation/package; after the real reply bind its separate user approval. Then set `phase:"animatic"`, build a genuinely simplified whole-timeline scene, and use ≤960px and ≤15fps with the selected aspect. A full-duration rough cut needs overall full-scope authorization, design and sample user decisions, not animatic acceptance in advance.

```bash
python3 <skill>/scripts/check_brief.py <project>/brief.json --for animatic
python3 <skill>/scripts/check_brief.py <project>/brief.json --for production
```

Only set `phase:"full"` after actual rough-cut acceptance. Full/repair/deliver entry additionally requires the existing current technical prototype evidence, selected recording and applicable subtitle/glyph checks. When refining source, recheck representative output and renew technical evidence as needed; preserve historical user-approved sample files. A fresh internal check cannot manufacture new user acceptance. Command purpose must agree with the phase. Canvas, p5 and custom backend skills all follow this director contract; guide-only engines run the same gate with their actual operation/dimensions/fps before commands.

## Resume, repair and delegate

Recover the current skill version, project phase, exact accepted artifact revisions, unresolved notes and scope before continuing. Legacy direction/content acceptance remains valid for that content; it cannot create missing design/pilot/animatic decisions. Recover actual prior artifact acceptance from evidence or present the missing stage. Preserve artifacts and avoid restarting a completed interview.

Changes to story, recording/meaning, cast or visible design reopen their affected stage and dependent work. Never update a package hash beneath an old acceptance. Routine in-scope correction can keep the already approved creative package, renew technical evidence and preserve the original accepted samples; if the correction actually changes their design/story, show the affected revision. Do not force a fresh creative interview for technical fixes.

While awaiting a user decision, work only on revisions to that stage or already authorized technical checks; never begin later-shot production in the background. Pass the complete skill, packages, real approvals/limited waivers, phase and affected notes to another agent. A receiving agent cannot self-approve, import hidden chat assumptions or let another rendering skill advance the phase.

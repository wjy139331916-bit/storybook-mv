# Sources and integration choices

Use a style-independent discovery/directing layer and one selected rendering adapter per project. Keep source methods distinct from executable template support.

## Bundled painted engine (optional)

- https://github.com/tuzhechen2005/opus-video-skills/tree/main/skills/painted-animation
- Pinned commit: `59744a69c7b916cfbe4c4ec84006b0c2f5e2fde1`.
- Derived from https://github.com/JohnHeibel/ClaudeAnimationBase .
- Keep `assets/painted-template/LICENSE` (John Heibel) and `assets/UPSTREAM_LICENSE` (tuzhechen2005 and credited portions).
- Retain drawing/camera/timing APIs, renderer, package lock and optional example character.
- Omit binary model-sheet images and duplicate README files.
- Adapt remote font loading, configurable zero-default boil, default 30fps, disabled demo, local rig and full-line subtitle modules. Place merged policy above engine creative defaults.

## Methods, rewritten into a single workflow

- https://github.com/BuzyOwl/song-video-director : measured music facts, scene reads, callbacks, grounded staging, quiet sections and timestamped visual repair. No automatic publishing/asset generation.
- https://github.com/Dracowyn/ai-music-video-skill : separate taste, canonical lyrics, timebase, shot anchors and coverage checks. Provide original lightweight LRC/schema tools here; retain heavy alignment as optional upstream reference, not a mandatory dependency.
- https://github.com/remotion-dev/skills : optional alternative composition/caption/export guidance, not a second required runtime.

The general revision adds adaptive questioning, a proposal checkpoint, engine-neutral briefs, an explicit canvas2d scaffold and a portable directory exporter. Painted art and the historical project profile are optional choices.

Version 2 adds original optional controlled studies, limited motion/transition components, neutral project visual/shot/review contracts, an RMS guide, bounded repair plans, a native Canvas2D renderer and an encoded runtime self-test. No new third-party source files are copied for those tools. The optional `@napi-rs/canvas` dependency remains external and exact-versioned; the runtime records actual scope. Check `assets/studies/verification.json` for empirical evidence; do not infer whole-film or other-engine quality from those samples.

No affiliation or endorsement is implied. Preserve licenses when importing more files; pin and review updates.

## Version 3 source review (2026-10-28)

| Source | Inspected commit | Adopted method |
|---|---|---|
| https://github.com/Win-Hao/music-mv | `0088b1422f7f82cdf51b456436a6313127a26d6b` | Native style construction, reference measurement, contact sheets, reduced-frame motion/cut candidates and original/output loudness review |
| https://github.com/cth9191/animate | `7e5eb56feb2dd573f890e1b7b34748af43d58263` | Separate drawing kit/rules/demo/checklist, measurable reference-to-render comparisons, local reference handling and actual-output layout checks |
| https://github.com/sagearbor/claude-music-video-skill | `c764e18b8927dca5ea219fa42b78194fde28214f` | Tempo phase/drift review, design assets reused in animation, representative pilot, clear shared-asset handoff and scoped production lessons |
| https://github.com/remotion-dev/skills | `30d4553ecd46fbc5212fd0ff006ae43af522158b` | Load composition, captions, Studio preview and rendering guidance only when the project selects Remotion |

Version 3 implementations of style packs, acting, media/reference/audio diagnostics, transient-grid proposals, SRT import, local review player, viewer-note import, tests and the original demonstration are newly authored here. No new upstream source files or examples are vendored. Preserve the existing bundled-engine licenses. If importing code later, review the exact file/license and retain its attribution; a method citation does not grant a blanket license.

Do not import conflicting upstream defaults: mandatory literal illustration for every line, all-black/white frames always forbidden, forced motion every second, automatic 4/4 downbeats, fixed warm/paper/cartoon styles, every gate requiring another user stop, compulsory parallel agents, a lesson file overriding policy, or one hardcoded host path. Adapt to the brief and actual evidence. Metrics and upstream author reports are not independently verified aesthetic guarantees.

## Conflict decisions

| Source default | Unified policy |
|---|---|
| No text except karaoke | Follow the chosen lyric mode; support full/selected/environmental/no text |
| Nothing still / boiling lines | Choose motion and texture rate for the approved style; quiet holds allowed |
| Default Clawd actor | Use a cast only when the concept needs one; otherwise inspect layout or behavior |
| Several hosts / generated art | Select asset policy and one host after discovery; no unauthorized service calls |
| Estimated character-fill timing | Select text mode; measured timing required for precise karaoke |
| Publish pipeline | Render/package within scope; publish only if explicitly instructed |
| Always many agents | Follow host delegation policy, clear ownership when authorized |

## Verification scope

Check metadata, discovery behavior, proposal/production separation, explicit scaffolds, portability checksums, syntax, LRC import, timeline and relevant rig invariants. Aesthetic quality and full-song sync require compatible runtime and actual project inputs. Record those separately; a validator pass is not finished-animation evidence.

## Version 3.5 executable integration

The offline pixel editor/exporter, original neutral character, bitmap atlas generator, narrative UI helpers and expanded environment/probe helpers are newly authored. The optional Remotion template/adapter is also original source written against official APIs, not a vendored copy of the upstream skill. Remotion/React/p5/Puppeteer remain external exact-version dependencies with their own terms. Keep their attribution and do not mislabel Remotion as permissively licensed or preinstalled.

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

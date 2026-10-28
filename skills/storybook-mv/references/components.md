# Optional motion and transition components

Copy only selected files from `assets/modules/` into the project's source directory and load them before the scene. Keep time, units and transforms explicit. These original modules use standard Canvas2D drawing and deterministic JavaScript; they do not choose a project style.

| File | Exposed functions | Intended scope |
|---|---|---|
| `motion.js` | `phase`, `point`, `twoBone`, `walk`, `handoff`, `turn` | Time-based interpolation and limited humanoid constraints |
| `canvas-actors.js` | `MVActors.actor(ctx, options)` | Optional simple stylized-person renderer and actual limb metadata |
| `transitions.js` | `wipe`, `shapeMatch`, `wordToObject` | Foreground cover, matched ellipses, text/shape opacity transition |

`MVMotion.walk(t,{start,duration,distance,heads})` returns root distance, feet, support flags, hip height and limb lengths. Foot phase is based on travelled distance; support feet stay fixed in world space. The helper's supported head-count range is specific to that scaffold, not a constraint on other styles. Check start, support transfers and the final settle with the selected proportion and speed. The sample character is deliberately simplified and not a realistic human rig.

`MVMotion.handoff(t,options)` returns giver/receiver local hand targets, transfer ownership and the contact interval. Align both hand targets in world space; attach the prop to the current owner. A shared timestamp alone does not create physical contact. `twoBone` reports unreachable targets; change blocking instead of stretching. `turn` returns an interpolation state only: custom view drawings and overlap changes are still required for a full-body turn. Eye targets, hair and accessories belong to the project's character system.

`MVActors.actor` returns actual drawn hand/feet points, limb endpoints, `reachable` and size metadata. Export these to `check_rig.mjs`; do not substitute ideal metadata for the rendered joints. Inspect silhouette, knee pose, contacts and occlusion visually even when lengths pass.

`wipe` covers/uncover frames with a foreground shape; the project decides when to switch the underlying shot. `shapeMatch` interpolates ellipse geometry. `wordToObject` is a simple overlap/opacity primitive; it does not implement glyph-outline morphing or infer which physical object a lyric means. Build those creative transformations from the approved shot objective.

Generate a small motion study with `build_study.py --kind motion --subject figures --style <selected-style>` and inspect the corresponding evidence. For non-character work choose a type/abstract study or implement another relevant difficult effect. Reuse a component only after its behavior fits the chosen film; modularity is not evidence of acting quality.

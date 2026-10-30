# Project assets and performance mechanics

Use concrete reusable code assets after choosing the visual grammar. A new engine can organize a film, but cannot supply its acting, staging or taste. Inspect a difficult original scene before expanding it.

## Character work

For pixel projects use the optional workbench linked from SKILL.md. Its editable layers, palette and explicit pose data are reusable code assets. The bundled step/sit/turn examples are intentionally limited construction aids, not a mature 360-degree cast or verified natural acting. Redesign the selected cast, test contacts, and retain source revisions. Swap a character only after recalibrating foot/ground, silhouette, grip, camera scale and occlusion.

For selected bitmap typography use `scripts/pixel_font.py --project <project> --font <selected-font> --text <canonical-lines.json> --size 16 --out assets/bitmap-font-r1`. It checks real cmap coverage, produces a one-bit glyph atlas and source hashes, and obeys the static-design gate. Use a matching permitted font and inspect stroke clarity at the delivery size; a missing glyph or unreadable tiny character cannot be certified by its font name. Latin pixel helpers also include digits for original time/distance story cards. A raster generated from code/font data can remain reproducible code-authored material. Third-party art is a different asset choice and needs the user's permission and applicable license.

## Specific acting plans

For character-led stories use `assets/contracts/performance-plan.template.json` to specify the relevant shot/actor, intent and visible key poses. Record the gaze target, head orientation, support/weight, contact/release and breathing or deliberate stillness as appropriate. No mandatory idle breathing/wiggle is implied. The agent derives the routine mechanics from the agreed performance instead of asking the user to fill JSON.

Bind that source in `visual-spec.json` as `performance_plan:{path,sha256}`. The actual contract inspector validates actor/shot identity, time ranges and nonempty specific mechanics before prototype promotion/full production. The cast/model source should also be part of the displayed design package. A plan describes intent, not an observed pass. Inspect the relevant playable clip or source-bound continuous frames; put actual timestamped observations and remaining problems in `review.json`. Do not infer emotion from head angles or five filled fields. The user still accepts the shown design, sample and overall cut separately.

## Optional narrative graphics

Load `assets/modules/narrative-ui.js` only when its mechanics fit the accepted design. It exposes:

| Helper | Purpose |
|---|---|
| `MVNarrativeUI.panel(ctx, options)` | A configurable information panel |
| `MVNarrativeUI.rows(ctx, options)` | Original call/message/history rows with title, detail, time and status |
| `MVNarrativeUI.stamp(ctx, options)` | A date/day/distance/section label and value |
| `MVNarrativeUI.route(ctx, options)` | A stylized route with normalized points and optional labels |

Pass approved geometry, palette, text and font. These are original generic graphics, not exact replicas of a phone brand. Returned text boxes can join the actual layout diagnostics. Long text is recorded as overflow rather than silently ellipsized; revise layout/font/shot duration and inspect the encoded result. Route/date/distance values are project story decisions, not automatically verified geography. Build transitions and emotional callbacks from the content rather than repeatedly inserting the same card.

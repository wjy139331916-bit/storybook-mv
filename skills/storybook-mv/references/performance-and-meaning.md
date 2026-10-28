# Acting and lyric-to-picture development

Read only for a project that needs character performance or semantic word/object transformations. Do not make typography/abstract projects invent a cast or plot.

## Prove performance in the selected design

Start from the action's intention and visible response: notice → hesitate/prepare → act → contact/reaction → settle. The pauses can carry the emotion. Use body weight, head angle, eye target, brow/lids/mouth and hand paths together; translating a single image or adding perpetual bounce does not establish acting.

`assets/modules/acting.js` is an original limited stylized example. `MVPerformance.performance(t,{emotion,gaze,gesture})` provides independent face/gesture controls with anticipation/action/settle; `actor` draws frontal-to-profile changes and articulated limbs, returning actual endpoints and local-pose metadata. It uses `motion.js`. Supported example emotions are calm/curious/sad/hopeful/surprised; gestures rest/wave/offer/chest. Customize from the approved model, not a generic mood preset.

This is not a realistic acting rig, full rear-view/360-degree turn, lip-sync engine, automatic choreography or universal anatomy. A full-body turn needs view drawings and occlusion order. A handoff needs both actors placed so the actual hands meet, a clear ownership/contact interval, then release. The demonstration proves only its selected geometry/timing; inspect changed bodies and proportions again. Pixel actions need discrete poses and their own contact tolerance.

Use a short test with the relevant expression change, gaze, difficult contact/support, camera and subtitle layout. Review consecutive frames at full resolution; do not promote limb-length invariants into a claim that the performance feels alive. For rich realistic acting, revisit feasibility and the allowed asset policy early.

## Give words and objects a role

For each selected lyric image record:

- Intended meaning in this project, distinguishing the user's interpretation from an agent's suggestion.
- A concrete event or changing graphic relationship the viewer can perceive.
- The object's role before, during and after the transition; how it returns or changes meaning later if relevant.
- The tracked geometry/position, occlusion or motion that actually joins the shots.
- Reading policy: full subtitle, selected word, in-world text or no visible lyric; do not duplicate contradictory text.

Choose among literal action, bodily reaction, metaphor, perspective/callback or an intentional contrast with the song. No single mode is mandatory. A train ticket can matter if established and revisited; a heart icon on every romantic line rarely develops a story. A repeated chorus can change the relationship, scale, location or graphic rule, or deliberately repeat with a stated reason.

Use a transition because of what it connects: a letter folds into a path; an umbrella's silhouette becomes a station roof; a word's components assemble into an object; the same light carries into another place. Plan the source/end geometry and what remains visible. A simple opacity overlap is not an outline morph. The type demo illustrates an explicit word/particle/light construction, not arbitrary CJK outline conversion.

At a major creative fork, present 2–3 concise alternatives with different visual logic and recommend one based on the brief. Once a direction is accepted, retain it. Do not repeatedly ask about routine shots or discard the entire story for a local repair. A short film/visualizer can develop through rhythm, form or material without a narrative ending.

An independent original example is `assets/style-packs/time-clock.js`: 14 reusable letter strokes become 12 hour marks and two hands, then return to TIME. It implements its own flat strokes and integer-cell pixel rasterizer. Use with the Canvas scaffold at 1280×720, six seconds, 30fps, `PROJECT.treatment='flat'` or `'pixel'`, and no lyric overlay. Its coordinates are example-specific; other aspects and words require a new layout/mapping. The paired encoded clips, comparison image and `time-verification.json` show the inspected scope. Study the correspondence between parts and meaning rather than reusing TIME for unrelated lyrics.

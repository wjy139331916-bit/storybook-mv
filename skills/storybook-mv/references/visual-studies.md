# Controlled visual studies

Use a study when a material taste decision is unresolved and a preview would help. Keep the subject, event, palette, camera, duration and timestamps the same across alternatives; vary only the stated visual treatment. Select 2–3 plausible alternatives from the interview, not a mandatory catalog. Respect the asset policy and production scope. For plan-only work, describe the proposed study; render only if previews are within the request.

The optional original studies cover `flat`, `paper` and `pixel`, using the same geometry and timing. They are modest implementation references, not finished film styles or proof of detailed acting. Select `figures`, `type` or `abstract` explicitly. Do not show humanoids for a no-character concept.

For an isolated toolkit implementation check only (not a substitute for a user-confirmed MV brief):

```bash
python3 <skill-dir>/scripts/build_study.py <new-flat-study> --kind style --subject figures --style flat --tool-self-test
python3 <skill-dir>/scripts/build_study.py <new-paper-study> --kind style --subject figures --style paper --tool-self-test
python3 <skill-dir>/scripts/build_study.py <new-pixel-study> --kind style --subject figures --style pixel --tool-self-test
node <skill-dir>/scripts/render_canvas.mjs --project=<new-flat-study> --out=out/comparison --times=0.5,3.6,4.8
```

For this optional CPU runtime install the exact local dependency stated in `assets/toolkit.json`, or pass `--canvas-module=/absolute/path/to/index.js`. The CLI resolves dependencies from the project. It never downloads packages by itself. To use the browser, install that project's browser dependencies and run its `render.mjs`. CPU output does not certify Chrome, p5 or WebGL behavior.

For no-character work substitute `--subject type` or `--subject abstract`. `--kind motion` adds a foreground wipe to the figures study; transitions for other subjects are already time-based. All studies last six seconds; this is not the song duration.

Inspect full-size stills, consecutive frames and a playable clip. Record identity/readability, material quality, contact, small-screen legibility, frame cost and difficult actions. If none fits, propose another direction rather than forcing a bundled example. Translate the chosen language into a project-specific `visual-spec.json`; do not import the study cast, palette or head count automatically.

See `assets/studies/verification.json` for what was actually rendered and inspected. Keep evidence labels separate: syntax checked, invariant checked, runtime rendered, visually inspected, and accepted by the user. None implies the next. The bundled boards and short clips demonstrate limited code paths, not an end-to-end production MV or general success across agents.

# Reusable drawing methods, not a fixed style menu

Read this after a visual direction is selected, when a reusable implementation can reduce repeated drawing work. Keep discovery open. A new look may use a new project-local pack, another engine, or a custom implementation.

`assets/style-packs/catalog.json` lists four original Canvas examples. Each manifest records palette roles, construction rules, relevant checks and limits. `kit.js` implements clean flat shapes, irregular layered paper, native low-resolution pixel drawing and clipped ink hatching. The illustrated subjects, palette and large-head actor are examples only. Do not import them into a project without reconciling its design.

For an isolated toolkit implementation check only (not a substitute for a user-confirmed MV brief):

```bash
python3 <skill>/scripts/build_demo.py <new-project> --kind style --style cut-paper --subject figures --tool-self-test
node <skill>/scripts/render_canvas.mjs --project=<new-project> --out=out/study-r1 --audio=assets/original-score.wav
```

Select `--style flat|cut-paper|pixel|ink` and `--subject figures|type|abstract` explicitly. All four can use the same eight-second staging and palette, so comparisons expose the drawing method. They do not imply that every original concept fits that staging. Choose 2–3 relevant treatments, or only refine an already selected look. Do not render every pack by default.

For a new project-local style retain:

- A versioned manifest: medium, palette roles, line/material rules, shape and composition rules, motion cadence, text policy and unsupported features.
- Renderer functions and a stable time-based API; isolate names and resources from other packs.
- A small scene using that implementation, including the hardest relevant effect. Reference images alone are not proof of the code renderer.
- A style-specific review checklist, sample outputs and a receipt naming actual code/runtime/inputs.

Keep the selected host and project design stable. Reuse the same character/type assets in design frames and animation. A finished design sheet that is redrawn differently during production defeats consistency.

Pixel example: draw at 240×135, use discrete geometry/poses and bundled Latin bitmap glyphs, constrain the palette, and upscale by integer nearest-neighbor steps. Other aspects are fitted with margins in this demonstration; production reframing needs a separate composition pass. Chinese glyphs require an approved font/atlas and actual inspection. A successful Latin sample is not a CJK result.

Exact grid/color-count checks apply to rendered PNG masters. Lossy H.264/YUV encoding can introduce edge/chroma colors; inspect the actual encoded result separately and use a suitable lossless/RGB master when exact palette preservation is a requirement.

The paper example uses seeded edges, material grain and small shadows. The ink example uses clipped hatch construction. Neither is physical 3D or a substitute for the optional p5.brush route. Freeze texture randomness by object/material and deliberate animation step; never by execution order or wall time.

For a complete original demonstration use `--kind film`: 30 seconds by default, six places, foreground-object joins, original procedural music and original on-screen lines. `--duration` changes only this example's scope; longer holds need a new pacing review. A 60-second development run exposed long pauses, motivating the tighter example. This is a reproducible toolkit example, not the user's song, cast, approved style or completed commission. See `assets/style-packs/verification.json` for actual results and remaining limits.

# Selected-engine execution and rendering

## Choose the adapter explicitly

Run `scripts/preflight.py --project <project-dir> --json` after selecting an engine in the brief. Planning does not require a renderer. A missing engine is reported rather than silently assuming a painterly host.

For Canvas2D explicitly select browser or `--runtime node-canvas`; the latter checks the optional native Canvas dependency without requiring Chrome/p5. Run the selected runtime's actual encoded self-test as described in the main skill's runtime-verification reference. The CPU runner is `scripts/render_canvas.mjs`; it renders the same standard drawing code and records determinism, source hashes and encoded-file checks, but does not emulate browser/p5/WebGL APIs.

Bundled templates: `painted-p5` and `canvas2d`. Remotion/three.js/Blender/custom are guide-only; the preflight reports basic facts and requires a separate executable probe for those adapters. Do not describe guide-only code or tools as installed.

```bash
python3 <skill-dir>/scripts/scaffold.py <project-dir> --engine canvas2d --duration 8 --fps 30
python3 <skill-dir>/scripts/scaffold.py <other-project> --engine painted-p5 --brief <agreed-brief.json> --duration 8
```

Both refuse nonempty destinations. Duration is a prototype length, not a measured song fact. `--brief` preserves chosen style; no style is invented if it is missing. Use `--width` and `--height` together for an explicit prototype size. The supplied portrait brief can select 1080×1920.

## Dependencies and local fonts

For painted-p5, provide Node/npm, p5, p5.brush, Puppeteer Core, Chrome and FFmpeg/FFprobe. For canvas2d, p5 and p5.brush are not needed. Run `npm ci` if a lockfile exists, otherwise `npm install` and keep the generated lock. Puppeteer Core does not download a browser. Use `CHROME_PATH` or `--chrome=/absolute/path`.

The bundled HTML does not fetch Google Fonts. For visible Chinese text add `--require-cjk` to preflight and inspect real glyphs. A valid font name in code does not prove the font is present.

## Frame inspection and encoding

The two bundled hosts share the pinned frame-render CLI:

```bash
node render.mjs --sheet=0,1,2,3 --cols=4 --w=480 --out=out/check/poses.jpg --fps=30
node render.mjs --strip=2:2.5 --out=out/check/action.jpg --fps=30
node render.mjs --sheet=2.3 --crop=760,420,500,400 --w=500 --out=out/check/detail.jpg --fps=30
node render.mjs --clip --range=0:8 --out=out/prototype.mp4 --fps=30
node render.mjs --frames --workers=2 --fps=30
node render.mjs --encode --out=out/video.mp4 --audio=assets/song.mp3 --fps=30
```

Open actual evidence. Choose the inspection according to the design: acting/contact for characters; text reads for typography; pixel grid for pixels; materials/camera for 3D. Inspect movement in consecutive frames and playable video. Repeat timestamps for procedural determinism.

Canvas2d supports screen-space crops; world-following `--crop-at` needs an explicit project adapter. The blank canvas scene is not a finished style sample. The optional painted Clawd/model helpers likewise do not establish a user's cast.

Use the same fps for frames and encoding. Use `--clip --range=a:b --audio=...` for audio-aligned excerpts. Do not feed sparse whole-film frame indices to a zero-based clip encode.

Measure representative frame cost on the actual machine. Watercolour and 3D can need different hardware/workers. Retain source, review evidence and resumable progress. Do not promise another machine's benchmark or call syntax checks a successful render.

## Selected lyric policy

Set `STORY_LYRICS_MODE` from the approved brief: `full-lines`, `key-lines`, `in-world`, `none`, or a project-specific adapter. The base overlay skips unset/no-text/in-world modes. For key lines supply `STORY_DISPLAY_CUES`; for full lines use canonical line cues. A custom typography treatment should use those timings but implement its own visible text logic. Do not let a generic subtitle layer override the concept.

Set `STORY_TEXT_STYLE` from the visual specification when using the base overlay: font, fontSize/minSize, background and color. The generic fallback is neutral and scales with output height; it does not select the project's palette. The CPU runner rejects actual caption overflow rather than silently encoding clipped lines. Inspect font family and glyphs in the selected runtime.

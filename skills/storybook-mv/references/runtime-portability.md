# Destination runtime verification

Transfer the full directory, verify its manifest, then test the chosen runtime on the destination. Dependencies, fonts, input media and project decisions remain separate from skill installation. Do not infer compatibility from a successful import or another machine's sample.

```bash
python3 <skill-dir>/scripts/verify_portable.py <exported-skill-directory>
python3 <skill-dir>/scripts/preflight.py --project <project> --runtime node-canvas --strict --json
```

Canvas2D has two distinct execution options: the existing Chrome/Puppeteer host, and an optional CPU runner using `@napi-rs/canvas` pinned in `assets/toolkit.json`. Select `brief.execution.runtime` explicitly. The CPU runner executes standard local drawing scripts, not the browser DOM, p5.brush or WebGL. Custom DOM/font/image loading needs an explicit adapter; it is not interchangeable automatically.

For the CPU option, install `@napi-rs/canvas@0.1.100` in the project with an exact version and retain the lockfile, or point `--canvas-module` to an existing installation. For browser execution retain the template's exact dependency versions, compatible Chrome and local fonts. Do not install every backend for a planning request. Respect host installation and network policy.

```bash
python3 <skill-dir>/scripts/runtime_smoke.py <new-self-test-project> --runtime node-canvas --record-in <project>
python3 <skill-dir>/scripts/runtime_smoke.py <other-new-self-test-project> --runtime browser --chrome <chrome-path> --record-in <project>
```

The two-second self-test creates original tones and original cue text, renders 60 frames, muxes audio, fully decodes the MP4, checks dimensions/frame count/duration/streams and locates the two known audio pulses. The CPU runner also compares identical timestamps after reverse seeking. The receipt records backend, versions, source/artifact hashes and verification scope. `--record-in` requires the destination to explicitly select that Canvas2D runtime; it copies the playable evidence and receipt without overwriting existing work.

Open the resulting frames/clip to inspect actual glyphs and cue presentation. Add `--require-cjk` to preflight for Chinese projects, supply a permitted local font if necessary and inspect Chinese test text; an English self-test does not certify Chinese glyphs. Preserve font versions/licenses. Re-run the test on another host or after backend/dependency changes.

The bundled self-test certifies only its limited Canvas2D exercise. For painted-p5, Remotion, three.js, Blender or custom projects implement an equivalent exercise with the actual selected adapter and save the same receipt fields; do not use a Canvas2D receipt as evidence for another engine. `engine`, `runtime_backend`, `artifact`, `encoded.full_decode`, `status` and named runtime/version facts are required. Runtime success is separate from project aesthetic and real-recording sync acceptance.

Official implementation references: https://github.com/Brooooooklyn/canvas (native Canvas API and platform support), https://pptr.dev/browsers-api (browser management), https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/reset (drawing-state reset). Consult current official documentation when adapting to a new runtime; keep tested versions in the project.

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

Each self-test certifies only its selected adapter and limited original exercise. Version 3.5 supplies distinct Canvas2D, painted-p5 and Remotion routes as described below; three.js, Blender or custom projects need an equivalent exercise with their actual selected adapter. Do not use a Canvas2D receipt as evidence for another engine. `engine`, `runtime_backend`, `artifact`, `encoded.full_decode`, `status` and named runtime/version facts are required. Runtime success is separate from project aesthetic and real-recording sync acceptance.

Official implementation references: https://github.com/Brooooooklyn/canvas (native Canvas API and platform support), https://pptr.dev/browsers-api (browser management), https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/reset (drawing-state reset). Consult current official documentation when adapting to a new runtime; keep tested versions in the project.

Version 3.2 uses the same Python 3 contract from JavaScript entrypoints; copied projects include its helpers. Select MV_PYTHON explicitly if the destination interpreter is named differently. Native range/resume/estimate behavior is described in native-incremental.md; it is separate from browser compatibility.

Version 3.3 user-stage contracts additionally decode actual design images with Pillow; install `scripts/requirements-media.txt` in the Python interpreter selected by `MV_PYTHON`. Preflight checks Pillow for a real user project even when optional media diagnostics are off. This adds no second rendering engine.

## Windows path, text and audio timelines

Normalize the project root before comparing resolved artifact boundaries: a Windows temporary root can use an 8.3 alias. Keep the project containment check; do not weaken it to a string prefix. Read/write project text as UTF-8 and keep CLI pipes and the Node/Python bridge explicitly UTF-8. The shared bridge selects Python UTF-8 mode; CLI entry points configure only their own streams, not the system locale.

For audio diagnostics, decode before sample-accurate filter trimming, preserve timeline gaps, and reset the trimmed excerpt timestamps. Input seeking at zero can handle AAC priming differently across FFmpeg builds. Check an actual delayed recording and a nonzero excerpt, not only metadata. These fixes do not establish sung-word timing.

The public repository pins text checkout line endings and checks its actual Windows checkout against the portable manifest. Keep binary media untouched. Font and selected-runtime checks remain separate; a Windows native probe does not validate every Windows font or browser.

## Version 3.5 destination recovery and broader probes

Use `runtime_smoke.py <new-project> --runtime browser --install` to prepare only the isolated selected dependencies; or pass `--deps-from <known-node_modules>` without modifying them. Missing packages are diagnosed before rendering. After a failure use `--retry` only for this tool-owned, source-checked workspace, or `--new-revision` to preserve it and create a new destination. Source/options changes reject reuse. Arbitrary existing folders are never deleted.

Use `--cjk --font <actual-local-font>` for a six-second original Chinese probe, actual cmap inspection and changing highlights inspected from decoded video. Its timing is authored synthetic data, not real-song word alignment. Python/platform/dependency versions and the selected bridge interpreter are recorded; diagnostics can suggest an available interpreter, never silently change MV_PYTHON.

Use `--engine painted-p5 --runtime browser --soft-gl` for the actual selected p5.brush exercise. Its browser probe records WebGL renderer identity and sampled frame timing; a Canvas pass cannot stand in for this result. `--engine remotion --runtime browser` uses the optional executable adapter and needs a permitted local server. Standard browser renderers now accept `--probe` and `--estimate`; estimates describe sampled cache costs and explicitly distinguish piped clips from retained JPEG/PNG caches. Whole-film actual cost still depends on the hard scenes.

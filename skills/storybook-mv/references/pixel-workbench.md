# Optional pixel character workbench

Use this module when the project selects pixel art or the user explicitly requests a pixel character tool. Preserve the agreed material policy and style. Do not turn other projects into pixel art. The tool supplies editing mechanics and an original neutral construction example, not an approved cast or proof of natural acting.

## Create the design workspace

Keep the project outside the installed skill. Reuse its truthful `brief.json` and existing workflow; after direction acceptance, use `phase:design`. The CLI checks the same content/stage contract as the video renderers.

```bash
python3 <skill>/scripts/pixel_workbench.py init --project <project> --out assets/pixel/actor-r1
```

Open the generated `workbench.html` through a host-accessible file/browser view. It is self-contained, works offline and makes no network requests. Browser editing needs no npm packages. Python image exports need Pillow from `scripts/requirements-media.txt`. For an isolated original tool exercise, omit `--project` and use `--tool-self-test`; never relabel a user production as a test.

Edit the palette, pixel matrices, per-pose part offsets/visibility/flips, and foot/grip anchors. Touch or pointer input paints the selected part's existing matrix. Use JSON to resize a part or add custom layers/shapes. Per-pose painting preserves other poses by default; clear that option only when deliberately changing the shared part. Palette changes affect all poses. Undo is available in the current session. Download `character.json` to preserve edits; a successful browser download is not a durable save by itself. Respect the host's project/artifact storage policy. Do not promise autosave or cloud storage.

The data format has `canvas`, a maximum 32-color palette, ordered `layers`, named static `frames` with offsets and integer anchors, and optional `actions` listing those frames. `.` means transparent. Use the actual approved proportions and pixel density, not the example's 48×64 canvas by habit. Keep the renderer's integer scaling and disable smoothing. The same matrices can generate a PNG without ceasing to be code-authored, reproducible art. External sprites require the project's explicit asset permission and appropriate attribution.

## Render revised static designs

Download the edited JSON into the same project, then run:

```bash
python3 <skill>/scripts/pixel_workbench.py build --project <project> --model assets/pixel/actor-r1/character.json --out out/pixel-design-r2
```

The output includes static pose PNGs, a labelled design board, the editable source, an offline editor, asset metadata and an honest `not_reviewed` receipt. Design mode permits at most twelve static poses and does not export an animation sheet or enable playback. Importing another JSON cannot enable motion. Existing outputs are preserved; use a new output path or `--new-revision`. Failed builds clean only their own temporary directory, never an existing project.

Show the actual images in the complete design/script review. Add the source model and `assets.json` as additional package artifacts alongside the required actual design frames. Their hashes should accompany the cast design so a material change cannot be silently substituted. The editor does not infer consent, update approvals or change the brief.

## Enable motion only after the correct user review

After the whole design/script package is accepted, retain its evidence and advance the existing brief to its truthful permitted phase. Then export the edited model:

```bash
python3 <skill>/scripts/pixel_workbench.py build --project <project> --model assets/pixel/actor-r1/character.json --out assets/pixel/actor-motion-r1 --mode motion
```

The shared gate rejects discovery, unaccepted designs, stale packages and later stages without their required evidence. Prototype motion duration is checked inside the accepted pilot interval. Each action preview is bounded to eight seconds. The motion workspace enables playback and exports `sprites.png`, `assets.json` and a small Canvas adapter, `sprite-player.js`. These are character assets, not a finished pilot: no soundtrack, sung-word alignment or user acceptance is claimed. Original step/sit/turn examples are rough construction aids; improve poses, weight, contacts and timing before using them as performance evidence.

Load the image and metadata in the selected drawing host. Use `PixelSprite.frameAt(metadata, action, seconds)` and `PixelSprite.draw(ctx, image, metadata, frame, x, y, integerScale, 'foot')`. The draw helper returns world foot/grip points. Align the holding prop to the actual grip, check ground contact and occlusion, and keep imported artwork consistent with the accepted scene. Replacing a sprite does not automatically repair blocking, anatomy or expression. The MV renderer still follows its own ordinary stage gate and reviews.

Only the CLI build supplies a freshly checked motion workspace. Browser exports are editable drafts; changing a JSON field or saving a sprite cannot approve a design. A local editor is not a security boundary against deliberately modified code. Material cast/style revisions return to design review; ordinary fixes within accepted design reuse the appropriate decisions.

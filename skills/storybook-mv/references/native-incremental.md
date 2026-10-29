# Native Canvas ranges, resume and measured cost

Use only after the content/stage gate. These flags belong to `render_canvas.mjs`; another adapter's success is not transferable. Existing nonempty outputs remain protected. Unknown flags fail rather than silently rendering a full film.

```bash
node <skill>/scripts/render_canvas.mjs --project=<project> --range=12:18 --out=out/repair-r2 --resume
node <skill>/scripts/render_canvas.mjs --project=<project> --range=12:18 --out=out/repair-r2 --resume
node <skill>/scripts/render_canvas.mjs --project=<project> --range=0:8 --estimate --times=0.5,3,6.5
```

Range endpoints are global timeline seconds and must align to frame boundaries. A clip starts at its requested source time; audio is trimmed to the same source interval. The report records range, output duration and full timeline duration. Include adjacent joins from the repair plan. This exports the selected interval; joining it into an accepted master requires a separate validated edit/encode and review. It does not automatically replace a section of the master file.

Pass `--resume` on the initial run to retain PNG frames and an atomic checkpoint. Repeating the command reuses frames only when their hashes and the source/config/renderer/audio/range signature match. Missing/corrupt frames are regenerated. Changed inputs require a new output revision; do not bypass the mismatch or relabel an old checkpoint. A completed clip changed outside the renderer is preserved and rejected for reuse.

Resumable PNG caches can be large. `--estimate` renders selected representative frames and reports measured median/max frame samples, estimated render time and conservative sampled PNG storage. It writes no output directory. Include hard frames in `--times`, then allow encoding, review and repair overhead. It does not estimate model billing or promise a completion time.

Use `--max-seconds=<positive-seconds>` and/or `--max-cache-bytes=<positive-bytes>` to reject a run whose measured sample exceeds the declared limit, before creating output. Limits are project choices, not universal quality targets. Offer resolution/material/action/scope tradeoffs when a limit fails. Never silently change the user's chosen look.

The render receipt's `status:"passed"` describes technical checks. `project_acceptance:"not_assessed"` explicitly preserves the distinction from story, beauty, natural performance, verified singing sync and user acceptance.

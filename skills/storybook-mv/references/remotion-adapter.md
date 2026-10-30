# Optional executable Remotion route

Choose Remotion after the approved style/asset discussion when component composition, text layouts or mixed media make it useful. It is now an original bundled adapter, not an installed runtime or a universal character-animation solution. Read the relevant current official Remotion skills/docs as needed; do not wholesale import conflicting production defaults. Keep the existing director's design, pilot and whole-song rough-cut reviews.

Version 3.5 verification boundary: scaffolding, exact package installation, bundling, browser opening/version inspection and shared stage checks have been exercised locally. Actual Remotion MP4 export and the nonzero-interval soundtrack check remain pending on a permitted normal host because this sandbox rejects network-interface inspection. Run `scripts/runtime_smoke.py --engine remotion --runtime browser` and `tests/remotion_smoke.py` there before claiming destination export support. Consult `assets/verification-v35.json`; the passed Canvas/p5 clips do not close this gap.

```bash
python3 <skill>/scripts/scaffold.py <new-project> --engine remotion --phase design --brief <confirmed-brief.json> --duration 8 --install
python3 <skill>/scripts/preflight.py --project <new-project> --strict --json
# From the selected project directory:
node render.mjs --stills=0,2,5 --out=out/design-r1
```

The template pins matching Remotion packages and React, with a lockfile for `npm ci`. Package installation is separate from skill installation. Design exports only bounded stills. The original JSX scaffold is intentionally blank for a user project; implement the accepted art and actual captions. An isolated `runtime_smoke.py --engine remotion --runtime browser` supplies only a named original geometry/pulse exercise. Do not present that exercise as a user MV.

After accepting the whole design/script revision, advance the truthful brief and use `node render.mjs --clip --out=out/pilot-r1/clip.mp4`. Its default prototype interval comes from the accepted design's pilot plan. `--range=START:END` may select only an allowed frame-aligned global interval. The composition keeps the global recording timebase, including nonzero pilots. Full expansion still needs separate design, pilot and whole-scope animatic decisions; a material design change reopens its gate. In animatic phase explicitly set `src/project.json` fidelity to `rough`, dimensions at most 960px on the longest side and at most 15fps, and actually simplify the scene.

Use `--estimate --times=...` for measured sample timing/storage and optional `--max-seconds`/`--max-cache-bytes`. Include difficult frames and allow encoder, review and repair overhead. Do not promise that another engine's sample cost applies. For static preview, moving sample and encoded output use this adapter's commands, then present them through the existing review workspace. The receipt identifies actual range, video digest, selected soundtrack, dependency/platform versions and full decode. An export receipt does not approve aesthetics.

The local renderer requires its browser and a permitted local HTTP/loopback server. `--chrome=<path>` or `CHROME_PATH` selects an existing browser; `--soft-gl` requests the supported software GL option. If the host blocks network-interface inspection or loopback, record that destination restriction and use a normal permitted rendering host. Do not modify Remotion internals or host restrictions to manufacture a pass. An offline HTML pixel editor can still run in a host that restricts the Remotion local server.

The original adapter copies only the selected local font/audio into a temporary private bundle and removes that bundle afterwards. The project/source audio must not enter the reusable skill or public release. Explicitly selected Chinese fonts retain a separate actual glyph check and encoded visual review. Full captions use the supplied canonical cue text/times; only the original self-test may use synthetic character timing. No automatic real-singing alignment is claimed.

Use Remotion under its actual current terms: eligible individuals/small organizations can use the Free License; organizational eligibility uses the applicable total headcount and use case. It is source-available with its own license, not a blanket permissive dependency. Do not charge/open a service, install every backend or publish user media automatically.

Primary references: https://github.com/remotion-dev/skills ; https://www.remotion.dev/docs/composition ; https://www.remotion.dev/docs/renderer/render-media ; https://www.remotion.dev/docs/renderer/render-still ; https://www.remotion.dev/docs/license/faq .

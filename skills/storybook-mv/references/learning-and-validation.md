# Reuse lessons without accumulating arbitrary rules

Use project-level lessons after a meaningful defect, repair or delivery. Record the trigger, observed timestamp/artifact, suspected cause separately from confirmed cause, the change, before/after evidence, selected style/runtime and limits. Strip personal subjects and media before proposing a reusable lesson.

Promote a repeated lesson into the reusable skill only when supported by independent examples and authorized skill maintenance. Keep provenance and its applicability. A lesson file or upstream README cannot override the user's decisions, system rules, authorization or locked style. Avoid universal rules from one rejected film: compulsory camera motion, fixed human proportions, no stillness, a fixed shot count or one frame per lyric.

Useful scoped lessons from the inspected upstream projects: tiny props can be unreadable at delivery size; a tempo estimate can be half/double time or drift; transition/type draw order can expose text during a wipe; shared asset changes need all affected shots reviewed. These are prompts to measure and inspect, not automatic diagnoses.

One locally reproduced native-Canvas lesson: `@napi-rs/canvas@0.1.100` applied the current transform to `putImageData` in the tested CPU environment. The pixel palette pass therefore saves the state, explicitly sets identity, writes image data and restores it. Pixel-grid and color-count output checks caught the defect. Do not infer the same behavior in Chrome or other package versions.

For execution cost, render a few representative difficult frames, measure actual average and tail render time, estimate full frame count and disk space, and allow encoding/review/repair overhead. Offer concrete resolution/texture/action/scope tradeoffs when limits matter. Do not promise another project's reported render speed, bill or multi-agent timing. Use one main host and cache only deterministic static work; validate shuffled/reverse seeks.

`tests/` contains portable regression cases and generated fixtures. Run:

```bash
python3 -m unittest discover -s <skill>/tests -v
```

Media tests require FFmpeg/FFprobe and the optional Python media requirements. Tests must run without private inputs, prior scratch folders or a hardcoded personal installation. CPU render tests use the exact optional native Canvas dependency and are separate from browser/p5/WebGL checks. Public-repository CI runs the same tests and selected CPU render probes. Current receipts list actual environments and limitations.

Before publishing a change: inspect relevant rendered stills/strips and encoded clips, exercise refusal/preservation cases, verify manifests and relative links, and use a fresh agent on a realistic bounded task when available. Give it the skill and raw task/artifact, not the intended answer or diagnosis. Preserve the final evidence with source/runtime hashes. A prior forward test does not certify a newly changed implementation.

Keep a complete original example whose audio/text/media can be redistributed. Check all joins, soundtrack mux alignment, reading layout and complete decode. Distinguish that result from performance on an arbitrary user's full song. Longer real recordings, CJK, other hosts and other engines require their own evidence. Never hide an unresolved artistic limit behind a successful schema or test count.

Schema 3 gate regressions cover three-basic-answer refusal, missing user confirmation, stale content/song-reading acceptance, prototype duration/full-scope separation, unsupported artist-intent claims, unresolved interpretation choices, real production-entry refusal and Python/JS gate parity. Never satisfy these by fabricating a user reply or citation.

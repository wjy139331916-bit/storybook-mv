# From reference to executable visual choices

Use actual supplied media or accessible source frames. Recover earlier analysis before repeating work. State unavailable evidence and separate observed mechanisms from interpretations. Study medium, staging and timing; preserve original subjects and story rather than copying reference scenes.

```bash
python3 <skill>/scripts/media_audit.py reference <reference.mp4> --out <project>/private-references/ref-r1 --crop 0,100,1280,720
python3 <skill>/scripts/media_audit.py compare <reference-frame.png> <rendered-frame.png> --out <project>/private-references/comparison-r1
```

`--crop` is x,y,width,height and must be measured from the real frame; omit it when no crop is needed. The tool measures decoded frame differences, cut candidates, candidate shot lengths and approximate palette colors, and produces a timestamped contact sheet. It does not infer camera moves, transitions, acting, line weight or lyric meaning. Fill its `manual_analysis` from inspected sequences and full-size crops.

Record these in the project reference/design record:

| Dimension | Inspect and record |
|---|---|
| Shapes and staging | Subject size, margins, silhouettes, depth layers, foreground occluders, recurring locations |
| Medium | Palette roles, line width relative to subject, edge construction, fill, grain, shadows |
| Motion | Which body parts change, actual support/contact, pose cadence, held poses, camera path |
| Editing | Shot-duration distribution, important joins and what is tracked across each join |
| Music and text | Entrances/holds, selected accents, reading time, subtitle/world-word separation |
| Meaning | What changes visibly and why a lyric-related object matters to the story or graphic system |

Inspect the whole progression at a coarse interval, then targeted consecutive frames across representative actions and joins. A montage grid cannot prove natural motion. Small frame differences can miss a slow dissolve; large differences can be lighting, rain or grain. Confirm candidates rather than treating the automatic log as ground truth.

Match 1–2 representative frames with original content, then compare subject scale/margins, palette, edges/material, typography, and finally motion in clips. The comparison grid fits differing aspects without stretching; it is a judgment aid, not a similarity score. Record deliberate differences and remaining gaps in `visual-spec.json` or the design notes. Reuse this evidence at the existing design checkpoint; do not create another permission ritual.

Reference media, derived crops and side-by-sides contain the source's pixels. Keep them in a project-private folder excluded from portable skill exports/public distribution, unless sharing those specific files is authorized. Export original code, manifests and original examples; never private photos, recordings or browser state. If a reference is missing, produce only explicitly provisional studies rather than claiming a visual match.

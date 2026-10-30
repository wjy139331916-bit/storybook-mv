# Style-independent route selection

A style is a visual grammar, not a software name. Keep style, assets and engine as separate decisions. The following examples are extensible.

| Desired direction | Plausible route | Main work and evidence |
|---|---|---|
| Watercolour, ink, hand-painted worlds | painted-p5 template | Custom drawing/acting, restrained or lively texture, model/material sheets and action proof |
| Flat/vector illustration, paper collage | canvas2d or suitable custom SVG/Canvas host | Shapes, layer attachment, contact and motivated cutout motion |
| Pixel art | canvas2d with integer logical pixels | Pixel grid, palette, pose frames and no smoothing; never automatically apply watercolour |
| Kinetic typography, graphic lyric MV | canvas2d or Remotion | Type layout, word/line time data, transition hierarchy and phone readability |
| Procedural 3D or camera-led worlds | three.js or Blender | Geometry/material/camera choices, performance and contact; only the route guide is bundled |
| Silhouette, minimal line, abstract visualization | canvas2d, shader or custom engine | Behavioral rules, composition and music mapping; often no character questions |
| Detailed anime or realistic acting | purpose-built 2D/3D rig or authorized hybrid assets | Larger design/animation burden; demonstrate a difficult shot before promising full-song quality |
| Provided/generated footage plus graphics | permitted media host, often Remotion | Explicit asset policy, continuity, timing and tool/cost availability |

Do not force a painterly host for pixels or a human body model for abstract graphics. Head count, palette, lyric mode, shot density and texture motion come from the approved design.

Bundled executable scaffolds: painted-p5, canvas2d and the optional original Remotion adapter. three.js/Blender/custom remain guide-only; do not claim their packages/models/renderers are installed. Remotion dependencies are installed only for the selected route. Consult current official documentation when actually implementing those routes.

Select one primary host, keep the timebase and project decisions shared, and implement only the needed adapter. Keep externally generated footage's time handling distinct from deterministic procedural layers.

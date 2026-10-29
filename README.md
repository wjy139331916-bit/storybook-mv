# MV 创作导演 · storybook-mv

通过分轮提问确认需求，再形成方案、制作样片并检查成片的 Agent Skill。当前版本：**3.2.0**。

不预设画风、人物比例、配色、画面比例或渲染引擎。支持叙事、人物动画、文字、抽象图形和其他适合项目的方向；素材政策由项目确定。

## 让其他 agent 安装

把本仓库地址和下面的指令一起发给编程 agent：

> 请获取这个仓库，先读取 `skills/storybook-mv/SKILL.md`，检查完整性后，将 `skills/storybook-mv/` 完整目录安装到当前工具支持的 Skills 目录，保留 scripts、references、assets 和许可证。若当前工具不支持 Skills 自动发现，则保留在项目中，并在开展相关任务前读取 SKILL.md。先完成安装，选定制作路线后再检查和安装对应依赖。使用时先复用已确认的信息，通过每轮 1—3 个关键问题确定需求，信息充分后给出具体方案，按用户已授权的范围制作。

不要只下载 `SKILL.md`；脚本、参考和素材目录都是技能的一部分。目标目录已经存在时，先比较版本并保留已有修改。

| 环境 | 安装目录 | 调用方式 |
|---|---|---|
| Codex CLI / IDE | `~/.agents/skills/storybook-mv/` 或项目的 `.agents/skills/storybook-mv/` | `$storybook-mv` |
| Claude Code | `~/.claude/skills/storybook-mv/` 或项目的 `.claude/skills/storybook-mv/` | `/storybook-mv` |
| 其他支持 Agent Skills 的工具 | 按宿主工具文档配置 | 读取完整目录中的 `SKILL.md` |
| 不支持 Skills 的 agent | 放入可访问的项目目录 | 每次相关任务先读取技能及必要参考 |

具体平台的安装机制与远程会话共享能力可能不同；本地安装不会自动同步到其他产品。平台说明与来源见 [交接参考](skills/storybook-mv/references/agent-interop.md)。

## 硬约束：先理解歌曲并确认具体内容

**一轮基础题答完，不代表可以开始制作。** 歌名、时长、画幅和画风只是基础信息。AI 必须继续确认具体表现什么、如何发展、有哪些关键画面，并复述内容让使用者确认。确认前只做澄清、参考分析、查证和方案讨论。

有歌词的歌曲须先阅读实际提供或核实的歌词，区分作者公开说明、文本解读和用户改编。不能凭歌名或印象编歌词、编本意。关键含义存在分歧时，给出有依据的不同方向，让使用者选定；事实查不到就保留未知。

制作还须有明确范围：同意短样片不能自动扩大成全曲。脚本会检查内容确认记录、所选歌曲理解和时长上限；旧项目缺少确认记录时不会自动放行。记录必须来自真实用户回复，不能为了通过检查自行填成“已确认”。

## 3.2 的执行检查

- 歌词解读绑定实际歌词文件、可追溯行号和来源快照；作者本意需有已检查的原始来源。
- 内容确认绑定真实用户回复和方案版本；规划状态、缺失音频、错误音轨与过期记录会拦截制作。
- Python 与 JavaScript 制作入口共用同一套校验，修复数值表示导致的确认误判和非横屏画幅错误。
- 整曲扩展前检查实际样片与评审回执；完整字幕检查漏句、重复、顺序、文本、复核状态和所选中文字体的实际字形覆盖。
- 原生 Canvas 支持时间范围导出、校验后的断点续渲染、实测耗时/缓存估算与预算上限。

这些检查不能认证伪造的用户回复、代替理解歌词或保证审美。具体协议见 [执行检查](skills/storybook-mv/references/execution-gates.md)、[局部渲染](skills/storybook-mv/references/native-incremental.md) 和 [能力状态](skills/storybook-mv/assets/capability-matrix.json)。相关记录由 agent 根据实际对话和文件填写，无需让使用者回答哈希或 JSON 问题。

## 能做什么

- 自适应提问、参考分析、可行性取舍和具体方案。
- 同内容的风格对照，以及可复用的扁平、纸艺、像素和线描代码画法；可继续扩展新风格。
- 参考片测量、原生画法拆解、参考画面与实际渲染并排对照。
- 项目视觉规范，统一角色、图形、文字和运动语言。
- 可选的表情、视线、动作与转场组件；歌词物件的意义、呼应和衔接设计。
- 音乐段落与分镜映射、带复核状态的节拍候选、LRC / SRT 导入。
- 解码画面的静止/黑帧/切点候选检查、声明布局与姿势检查、音轨偏移和响度测量。
- 本地看片播放器，支持对照播放、片段循环和按视频校验值绑定的时间点反馈。
- 时间点问题记录、样片检查、共享素材修复范围和定点返工。
- 完整目录导出、文件校验和可播放的 Canvas2D 运行自检。

## 完整性检查

下载后在仓库目录运行：

```bash
python3 skills/storybook-mv/scripts/verify_portable.py skills/storybook-mv
```

这验证导出文件及版本，不代表运行环境或艺术效果已经通过。

## 制作依赖

规划阶段不需要安装所有渲染工具。制作入口使用 Python 3 的统一校验；JavaScript 渲染项目也需要 Python，可用 `MV_PYTHON` 指定解释器。先确定方案和一个主要引擎，再按需准备依赖：

- `canvas2d`：内置空白 Canvas2D 项目，可选择浏览器或可选的 Node Canvas 运行方式。
- `painted-p5`：内置 p5.js / p5.brush 模板，需要对应包、Chrome、FFmpeg 等依赖。
- Remotion、three.js、Blender 和自定义路线：提供选型指导，需要另行实现与验证适配器。

中文项目需要可用的本地中文字体，并检查真实字形。运行方式、版本、自检与验证范围见 [运行参考](skills/storybook-mv/references/runtime-portability.md)。技能不会自行开通付费服务、替换音乐或发布作品。

## 示例与验证范围

![同场景代码处理对照](skills/storybook-mv/assets/style-packs/evidence/style-board.png)

上图是受控实现对照，用来比较处理方式；实际作品需要自己的角色、构图、场景和动作设计。示例不限定可选风格。

版本 3.0.0 增加四种可执行画法、原创完整 30 秒示例、成片与音轨检查工具，以及随仓库分发的回归测试。所有示例都使用原创代码、测试文字和程序合成音乐，不包含个人照片或原歌曲音频。

现有验证主要使用 CPU Canvas2D。浏览器、p5/WebGL、任意完整歌曲及艺术效果需要按实际项目分别验证；3.2 增加了所选中文字体覆盖及原创中文字幕的局部验证；不能把测试通过当作审美保证。3.2 新增验证见 [3.2 验证记录](skills/storybook-mv/assets/verification-v32.json)。早期示例和实测范围见 [3.0 验证记录](skills/storybook-mv/assets/style-packs/verification.json)，旧版受控研究见 [2.0 记录](skills/storybook-mv/assets/studies/verification.json)。

## 测试和示例

```bash
python3 -m pip install -r skills/storybook-mv/scripts/requirements-media.txt
python3 -m unittest discover -s skills/storybook-mv/tests -v
```

媒体测试还需要 FFmpeg / FFprobe。开发环境已通过 78 项回归测试（包含原生渲染条件下的确认与拦截检查）；缺少可选运行环境时相应测试会明确跳过。原生渲染检查可选择精确版本的 `@napi-rs/canvas@0.1.100`，再运行 `tests/render_smoke.py --canvas-module <模块路径> --encode`。仓库自动检查会运行测试和选定的原生渲染探针。

`tests/player_browser.mjs` 提供可选的真实浏览器交互检查，需要 Playwright 与匹配的 Chromium；当前环境未完成该项验证，不能用脚本语法通过替代。

创建独立的工具验证示例（不会改动现有非空目录，不能当作跳过内容确认的用户 MV）：

```bash
python3 skills/storybook-mv/scripts/build_demo.py ./original-mv --kind film --style cut-paper --subject figures --tool-self-test
```

也可以用 `--kind style` 创建 8 秒对照，明确选择 `flat`、`cut-paper`、`pixel` 或 `ink`，以及 `figures`、`type` 或 `abstract`。这些是实现样例，不是技能限定的风格菜单。

打开技能中的 `assets/review-player.html`，选择本地视频即可记录反馈。播放器不上传文件；导出意见后由 agent 核对视频版本，再合并到新的评审记录。

## 项目交接

交给另一个 agent 时，除技能目录外，还需提供项目的 `brief.json`、`DECISIONS.md`、`PROPOSAL.md`，以及已有的视觉规范、分镜、评审、源码和获准转移的素材。注明当前阶段、已锁定的选择和交付要求。

此通用发行目录不包含个人歌曲项目的角色设定、私人照片、歌曲音频、账号凭据或浏览器状态。

## 来源与许可证

保留了第三方代码的原有声明和许可证：

- [上游许可证](skills/storybook-mv/assets/UPSTREAM_LICENSE)
- [绘画模板许可证](skills/storybook-mv/assets/painted-template/LICENSE)
- [Canvas 模板与共用渲染器许可证](skills/storybook-mv/assets/canvas-template/LICENSE)
- [来源与整合说明](skills/storybook-mv/references/upstream-sources.md)

这些许可声明分别适用于所注明的第三方部分；本次发布未为其余新增内容另行指定开源许可。

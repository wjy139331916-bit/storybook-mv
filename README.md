# MV 创作导演 · storybook-mv

通过分轮提问确认需求，再形成方案、制作样片并检查成片的 Agent Skill。当前版本：**2.0.0**。

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

## 能做什么

- 自适应提问、参考分析、可行性取舍和具体方案。
- 同内容、同时间和同配色的代码风格对照；有无人物均可按需选择。
- 项目视觉规范，统一角色、图形、文字和运动语言。
- 可选的动作与转场组件、音乐段落和分镜映射。
- 时间点问题记录、样片检查、共享素材修复范围和定点返工。
- 完整目录导出、文件校验和可播放的 Canvas2D 运行自检。

## 完整性检查

下载后在仓库目录运行：

```bash
python3 skills/storybook-mv/scripts/verify_portable.py skills/storybook-mv
```

这验证导出文件及版本，不代表运行环境或艺术效果已经通过。

## 制作依赖

规划阶段不需要安装所有渲染工具。先确定方案和一个主要引擎，再按需准备依赖：

- `canvas2d`：内置空白 Canvas2D 项目，可选择浏览器或可选的 Node Canvas 运行方式。
- `painted-p5`：内置 p5.js / p5.brush 模板，需要对应包、Chrome、FFmpeg 等依赖。
- Remotion、three.js、Blender 和自定义路线：提供选型指导，需要另行实现与验证适配器。

中文项目需要可用的本地中文字体，并检查真实字形。运行方式、版本、自检与验证范围见 [运行参考](skills/storybook-mv/references/runtime-portability.md)。技能不会自行开通付费服务、替换音乐或发布作品。

## 示例与验证范围

![同场景代码处理对照](skills/storybook-mv/assets/studies/evidence/style-board.png)

上图是受控实现对照，用来比较处理方式；实际作品需要自己的角色、构图、场景和动作设计。示例不限定可选风格。

版本 2.0.0 已实际渲染六段 6 秒代码示例，检查关键连续帧、文件解码和确定性，并完成 2 秒带合成测试音的运行自检。开发时通过 17 项工具检查，以及独立 agent 的提问和无人物样片任务。

实际验证使用 CPU Canvas2D；这不等于已验证浏览器、p5/WebGL、完整歌曲同步、中文字体或所有画风的成片质量。详细记录及样片见 [验证记录](skills/storybook-mv/assets/studies/verification.json)。

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

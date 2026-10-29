# Other agents, portability and handoff

For project continuation use the review workspace helper linked directly from SKILL.md to derive `plan/STATUS.md` and `plan/status.json` from actual packages, decisions and unresolved issues. The card is a concise starting point, not new acceptance; verify its underlying revisions before continuing. Preserve known limitations and do not restart an already settled interview.

## Transfer a complete skill

A host-neutral Agent Skill consists of SKILL.md and its referenced scripts, references and assets. The recipient needs the whole directory, with relative paths preserved. A skill name in a chat or a ChatGPT installation alone does not transfer files, tools, subscriptions or private project inputs to another host.

Export from a local materialized copy:

```bash
python3 <skill-dir>/scripts/export_skill.py --dest <export-parent>
```

This creates `<export-parent>/storybook-mv/`, a normal folder, not an archive. It omits the personal 《特别的人》 profile and `agents/openai.yaml` by default, removes the profile-only link block and includes a SHA-256 manifest. Use `--include-project-profile` only when intentionally moving that project; use `--include-host-metadata` only when the destination wants the original UI metadata. Source licenses remain included.

Do not overwrite an installed destination silently. Do not export credentials, browser state, dependency caches or private photos/audio. Copy project inputs separately only as authorized.

## Local host loading

| Host | Local folder / invocation |
|---|---|
| Codex CLI / IDE | Personal `~/.agents/skills/storybook-mv/`, or project `.agents/skills/storybook-mv/`; invoke `$storybook-mv` or select it in `/skills` |
| Claude Code local | Personal `~/.claude/skills/storybook-mv/`, or project `.claude/skills/storybook-mv/`; invoke `/storybook-mv` |
| Another Agent Skills host | Use its documented discovery folder; retain SKILL.md and resources |
| Agent without skill discovery | Put the directory in an accessible workspace and explicitly ask it to read `storybook-mv/SKILL.md` and relevant references before working |

A local folder does not automatically appear in another product's cloud sessions. Use that host's documented upload/mount/sharing mechanism. For distribution to many users, a host plugin may be appropriate; this skill does not publish itself.

Check the destination's tools. Planning needs reference-reading and conversation ability; executing scripts/rendering needs file access, terminal and the selected backend's prerequisites. Question widgets, image viewers and shell tools differ; use equivalent capabilities, and fall back to plain questions when needed.

## Project handoff contract

Provide these as files, not assumptions about inherited memory:
- `brief.json`: goal, style/asset/output choices, open questions and authorization/phase.
- Schema 5 content/song-reading records plus the actual design/script, pilot and animatic packages and real stage-specific user approvals/limited waivers and actual user confirmation/scope evidence. Missing legacy fields are pending, not implicitly accepted. A new agent must preserve the exact accepted reading/content and cannot broaden prototype duration to a whole song.
- `DECISIONS.md`: confirmed choices, proposed assumptions and explicit revisions.
- `PROPOSAL.md`: intended film, representative moments, proposed backend, tradeoffs and staged deliverables.
- Actual input paths; current timeline/cues/code/review evidence if production has begun.
- `visual-spec.json`, `shot-map.json`, `review.json` and the selected runtime receipt when production has begun; retain issue history and accepted versions.
- Selected style-pack version and project-local modifications; canonical cue files, music-grid review status, diagnostic reports/policies and exact-video viewer notes when present. Include project lessons only with their evidence and applicability, never as instructions overriding the brief.
- A bounded task: current phase, owned output files, acceptance criteria and which decisions are locked.

A new agent reads the brief and current phase before asking questions. It must preserve locked choices, use the selected asset policy and avoid claiming access to unsupplied chat context or tools.

For versioned exports, run `scripts/verify_portable.py` to detect missing/changed resources. Installation integrity is separate from destination runtime compatibility. Re-run the chosen adapter's playable self-test on the destination, and use the project contracts before expanding or revising production. See the main skill's runtime-verification reference; do not import another project's cast or palette from optional studies.

If a team is authorized, split file ownership and keep a coordinator for shared timing, character assets, style and joins. For local Claude Code custom subagents, the host supports preloading skill names with a `skills` field; otherwise pass the skill path explicitly. Do not assume a subagent receives its parent's loaded skill or full interview automatically.

## Sources checked 2026-10-28

- Agent Skills format and relative references: https://agentskills.io/specification
- OpenAI official local skill locations and invocation: https://learn.chatgpt.com/docs/build-skills
- Claude Code local skill locations and invocation: https://code.claude.com/docs/en/skills

Paths describe the respective local products, not a claim that another product reads ChatGPT's private skill store.

For 3.2 transfer the small bound user-confirmation record, canonical/display lyric documents, checked primary-source snapshots, selected audio/font files and hashes, current pilot receipt and actual review artifacts. Preserve private inputs in the project; the generic skill export omits them. The recipient also needs Python 3 for the unified render-entry contract.

A receiving agent resumes the earliest missing/affected review stage. It must present readable scripts, rendered images and playable clips to the user before claiming acceptance. Overall full-song scope, content acceptance and a prototype-pass technical receipt do not replace later user decisions. Other backend skills cannot bypass the director phase; apply the shared operation/dimensions/fps entry check.

# Tool capabilities and adapters

`python tools/adapters.py --target <project> --tools <list>` writes these files. Every file is a thin pointer to
`.ba/core/`; nothing of the workflow is duplicated. Instruction files the user may also edit get a managed
`BA-PIPELINE` block (a `BA-GUARDIAN` or `BA-COPILOT` block left by a predecessor is replaced in place); the rest of those files is never touched.

## What each tool gets

| Capability | Claude Code | AGENTS.md tools¹ | GitHub Copilot | Cursor | Gemini CLI | Kiro |
|---|---|---|---|---|---|---|
| **Instructions** (always loaded) | `CLAUDE.md` block, imports `@.ba/core/MANUAL.md` | `AGENTS.md` block | `.github/copilot-instructions.md` block (Copilot also reads `AGENTS.md`) | `.cursor/rules/ba-pipeline.mdc` (`alwaysApply`) | `GEMINI.md` block, imports `@./.ba/core/MANUAL.md` | `.kiro/steering/ba-pipeline.md` (`inclusion: always`), includes `#[[file:.ba/core/MANUAL.md]]` |
| **Stage commands** (`/ba-intake` …) | Skills `.claude/skills/ba-*/SKILL.md` | — say "run intake"; the instructions map requests to stages | Prompt files `.github/prompts/ba-*.prompt.md` | Commands `.cursor/commands/ba-*.md` | Commands `.gemini/commands/ba-*.toml` | Type `#ba-intake` … (manual steering `.kiro/steering/ba-*.md`) or say "run intake" |
| **Independent reviewer** | Sub-agent `.claude/agents/requirements-reviewer.md` (read-only tools) | Tool's sub-agent if any, else new chat (MANUAL §7) | Custom agent `.github/agents/requirements-reviewer.agent.md`; else new chat | New chat or background agent (MANUAL §7) | New session (MANUAL §7) | New session (MANUAL §7) |
| **Automatic file audit** | `PostToolUse` hook → `ba audit hook` (merged into `.claude/settings.json`) | `ba turn` per turn | `ba turn` per turn | `ba turn` per turn | `ba turn` per turn | `ba turn` per turn |
| **Protect audit logs & core** | Deny rules in `.claude/settings.json` | Instruction only | Instruction only | Instruction only | Instruction only | Instruction only |
| **Runs `ba` tooling** | Yes (shell) | If the tool can run shell commands | Agent mode | Agent | Yes (shell) | Yes (agent runs shell commands, asks first) |

¹ `AGENTS.md` is read by many agents — e.g. OpenAI Codex, GitHub Copilot's coding agent, Cursor, Jules, Amp,
Windsurf and others; Aider and Gemini CLI can be configured to read it. Generate it for any tool not listed.

## Confidence in the generated formats

The formats below were current when this version was written. Tools change their file formats; if a command or
agent doesn't appear, check the tool's docs and adjust `tools/adapters.py` (one function per tool).

| File | Confidence | Check if it doesn't work |
|---|---|---|
| `CLAUDE.md` `@` import, skills, sub-agent, hooks, deny rules | High — tested in this project | Start a new session after generating (skills, agents and hooks load at start) |
| `AGENTS.md` | High — plain markdown | — |
| `.github/copilot-instructions.md` | High | — |
| `.github/prompts/*.prompt.md` (`mode: agent`) | Medium — frontmatter keys have changed between versions | Prompt files enabled in VS Code settings; frontmatter key name (`mode` vs `agent`) |
| `.github/agents/*.agent.md` | Medium — custom agents are recent | Your Copilot plan/version supports custom agents |
| `.cursor/rules/*.mdc` | High | — |
| `.cursor/commands/*.md` | Medium | Your Cursor version supports custom commands |
| `GEMINI.md` `@` import, `.gemini/commands/*.toml` | Medium-high | Imports and custom commands enabled in your Gemini CLI version |
| `.kiro/steering/*.md` (`inclusion: always / manual`, `#[[file:…]]`) | Medium — not yet tried in Kiro | Steering panel lists the files; `#ba-intake` appears in chat suggestions; the manual's content is included |

**Kiro Power:** besides the steering files, the repository ships a self-contained Kiro Power in `kiro-power/`
(Agent Plugins layout: `plugin.json`, 22 skills with their playbooks inline, `POWER.md`, and the workflow in
`package/`). Import it from GitHub (`.../tree/main/kiro-power`) or from a folder; nothing is installed in the project —
the skills find `package/` (marker file `ba-pipeline.package`) and run `package/tools/ba.py`; `ba where --save`
records the path in `.ba/config.json`. The optional `ba-setup` skill pins a copy in `.ba/` with `install.py`.
Kiro's terminals set `TERM_PROGRAM=kiro`: events from them are recorded as `via: assistant:kiro`, and `ba approve`
must run in an operating-system terminal. Rebuild the power with `python tools/build_power.py`. Confidence: medium —
the layout follows the Agent Plugins v1 spec and Kiro's power docs; a power with the same layout runs in Kiro, but
this one has not yet been run in Kiro by the maintainers.

**Kiro note:** Kiro also has its own *Spec* mode that writes requirements in its own format. Use normal chat
sessions for BA Pipeline so the two don't compete for the same work.

## Degraded but safe

Without commands, sub-agents or hooks, the workflow still works: the instruction file maps plain requests to
stage files; the review runs in a fresh chat (a same-conversation review caps the verdict at *Conditional*); and
`ba turn` (or `ba audit sync`) records file changes by hash at the end of every turn. The mechanical checks (`ba check`) and the gates do
not depend on the tool at all.

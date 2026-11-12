---
name: ba-setup
description: "Optional: pin a copy of BA Pipeline inside the open project (.ba/) so the project keeps one version whatever the power's version is, and write Kiro steering files and AGENTS.md; also updates a pinned copy. Not needed to start - the power runs the workflow from its own package. Use when the BA asks to install, pin, update or upgrade the workflow in the project, or the team also uses other AI tools on it. Tiếng Việt: (tuỳ chọn) cài cố định BA Pipeline vào dự án hoặc cập nhật bản đã cài."
compatibility: Needs Python 3.9 or newer (python or python3) and permission to run it.
metadata:
  version: "1.0.0"
---

# ba-setup — pin the workflow inside the project (optional)

The power already runs everything from its `package/` folder; pinning is for teams that want the project to keep
one version, or that also open the project with Claude Code, Copilot, Cursor or Gemini.

## Running BA Pipeline from this power

This power carries the whole workflow in its `package/` folder; the project keeps only its data (`requirements/`,
`audit/`, `.ba/config.json`, `.ba/local/` overrides). Once per session, find the copy to use:

1. **The project pinned its own copy?** If `.ba/tools/ba.py` exists in the project, use it: `python .ba/tools/ba.py`
   and the files in `.ba/core/`.
2. **Otherwise use the power's package** — the folder that holds `ba-pipeline.package`, i.e. `package/` next to this power's
   `skills/` folder. If `.ba/config.json` has `"package"`, that is the path. If you don't know this skill's folder,
   find the marker:
   - Windows (PowerShell): `Get-ChildItem -Path "$env:USERPROFILE\.kiro" -Recurse -Filter ba-pipeline.package -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty DirectoryName`
   - macOS / Linux: `find ~/.kiro -name ba-pipeline.package 2>/dev/null | head -1 | xargs dirname`
   - Not found (the power was imported from a folder elsewhere): ask the BA where the `kiro-power` folder is.
3. Run `python "<package>/tools/ba.py" where --save` from the project root (use `python3` on macOS/Linux; Python
   3.9+ is needed — if it is missing, ask the BA to install it). It prints the command, the manual and the core
   folder to use from now on, and saves the package path in `.ba/config.json` for the next sessions.

In the text below, `ba <command>` means that command (`python "<package>/tools/ba.py" <command>`), `.ba/core/` means
the core folder `ba where` printed, and `templates/…`, `checklists/…`, `profiles/…`, `reference/…` resolve to
`.ba/local/<path>` if the project has it, otherwise `<core>/<path>`. Run commands from the project root.

In Kiro: use a normal chat (Vibe) session, not Spec mode. Human gates are closed by the approver — never by you; in
controlled mode the approver runs `ba approve` in an operating-system terminal outside Kiro.

**Pin (first time):** ask the BA which AI model they use (it is recorded on audit events), then from the project root:
`python "<package>/install.py" init --target . --tools kiro,agents-md --model "<model>"` (add other tools if the team
uses them: `claude`, `copilot`, `cursor`, `gemini`). Preview with `--dry-run` if the BA wants. It copies the workflow
into `.ba/`, keeps the settings already in `.ba/config.json`, and writes `.kiro/steering/` and `AGENTS.md`.

**Update a pinned copy:** `python "<package>/install.py" update --target .` — it keeps the tools already set up
(`--tools` only adds), `.ba/local/`, the settings and every requirement, and migrates status pages.

Afterwards the skills use the project's `.ba/` copy. Tell the BA to start a new chat session so Kiro loads the
steering files, and to use normal (Vibe) sessions. Never edit `.ba/core/` or any `_audit/` file.

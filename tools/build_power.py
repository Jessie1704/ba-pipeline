#!/usr/bin/env python3
"""Build the Kiro Power (Agent Plugins layout) of BA Pipeline from this package.

  python tools/build_power.py [--out kiro-power] [--check]

The power is self-contained: import it and call its skills - no install into the project is needed.

  kiro-power/
    plugin.json                         manifest (name, version, description, author, keywords)
    POWER.md                            Kiro power page (Kiro's earlier power format; same content in short)
    package/                            the workflow: core/, tools/ba.py, install.py, VERSION, CHANGELOG.md
      ba-pipeline.package         marker file - how a skill finds this folder when it doesn't know its path
    skills/ba-pipeline/SKILL.md   entry skill: the operating manual, routing, how to run the tools
    skills/<stage>/SKILL.md             one skill per stage, with the stage playbook inline
    skills/ba-setup/SKILL.md            optional: pin a copy of the workflow inside the project (.ba/)

The project keeps only its own data (requirements/, audit/, .ba/config.json and .ba/local/ overrides); the manual,
templates, checklists and the `ba` tool run from package/. A project that wants its own pinned copy runs ba-setup;
the skills then use the project's .ba/ copy. `--check` exits 1 if the committed power is out of date.
"""

import argparse
import filecmp
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
PACKAGE = TOOLS_DIR.parent
sys.path.insert(0, str(TOOLS_DIR))
import adapters  # noqa: E402

NAME = "ba-pipeline"
MARKER = "ba-pipeline.package"
VERSION = (PACKAGE / "VERSION").read_text(encoding="utf-8").strip()
PACKAGE_FILES = ("core", "tools", "install.py", "VERSION", "CHANGELOG.md", "adapters")
SKIP = shutil.ignore_patterns("__pycache__", "*.pyc", "*.lock", "build_power.py")
DESCRIPTION_LIMIT = 1024  # Agent Skills: description <= 1024 characters
KEYWORDS = ["business analysis", "BA", "requirements", "user story", "acceptance criteria", "BRD", "URD", "RTM",
            "traceability", "UAT", "refinement", "change request", "audit trail", "phân tích nghiệp vụ",
            "yêu cầu nghiệp vụ", "tài liệu BRD", "hướng dẫn sử dụng", "kiểm thử UAT"]
SUMMARY = ("AI-assisted business analysis from the first request to the release: build-ready requirements with "
           "human gates, an independent review, a live traceability matrix and a tamper-evident audit trail. "
           "Tiếng Việt: quy trình BA có AI hỗ trợ từ yêu cầu đầu tiên đến phát hành.")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def fit(text, limit=DESCRIPTION_LIMIT):
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1].rsplit(" ", 1)[0] + "…"


def frontmatter(name, description, extra=""):
    return f"---\nname: {name}\ndescription: {adapters.yaml_value(fit(description))}\n{extra}---\n"


def body(path):
    """A markdown file without its frontmatter."""
    text = path.read_text(encoding="utf-8")
    return re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.S).lstrip("\n")


# How every skill finds and runs the tools. Written once, included in every skill so each one works on its own.
RUN = f"""## Running BA Pipeline from this power

This power carries the whole workflow in its `package/` folder; the project keeps only its data (`requirements/`,
`audit/`, `.ba/config.json`, `.ba/local/` overrides). Once per session, find the copy to use:

1. **The project pinned its own copy?** If `.ba/tools/ba.py` exists in the project, use it: `python .ba/tools/ba.py`
   and the files in `.ba/core/`.
2. **Otherwise use the power's package** — the folder that holds `{MARKER}`, i.e. `package/` next to this power's
   `skills/` folder. If `.ba/config.json` has `"package"`, that is the path. If you don't know this skill's folder,
   find the marker:
   - Windows (PowerShell): `Get-ChildItem -Path "$env:USERPROFILE\\.kiro" -Recurse -Filter {MARKER} -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty DirectoryName`
   - macOS / Linux: `find ~/.kiro -name {MARKER} 2>/dev/null | head -1 | xargs dirname`
   - Not found (the power was imported from a folder elsewhere): ask the BA where the `kiro-power` folder is.
3. Run `python "<package>/tools/ba.py" where --save` from the project root (use `python3` on macOS/Linux; Python
   3.9+ is needed — if it is missing, ask the BA to install it). It prints the command, the manual and the core
   folder to use from now on, and saves the package path in `.ba/config.json` for the next sessions.

In the text below, `ba <command>` means that command (`python "<package>/tools/ba.py" <command>`), `.ba/core/` means
the core folder `ba where` printed, and `templates/…`, `checklists/…`, `profiles/…`, `reference/…` resolve to
`.ba/local/<path>` if the project has it, otherwise `<core>/<path>`. Run commands from the project root.

In Kiro: use a normal chat (Vibe) session, not Spec mode. Human gates are closed by the approver — never by you; in
controlled mode the approver runs `ba approve` in an operating-system terminal outside Kiro.
"""


def stage_skill(name, description):
    return frontmatter(name, description, f"metadata:\n  version: \"{VERSION}\"\n  package: {NAME}\n") + f"""
# {name}

{RUN}
Read the operating manual (`<core>/MANUAL.md`, or the **ba-pipeline** skill) once per session before the first
stage, then follow this playbook exactly.

---

{body(PACKAGE / "core" / "stages" / f"{name}.md")}"""


def entry_skill():
    return frontmatter(NAME, (
        "Business analysis and requirements work with BA Pipeline: new features or requests, meeting notes, "
        "stakeholder questions and answers, scope, process models, user stories with acceptance criteria, UX, "
        "specifications, reviews, handoff packs, BRD/URD/user guides, refinement, UAT, release, change requests, "
        "learning an existing system, audit questions. Use for any requirements task when no more specific "
        "ba-* skill was named, and read it once per session before any ba-* skill. Tiếng Việt: mọi việc phân tích "
        "nghiệp vụ và requirements — feature mới, ghi chú họp, câu hỏi cho stakeholder, phạm vi, user story, đặc tả, "
        "review, bàn giao, BRD/URD, UAT, phát hành, thay đổi."
    ), f"metadata:\n  version: \"{VERSION}\"\n") + f"""
# BA Pipeline — start here

{RUN}
## Pick the stage

Match the request to a stage with `<core>/reference/routing.md` (English and Vietnamese examples). If two stages fit,
ask the BA one question with the options — never start a stage on a guess. A named stage wins. Each stage is also a
skill of this power with its playbook inside (`ba-start`, `ba-intake`, …). Unsure what's next: `ba-next`.

| Stage | When the BA wants to… |
|---|---|
""" + "\n".join(f"| `{n}` | {adapters.STAGE_INTENTS.get(n) or adapters.one_line(d.split('. ')[0], 90)} |"
                for n, d in adapters.stages()) + f"""

---

# Operating manual (the same text as `<core>/MANUAL.md`)

{body(PACKAGE / "core" / "MANUAL.md")}"""


def setup_skill():
    return frontmatter("ba-setup", (
        "Optional: pin a copy of BA Pipeline inside the open project (.ba/) so the project keeps one version "
        "whatever the power's version is, and write Kiro steering files and AGENTS.md; also updates a pinned copy. "
        "Not needed to start - the power runs the workflow from its own package. Use when the BA asks to install, pin, "
        "update or upgrade the workflow in the project, or the team also uses other AI tools on it. Tiếng Việt: (tuỳ "
        "chọn) cài cố định BA Pipeline vào dự án hoặc cập nhật bản đã cài."
    ), f"compatibility: Needs Python 3.9 or newer (python or python3) and permission to run it.\n"
       f"metadata:\n  version: \"{VERSION}\"\n") + f"""
# ba-setup — pin the workflow inside the project (optional)

The power already runs everything from its `package/` folder; pinning is for teams that want the project to keep
one version, or that also open the project with Claude Code, Copilot, Cursor or Gemini.

{RUN}
**Pin (first time):** ask the BA which AI model they use (it is recorded on audit events), then from the project root:
`python "<package>/install.py" init --target . --tools kiro,agents-md --model "<model>"` (add other tools if the team
uses them: `claude`, `copilot`, `cursor`, `gemini`). Preview with `--dry-run` if the BA wants. It copies the workflow
into `.ba/`, keeps the settings already in `.ba/config.json`, and writes `.kiro/steering/` and `AGENTS.md`.

**Update a pinned copy:** `python "<package>/install.py" update --target .` — it keeps the tools already set up
(`--tools` only adds), `.ba/local/`, the settings and every requirement, and migrates status pages.

Afterwards the skills use the project's `.ba/` copy. Tell the BA to start a new chat session so Kiro loads the
steering files, and to use normal (Vibe) sessions. Never edit `.ba/core/` or any `_audit/` file.
"""


def power_md():
    return f"""---
name: "{NAME}"
displayName: "BA Pipeline"
description: {json.dumps(SUMMARY, ensure_ascii=False)}
keywords: {json.dumps(KEYWORDS, ensure_ascii=False)}
author: "Jessie1704"
---

# BA Pipeline {VERSION}

{SUMMARY}

## Start
1. Open the project folder in Kiro and start a normal (Vibe) chat — not Spec mode. Python 3.9+ must be installed.
2. Describe the work, in English or Vietnamese — *"start a new feature: …"*, *"đây là ghi chú họp"* — or call a skill
   (`/ba-start`, `/ba-intake`, …). The skills run the workflow from this power's `package/` folder: nothing to install.
   The first command saves the package path in the project's `.ba/config.json`.
3. Optional: say *"pin BA Pipeline in this project"* (**ba-setup**) to keep a copy of the workflow in `.ba/`.

## What it does
- **Define:** start · intake · elicit · scope · model · stories · UX · spec · review · handoff.
- **Deliver:** refinement (Definition of Ready) · test & UAT · release.
- **Any time:** change requests · BRD/URD/user guides (`ba-docs`) · learn an existing system (`ba-discover`) ·
  what next · audit · profiles · extra stages.
- Modes *quick · standard · controlled*; language *en · vi*.

## Guardrails (the AI follows them in every stage)
- Every statement is a fact with a source, a labelled assumption, a labelled inference or an open question.
- The AI never sets priority, estimates, severity, test results or acceptance, and never closes a human gate: the
  approver does (in controlled mode with `ba approve`, in an operating-system terminal outside Kiro).
- Drafts stay drafts until a named person reviews them; secrets and personal data stay out of prompts.

## Skills in this power
`ba-pipeline` (entry, manual and routing) · {" · ".join(f"`{n}`" for n, _ in adapters.stages())} · `ba-setup`
(optional pin)

Documentation: `package/core/README.md` (English), `package/core/README.vi.md` (tiếng Việt). All rights reserved by the
repository owner; the material adapted from ba-workflow (toaidx1) is included with the author's permission.
"""


def plugin_json():
    return json.dumps({
        "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
        "name": NAME, "version": VERSION, "description": SUMMARY,
        "author": {"name": "Jessie1704"}, "keywords": KEYWORDS,
    }, ensure_ascii=False, indent=2) + "\n"


def build(out):
    out = Path(out)
    if out.exists():
        shutil.rmtree(out)
    (out / "skills").mkdir(parents=True)
    adapters.write_lf(out / "plugin.json", plugin_json())
    adapters.write_lf(out / "POWER.md", power_md())
    files = {f"skills/{NAME}/SKILL.md": entry_skill(), "skills/ba-setup/SKILL.md": setup_skill()}
    files.update({f"skills/{n}/SKILL.md": stage_skill(n, d) for n, d in adapters.stages()})
    for rel, text in files.items():
        (out / rel).parent.mkdir(parents=True, exist_ok=True)
        adapters.write_lf(out / rel, text)
    package = out / "package"
    package.mkdir()
    for name in PACKAGE_FILES:
        source = PACKAGE / name
        if source.is_dir():
            shutil.copytree(source, package / name, ignore=SKIP)
        elif source.is_file():
            shutil.copy2(source, package / name)
    adapters.write_lf(package / MARKER, f"BA Pipeline {VERSION} - the workflow bundled in the Kiro Power.\n"
                                         f"The skills find this folder by this file. Do not edit the files here.\n")
    return sorted(p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file())


def same_tree(a, b):
    cmp = filecmp.dircmp(a, b, ignore=["__pycache__"])
    if cmp.left_only or cmp.right_only or cmp.funny_files:
        return False
    _, mismatch, errors = filecmp.cmpfiles(a, b, cmp.common_files, shallow=False)
    return not mismatch and not errors and all(same_tree(Path(a) / d, Path(b) / d) for d in cmp.common_dirs)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="build_power", description="Build the Kiro Power of BA Pipeline")
    parser.add_argument("--out", default=str(PACKAGE / "kiro-power"))
    parser.add_argument("--check", action="store_true", help="exit 1 if --out differs from a fresh build")
    args = parser.parse_args(argv)
    if args.check:
        with tempfile.TemporaryDirectory() as tmp:
            build(Path(tmp) / "power")
            ok = Path(args.out).is_dir() and same_tree(Path(tmp) / "power", args.out)
        print("kiro power is up to date" if ok else "kiro power is out of date - run python tools/build_power.py")
        return 0 if ok else 1
    files = build(args.out)
    skills = sum(1 for f in files if f.endswith("/SKILL.md"))
    print(f"built {args.out}: {skills} skills, {len(files)} files (BA Pipeline {VERSION})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Tests for install.py. Run from the package root:  python -m unittest discover -s tests -v"""

import io
import json
import re
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE))
sys.path.insert(0, str(PACKAGE / "tools"))
import install  # noqa: E402
import ba  # noqa: E402

FEATURE = "expense-claims"


EXAMPLE_FILE_DATE = 1577836800  # 2020-01-01


def copy_example(target):
    """Copy the example with old file dates: a fresh checkout dates them today, later than its 'Last updated'."""
    shutil.copytree(PACKAGE / "examples" / "requirements", target)
    for path in Path(target).rglob("*"):
        os.utime(path, (EXAMPLE_FILE_DATE, EXAMPLE_FILE_DATE))


class InstallCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="ba-install-"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def inst(self, *argv):
        out = io.StringIO()
        with redirect_stdout(out):
            code = install.main([argv[0], "--target", str(self.tmp), *argv[1:]])
        return code, out.getvalue()

    def check(self, *argv):
        out = io.StringIO()
        with redirect_stdout(out):
            code = ba.main(["--root", str(self.tmp), *argv])
        return code, out.getvalue()

    def add_example(self):
        copy_example(self.tmp / "requirements")

    def events(self, feature=None):
        path = self.tmp / ("requirements/%s/_audit/events.jsonl" % feature if feature else "audit/workspace.jsonl")
        return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


class FreshInstall(InstallCase):
    def test_init_creates_layout(self):
        code, out = self.inst("init")
        self.assertEqual(code, 0, out)
        for rel in (".ba/core/MANUAL.md", ".ba/tools/ba.py", ".ba/VERSION", ".ba/local/README.md",
                    ".ba/local/profiles", "CLAUDE.md", "AGENTS.md", ".claude/skills/ba-intake/SKILL.md"):
            self.assertTrue((self.tmp / rel).exists(), rel)
        config = json.loads((self.tmp / ".ba/config.json").read_text(encoding="utf-8"))
        self.assertEqual(config, {"product": "BA Pipeline", "ba_version": install.VERSION, "requirements_dir": "requirements",
                                  "tools": ["claude", "agents-md"]})
        self.assertEqual(self.events()[-1]["type"], "ba.installed")

    def test_init_twice_refuses(self):
        self.inst("init")
        code, out = self.inst("init")
        self.assertEqual(code, 1)
        self.assertIn("use 'update'", out)

    def test_dry_run_writes_nothing(self):
        code, _ = self.inst("init", "--dry-run")
        self.assertEqual(code, 0)
        self.assertEqual(list(self.tmp.iterdir()), [])

    def test_unrelated_templates_folder_is_left_alone(self):
        (self.tmp / "templates").mkdir()
        (self.tmp / "templates" / "invoice.html").write_text("mine", encoding="utf-8")
        code, out = self.inst("init")
        self.assertEqual(code, 0, out)
        self.assertEqual((self.tmp / "templates" / "invoice.html").read_text(encoding="utf-8"), "mine")


class Update(InstallCase):
    def test_update_keeps_local_and_config(self):
        self.inst("init", "--tools", "agents-md", "--requirements-dir", "requirements")
        (self.tmp / ".ba/local/profiles/my-profile.md").write_text("custom", encoding="utf-8")
        (self.tmp / ".ba/core/MANUAL.md").write_text("tampered", encoding="utf-8")
        code, out = self.inst("update")
        self.assertEqual(code, 0, out)
        self.assertEqual((self.tmp / ".ba/local/profiles/my-profile.md").read_text(encoding="utf-8"), "custom")
        self.assertNotEqual((self.tmp / ".ba/core/MANUAL.md").read_text(encoding="utf-8"), "tampered")
        self.assertEqual(json.loads((self.tmp / ".ba/config.json").read_text(encoding="utf-8"))["tools"], ["agents-md"])
        self.assertEqual(self.events()[-1]["type"], "ba.updated")

    def test_downgrade_refused_unless_forced(self):
        self.inst("init")
        config = json.loads((self.tmp / ".ba/config.json").read_text(encoding="utf-8"))
        config["ba_version"] = "9.9.9"
        (self.tmp / ".ba/config.json").write_text(json.dumps(config), encoding="utf-8")
        code, out = self.inst("update")
        self.assertEqual(code, 1)
        self.assertIn("Refusing to downgrade", out)
        self.assertEqual(self.inst("update", "--force")[0], 0)

    def test_changelog_shown_since_installed_version(self):
        self.inst("init")
        config = json.loads((self.tmp / ".ba/config.json").read_text(encoding="utf-8"))
        config["ba_version"] = "0.1.0"
        (self.tmp / ".ba/config.json").write_text(json.dumps(config), encoding="utf-8")
        code, out = self.inst("update")
        self.assertIn("## 1.0.0", out)
        self.assertNotIn("Before BA Pipeline", out)

    def test_status_reports(self):
        self.inst("init")
        code, out = self.inst("status")
        self.assertEqual(code, 0)
        self.assertIn(f"BA Pipeline {install.VERSION} installed", out)
        self.assertIn("generated files out of date: 0", out)


class Migrations(InstallCase):
    def strip_template_parts(self):
        status = self.tmp / "requirements" / FEATURE / "_status.md"
        text = status.read_text(encoding="utf-8")
        text = re.sub(r"\| Elicitation round \| \d+ \|\n", "", text)
        lines = text.split("\n")
        head = next(i for i, l in enumerate(lines) if l.startswith("## Decision log"))
        i = head + 1
        while i < len(lines) and lines[i].startswith("|"):
            lines[i] = lines[i].rstrip().rsplit("|", 2)[0] + "|"  # drop the last column (Revisit at)
            i += 1
        status.write_text("\n".join(lines), encoding="utf-8")
        return status

    def test_init_migrates_old_status_and_records_it(self):
        self.add_example()
        self.strip_template_parts()
        self.assertIn("missing template parts", self.check("check", FEATURE, "--only", "status")[1])
        code, out = self.inst("init")
        self.assertEqual(code, 0, out)
        self.assertIn("migrate      expense-claims: elicitation-round, revisit-at, answer-mode, questions-per-message, governance", out)
        self.assertIn("expense-claims: fill _status.md -> Governance", out)
        code, out = self.check("check", FEATURE, "--only", "status")
        self.assertIn("PASS  status", out)
        types = [e["type"] for e in self.events(FEATURE)]
        self.assertEqual(types[-1], "template.migrated")
        self.assertIn("file.changed", types)
        self.assertEqual(self.check("audit", "verify", "--all")[0], 0)

    def test_revisit_column_keeps_rows_aligned(self):
        self.add_example()
        status = self.strip_template_parts()
        text = install.mig_revisit_at(status.read_text(encoding="utf-8"))
        lines = text.split("\n")
        head = next(i for i, l in enumerate(lines) if l.startswith("## Decision log")) + 1
        widths = set()
        while lines[head].startswith("|"):
            widths.add(lines[head].count("|"))
            head += 1
        self.assertEqual(len(widths), 1, widths)

    def test_migrations_are_idempotent(self):
        self.add_example()
        text = (self.tmp / "requirements" / FEATURE / "_status.md").read_text(encoding="utf-8")
        for _, _, apply in install.MIGRATIONS:
            text = apply(text)
        for _, _, apply in install.MIGRATIONS:
            self.assertEqual(apply(text), text)

    def test_governance_migration_keeps_po(self):
        self.add_example()
        text = install.mig_governance((self.tmp / "requirements" / FEATURE / "_status.md").read_text(encoding="utf-8"))
        self.assertIn("| Product Owner | Linh Tran (Finance Controller) |", text)
        self.assertLess(text.index("## Governance"), text.index("## Decision log"))
        text = install.mig_answer_mode(text)
        self.assertIn("| Answer mode | ask |", text)
        self.assertIn("| Answer mode | ask |\n| Questions per message | 5 |", install.mig_questions_per_message(text))


class Legacy(InstallCase):
    def make_legacy(self):
        (self.tmp / "CLAUDE.md").write_text("# BA Copilot — Operating Manual\nfull manual here\n", encoding="utf-8")
        skill = self.tmp / ".claude/skills/ba-intake/SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("---\nname: ba-intake\n---\nold full skill\n", encoding="utf-8")
        (self.tmp / ".claude/hooks").mkdir()
        (self.tmp / ".claude/hooks/audit-log.ps1").write_text("# ps", encoding="utf-8")
        (self.tmp / ".claude/settings.json").write_text(json.dumps({"model": "opus", "hooks": {"PostToolUse": [
            {"matcher": "Write|Edit", "hooks": [{"type": "command", "command": "powershell.exe -File .claude/hooks/audit-log.ps1"}]}]}}),
            encoding="utf-8")
        shutil.copytree(PACKAGE / "core" / "templates", self.tmp / "templates")
        shutil.copytree(PACKAGE / "core" / "profiles", self.tmp / "profiles")
        (self.tmp / "profiles" / "my-custom.md").write_text("custom profile", encoding="utf-8")
        (self.tmp / "glossary.md").write_text("# Organisation Glossary\n| Term |\n", encoding="utf-8")

    def test_legacy_needs_flag(self):
        self.make_legacy()
        code, out = self.inst("init")
        self.assertEqual(code, 1)
        self.assertIn("--from-legacy", out)
        self.assertTrue((self.tmp / "CLAUDE.md").read_text(encoding="utf-8").startswith("# BA Copilot"))

    def test_legacy_migration(self):
        self.make_legacy()
        code, out = self.inst("init", "--from-legacy")
        self.assertEqual(code, 0, out)
        backup = next((self.tmp / ".ba/backup").iterdir())
        for rel in ("CLAUDE.md", ".claude/skills/ba-intake/SKILL.md", ".claude/hooks/audit-log.ps1",
                    "templates/_status.md", "profiles/my-custom.md", "glossary.md"):
            self.assertTrue((backup / rel).exists(), rel)
        self.assertEqual((self.tmp / ".ba/local/profiles/my-custom.md").read_text(encoding="utf-8"), "custom profile")
        self.assertTrue((self.tmp / ".ba/local/glossary.md").is_file())
        self.assertFalse((self.tmp / "templates").exists())
        claude = (self.tmp / "CLAUDE.md").read_text(encoding="utf-8")
        self.assertIn("BA-PIPELINE:START", claude)
        self.assertNotIn("full manual here", claude)
        self.assertIn("generated by BA Pipeline", (self.tmp / ".claude/skills/ba-intake/SKILL.md").read_text(encoding="utf-8"))
        settings = json.loads((self.tmp / ".claude/settings.json").read_text(encoding="utf-8"))
        commands = [h["command"] for g in settings["hooks"]["PostToolUse"] for h in g["hooks"]]
        self.assertEqual(settings["model"], "opus")
        self.assertFalse(any("audit-log.ps1" in c for c in commands))
        self.assertTrue(any("audit hook" in c for c in commands))


if __name__ == "__main__":
    unittest.main()

"""Tests for the Kiro Power (tools/build_power.py and the committed kiro-power/ folder).
Run from the package root:  python -m unittest discover -s tests -v
"""

import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE / "tools"))
import adapters  # noqa: E402
import build_power  # noqa: E402

POWER = PACKAGE / "kiro-power"


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, f"{path}: no frontmatter"
    fields = {}
    for line in m.group(1).splitlines():
        if re.match(r"^[a-zA-Z]+:", line):
            key, value = line.split(":", 1)
            value = value.strip()
            fields[key] = json.loads(value) if value.startswith('"') else value
    return fields


class PowerTests(unittest.TestCase):
    def test_committed_power_is_up_to_date(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = build_power.main(["--check"])
        self.assertEqual(code, 0, "kiro-power/ is stale: run python tools/build_power.py")

    def test_manifest_and_power_page(self):
        manifest = json.loads((POWER / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "ba-pipeline")
        self.assertEqual(manifest["version"], (PACKAGE / "VERSION").read_text(encoding="utf-8").strip())
        meta = frontmatter(POWER / "POWER.md")
        self.assertEqual(meta["name"], "ba-pipeline")
        self.assertIn("displayName", meta)

    def test_every_stage_has_a_valid_skill(self):
        names = {p.parent.name for p in (POWER / "skills").glob("*/SKILL.md")}
        expected = {n for n, _ in adapters.stages()} | {"ba-pipeline", "ba-setup"}
        self.assertEqual(names, expected)
        for path in (POWER / "skills").glob("*/SKILL.md"):
            meta = frontmatter(path)
            self.assertEqual(meta["name"], path.parent.name)
            self.assertRegex(meta["name"], r"^[a-z0-9]+(-[a-z0-9]+)*$")
            self.assertLessEqual(len(meta["description"]), 1024, path)

    def test_stage_skills_carry_their_playbook_and_find_the_package(self):
        for name, _ in adapters.stages():
            text = (POWER / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
            playbook = (PACKAGE / "core" / "stages" / f"{name}.md").read_text(encoding="utf-8").split("---\n", 2)[2]
            self.assertIn(playbook.strip()[:200], text)
            self.assertIn(build_power.MARKER, text)
            self.assertIn("where --save", text)
        entry = (POWER / "skills" / "ba-pipeline" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("## 4a. AI guardrails", entry)

    def test_bundled_package_installs_a_project(self):
        tmp = Path(tempfile.mkdtemp(prefix="bga-power-"))
        try:
            installer = POWER / "package" / "install.py"
            result = subprocess.run([sys.executable, str(installer), "init", "--target", str(tmp), "--tools",
                                     "kiro,agents-md", "--model", "claude-opus-5-5"],
                                    capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((tmp / ".ba" / "core" / "MANUAL.md").is_file())
            self.assertTrue((tmp / ".kiro" / "steering" / "ba-pipeline.md").is_file())
            self.assertTrue((tmp / ".kiro" / "steering" / "ba-intake.md").is_file())
            config = json.loads((tmp / ".ba" / "config.json").read_text(encoding="utf-8"))
            self.assertEqual(config["model"], "claude-opus-5-5")
            self.assertEqual(config["tools"], ["kiro", "agents-md"])
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_power_runs_without_installing(self):
        tmp = Path(tempfile.mkdtemp(prefix="bga-noinst-"))
        try:
            shutil.copytree(PACKAGE / "examples" / "requirements", tmp / "requirements")
            tool = POWER / "package" / "tools" / "ba.py"
            run = lambda *a: subprocess.run([sys.executable, str(tool), *a], cwd=tmp, capture_output=True, text=True,  # noqa: E731
                                            encoding="utf-8")
            where = run("where", "--save")
            self.assertEqual(where.returncode, 0, where.stderr)
            self.assertIn("package/tools/ba.py", where.stdout.replace("\\", "/"))
            config = json.loads((tmp / ".ba" / "config.json").read_text(encoding="utf-8"))
            self.assertTrue(config["package"].endswith("kiro-power/package"))
            check = run("check", "expense-claims")
            self.assertNotIn("FAIL", check.stdout, check.stdout)
            context = run("context", "expense-claims", "ba-intake")
            self.assertIn("kiro-power/package/core/", context.stdout.replace("\\", "/"))
            self.assertFalse((tmp / ".ba" / "core").exists(), "nothing is copied into the project")
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_package_has_the_marker_and_no_builder(self):
        self.assertTrue((POWER / "package" / build_power.MARKER).is_file())
        self.assertFalse((POWER / "package" / "tools" / "build_power.py").exists())

    def test_build_writes_lf_and_no_caches(self):
        tmp = Path(tempfile.mkdtemp(prefix="bga-build-"))
        try:
            files = build_power.build(tmp / "p")
            self.assertFalse([f for f in files if "__pycache__" in f or f.endswith(".pyc")])
            for rel in files:
                if rel.endswith((".md", ".json", ".py")):
                    self.assertNotIn(b"\r\n", (tmp / "p" / rel).read_bytes(), rel)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()

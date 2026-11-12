"""Tests for tools/ba.py. Run from the package root:  python -m unittest discover -s tests -v

Each test works on a throwaway copy of examples/ (the expense-claims pilot), so the example stays intact.
"""

import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

PACKAGE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PACKAGE / "tools"))
import ba  # noqa: E402

FEATURE = "expense-claims"


def run(*argv):
    out = io.StringIO()
    with redirect_stdout(out):
        code = ba.main(list(argv))
    return code, out.getvalue()


EXAMPLE_FILE_DATE = 1577836800  # 2020-01-01


def copy_example(target):
    """Copy the example with old file dates: a fresh checkout dates them today, later than its 'Last updated'."""
    shutil.copytree(PACKAGE / "examples" / "requirements", target)
    for path in Path(target).rglob("*"):
        os.utime(path, (EXAMPLE_FILE_DATE, EXAMPLE_FILE_DATE))


class ProjectCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="ba-test-"))
        copy_example(self.tmp / "requirements")
        self.feature = self.tmp / "requirements" / FEATURE

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def ba(self, *argv):
        return run("--root", str(self.tmp), *argv)

    def edit(self, name, old, new):
        path = self.feature / name
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text, f"fixture changed: '{old}' not in {name}")
        path.write_text(text.replace(old, new, 1), encoding="utf-8")


class CheckTests(ProjectCase):
    def test_example_has_no_fail(self):
        code, out = self.ba("check", FEATURE)
        self.assertEqual(code, 0, out)
        self.assertIn("PASS  ground: 28 business rules", out)
        self.assertIn("blocking questions open: 2 (Q-039, Q-057)", out)

    def test_wrong_snapshot_fails(self):
        self.edit("_status.md", "| Questions `Q-` | 24 open", "| Questions `Q-` | 30 open")
        code, out = self.ba("check", FEATURE, "--only", "status")
        self.assertEqual(code, 1)
        self.assertIn("open Q says 30, register has 24", out)

    def test_bold_blocking_is_counted(self):
        code, out = self.ba("check", FEATURE, "--only", "open")
        self.assertIn("Q-039", out)  # its Priority cell is "**Blocking** (...)"

    def test_non_canonical_value_fails(self):
        self.edit("02-questions.md", "| Medium | Rejected — volume", "| Medium | Partly rejected — volume")
        code, out = self.ba("check", FEATURE, "--only", "open")
        self.assertEqual(code, 1)
        self.assertIn("A-028 Status 'Partly rejected", out)

    def test_missing_template_part_warns(self):
        self.edit("_status.md", "| Elicitation round | 2 |\n", "")
        code, out = self.ba("check", FEATURE, "--only", "status")
        self.assertIn("WARN  status: missing template parts ('Elicitation round' preference)", out)

    def test_ranges_flagged_except_history(self):
        with open(self.feature / "_status.md", "a", encoding="utf-8") as f:
            f.write("- Decisions D-017 to D-044 recorded.\n")  # appended under ## History
        code, out = self.ba("check", FEATURE, "--only", "ranges")
        self.assertIn("PASS  ranges", out)
        self.edit("05-stories.md", "## US-001", "See US-002 to US-004.\n\n## US-001")
        code, out = self.ba("check", FEATURE, "--only", "ranges")
        self.assertIn("WARN  ranges: 1 ID ranges", out)

    def test_withdrawn_inline_id_is_defined(self):
        with open(self.feature / "05-stories.md", "a", encoding="utf-8") as f:
            f.write("\nNote: ~~US-099~~ was withdrawn; see US-099 history.\n")
        code, out = self.ba("check", FEATURE, "--only", "ids")
        self.assertIn("PASS  ids", out)

    def test_scenario_without_when_fails(self):
        text = (self.feature / "05-stories.md").read_text(encoding="utf-8")
        first_when = next(line for line in text.splitlines() if line.strip().startswith("When "))
        self.edit("05-stories.md", first_when + "\n", "")
        code, out = self.ba("check", FEATURE, "--only", "gherkin")
        self.assertEqual(code, 1)
        self.assertIn("scenarios missing When/Then", out)

    def test_rule_without_source_fails(self):
        spec = (self.feature / "07-spec.md").read_text(encoding="utf-8")
        row = next(l for l in spec.splitlines() if l.startswith("| BR-001 |"))
        cells = row.split("|")
        cells[4] = " — "  # Source column of: | ID | Rule | Type | Source | Used by |
        self.edit("07-spec.md", row, "|".join(cells))
        code, out = self.ba("check", FEATURE, "--only", "ground")
        self.assertEqual(code, 1)
        self.assertIn("BR-001", out)

    def test_unknown_feature(self):
        code, out = self.ba("check", "nope")
        self.assertEqual(code, 1)
        self.assertIn("FAIL  setup", out)


class AuditTests(ProjectCase):
    def log(self):
        return self.feature / "_audit" / "events.jsonl"

    def entries(self):
        return [json.loads(l) for l in self.log().read_text(encoding="utf-8").splitlines() if l.strip()]

    def test_existing_log_verifies(self):
        code, out = self.ba("audit", "verify", FEATURE)
        self.assertEqual(code, 0, out)

    def test_event_appends_and_chain_holds(self):
        before = len(self.entries())
        code, out = self.ba("audit", "event", "--feature", FEATURE, "--type", "decision.recorded",
                            "--refs", "D-099, D-100", "--summary", "test; with semicolon — and dash", "--actor", "Tester")
        self.assertEqual(code, 0, out)
        last = self.entries()[-1]
        self.assertEqual(last["seq"], before + 1)
        self.assertEqual(last["refs"], ["D-099", "D-100"])
        self.assertEqual(last["actor"], "Tester")
        self.assertEqual(self.ba("audit", "verify", FEATURE)[0], 0)

    def test_tampering_detected(self):
        lines = self.log().read_text(encoding="utf-8").splitlines()
        lines[5] = lines[5].replace('"seq":6', '"seq":6 ', 1) if '"seq":6' in lines[5] else lines[5] + " "
        self.log().write_text("\n".join(lines) + "\n", encoding="utf-8")
        code, out = self.ba("audit", "verify", FEATURE)
        self.assertEqual(code, 1)
        self.assertIn("FAILED", out)

    def test_deleted_line_detected(self):
        lines = self.log().read_text(encoding="utf-8").splitlines()
        del lines[3]
        self.log().write_text("\n".join(lines) + "\n", encoding="utf-8")
        code, out = self.ba("audit", "verify", FEATURE)
        self.assertEqual(code, 1)
        self.assertIn("chain broken", out)

    def test_batch_is_all_or_nothing(self):
        before = len(self.entries())
        bad = self.tmp / "bad.json"
        bad.write_text(json.dumps([{"type": "correction"}, {"summary": "no type"}]), encoding="utf-8")
        code, _ = self.ba("audit", "event", "--json-file", str(bad), "--feature", FEATURE)
        self.assertEqual(code, 1)
        self.assertEqual(len(self.entries()), before)
        good = self.tmp / "good.json"
        good.write_text(json.dumps([{"type": "decision.recorded", "refs": "D-101"},
                                    {"Type": "approval.recorded", "Actor": "Linh Tran", "Refs": "D-043"}]), encoding="utf-8")
        code, out = self.ba("audit", "event", "--json-file", str(good), "--feature", FEATURE)
        self.assertEqual(code, 0, out)
        self.assertEqual(len(self.entries()), before + 2)
        self.assertEqual(self.entries()[-1]["actor"], "Linh Tran")

    def test_workspace_event(self):
        code, out = self.ba("audit", "event", "--type", "profile.changed", "--summary", "x")
        self.assertEqual(code, 0, out)
        self.assertTrue((self.tmp / "audit" / "workspace.jsonl").is_file())
        self.assertEqual(self.ba("audit", "verify", "--all")[0], 0)

    def test_sync_records_added_changed_removed(self):
        code, out = self.ba("audit", "sync", FEATURE)
        self.assertEqual(code, 0, out)
        code, out = self.ba("audit", "sync", FEATURE)
        self.assertIn("nothing changed", out)
        (self.feature / "03-scope.md").write_text("changed\n", encoding="utf-8")
        (self.feature / "09-new.md").write_text("new\n", encoding="utf-8")
        (self.feature / "06-ux.md").unlink()
        code, out = self.ba("audit", "sync", FEATURE, "--dry-run")
        self.assertIn("not yet recorded: 1 added, 1 changed, 1 removed", out)
        code, out = self.ba("audit", "sync", FEATURE)
        self.assertIn("sync: 1 added, 1 changed, 1 removed", out)
        kinds = [e["type"] for e in self.entries()[-3:]]
        self.assertEqual(sorted(kinds), ["file.added", "file.changed", "file.removed"])
        self.assertEqual(self.ba("audit", "verify", FEATURE)[0], 0)

    def test_hook_records_tracked_file_only(self):
        before = len(self.entries())
        for target in (self.feature / "03-scope.md", self.tmp / "README.md", self.feature / "_audit" / "events.jsonl"):
            payload = json.dumps({"session_id": "s1", "tool_name": "Edit", "tool_input": {"file_path": str(target)}})
            sys.stdin = io.TextIOWrapper(io.BytesIO(payload.encode("utf-8")), encoding="utf-8")
            try:
                self.assertEqual(self.ba("audit", "hook")[0], 0)
            finally:
                sys.stdin = sys.__stdin__
        entries = self.entries()
        self.assertEqual(len(entries), before + 1)
        self.assertEqual(entries[-1]["file"], f"requirements/{FEATURE}/03-scope.md")
        self.assertEqual(entries[-1]["source"], "hook")

    def test_hook_never_fails(self):
        sys.stdin = io.TextIOWrapper(io.BytesIO(b"not json"), encoding="utf-8")
        try:
            self.assertEqual(self.ba("audit", "hook")[0], 0)
        finally:
            sys.stdin = sys.__stdin__
        self.assertTrue((self.tmp / "audit" / "hook-errors.log").is_file())


if __name__ == "__main__":
    unittest.main()

"""Tests for what BA Pipeline adds to the BA Copilot base: human gates and approval authority, AI
metadata in the log, the live RTM, KPIs, status/dashboard, Excel export, the handoff check, the new status
migrations and the upgrade path from BA Copilot adapter files.
Run from the package root:  python -m unittest discover -s tests -v
"""

import json
import re
import sys
import unittest
import zipfile
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_ba import FEATURE, PACKAGE, ProjectCase  # noqa: E402
import ba  # noqa: E402

sys.path.insert(0, str(PACKAGE))
import install  # noqa: E402
import adapters  # noqa: E402

QA_PACK = """# QA Pack

## Scenarios
| TS-ID | Covers AC | Type | Preconditions | Steps | Expected result | Priority |
|-------|-----------|------|------|------|------|------|
| TS-001 | AC-001.1 | happy | - | - | - | High |
| TS-002 | AC-001.2, AC-001.3 | alt | - | - | - | High |
"""


class GatesCase(ProjectCase):
    def setUp(self):
        super().setUp()
        # Tests run inside AI tools too: don't let the runner's own environment decide 'via'.
        names = [var for var, _ in ba.ASSISTANT_ENV] + ["BA_VIA"]
        patcher = mock.patch.dict("os.environ", {k: v for k, v in __import__("os").environ.items() if k not in names},
                                  clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)

    def entries(self):
        log = self.feature / "_audit" / "events.jsonl"
        return [json.loads(l) for l in log.read_text(encoding="utf-8").splitlines() if l.strip()]

    def event(self, **fields):
        path = self.tmp / "ev.json"
        path.write_text(json.dumps([fields]), encoding="utf-8")
        return self.ba("turn", FEATURE, "--events", str(path))

    def set_pref(self, name, value):
        path = self.feature / "_status.md"
        text = path.read_text(encoding="utf-8")
        if re.search(r"^\|\s*" + name + r"\s*\|", text, re.M):
            text = re.sub(r"^(\|\s*" + name + r"\s*\|)[^|]*\|", lambda m: f"{m.group(1)} {value} |", text, flags=re.M)
        else:
            text = text.replace("| Stage prompts |", f"| {name} | {value} |\n| Stage prompts |", 1)
        path.write_text(text, encoding="utf-8")

    def rtm_set(self, ac, **values):
        """Set cells of the live row of an AC in rtm.md, the way a tester would."""
        path = self.feature / "rtm.md"
        lines = path.read_text(encoding="utf-8").split("\n")
        header = next(l for l in lines if l.startswith("| AC |"))
        cols = [c.strip() for c in header.strip().strip("|").split("|")]
        for i, line in enumerate(lines):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if cells and cells[0] == ac and not cells[cols.index("Notes")].startswith("Superseded"):
                for key, value in values.items():
                    cells[cols.index(key)] = value
                lines[i] = "| " + " | ".join(cells) + " |"
        path.write_text("\n".join(lines), encoding="utf-8")

    def rtm_row(self, ac, live=True):
        text = (self.feature / "rtm.md").read_text(encoding="utf-8").split("\n")
        header = next(l for l in text if l.startswith("| AC |"))
        cols = [c.strip() for c in header.strip().strip("|").split("|")]
        rows = [dict(zip(cols, [c.strip() for c in l.strip().strip("|").split("|")])) for l in text
                if l.startswith(f"| {ac} |")]
        return [r for r in rows if not r["Notes"].startswith("Superseded")] if live else rows


class AuthorityTests(GatesCase):
    def test_human_gate_needs_named_approver_and_evidence(self):
        before = len(self.entries())
        code, _ = self.event(type="gate.passed", stage="3 Scope")
        self.assertEqual(code, 1)
        code, _ = self.event(type="gate.passed", stage="3 Scope", actor="Claude", refs=["D-043"])
        self.assertEqual(code, 1, "the assistant may not close a human gate")
        code, _ = self.event(type="gate.passed", stage="3 Scope", actor="Linh Tran", refs=["D-043"])
        self.assertEqual(code, 0)
        self.assertEqual(len([e for e in self.entries()[before:] if e["type"] == "gate.passed"]), 1)

    def test_machine_gate_needs_nothing_extra(self):
        code, out = self.event(type="gate.passed", stage="4 Model")
        self.assertEqual(code, 0, out)

    def test_quick_mode_has_fewer_human_gates(self):
        self.set_pref("Mode", "quick")
        code, out = self.event(type="gate.passed", stage="3 Scope")
        self.assertEqual(code, 0, out)
        code, _ = self.event(type="gate.passed", stage="11 Test/UAT")
        self.assertEqual(code, 1)

    def test_template_placeholder_is_not_a_mode(self):
        self.set_pref("Mode", "quick · standard · controlled")
        code, _ = self.event(type="gate.passed", stage="3 Scope")
        self.assertEqual(code, 1, "an unfilled Mode row must fall back to standard, not quick")

    def test_approval_needs_approver_and_evidence(self):
        self.assertEqual(self.event(type="approval.recorded", actor="Linh Tran")[0], 1)
        self.assertEqual(self.event(type="approval.recorded", refs=["D-043"])[0], 1)
        self.assertEqual(self.event(type="approval.recorded", actor="Linh Tran", refs=["D-043"])[0], 0)

    def test_event_records_reporter_model_and_tool(self):
        with mock.patch.dict("os.environ", {"BA_ACTOR": "pilot-BA", "BA_MODEL": "claude-opus-5-5", "BA_VIA": "assistant:test"}):
            code, out = self.event(type="decision.recorded", summary="D-099", actor="Linh Tran")
        self.assertEqual(code, 0, out)
        last = [e for e in self.entries() if e["type"] == "decision.recorded"][-1]
        self.assertEqual(last["actor"], "Linh Tran")
        self.assertEqual(last["reported_by"], "pilot-BA")
        self.assertEqual(last["model"], "claude-opus-5-5")
        self.assertTrue(last["tool"].startswith("ba-pipeline "))
        _, verify = self.ba("audit", "verify", FEATURE)
        self.assertIn("OK", verify)

    def test_controlled_mode_requires_model(self):
        self.set_pref("Mode", "controlled")
        with mock.patch.dict("os.environ", {"BA_MODEL": ""}):
            self.assertEqual(self.event(type="decision.recorded", summary="x")[0], 1)
            self.assertEqual(self.event(type="decision.recorded", summary="x", model="claude-opus-5-5")[0], 0)

    def test_context_names_human_gate(self):
        _, out = self.ba("context", FEATURE, "ba-scope")
        self.assertIn("Human gates in this mode", out)
        self.assertIn("closed by the approver", out)
        _, out = self.ba("context", FEATURE, "ba-model")
        self.assertNotIn("closed by the approver", out)


class RtmTests(GatesCase):
    def build(self):
        (self.feature / "handoff").mkdir(exist_ok=True)
        (self.feature / "handoff" / "qa-pack.md").write_text(QA_PACK, encoding="utf-8")
        code, out = self.ba("rtm", FEATURE)
        self.assertEqual(code, 0, out)
        return out

    def test_build_links_tests_and_computes_coverage(self):
        out = self.build()
        self.assertIn("rows", out)
        self.assertEqual(self.rtm_row("AC-001.1")[0]["Test"], "TS-001")
        self.assertEqual(self.rtm_row("AC-001.1")[0]["Link"], "Confirmed")
        self.assertEqual(self.rtm_row("AC-001.1")[0]["Coverage"], "Pending")
        self.assertEqual(self.rtm_row("AC-001.4")[0]["Coverage"], "Missing link")
        self.assertIn("rtm.md", [p.name for p in self.feature.iterdir()])
        _, again = self.ba("rtm", FEATURE)
        self.assertIn("unchanged", again)

    def test_result_without_evidence_fails(self):
        self.build()
        self.rtm_set("AC-001.1", **{"Test result": "Pass"})
        _, out = self.ba("check", FEATURE, "--only", "rtm")
        self.assertIn("FAIL  rtm", out)
        self.assertIn("without Evidence", out)
        self.rtm_set("AC-001.1", **{"UAT result": "Pass", "Evidence": "https://ci/run/42", "Recorded by": "QA An"})
        self.ba("rtm", FEATURE)
        self.assertEqual(self.rtm_row("AC-001.1")[0]["Coverage"], "Covered")
        _, out = self.ba("check", FEATURE, "--only", "rtm")
        self.assertNotIn("FAIL", out)

    def test_inferred_link_never_counts_as_covered(self):
        self.build()
        self.rtm_set("AC-001.1", **{"Link": "Inferred", "Test result": "Pass", "UAT result": "Pass",
                                    "Evidence": "x", "Recorded by": "QA An"})
        self.ba("rtm", FEATURE)
        self.assertEqual(self.rtm_row("AC-001.1")[0]["Coverage"], "Inferred link")

    def test_stale_coverage_fails_until_rebuilt(self):
        self.build()
        self.rtm_set("AC-001.1", Coverage="Covered")
        _, out = self.ba("check", FEATURE, "--only", "rtm")
        self.assertIn("out of date", out)

    def test_changed_ac_after_testing_is_superseded(self):
        self.build()
        self.rtm_set("AC-001.1", **{"Test result": "Pass", "Evidence": "https://ci/run/42", "Recorded by": "QA An"})
        stories = self.feature / "05-stories.md"
        text = stories.read_text(encoding="utf-8")
        start = text.index("# AC-001.1")
        then = text.index("Then", start)
        stories.write_text(text[:then] + "Then the changed outcome is shown\n  And " + text[then:], encoding="utf-8")
        _, out = self.ba("rtm", FEATURE)
        self.assertIn("1 superseded", out)
        rows = self.rtm_row("AC-001.1", live=False)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["Coverage"], "Superseded")
        self.assertEqual(rows[0]["Test result"], "Pass", "history is kept")
        self.assertEqual(rows[1]["Test result"], "Not run")
        self.assertIn("retest", rows[1]["Notes"])

    def test_untested_changed_ac_is_updated_in_place(self):
        self.build()
        stories = self.feature / "05-stories.md"
        text = stories.read_text(encoding="utf-8")
        then = text.index("Then", text.index("# AC-001.2"))
        stories.write_text(text[:then] + "Then something else\n  And " + text[then:], encoding="utf-8")
        _, out = self.ba("rtm", FEATURE)
        self.assertIn("0 superseded", out)
        self.assertEqual(len(self.rtm_row("AC-001.2", live=False)), 1)

    def test_kpi(self):
        self.build()
        self.rtm_set("AC-001.1", **{"Test result": "Pass", "UAT result": "Pass", "Evidence": "e", "Recorded by": "QA"})
        self.ba("rtm", FEATURE)
        code, out = self.ba("kpi", FEATURE, "--json")
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertTrue(data["Test pass rate: Pass / (Pass + Fail + Blocked)"].startswith("100%"))
        self.assertIn("Review rounds / latest result", data)


class StatusExportTests(GatesCase):
    def test_status_plain_language_and_vietnamese(self):
        code, out = self.ba("status", FEATURE)
        self.assertEqual(code, 0)
        self.assertIn("Waiting for people", out)
        self.assertIn("Linh", out)
        _, out = self.ba("status", FEATURE, "--lang", "vi")
        self.assertIn("Đang chờ ai trả lời", out)

    def test_dashboard_html(self):
        target = self.tmp / "exports" / "d.html"
        target.parent.mkdir()
        code, _ = self.ba("status", FEATURE, "--html", str(target))
        self.assertEqual(code, 0)
        html = target.read_text(encoding="utf-8")
        self.assertIn("<!doctype html>", html)
        self.assertIn("prefers-color-scheme", html)
        self.assertNotIn("<script", html)

    def test_export_xlsx(self):
        out_path = self.tmp / "exports" / "x.xlsx"
        code, out = self.ba("export", FEATURE, "--out", str(out_path))
        self.assertEqual(code, 0, out)
        with zipfile.ZipFile(out_path) as z:
            self.assertIsNone(z.testzip())
            names = z.namelist()
            workbook = z.read("xl/workbook.xml").decode("utf-8")
            sheet = z.read("xl/worksheets/sheet1.xml").decode("utf-8")
        self.assertIn("[Content_Types].xml", names)
        self.assertIn("Decision log", workbook)
        self.assertIn("Acceptance criteria", workbook)
        self.assertIn('state="frozen"', sheet)
        for match in re.findall(r'<sheet name="([^"]+)"', workbook):
            self.assertLessEqual(len(match), 31)

    def test_export_default_is_outside_the_feature(self):
        self.ba("export", FEATURE)
        self.assertTrue((self.tmp / "exports" / f"{FEATURE}.xlsx").is_file())
        self.assertFalse((self.feature / "exports").exists())


class HandoffCheckTests(GatesCase):
    def test_missing_deliverable_fails(self):
        (self.feature / "handoff").mkdir(exist_ok=True)
        status = self.feature / "_status.md"
        listed = set(re.findall(r"`(handoff/[\w.-]+\.md)`", status.read_text(encoding="utf-8")))
        self.assertTrue(listed, "the example lists its deliverables")
        _, out = self.ba("check", FEATURE, "--only", "handoff")
        self.assertIn("FAIL  handoff", out)
        for rel in listed:
            (self.feature / rel).write_text("# pack\n", encoding="utf-8")
        _, out = self.ba("check", FEATURE, "--only", "handoff")
        self.assertIn("PASS  handoff", out)

    def test_ambiguity_catches_vietnamese(self):
        spec = self.feature / "07-spec.md"
        spec.write_text(spec.read_text(encoding="utf-8") + "\nHệ thống phải phản hồi nhanh và thân thiện.\n",
                        encoding="utf-8")
        _, out = self.ba("check", FEATURE, "--only", "ambiguity")
        self.assertIn("'nhanh'", out)
        self.assertIn("'thân thiện'", out)


class MigrationTests(unittest.TestCase):
    STATUS = ("# X — Status\n\n## Preferences\n| Setting | Value |\n|---|---|\n| Stage prompts | on-deviation |\n"
              "| Elicitation round | 1 |\n\n## Gates\n| Stage | Gate | Result | Date | Notes |\n|---|---|---|---|---|\n"
              "| 9 Handoff | Packs | – | | |\n\n## Decision log\n")

    def test_new_migrations_and_idempotence(self):
        text = self.STATUS
        for _, _, apply in install.MIGRATIONS:
            text = apply(text)
        self.assertIn("| Mode | standard |", text)
        self.assertIn("| Language | en |", text)
        self.assertIn("| 11 Test/UAT |", text)
        self.assertLess(text.index("| 9 Handoff |"), text.index("| 10 Refine |"))
        again = text
        for _, _, apply in install.MIGRATIONS:
            again = apply(again)
        self.assertEqual(again, text)


class UpgradeFromCopilotTests(unittest.TestCase):
    def test_copilot_block_and_renamed_files_are_replaced(self):
        import shutil
        import tempfile
        tmp = Path(tempfile.mkdtemp(prefix="bga-up-"))
        try:
            (tmp / "AGENTS.md").write_text("# Mine\n\nkeep me\n\n<!-- BA-COPILOT:START -->\nold\n<!-- BA-COPILOT:END -->\n",
                                           encoding="utf-8")
            old_rule = tmp / ".cursor" / "rules" / "ba-copilot.mdc"
            old_rule.parent.mkdir(parents=True)
            old_rule.write_text("<!-- generated by BA Copilot 0.5.0 - do not edit -->\n", encoding="utf-8")
            user_rule = tmp / ".kiro" / "steering" / "ba-copilot.md"
            user_rule.parent.mkdir(parents=True)
            user_rule.write_text("my own notes\n", encoding="utf-8")
            actions = adapters.generate(tmp, ["agents-md", "cursor", "kiro"])
            agents = (tmp / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("keep me", agents)
            self.assertNotIn("BA-COPILOT", agents)
            self.assertEqual(agents.count("BA-PIPELINE:START"), 1)
            self.assertFalse(old_rule.exists(), "generated BA Copilot file removed")
            self.assertTrue(user_rule.exists(), "a user's file is never removed")
            self.assertIn(("removed (renamed)", ".cursor/rules/ba-copilot.mdc"), actions)
            for stage in ("ba-refine", "ba-uat", "ba-release"):
                self.assertTrue((tmp / ".cursor" / "commands" / f"{stage}.md").is_file())
        finally:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()

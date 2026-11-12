"""Tests for the findings of pre-release review round 2 (N1-N4, RA, n1-n14).
Run from the package root:  python -m unittest discover -s tests -v
"""

import json
import re
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_ba import FEATURE  # noqa: E402
from test_gates import QA_PACK  # noqa: E402
from test_v11 import V11Case  # noqa: E402
import ba  # noqa: E402

VN_GOVERNANCE = """## Governance
| Role | Who (STK-) | Decides on | Source |
|------|-----------|------------|--------|
| Business owner (final say in conflicts) | STK-04 | Priorities | SRC-05 |
| Product Owner | Nguyễn Thị Lan Anh | Scope, acceptance | SRC-05 |
| Gate approvers | {approvers} | | SRC-05 |
| Role conflicts | none | | |

"""
STAKEHOLDERS = """| STK-04 | Trần Văn Minh | Sponsor | | H | budget | priorities |
| STK-05 | Lê Thu Mai | QA lead | | M | tests | acceptance of tests |
"""


class VietnameseCase(V11Case):
    """The example feature with a Vietnamese PO, a BA called 'An' and decisions taken today."""

    def setUp(self):
        super().setUp()
        self.vn_setup()

    def vn_setup(self, approvers="Nguyễn Thị Lan Anh"):
        path = self.feature / "_status.md"
        text = path.read_text(encoding="utf-8")
        text = text.replace("| Product Owner | Linh Tran (Finance Controller) |", "| Product Owner | Nguyễn Thị Lan Anh |")
        text = text.replace("| BA | pilot-BA |", "| BA | An |")
        text = text.replace("## Decision log", VN_GOVERNANCE.format(approvers=approvers) + "## Decision log", 1)
        lines = text.split("\n")
        head = next(i for i, l in enumerate(lines) if l.startswith("## Stakeholders"))
        at = next(i for i in range(head + 3, len(lines)) if not lines[i].startswith("|"))
        lines[at:at] = STAKEHOLDERS.rstrip("\n").split("\n")
        path.write_text("\n".join(lines), encoding="utf-8")
        self.add_decision("D-090", "Scope approved", "chị Lan Anh (PO)")
        self.add_decision("D-091", "Mode quick for this change", "Nguyễn Thị Lan Anh")
        self.add_decision("D-092", "BA's own note", "An")
        self.add_decision("D-093", "Tests accepted", "STK-05")

    def gate(self, actor, refs, stage="3 Scope"):
        return self.event(type="gate.passed", stage=stage, actor=actor, refs=refs)[0]


class NameMatching(VietnameseCase):
    def test_fragments_are_not_people(self):
        for actor in ("a", "h", "An", "Thị", "Anh", "Lan"):
            self.assertEqual(self.gate(actor, ["D-090"]), 1, actor)

    def test_real_po_is_not_blocked_by_a_short_ba_name(self):
        self.assertEqual(self.gate("Nguyễn Thị Lan Anh", ["D-090"]), 0)

    def test_forms_of_address_and_given_names(self):
        self.assertEqual(self.gate("chị Lan Anh", ["D-090"]), 0)

    def test_po_role_word_in_decided_by(self):
        self.add_decision("D-094", "Scope approved again", "PO")
        self.assertEqual(self.gate("Nguyễn Thị Lan Anh", ["D-094"]), 0)

    def test_stakeholder_id_is_resolved(self):
        self.add_decision("D-095", "Scope approved by the sponsor", "Trần Văn Minh")
        self.assertEqual(self.gate("STK-04", ["D-095"]), 0)
        self.assertEqual(self.gate("Trần Văn Minh", ["D-095"]), 0)

    def test_gate_specific_approvers(self):
        path = self.feature / "_status.md"
        path.write_text(path.read_text(encoding="utf-8").replace(
            "| Gate approvers | Nguyễn Thị Lan Anh |", "| Gate approvers | 3,8,9: Nguyễn Thị Lan Anh; 11: STK-05 |"),
            encoding="utf-8")
        self.assertEqual(self.gate("Lê Thu Mai", ["D-093"], "3 Scope"), 1, "QA can't close the scope gate")
        self.assertEqual(self.gate("Lê Thu Mai", ["D-093"], "11 Test/UAT"), 0)
        self.assertEqual(self.gate("Nguyễn Thị Lan Anh", ["D-091"], "11 Test/UAT"), 1, "mapped gate: only its people")


class RulesOfTheGame(VietnameseCase):
    def test_assistant_or_ba_cannot_change_the_mode(self):
        self.assertEqual(self.event(type="settings.changed", summary="Mode: quick", actor="Claude")[0], 1)
        self.assertEqual(self.event(type="settings.changed", summary="Mode: quick", actor="An", refs=["D-092"])[0], 1)
        self.assertEqual(self.event(type="settings.changed", summary="Mode: quick", actor="Nguyễn Thị Lan Anh",
                                    refs=["D-091"])[0], 0)

    def test_gates_check_needs_a_valid_mode_event(self):
        self.set_pref("Mode", "quick")
        self.assertIn("FAIL", self.check_line("gates"))
        self.event(type="settings.changed", summary="Mode: quick", actor="Nguyễn Thị Lan Anh", refs=["D-091"])
        self.assertNotIn("Mode is", self.check_line("gates"))

    def test_evidence_must_be_the_approvers_decision(self):
        self.assertEqual(self.gate("Nguyễn Thị Lan Anh", ["SRC-01"]), 1, "an old source alone")
        self.assertEqual(self.gate("Nguyễn Thị Lan Anh", ["maybe later, see D-090 draft"]), 1, "prose")
        scope = self.feature / "03-scope.md"
        scope.write_text(scope.read_text(encoding="utf-8") + "\n| D-096 | an aside |\n", encoding="utf-8")
        self.assertEqual(self.gate("Nguyễn Thị Lan Anh", ["D-096"]), 1, "a D- outside the Decision log")

    def test_decision_older_than_the_stage_run(self):
        self.add_decision("D-097", "Old approval", "Nguyễn Thị Lan Anh", date="2026-01-01")
        self.event(type="stage.started", stage="3 Scope", decision="run")
        self.assertEqual(self.gate("Nguyễn Thị Lan Anh", ["D-097"]), 1)

    def test_workspace_approval_is_refused(self):
        code, _ = self.ba("audit", "event", "--type", "approval.recorded", "--actor", "Someone", "--refs", "D-999")
        self.assertEqual(code, 1)


class GateValues(VietnameseCase):
    def test_non_canonical_passed_words_fail(self):
        for word in ("Đạt", "Pass", "✅ Passed", "Approved", "**Passed**"):
            self.set_gate(8, word)
            line = self.check_line("gates")
            self.assertIn("FAIL", line, word)
            self.assertIn("8 Review", line, word)

    def test_relayed_approval_without_source_warns(self):
        with mock.patch.dict("os.environ", {"BA_VIA": "assistant:test"}):
            self.assertEqual(self.gate("Nguyễn Thị Lan Anh", ["D-090"]), 0)
        self.set_gate(3, "Passed")
        self.assertIn("relayed by the AI tool", self.check_line("gates"))

    def test_review_reading(self):
        review = self.feature / "08-review.md"
        review.write_text("# 08\n\n**Score:** 60 / 100 · **Verdict:** **Pass**\n\n## Defects\n| # | Severity | Problem | Status |\n"
                          "|---|---|---|---|\n| 1 | 🔴 critical | x | Open |\n", encoding="utf-8")
        line = self.check_line("gates")
        self.assertIn("Pass with Critical", line)
        self.assertIn("score of 60", line)

    def test_deferral_must_be_the_po_s_decision(self):
        self.gate("Nguyễn Thị Lan Anh", ["D-090"], "9 Handoff")
        self.set_gate(9, "Passed")
        review = self.feature / "08-review.md"
        body = "# 08\n\n**Verdict:** Conditional\n\n## Defects\n| # | Severity | Problem | Status |\n|---|---|---|---|\n"
        review.write_text(body + "| 1 | Major | x | Deferred (D-092) |\n", encoding="utf-8")
        self.assertIn("neither fixed nor deferred", self.check_line("gates"))
        review.write_text(body + "| 1 | Major | x | Deferred (D-091) |\n", encoding="utf-8")
        self.assertNotIn("neither fixed nor deferred", self.check_line("gates"))


class ApproveCommand(VietnameseCase):
    def run_approve(self, *extra, typed="Nguyễn Thị Lan Anh", tty=True):
        size = mock.patch("os.get_terminal_size", return_value=__import__("os").terminal_size((80, 24))) if tty else \
            mock.patch("os.get_terminal_size", side_effect=OSError("not a terminal"))
        with size, mock.patch("sys.stdin.isatty", return_value=tty), mock.patch("builtins.input", return_value=typed):
            return self.ba("approve", FEATURE, *extra)

    def test_person_in_a_terminal_can_approve(self):
        code, out = self.run_approve("--gate", "3 Scope", "--as", "Nguyễn Thị Lan Anh", "--decision", "D-090")
        self.assertEqual(code, 0, out)
        last = [e for e in self.entries() if e["type"] == "gate.passed"][-1]
        self.assertEqual(last["via"], "approve")

    def test_refused_inside_an_ai_tool_or_without_a_terminal(self):
        with mock.patch.dict("os.environ", {"CLAUDECODE": "1"}):
            self.assertEqual(self.run_approve("--gate", "3 Scope", "--as", "Nguyễn Thị Lan Anh", "--decision", "D-090")[0], 1)
        self.assertEqual(self.run_approve("--gate", "3 Scope", "--as", "Nguyễn Thị Lan Anh", "--decision", "D-090",
                                          tty=False)[0], 1)
        self.assertEqual(self.run_approve("--gate", "3 Scope", "--as", "Nguyễn Thị Lan Anh", "--decision", "D-090",
                                          typed="someone else")[0], 1)

    def test_controlled_mode_needs_approve(self):
        self.set_pref("Mode", "controlled")
        with mock.patch.dict("os.environ", {"BA_MODEL": "claude-opus-5-5"}):
            self.assertEqual(self.gate("Nguyễn Thị Lan Anh", ["D-090"]), 1)

    def test_document_approval_is_pinned_to_its_content(self):
        (self.feature / "docs").mkdir()
        doc = self.feature / "docs" / "brd.md"
        doc.write_text("# BRD\n\n| Item | Detail |\n|---|---|\n| Review status | Approved |\n", encoding="utf-8")
        self.event(type="approval.recorded", actor="Nguyễn Thị Lan Anh", refs=["D-090"], summary="old-brd.md REJECTED")
        self.assertIn("FAIL", self.check_line("docs"))
        code, out = self.run_approve("--doc", "docs/brd.md", "--as", "Nguyễn Thị Lan Anh", "--decision", "D-090")
        self.assertEqual(code, 0, out)
        self.assertIn("PASS  docs", self.check_line("docs"))
        doc.write_text(doc.read_text(encoding="utf-8") + "\nA change after approval.\n", encoding="utf-8")
        self.assertIn("changed after it was approved", self.check_line("docs"))


class RtmV111(VietnameseCase):
    def test_evidence_that_points_nowhere(self):
        for bad in ("n/a", "see above", "see below", "tested 2026", "Passed 100%", "pass.ok", "ok", "x"):
            self.assertFalse(ba.evidence_ok(bad), bad)
        for good in ("https://ci/run/42", "QA-123", "run 4521", "build #88", "shot-01.png", "SRC-07", "#4521"):
            self.assertTrue(ba.evidence_ok(good), good)

    def test_combined_row_keeps_its_result_on_one_test_only(self):
        self.qa_pack()
        self.ba("rtm", FEATURE)
        path = self.feature / "rtm.md"
        text = path.read_text(encoding="utf-8")
        row = next(l for l in text.split("\n") if l.startswith("| AC-001.2 |"))
        cells = [c.strip() for c in row.strip().strip("|").split("|")]
        cells[4], cells[5], cells[6], cells[7], cells[8] = "TS-002, TS-009", "Pass", "Pass", "https://ci/1", "Lê Thu Mai"
        path.write_text(text.replace(row, "| " + " | ".join(cells) + " |"), encoding="utf-8")
        self.ba("rtm", FEATURE)
        rows = {r["Test"]: r for r in self.rtm_row("AC-001.2")}
        self.assertEqual(rows["TS-002"]["Test result"], "Pass")
        self.assertEqual(rows["TS-009"]["Test result"], "Not run")

    def test_result_log_edits_are_caught(self):
        self.qa_pack()
        self.ba("rtm", FEATURE)
        self.rtm_set("AC-001.1", **{"Test result": "Fail", "Evidence": "https://ci/41", "Recorded by": "Lê Thu Mai"})
        self.ba("rtm", FEATURE)
        path = self.feature / "rtm.md"
        text = path.read_text(encoding="utf-8")
        path.write_text(re.sub(r"^\| \d{4}-\d{2}-\d{2} \| AC-001\.1 \|.*\n", "", text, flags=re.M), encoding="utf-8")
        self.assertIn("Result log differs", self.check_line("rtm"))


class MinorV111(VietnameseCase):
    def test_discover_names(self):
        code, out = self.ba("discover", "Quản lý đơn hàng")
        self.assertEqual(code, 0, out)
        self.assertTrue((self.tmp / "knowledge" / "quan-ly-don-hang").is_dir())
        self.assertEqual(self.ba("discover", "顧客管理")[0], 1)

    def test_verified_needs_a_person_and_a_date(self):
        self.ba("discover", "erp")
        page = self.tmp / "knowledge" / "erp" / "03-rules.md"
        page.write_text(page.read_text(encoding="utf-8").replace("| Status | Draft · Verified |", "| Status | Verified |"),
                        encoding="utf-8")
        _, out = self.ba("discover", "erp")
        self.assertIn("Verified needs a person and a date", out)
        page.write_text(page.read_text(encoding="utf-8").replace("| Verified by | <system or area owner> |", "| Verified by | Marco |")
                        .replace("| Verified on | YYYY-MM-DD |", "| Verified on | 05/01/2025 |"), encoding="utf-8")
        _, out = self.ba("discover", "erp")
        self.assertIn("STALE", out)

    def test_vietnamese_thresholds(self):
        self.set_pref("UAT thresholds", "độ phủ 100, tỉ lệ đạt 95")
        self.assertEqual(ba.uat_thresholds(self.tmp, FEATURE), {"coverage": 100, "pass": 95})
        self.set_pref("UAT thresholds", "coverage 100%")
        _, out = self.ba("kpi", FEATURE, "--json")
        self.assertIn("not set", json.loads(out)["UAT thresholds (PO): coverage / pass"])

    def test_vietnamese_field_names_are_not_vague(self):
        spec = self.feature / "07-spec.md"
        spec.write_text(spec.read_text(encoding="utf-8") + "\nHọ và tên đầy đủ của khách. Quan hệ một - nhiều. "
                        "Ngày hiệu lực sớm nhất. Báo cáo định kỳ lúc 02:00 ngày 1. Nhập một số nguyên.\n", encoding="utf-8")
        line = self.check_line("ambiguity")
        for word in ("'đầy đủ'", "'nhiều'", "'sớm'", "'định kỳ'", "'một số'"):
            self.assertNotIn(word, line)

    def test_cli_events_have_no_model_and_via_cannot_be_faked(self):
        with mock.patch.dict("os.environ", {"BA_MODEL": "claude-opus-5-5"}):
            self.event(type="note", summary="typed by a person")
        self.assertNotIn("model", [e for e in self.entries() if e["type"] == "note"][-1])
        with mock.patch.dict("os.environ", {"CLAUDECODE": "1", "BA_VIA": "cli"}):
            self.event(type="note", summary="assistant pretending")
        self.assertEqual([e for e in self.entries() if e["type"] == "note"][-1]["via"], "assistant:claude-code")


if __name__ == "__main__":
    unittest.main()

"""Tests for the findings of pre-release review round 3 (G1-G12).
Run from the package root:  python -m unittest discover -s tests -v
"""

import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_ba import FEATURE, PACKAGE  # noqa: E402
from test_install import InstallCase  # noqa: E402
from test_v111 import VietnameseCase  # noqa: E402
import ba  # noqa: E402


class ModeAuthority(VietnameseCase):
    """G1, G9: the mode the rules use comes from the PO's logged decision, not from the cell."""

    def go_controlled(self):
        self.set_pref("Mode", "controlled")
        with mock.patch.dict("os.environ", {"BA_MODEL": "claude-opus-5-5"}):
            code, out = self.event(type="settings.changed", summary="Mode: controlled", actor="Nguyễn Thị Lan Anh",
                                   refs=["D-091"])
        self.assertEqual(code, 0, out)

    def test_editing_the_cell_back_to_standard_changes_nothing(self):
        self.go_controlled()
        self.set_pref("Mode", "standard")
        self.assertEqual(ba.effective_mode(self.tmp, FEATURE), "controlled")
        with mock.patch.dict("os.environ", {"BA_MODEL": "claude-opus-5-5"}):
            self.assertEqual(self.gate("Nguyễn Thị Lan Anh", ["D-090"]), 1, "still needs ba approve")
        self.assertIn("Mode cell says 'standard'", self.check_line("gates"))

    def test_notes_and_vietnamese_in_the_mode_cell(self):
        for text, mode in (("controlled · (PO, D-090)", "controlled"), ("Kiểm soát (controlled)", "controlled"),
                           ("nhanh", "quick"), ("quick · standard · controlled", "standard")):
            self.set_pref("Mode", text)
            self.assertEqual(ba.mode_cell(self.tmp, FEATURE)[0], mode, text)

    def test_unreadable_mode_fails(self):
        self.set_pref("Mode", "ki")
        self.assertIn("names no mode", self.check_line("gates"))


class GatesTable(VietnameseCase):
    """G2: the check fails closed."""

    def test_unnumbered_row_fails(self):
        path = self.feature / "_status.md"
        path.write_text(re.sub(r"^\| 8 Review \|", "| Review |", path.read_text(encoding="utf-8"), count=1, flags=re.M),
                        encoding="utf-8")
        self.assertIn("doesn't start with its stage number", self.check_line("gates"))

    def test_renamed_heading_is_still_found(self):
        path = self.feature / "_status.md"
        path.write_text(path.read_text(encoding="utf-8").replace("## Gates", "## 🚦 Cổng kiểm soát (Gates)", 1),
                        encoding="utf-8")
        self.set_gate(8, "Passed")
        self.assertIn("8 Review says passed", self.check_line("gates"))

    def test_missing_table_fails(self):
        path = self.feature / "_status.md"
        text = path.read_text(encoding="utf-8")
        start = text.index("## Gates")
        end = text.index("\n## ", start + 3)
        path.write_text(text[:start] + text[end + 1:], encoding="utf-8")
        self.assertIn("no Gates table", self.check_line("gates"))


class Names(VietnameseCase):
    """G3: names - no family/middle-name matches, one person only, no role words as actors, short names unique."""

    def test_family_and_middle_name_is_not_the_po(self):
        self.assertEqual(self.gate("Nguyễn Thị", ["D-091"]), 1)

    def test_one_person_only(self):
        self.assertEqual(self.gate("Hacker X / Lan Anh", ["D-090"]), 1)

    def test_role_word_is_not_an_actor(self):
        self.assertEqual(self.gate("PO", ["D-090"]), 1)

    def test_resolved_name_is_logged(self):
        self.assertEqual(self.gate("Lan Anh", ["D-090"]), 0)
        last = [e for e in self.entries() if e["type"] == "gate.passed"][-1]
        self.assertEqual(last["actor_resolved"], "Nguyễn Thị Lan Anh")

    def test_notes_and_missing_diacritics(self):
        self.add_decision("D-094", "Scope approved", "Lan Anh - PO")
        self.assertEqual(self.gate("Nguyen Thi Lan Anh", ["D-094"]), 0)

    def test_ba_with_the_po_s_given_name_does_not_block_the_po(self):
        path = self.feature / "_status.md"
        path.write_text(path.read_text(encoding="utf-8").replace("| BA | An |", "| BA | Lan Anh |"), encoding="utf-8")
        self.assertEqual(self.gate("Nguyễn Thị Lan Anh", ["D-091"]), 0)

    def test_forms_of_address_that_are_part_of_the_name(self):
        path = self.feature / "_status.md"
        path.write_text(path.read_text(encoding="utf-8").replace("Nguyễn Thị Lan Anh", "Nguyễn Anh Tuấn"), encoding="utf-8")
        self.add_decision("D-095", "Scope approved", "anh Tuấn")
        self.assertEqual(self.gate("Anh Tuấn", ["D-091"]), 0)
        self.assertEqual(self.gate("Tuấn", ["D-091"]), 1, "one word never")

    def test_short_name_shared_by_two_people_is_ambiguous(self):
        path = self.feature / "_status.md"
        lines = path.read_text(encoding="utf-8").split("\n")
        head = next(i for i, l in enumerate(lines) if l.startswith("## Stakeholders"))
        at = next(i for i in range(head + 3, len(lines)) if not lines[i].startswith("|"))
        lines.insert(at, "| STK-06 | Trần Thị Lan Anh | Finance | | M | invoices | |")
        path.write_text("\n".join(lines), encoding="utf-8")
        self.assertEqual(self.gate("Lan Anh", ["D-091"]), 1)
        self.assertEqual(self.gate("Nguyễn Thị Lan Anh", ["D-091"]), 0)


class KiroAndTerminals(VietnameseCase):
    """G4, G6: Kiro's shell is an AI tool's shell; a redirected stdin is not a terminal."""

    def test_kiro_is_detected(self):
        with mock.patch.dict("os.environ", {"TERM_PROGRAM": "kiro", "BA_MODEL": "claude-opus-5-5"}):
            self.event(type="note", summary="from kiro")
        last = [e for e in self.entries() if e["type"] == "note"][-1]
        self.assertEqual(last["via"], "assistant:kiro")
        self.assertEqual(last["model"], "claude-opus-5-5")

    def test_approve_is_refused_in_kiro_and_without_a_terminal(self):
        with mock.patch.dict("os.environ", {"TERM_PROGRAM": "kiro"}), mock.patch("sys.stdin.isatty", return_value=True):
            code, _ = self.ba("approve", FEATURE, "--gate", "3 Scope", "--as", "Nguyễn Thị Lan Anh", "--decision", "D-090")
        self.assertEqual(code, 1)
        with mock.patch("sys.stdin.isatty", return_value=True), \
                mock.patch("os.get_terminal_size", side_effect=OSError("NUL")):
            code, _ = self.ba("approve", FEATURE, "--gate", "3 Scope", "--as", "Nguyễn Thị Lan Anh", "--decision", "D-090")
        self.assertEqual(code, 1)


class SmallerFixes(VietnameseCase):
    def test_vietnamese_decision_dates(self):
        self.add_decision("D-096", "Scope approved", "Nguyễn Thị Lan Anh", date="12/11/2026")
        self.assertEqual(self.gate("Nguyễn Thị Lan Anh", ["D-096"]), 0)
        self.add_decision("D-097", "Scope approved", "Nguyễn Thị Lan Anh", date="sometime")
        self.assertEqual(self.gate("Nguyễn Thị Lan Anh", ["D-097"]), 1, "an undated decision proves nothing")

    def test_severity_column_variants(self):
        review = self.feature / "08-review.md"
        review.write_text("# 08\n\n**Verdict:** Pass\n\n## Defects\n| # | Sev | Problem | Status |\n|---|---|---|---|\n"
                          "| 1 | Critical | x | Open |\n", encoding="utf-8")
        self.assertIn("Pass with Critical", self.check_line("gates"))
        review.write_text("# 08\n\n**Verdict:** Fail\n\n## Defects\n| # | Problem | Status |\n|---|---|---|\n| 1 | x | Open |\n",
                          encoding="utf-8")
        self.assertIn("no Severity column", self.check_line("gates"))

    def test_vietnamese_rejection_is_not_an_approval(self):
        (self.feature / "docs").mkdir()
        (self.feature / "docs" / "brd.md").write_text("# BRD\n\n| Item | Detail |\n|---|---|\n| Review status | Approved |\n",
                                                      encoding="utf-8")
        self.event(type="approval.recorded", actor="Nguyễn Thị Lan Anh", refs=["D-090"], summary="PO không duyệt brd.md")
        self.assertIn("FAIL", self.check_line("docs"))


class InstallV121(InstallCase):
    def test_update_adds_tools_and_skips_the_builder(self):
        self.assertEqual(self.inst("init", "--tools", "claude")[0], 0)
        self.assertFalse((self.tmp / ".ba" / "tools" / "build_power.py").exists())
        config = json.loads((self.tmp / ".ba" / "config.json").read_text(encoding="utf-8"))
        config["ba_version"] = "1.0.0"
        (self.tmp / ".ba" / "config.json").write_text(json.dumps(config), encoding="utf-8")
        code, out = self.inst("update", "--tools", "kiro")
        self.assertEqual(code, 0, out)
        tools = json.loads((self.tmp / ".ba" / "config.json").read_text(encoding="utf-8"))["tools"]
        self.assertEqual(tools, ["claude", "kiro"])

    def test_init_keeps_power_mode_settings(self):
        (self.tmp / ".ba").mkdir()
        (self.tmp / ".ba" / "config.json").write_text(json.dumps({"requirements_dir": "requirements",
                                                                  "package": "C:/x/kiro-power/package",
                                                                  "model": "claude-opus-5-5"}), encoding="utf-8")
        code, out = self.inst("init", "--tools", "kiro")
        self.assertEqual(code, 0, out)
        config = json.loads((self.tmp / ".ba" / "config.json").read_text(encoding="utf-8"))
        self.assertEqual(config["model"], "claude-opus-5-5")
        self.assertNotIn("package", config)


if __name__ == "__main__":
    unittest.main()

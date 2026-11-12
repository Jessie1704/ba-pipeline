"""Tests for the 0.5 workflow commands in tools/ba.py: turn, context, answers, questions archive, and the
governance / audit / Decision-critical checks. Run from the package root:  python -m unittest discover -s tests -v
"""

import io
import json
import re
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_ba import FEATURE, ProjectCase  # noqa: E402

GOVERNANCE = """
## Governance
| Role | Who (STK-) | Decides on | Source |
|------|-----------|------------|--------|
| Business owner (final say in conflicts) | {bo} | Priorities, conflicts between stakeholders | SRC-05 |
| Product Owner | {po} | Scope, stories, acceptance | SRC-05 |
| Area owner: payroll | STK-02 Marco Rossi | Payroll file | SRC-06 |
| Escalation path | STK-01 → STK-04 | | SRC-06 |
| Role conflicts | {conflict} | | |
"""


class WorkflowCase(ProjectCase):
    def entries(self):
        log = self.feature / "_audit" / "events.jsonl"
        return [json.loads(l) for l in log.read_text(encoding="utf-8").splitlines() if l.strip()]

    def add_governance(self, bo="STK-04 Pierre Laurent", po="STK-01 Linh Tran", conflict="none"):
        path = self.feature / "_status.md"
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace("## Decision log", GOVERNANCE.format(bo=bo, po=po, conflict=conflict).lstrip()
                                     + "\n## Decision log", 1), encoding="utf-8")

    def check(self, name):
        _, out = self.ba("check", FEATURE, "--only", name)
        return next(l for l in out.splitlines() if f"  {name}:" in l)

    def events_file(self, events):
        path = self.tmp / "events.json"
        path.write_text(json.dumps(events), encoding="utf-8")
        return str(path)


class TurnTests(WorkflowCase):
    def test_turn_logs_events_snapshot_and_files(self):
        self.edit("_status.md", "| Questions `Q-` | 24 open", "| Questions `Q-` | 3 open")
        self.edit("03-scope.md", "## In scope", "## In scope\n")
        before = len(self.entries())
        code, out = self.ba("turn", FEATURE, "--events", self.events_file([
            {"type": "decision.recorded", "stage": "3 Scope", "summary": "D-099 test", "refs": ["D-099"]},
            {"type": "question.raised", "stage": "2 Elicit", "summary": "Q-099"}]))
        self.assertEqual(code, 0, out)
        self.assertIn("logged 2 events", out)
        self.assertIn("snapshot updated", out)
        types = [e["type"] for e in self.entries()[before:]]
        self.assertEqual(types[:2], ["decision.recorded", "question.raised"])
        self.assertIn("file.changed", types)
        self.assertIn("PASS  status", self.check("status"))
        _, verify = self.ba("audit", "verify", FEATURE)
        self.assertNotIn("FAIL", verify)

    def test_turn_rejects_whole_batch(self):
        before = len(self.entries())
        code, out = self.ba("turn", FEATURE, "--events", self.events_file([
            {"type": "decision.recorded", "summary": "ok"}, {"type": "stage.skipped", "severity": "Huge"}]))
        self.assertNotEqual(code, 0)
        self.assertEqual(len(self.entries()), before)

    def test_turn_reads_stdin(self):
        for prefix in (b"", b"\xef\xbb\xbf"):  # PowerShell may add a BOM
            events = json.dumps([{"type": "decision.recorded", "summary": "Chỉ số thành công"}], ensure_ascii=False)
            stdin = io.TextIOWrapper(io.BytesIO(prefix + events.encode("utf-8")), encoding="cp1252")  # a Windows console
            with mock.patch("sys.stdin", stdin):
                code, out = self.ba("turn", FEATURE, "--events", "-")
            self.assertEqual(code, 0, out)
            self.assertEqual([e for e in self.entries() if e["type"] == "decision.recorded"][-1]["summary"],
                             "Chỉ số thành công")

    def test_turn_rejects_event_that_is_not_an_object(self):
        before = len(self.entries())
        code, _ = self.ba("turn", FEATURE, "--events", self.events_file(["x"]))
        self.assertEqual(code, 1)
        self.assertEqual(len(self.entries()), before)

    def test_turn_gate_runs_checks_and_logs_them(self):
        code, out = self.ba("turn", FEATURE, "--gate", "--stage", "8 Review")
        self.assertIn("checks:", out)
        runs = [e for e in self.entries() if e["type"] == "check.run"]
        self.assertTrue(runs and re.search(r"\d+ FAIL, \d+ WARN", runs[-1]["summary"]))

    def test_turn_without_events_is_quiet_when_nothing_changed(self):
        self.ba("turn", FEATURE)
        before = len(self.entries())
        code, out = self.ba("turn", FEATURE)
        self.assertEqual(code, 0, out)
        self.assertEqual(len(self.entries()), before)


class ContextTests(WorkflowCase):
    def test_context_for_spec_is_focused(self):
        code, out = self.ba("context", FEATURE, "ba-spec")
        self.assertEqual(code, 0, out)
        for part in ("## Gates", "## Open items", "workflow-approval"):
            self.assertIn(part, out)
        self.assertLess(len(out.encode("utf-8")), 40_000)

    def test_drafting_stages_get_open_questions(self):
        _, out = self.ba("context", FEATURE, "ba-stories")
        self.assertIn("## Open questions", out)
        self.assertIn("- Q-057 [Blocking]", out)
        self.assertNotIn("- Q-038", out)  # Nice to know left out
        _, scope = self.ba("context", FEATURE, "ba-scope")
        self.assertNotIn("## Open questions", scope)

    def test_context_prompts_for_foundations_before_scope(self):
        note = "Foundations not checked yet"
        self.assertNotIn(note, self.ba("context", FEATURE, "ba-elicit")[1])  # scope already exists
        (self.feature / "03-scope.md").unlink()
        self.assertIn(note, self.ba("context", FEATURE, "ba-elicit")[1])
        self.edit("01-intake.md", "## Actors", "## Foundations\n\n## Actors")
        self.assertNotIn(note, self.ba("context", FEATURE, "ba-elicit")[1])

    def test_context_prompts_for_areas_until_one_is_named(self):
        self.add_governance()
        self.assertNotIn("No areas named yet", self.ba("context", FEATURE, "ba-scope")[1])
        self.edit("_status.md", "| Area owner: payroll | STK-02 Marco Rossi |", "| Area owner: <area> | |")
        self.assertIn("No areas named yet", self.ba("context", FEATURE, "ba-scope")[1])
        self.edit("_status.md", "| `workflow-approval` |", "| `small-change` |")
        self.assertNotIn("No areas named yet", self.ba("context", FEATURE, "ba-scope")[1])

    def test_context_for_intake_lists_profile_signals(self):
        code, out = self.ba("context", FEATURE, "ba-intake")
        self.assertEqual(code, 0, out)
        self.assertIn("Signals", out)

    def test_unknown_stage(self):
        code, _ = self.ba("context", FEATURE, "ba-nope")
        self.assertNotEqual(code, 0)


class AnswerFormTests(WorkflowCase):
    def test_round_trip(self):
        code, out = self.ba("answers", "new", FEATURE, "--ids", "Q-034,Q-035,Q-036")
        self.assertEqual(code, 0, out)
        form = self.feature / "answers" / "round-01.md"
        text = form.read_text(encoding="utf-8")
        self.assertEqual(text.count("### Q-"), 3)
        self.assertIn("← recommended", text)
        text = text.replace("Answered by (default for every question): ", "Answered by (default for every question): Linh", 1)
        i = text.index("### Q-034")
        j = text.index("- [ ] (a)", i)
        text = text[:j] + "- [x] (a)" + text[j + 9:]
        i = text.index("### Q-036")
        j = text.index("Answer / notes: ", i)
        text = text[:j] + "Answer / notes: hold only the mismatched claims" + text[j + 16:]
        form.write_text(text, encoding="utf-8")

        code, out = self.ba("answers", "read", FEATURE)
        self.assertEqual(code, 0, out)
        self.assertRegex(out, r"Q-034: \(a\) .*by: Linh")
        self.assertIn("hold only the mismatched claims", out)
        self.assertIn("skipped (no answer): Q-035", out)
        self.assertFalse(form.exists())
        moved = list((self.feature / "sources").glob("SRC-*-answers-round-01.md"))
        self.assertEqual(len(moved), 1)

    def fill(self, question, old, new):
        form = self.feature / "answers" / "round-01.md"
        text = form.read_text(encoding="utf-8")
        i = text.index(old, text.index(f"### {question}"))
        form.write_text(text[:i] + new + text[i + len(old):], encoding="utf-8")

    def test_text_written_under_an_option_is_read(self):
        self.ba("answers", "new", FEATURE, "--ids", "Q-034,Q-035")
        self.fill("Q-034", "- [ ] Other (write below)\n", "- [x] Other (write below)\n3 working days\n")
        self.fill("Q-035", "- [ ] Other (write below)\n", "- [ ] Other (write below)\nmy own words\n")
        _, out = self.ba("answers", "read", FEATURE)
        self.assertRegex(out, r"Q-034: other \| notes: 3 working days")
        self.assertRegex(out, r"Q-035: — \| notes: my own words")
        self.assertNotIn("skipped", out)

    def test_new_source_number_skips_ids_registered_without_a_file(self):
        self.edit("01-intake.md", "## Actors", "| SRC-90 | chat | 2026-11-06 | Linh | primary |\n\n## Actors")
        self.ba("answers", "new", FEATURE, "--ids", "Q-034")
        self.fill("Q-034", "- [ ] (a)", "- [x] (a)")
        _, out = self.ba("answers", "read", FEATURE)
        self.assertIn("as SRC-91", out)

    def test_new_form_notes_questions_already_out(self):
        self.ba("answers", "new", FEATURE, "--ids", "Q-034,Q-035")
        _, out = self.ba("answers", "new", FEATURE, "--ids", "Q-035,Q-036")
        self.assertIn("note: already out in round-01.md (not read yet): Q-035", out)
        self.assertTrue((self.feature / "answers" / "round-02.md").exists())

    def test_keep_leaves_form(self):
        self.ba("answers", "new", FEATURE, "--ids", "Q-034")
        self.ba("answers", "read", FEATURE, "--keep")
        self.assertTrue((self.feature / "answers" / "round-01.md").exists())

    def test_default_takes_open_questions_for_one_person(self):
        code, out = self.ba("answers", "new", FEATURE, "--who", "Linh")
        self.assertEqual(code, 0, out)
        text = (self.feature / "answers" / "round-01.md").read_text(encoding="utf-8")
        self.assertGreater(text.count("### Q-"), 0)
        asks = re.findall(r"· ask: (.*)", text)
        self.assertTrue(asks and all("Linh" in a for a in asks), asks)


    def test_chat_round_prints_everything_and_writes_nothing(self):
        code, out = self.ba("answers", "new", FEATURE, "--chat")
        self.assertEqual(code, 0, out)
        self.assertFalse((self.feature / "answers").exists())
        self.assertIn("in the order to ask them", out)
        self.assertIn("(for Linh)", out)
        self.assertRegex(out, r"\n1\. \*\*Q-\d{3}\*\* \[Blocking\]")  # priority decides the order, not the person
        self.assertIn("**Q-057** [Blocking]", out)
        self.assertIn("(a) ★", out)
        self.assertNotIn("Q-038", out)  # Nice to know is parked
        self.assertIn("5 per message", out)
        self.assertRegex(out, r"\n1\. \*\*Q-\d{3}\*\*")
        _, everything = self.ba("answers", "new", FEATURE, "--chat", "--all")
        self.assertIn("Q-038", everything)

    def test_chat_round_uses_questions_per_message(self):
        self.edit("_status.md", "| Elicitation round | 2 |", "| Elicitation round | 2 |\n| Questions per message | 3 |")
        _, out = self.ba("answers", "new", FEATURE, "--chat")
        self.assertIn("3 per message", out)
        self.ba("turn", FEATURE)  # the snapshot rewrite must not touch the preference row
        status = (self.feature / "_status.md").read_text(encoding="utf-8")
        self.assertIn("| Questions per message | 3 |", status)
        self.assertIn("PASS  status", self.check("status"))


    def test_read_files_filled_forms_and_leaves_blank_ones(self):
        self.ba("answers", "new", FEATURE, "--ids", "Q-034")
        self.ba("answers", "new", FEATURE, "--ids", "Q-035")
        first = self.feature / "answers" / "round-01.md"
        first.write_text(first.read_text(encoding="utf-8").replace("- [ ] (a)", "- [x] (a)", 1), encoding="utf-8")
        code, out = self.ba("answers", "read", FEATURE)
        self.assertEqual(code, 0, out)
        self.assertIn("Q-034: (a)", out)
        self.assertIn("round-02.md: no answers yet", out)
        self.assertFalse(first.exists())
        self.assertTrue((self.feature / "answers" / "round-02.md").exists())

    def test_split_options(self):
        import ba
        self.assertEqual(ba.split_options("(a) Notify approver(s) ★ (b) No notice"),
                         [("a", "Notify approver(s)", True), ("b", "No notice", False)])
        self.assertEqual(ba.split_options("Yes ★"), [("a", "Yes", True)])
        self.assertEqual(ba.split_options("—"), [])


class ArchiveTests(WorkflowCase):
    def test_archive_keeps_register_complete(self):
        main = self.feature / "02-questions.md"
        size = main.stat().st_size
        code, out = self.ba("questions", "archive", FEATURE)
        self.assertEqual(code, 0, out)
        self.assertLess(main.stat().st_size, size)
        closed = (self.feature / "02-closed.md").read_text(encoding="utf-8")
        self.assertIn("| Q-001 |", closed)
        self.assertNotIn("| Q-001 |", main.read_text(encoding="utf-8"))
        for name in ("register", "ids", "status"):
            self.assertNotIn("FAIL", self.check(name), name)

    def test_archive_twice_changes_nothing(self):
        self.ba("questions", "archive", FEATURE)
        first = (self.feature / "02-questions.md").read_text(encoding="utf-8")
        self.ba("questions", "archive", FEATURE)
        self.assertEqual((self.feature / "02-questions.md").read_text(encoding="utf-8"), first)


class GovernanceTests(WorkflowCase):
    def test_missing_section_warns(self):
        self.assertIn("WARN  governance: no Governance section", self.check("governance"))

    def test_unnamed_owners_fail_once_scope_exists(self):
        self.add_governance(bo="—", po="<who>")
        line = self.check("governance")
        self.assertIn("FAIL", line)
        self.assertIn("business owner", line)
        self.assertIn("Product Owner not named", line)

    def test_named_owners_pass_except_owner_column(self):
        self.add_governance()
        line = self.check("governance")
        self.assertIn("WARN", line)
        self.assertIn("no Owner column", line)
        self.assertNotIn("not named", line)

    def test_named_area_without_owner_fails_but_placeholder_is_ignored(self):
        self.add_governance()
        self.edit("_status.md", "| Area owner: payroll | STK-02 Marco Rossi |", "| Area owner: Culture | |")
        line = self.check("governance")
        self.assertIn("FAIL", line)
        self.assertIn("areas without an owner: Culture", line)
        self.edit("_status.md", "| Area owner: Culture | |", "| Area owner: <area> | |")
        self.assertNotIn("areas without an owner", self.check("governance"))

    def test_goal_with_blank_measure_fails(self):
        self.add_governance()
        self.edit("03-scope.md", "| 19 days (SRC-01) |", "| |")
        line = self.check("governance")
        self.assertIn("FAIL", line)
        self.assertIn("G-01 Baseline", line)

    def test_goal_measure_may_be_unknown_with_plan_or_waived(self):
        self.add_governance()
        self.edit("03-scope.md", "| 19 days (SRC-01) |", "| unknown — measured by 2027-01-31 |")
        self.edit("03-scope.md", "| ≤ 2% (D-005) |", "| waived (D-005) |")
        line = self.check("governance")
        self.assertNotIn("not measurable", line)
        self.assertNotIn("G-01", line.split("no plan to measure")[-1])

    def test_unknown_without_plan_warns(self):
        self.add_governance()
        self.edit("03-scope.md", "| 19 days (SRC-01) |", "| Unknown |")
        self.assertIn("no plan to measure them: G-01", self.check("governance"))

    def test_foundation_without_status_warns(self):
        self.edit("01-intake.md", "## Actors", "## Foundations\n| Foundation | What the sources say | Status |\n"
                                               "|------------|----------------------|--------|\n"
                                               "| Success metrics | | |\n\n## Actors")
        self.assertIn("foundations neither known nor asked: Success metrics", self.check("governance"))

    def test_small_change_lets_po_stand_in_for_business_owner(self):
        self.add_governance(bo="")
        self.assertIn("business owner", self.check("governance"))
        self.edit("_status.md", "| `workflow-approval` |", "| `small-change` |")
        self.assertNotIn("business owner", self.check("governance"))
        self.edit("_status.md", "| Product Owner | STK-01 Linh Tran |", "| Product Owner | — |")
        self.assertIn("Product Owner not named", self.check("governance"))

    def test_role_conflict_warns_until_accepted(self):
        self.add_governance(po="pilot-BA")
        self.assertIn("role conflict", self.check("governance"))
        self.edit("_status.md", "| Role conflicts | none |", "| Role conflicts | BA is PO, CFO reviews (D-045) |")
        self.assertNotIn("role conflict", self.check("governance"))

    def test_scope_item_without_goal_or_mandate_fails(self):
        self.add_governance()
        self.edit("03-scope.md", "| G-01, G-02 | web-app | MVP |", "| — | web-app | MVP |")
        self.assertIn("serving no goal", self.check("governance"))

    def test_mandated_scope_item_passes(self):
        self.add_governance()
        self.edit("03-scope.md", "| G-01, G-02 | web-app | MVP |", "| mandatory: tax law (SRC-02) | web-app | MVP |")
        self.assertNotIn("serving no goal", self.check("governance"))

    def test_owner_column_enforced(self):
        self.add_governance()
        self.edit("03-scope.md", "| ID | Capability | Goal | Profile | Slice |\n|----|-----------|------|---------|-------|",
                  "| ID | Capability | Goal | Profile | Slice | Owner |\n|----|-----------|------|---------|-------|-------|")
        line = self.check("governance")
        self.assertIn("FAIL", line)
        self.assertIn("without an owner", line)


class AuditCheckTests(WorkflowCase):
    def test_unlogged_decision_warns(self):
        self.ba("turn", FEATURE)
        self.edit("_status.md", "| D-002 | Claim deadline", "| D-098 | Unlogged | x | 2026-10-26 | SRC-05 | — | — |\n"
                                                         "| D-002 | Claim deadline")
        line = self.check("audit")
        self.assertIn("D-098", line)
        self.assertIn("file changes not recorded", line)

    def test_clean_after_turn(self):
        self.ba("turn", FEATURE)
        self.assertNotIn("D-0", self.check("audit").split("file changes")[0].replace("every decision", ""))


class PriorityTests(WorkflowCase):
    def test_decision_critical_is_canonical_and_reported(self):
        self.edit("02-questions.md", "| Important | Linh | Open | A-03", "| Decision-critical | Linh | Open | A-03")
        line = self.check("open")
        self.assertIn("decision-critical open: 1 (Q-034)", line)
        self.assertIn("WARN", line)


if __name__ == "__main__":
    unittest.main()

"""Tests for the fixes from the first independent review (pre-release round 1) (human gates that can't be bypassed,
the gates check, RTM rules, handoff templates, honest audit fields, KPIs, minor fixes) and the new /ba-docs and
/ba-discover support. Run from the package root:  python -m unittest discover -s tests -v
"""

import json
import re
import shutil
import sys
import unicodedata
import unittest
import zipfile
from pathlib import Path
from unittest import mock
from xml.dom import minidom

sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_ba import FEATURE, PACKAGE  # noqa: E402
from test_gates import QA_PACK, GatesCase  # noqa: E402
from test_install import InstallCase  # noqa: E402

sys.path.insert(0, str(PACKAGE))
import install  # noqa: E402

GOVERNANCE = """## Governance
| Role | Who (STK-) | Decides on | Source |
|------|-----------|------------|--------|
| Business owner (final say in conflicts) | Pierre Laurent | Priorities | SRC-05 |
| Product Owner | Linh Tran | Scope, acceptance | SRC-05 |
| Gate approvers | Linh Tran; pilot-BA | Scope, Review, Handoff | SRC-05 |
| Role conflicts | {conflict} | | |

"""


class V11Case(GatesCase):
    def set_gate(self, number, result):
        path = self.feature / "_status.md"
        lines = path.read_text(encoding="utf-8").split("\n")
        for i, line in enumerate(lines):
            if re.match(r"^\|\s*" + str(number) + r" ", line):
                cells = line.strip().strip("|").split("|")
                cells[2] = f" {result} "
                lines[i] = "|" + "|".join(cells) + "|"
                break
        path.write_text("\n".join(lines), encoding="utf-8")

    def add_governance(self, conflict="none"):
        path = self.feature / "_status.md"
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace("## Decision log", GOVERNANCE.format(conflict=conflict) + "## Decision log", 1),
                        encoding="utf-8")

    def add_decision(self, ident, text, who, date=None):
        import datetime
        path = self.feature / "_status.md"
        lines = path.read_text(encoding="utf-8").split("\n")
        head = next(i for i, l in enumerate(lines) if l.startswith("## Decision log"))
        at = next(i for i in range(head + 3, len(lines)) if not lines[i].startswith("|"))
        lines.insert(at, f"| {ident} | {text} | {who} | {date or datetime.date.today().isoformat()} | test | x | — |")
        path.write_text("\n".join(lines), encoding="utf-8")

    def check_line(self, name):
        _, out = self.ba("check", FEATURE, "--only", name)
        return next(l for l in out.splitlines() if f"  {name}:" in l)

    def qa_pack(self, text=QA_PACK):
        (self.feature / "handoff").mkdir(exist_ok=True)
        (self.feature / "handoff" / "qa-pack.md").write_text(text, encoding="utf-8")


class AuthorityV11(V11Case):
    def test_miscased_or_unknown_type_is_refused(self):
        for kind in ("Gate.Passed", "gate.pass", "approval"):
            self.assertEqual(self.event(type=kind, stage="8 Review")[0], 1, kind)

    def test_unnumbered_stage_is_refused(self):
        for stage in ("Review", "Stage 8 Review", ""):
            self.assertEqual(self.event(type="gate.passed", stage=stage)[0], 1, stage)

    def test_evidence_must_exist(self):
        self.assertEqual(self.event(type="gate.passed", stage="3 Scope", actor="Linh Tran", refs=["D-999"])[0], 1)

    def test_cited_decision_must_be_the_actors(self):
        # D-001 was decided by pilot-BA, not by the PO
        self.assertEqual(self.event(type="gate.passed", stage="3 Scope", actor="Linh Tran", refs=["D-001"])[0], 1)
        self.assertEqual(self.event(type="gate.passed", stage="3 Scope", actor="Linh Tran", refs=["D-043"])[0], 0)

    def test_actor_must_be_an_approver(self):
        self.assertEqual(self.event(type="gate.passed", stage="3 Scope", actor="Jessie", refs=["SRC-05"])[0], 1)

    def test_ai_names_are_refused(self):
        for name in ("ChatGPT", "The assistant", "BA Copilot", "claude-opus-5-5", "AI agent"):
            self.assertEqual(self.event(type="approval.recorded", actor=name, refs=["SRC-05"])[0], 1, name)

    def test_ba_as_approver_needs_a_recorded_role_conflict(self):
        self.add_governance()
        self.add_decision("D-099", "BA approves the scope", "pilot-BA")
        self.assertEqual(self.event(type="gate.passed", stage="3 Scope", actor="pilot-BA", refs=["D-099"])[0], 1)
        path = self.feature / "_status.md"
        path.write_text(path.read_text(encoding="utf-8").replace("| Role conflicts | none |",
                                                                  "| Role conflicts | BA approves gate 3, accepted D-043 |"),
                        encoding="utf-8")
        self.assertEqual(self.event(type="gate.passed", stage="3 Scope", actor="pilot-BA", refs=["D-099"])[0], 0)

    def test_skipping_a_human_gate_needs_the_approver(self):
        self.assertEqual(self.event(type="stage.skipped", stage="8 Review", severity="High")[0], 1)
        self.assertEqual(self.event(type="stage.skipped", stage="8 Review", actor="Linh Tran", refs=["D-043"])[0], 0)
        self.assertEqual(self.event(type="stage.skipped", stage="4 Model")[0], 0, "machine gates: the BA decides")

    def test_stage_events_need_a_feature(self):
        code, _ = self.ba("audit", "event", "--type", "gate.passed", "--stage", "9 Handoff")
        self.assertEqual(code, 1)

    def test_reporter_and_via_always_recorded(self):
        with mock.patch.dict("os.environ", {"BA_ACTOR": "Jessie", "BA_VIA": "assistant:test-tool"}):
            self.assertEqual(self.event(type="note", summary="x")[0], 0)
        last = [e for e in self.entries() if e["type"] == "note"][-1]
        self.assertEqual(last["actor"], "Jessie")
        self.assertEqual(last["reported_by"], "Jessie")
        self.assertEqual(last["via"], "assistant:test-tool")

    def test_controlled_mode_rejects_placeholder_model(self):
        self.set_pref("Mode", "controlled")
        with mock.patch.dict("os.environ", {"BA_MODEL": ""}):
            self.assertEqual(self.event(type="note", model="x")[0], 1)
            self.assertEqual(self.event(type="note", model="claude-opus-5-5")[0], 0)


class GatesCheck(V11Case):
    def test_example_passes(self):
        self.assertIn("PASS  gates", self.check_line("gates"))

    def test_hand_edited_gate_fails(self):
        self.set_gate(8, "Passed")
        line = self.check_line("gates")
        self.assertIn("FAIL", line)
        self.assertIn("8 Review", line)

    def test_mode_change_must_be_logged(self):
        self.set_pref("Mode", "quick")
        self.assertIn("FAIL", self.check_line("gates"))
        self.assertEqual(self.event(type="settings.changed", summary="Mode: quick", actor="Linh Tran", refs=["D-043"])[0], 0)
        self.assertIn("PASS  gates", self.check_line("gates"))

    def write_review(self, verdict, rows):
        (self.feature / "08-review.md").write_text(
            f"# 08 · Review\n\n**Score:** 82 / 100 · **Verdict:** {verdict}\n\n## Defects (proven)\n"
            "| # | Severity | Problem | Status |\n|---|---|---|---|\n" + "".join(f"| {i} | {s} | x | {st} |\n" for i, s, st in rows),
            encoding="utf-8")

    def test_handoff_with_open_major_fails(self):
        self.assertEqual(self.event(type="gate.passed", stage="9 Handoff", actor="Linh Tran", refs=["D-043"])[0], 0)
        self.set_gate(9, "Passed")
        self.write_review("Conditional", [(1, "Major", "Open"), (2, "Minor", "Open")])
        self.assertIn("FAIL", self.check_line("gates"))
        self.write_review("Conditional", [(1, "Major", "Deferred (D-043)"), (2, "Minor", "Open")])
        self.assertIn("PASS  gates", self.check_line("gates"))

    def test_pass_verdict_with_open_critical_fails(self):
        self.write_review("Pass", [(1, "Critical", "Open")])
        self.assertIn("FAIL", self.check_line("gates"))

    def test_empty_human_gates_list_is_respected_and_flagged(self):
        (self.tmp / ".ba").mkdir()
        (self.tmp / ".ba" / "config.json").write_text(json.dumps({"human_gates": {"standard": []}}), encoding="utf-8")
        self.assertEqual(self.event(type="gate.passed", stage="3 Scope")[0], 0)
        self.assertIn("WARN", self.check_line("gates"))


class HandoffTemplates(V11Case):
    def test_packs_from_templates_pass_with_a_skipped_stage(self):
        self.qa_pack()
        for template in (PACKAGE / "core" / "templates" / "handoff").glob("*.md"):
            if template.name != "qa-pack.md":
                shutil.copy(template, self.feature / "handoff" / template.name)
        for extra in ("supervisor-guide.md", "ops-runbook.md"):
            (self.feature / "handoff" / extra).write_text("# x\n\n## Skipped stages & known gaps\nUX skipped.\n",
                                                          encoding="utf-8")
        qa = self.feature / "handoff" / "qa-pack.md"
        qa.write_text("## Skipped stages & known gaps\nUX skipped.\n\n" + QA_PACK, encoding="utf-8")
        self.set_gate(6, "Skipped (O-01)")
        status = self.feature / "_status.md"
        status.write_text(status.read_text(encoding="utf-8").replace(
            "- [ ] `handoff/ops-runbook.md` (integration)",
            "- [ ] `handoff/ops-runbook.md` (integration)\n- [ ] <profile extras, e.g. `handoff/foo.md`>"), encoding="utf-8")
        self.assertIn("PASS  handoff", self.check_line("handoff"))


class RtmV11(V11Case):
    def test_ai_recorder_and_pointless_evidence_fail(self):
        self.qa_pack()
        self.ba("rtm", FEATURE)
        self.rtm_set("AC-001.1", **{"Test result": "Pass", "UAT result": "Pass", "Evidence": "x", "Recorded by": "QA An"})
        self.assertIn("points nowhere", self.check_line("rtm"))
        self.rtm_set("AC-001.1", **{"Evidence": "https://ci/run/42", "Recorded by": "Claude"})
        self.assertIn("recorded by the assistant", self.check_line("rtm"))
        self.ba("rtm", FEATURE)
        self.assertNotEqual(self.rtm_row("AC-001.1")[0]["Coverage"], "Covered")

    def test_one_row_per_test(self):
        self.qa_pack(QA_PACK + "| TS-003 | AC-001.1 | negative | - | - | - | High |\n")
        self.ba("rtm", FEATURE)
        self.assertEqual(sorted(r["Test"] for r in self.rtm_row("AC-001.1")), ["TS-001", "TS-003"])

    def test_combined_row_from_1_0_is_split(self):
        self.qa_pack(QA_PACK + "| TS-003 | AC-001.1 | negative | - | - | - | High |\n")
        self.ba("rtm", FEATURE)
        path = self.feature / "rtm.md"
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"^\| AC-001\.1 \|.*\| TS-003 \|.*\n", "", text, flags=re.M)
        text = text.replace("| AC-001.1 | US-001 | G-01, G-02 | BR-001, BR-002, BR-003, BR-004, BR-005, BR-006, BR-012 | TS-001 |",
                            "| AC-001.1 | US-001 | G-01, G-02 | BR-001, BR-002, BR-003, BR-004, BR-005, BR-006, BR-012 | TS-001, TS-003 |")
        path.write_text(text, encoding="utf-8")
        _, out = self.ba("rtm", FEATURE)
        self.assertIn("1 combined rows split", out)
        self.assertEqual(sorted(r["Test"] for r in self.rtm_row("AC-001.1")), ["TS-001", "TS-003"])

    def test_removed_test_is_a_stale_link(self):
        self.qa_pack()
        self.ba("rtm", FEATURE)
        self.qa_pack(QA_PACK.replace("| TS-001 | AC-001.1 |", "| TS-001 | AC-002.1 |"))
        self.ba("rtm", FEATURE)
        rows = {r["Test"]: r["Coverage"] for r in self.rtm_row("AC-001.1")}
        self.assertEqual(rows.get("TS-001"), "Stale link")

    def test_renamed_ac_keeps_its_tests(self):
        self.qa_pack()
        self.ba("rtm", FEATURE)
        stories = self.feature / "05-stories.md"
        text = stories.read_text(encoding="utf-8").replace("# AC-001.1", "# AC-001.9", 1)
        stories.write_text(text + "\n| Renamed | ~~AC-001.1~~ → AC-001.9 (D-043) |\n", encoding="utf-8")
        _, out = self.ba("rtm", FEATURE)
        self.assertIn("carried from renamed AC", out)
        new = self.rtm_row("AC-001.9")
        self.assertEqual(new[0]["Test"], "TS-001")
        self.assertIn("renamed from AC-001.1", new[0]["Notes"])
        self.assertEqual(self.rtm_row("AC-001.1")[0]["Coverage"], "Withdrawn")

    def test_result_log_keeps_history_and_logs_the_tester(self):
        self.qa_pack()
        self.ba("rtm", FEATURE)
        self.rtm_set("AC-001.1", **{"Test result": "Fail", "Evidence": "https://ci/run/41", "Recorded by": "QA An"})
        self.ba("rtm", FEATURE)
        self.rtm_set("AC-001.1", **{"Test result": "Pass", "Evidence": "https://ci/run/42"})
        _, out = self.ba("rtm", FEATURE)
        self.assertIn("1 results logged", out)
        log = (self.feature / "rtm.md").read_text(encoding="utf-8").split("## Result log", 1)[1]
        self.assertIn("run/41", log)
        self.assertIn("run/42", log)
        recorded = [e for e in self.entries() if e["type"] == "result.recorded"]
        self.assertEqual(len(recorded), 2)
        self.assertEqual(recorded[-1]["actor"], "QA An")
        _, verify = self.ba("audit", "verify", FEATURE)
        self.assertNotIn("FAIL", verify)

    def test_pass_rate_counts_blocked_not_na(self):
        self.qa_pack()
        self.ba("rtm", FEATURE)
        common = {"Evidence": "https://ci/1", "Recorded by": "QA An"}
        self.rtm_set("AC-001.1", **dict(common, **{"Test result": "Pass"}))
        self.rtm_set("AC-001.2", **dict(common, **{"Test result": "Blocked"}))
        self.rtm_set("AC-001.3", **dict(common, **{"Test result": "N/A"}))
        self.ba("rtm", FEATURE)
        _, out = self.ba("kpi", FEATURE, "--json")
        self.assertTrue(json.loads(out)["Test pass rate: Pass / (Pass + Fail + Blocked)"].startswith("50% (1/2)"))


class MinorFixes(V11Case):
    def test_xlsx_with_quotes_in_a_heading_is_valid(self):
        status = self.feature / "_status.md"
        status.write_text(status.read_text(encoding="utf-8").replace("## Risks", '## Risks "top" & <others>', 1),
                          encoding="utf-8")
        out_path = self.tmp / "x.xlsx"
        self.assertEqual(self.ba("export", FEATURE, "--out", str(out_path))[0], 0)
        with zipfile.ZipFile(out_path) as z:
            for name in z.namelist():
                if name.endswith(".xml") or name.endswith(".rels"):
                    minidom.parseString(z.read(name))

    def test_dashboard_creates_its_folder(self):
        target = self.tmp / "dash board" / "bảng điều khiển.html"
        self.assertEqual(self.ba("status", FEATURE, "--html", str(target))[0], 0)
        self.assertTrue(target.is_file())

    def test_vietnamese_ambiguity_nfd_and_exceptions(self):
        spec = self.feature / "07-spec.md"
        nfd = unicodedata.normalize("NFD", "Hệ thống phản hồi nhanh.")
        spec.write_text(spec.read_text(encoding="utf-8") + f"\n{nfd}\nGửi OTP tới một số điện thoại. Trạng thái trở nên khoá.\n",
                        encoding="utf-8")
        line = self.check_line("ambiguity")
        self.assertIn("'nhanh'", line)
        self.assertNotIn("'một số'", line)
        self.assertNotIn("'nên'", line)

    def test_gate_wording_migration(self):
        text = "## Gates\n| Stage | Gate | Result | Date | Notes |\n|---|---|---|---|---|\n| 8 Review | Score ≥ 85, zero Critical | Passed | | |\n"
        new = install.mig_gate_wording(text)
        self.assertIn("| 8 Review | 👤 No Critical; Majors owned; score ≥ 80; team walkthrough (Dev + QA) | Passed |", new)
        self.assertEqual(install.mig_gate_wording(new), new)


class DocsV11(V11Case):
    def write_doc(self, name, status, body=""):
        (self.feature / "docs").mkdir(exist_ok=True)
        (self.feature / "docs" / name).write_text(f"# Doc\n\n| Item | Detail |\n|---|---|\n| Review status | {status} |\n\n{body}",
                                                 encoding="utf-8")

    def test_unchosen_status_and_unrecorded_approval_fail(self):
        self.write_doc("brd.md", "Draft · In review · Approved")
        self.assertIn("FAIL", self.check_line("docs"))
        self.write_doc("brd.md", "Approved")
        self.assertIn("no approval of brd.md", self.check_line("docs"))
        self.assertEqual(self.event(type="approval.recorded", actor="Linh Tran", refs=["D-043"],
                                    summary="brd.md v1.0 approved")[0], 0)
        self.assertIn("PASS  docs", self.check_line("docs"))

    def test_user_guide_only_tested_behaviour(self):
        self.qa_pack()
        self.ba("rtm", FEATURE)
        self.write_doc("user-guide.md", "In review", "*For the support team:* US-001, AC-001.1\n")
        self.assertIn("not yet Covered", self.check_line("docs"))

    def test_documents_never_define_ids(self):
        self.write_doc("brd.md", "Draft", "| ID | Rule | Source |\n|---|---|---|\n| BR-999 | x | SRC-01 |\n")
        self.assertIn("BR-999", self.check_line("ids"))


class DiscoverV11(V11Case):
    def test_scaffold_status_and_context(self):
        code, out = self.ba("discover", "Core Banking")
        self.assertEqual(code, 0, out)
        folder = self.tmp / "knowledge" / "core-banking"
        for page in ("README.md", "01-landscape.md", "03-rules.md", "06-open-questions.md", "sources/README.md"):
            self.assertTrue((folder / page).is_file(), page)
        ws = [json.loads(l) for l in (self.tmp / "audit" / "workspace.jsonl").read_text(encoding="utf-8").splitlines()]
        self.assertTrue(any(e["type"] == "knowledge.updated" for e in ws))
        self.assertTrue(any(e.get("file", "").startswith("knowledge/core-banking/") for e in ws))
        page = folder / "03-rules.md"
        page.write_text(page.read_text(encoding="utf-8").replace("| Status | Draft · Verified |", "| Status | Verified |")
                        .replace("| Verified on | YYYY-MM-DD |", "| Verified on | 2020-01-01 |")
                        .replace("| Verified by | <system or area owner> |", "| Verified by | Marco |"), encoding="utf-8")
        _, out = self.ba("discover", "Core Banking")
        self.assertIn("STALE", out)
        _, out = self.ba("context", FEATURE, "ba-intake")
        self.assertIn("knowledge/core-banking/: 1/6 pages verified, stale: 03-rules.md", out)
        _, sync = self.ba("audit", "sync", "--workspace")
        self.assertIn("1 changed", sync)
        _, verify = self.ba("audit", "verify", "--all")
        self.assertNotIn("FAIL", verify)


class InstallModel(InstallCase):
    def test_model_is_recorded_in_config(self):
        code, out = self.inst("init", "--model", "claude-opus-5-5")
        self.assertEqual(code, 0, out)
        config = json.loads((self.tmp / ".ba" / "config.json").read_text(encoding="utf-8"))
        self.assertEqual(config["model"], "claude-opus-5-5")


if __name__ == "__main__":
    unittest.main()

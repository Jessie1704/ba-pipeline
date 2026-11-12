#!/usr/bin/env python3
"""BA Pipeline tooling: quality checks, a live traceability matrix and a tamper-evident audit trail.

Usage (from the project root; Python 3.9+, standard library only):
  python .ba/tools/ba.py rtm <feature>                         build/refresh rtm.md (live traceability matrix)
  python .ba/tools/ba.py kpi <feature> [--json]                release KPIs from the RTM and the audit log
  python .ba/tools/ba.py status <feature> [--html FILE] [--lang en|vi]   plain-language status / dashboard
  python .ba/tools/ba.py export <feature> [--out FILE.xlsx]   registers, decisions, AC, spec, RTM to Excel
  python .ba/tools/ba.py check <feature> [--only status,ids,...]
  python .ba/tools/ba.py audit event [--feature F] --type T [--stage S] [--summary ...] [--reason ...]
                                     [--decision ...] [--severity Critical|High|Medium|Low] [--refs "D-01,O-02"] [--actor NAME]
  python .ba/tools/ba.py audit event --json-file events.json [--feature F]
  python .ba/tools/ba.py audit sync <feature> [--dry-run]       record file changes by hash (tools without hooks)
  python .ba/tools/ba.py audit sync --workspace [--dry-run]     same for .ba/local and .ba/config.json
  python .ba/tools/ba.py audit verify [<feature> | --all]       check the hash chain
  python .ba/tools/ba.py audit hook                             post-edit hook: reads the tool's JSON on stdin
  python .ba/tools/ba.py turn <feature> [--events FILE|-] [--gate] [--stage S]   end of every turn, one call
  python .ba/tools/ba.py context <feature> <stage>             only what a stage needs to read
  python .ba/tools/ba.py answers new <feature> [--ids ...] [--who ...] [--all] [--chat]   answer form for the BA
  python .ba/tools/ba.py answers read <feature> [file] [--keep]          read a filled form, file it as a source
  python .ba/tools/ba.py questions archive <feature>            move closed questions to 02-closed.md
  python .ba/tools/ba.py version

Exit codes: 0 ok, 1 a check FAILed / the chain is broken / input was invalid.

Audit log format (compatible with the earlier PowerShell scripts): one JSON object per line; "prev" is the
previous line's hash; "hash" = SHA-256(prev + body), where body is the line without its trailing hash field.
"""

import argparse
import datetime
import hashlib
import io
import json
import os
import re
import sys
import time
import unicodedata
from contextlib import redirect_stdout
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
PACKAGE_DIR = TOOLS_DIR.parent

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def write_lf(path, text):
    """Write UTF-8 text with LF line endings on every OS (Path.write_text only takes newline= from Python 3.10)."""
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


# --------------------------------------------------------------------------- project discovery

def find_root(explicit=None):
    """Project root: --root, $BA_ROOT, $CLAUDE_PROJECT_DIR, else the nearest folder up from cwd with .ba/ or requirements/."""
    for candidate in (explicit, os.environ.get("BA_ROOT"), os.environ.get("CLAUDE_PROJECT_DIR")):
        if candidate:
            return Path(candidate).resolve()
    here = Path.cwd().resolve()
    for folder in (here, *here.parents):
        if (folder / ".ba").is_dir() or (folder / "requirements").is_dir():
            return folder
    return here


def load_config(root):
    config = {"requirements_dir": "requirements"}
    path = root / ".ba" / "config.json"
    if path.is_file():
        config.update(json.loads(path.read_text(encoding="utf-8-sig")))
    return config


def requirements_dir(root):
    return root / load_config(root)["requirements_dir"]


def actor_default():
    return os.environ.get("BA_ACTOR") or os.environ.get("USERNAME") or os.environ.get("USER") or "unknown"


def session_default():
    return (os.environ.get("BA_SESSION") or os.environ.get("CLAUDE_CODE_SESSION_ID")
            or os.environ.get("CLAUDE_SESSION_ID") or None)


# Environment variables an AI tool sets in the shell it runs commands in (best effort).
ASSISTANT_ENV = (("CLAUDECODE", "claude-code"), ("CLAUDE_CODE_ENTRYPOINT", "claude-code"),
                 ("CLAUDE_CODE_SESSION_ID", "claude-code"), ("CURSOR_TRACE_ID", "cursor"), ("CURSOR_AGENT", "cursor"),
                 ("GEMINI_CLI", "gemini-cli"), ("CODEX_SANDBOX", "codex"), ("CODEX_HOME", "codex"),
                 ("KIRO_SESSION", "kiro"), ("VSCODE_COPILOT_AGENT", "copilot"), ("AI_AGENT", "ai-agent"))


def assistant_tool():
    """The AI tool whose shell runs this command, or None. Kiro's terminals set TERM_PROGRAM=kiro - for its agent and
    for a person typing alike, so `ba approve` must run in an operating-system terminal outside Kiro."""
    found = next((name for var, name in ASSISTANT_ENV if os.environ.get(var)), None)
    if found:
        return found
    term = os.environ.get("TERM_PROGRAM", "").lower()
    if term == "kiro":
        return "kiro"
    if term == "vscode" and any(os.environ.get(v) for v in ("VSCODE_COPILOT_AGENT", "COPILOT_AGENT", "GITHUB_COPILOT_AGENT")):
        return "copilot"
    return None


def via_default():
    """'assistant:<tool>' when an AI tool's shell runs the command. BA_VIA may name a tool the list doesn't know,
    but can't turn an assistant's command into a person's: inside an AI tool, BA_VIA=cli is ignored."""
    tool, override = assistant_tool(), os.environ.get("BA_VIA", "")
    if override.startswith("assistant:"):
        return override
    if tool:
        return f"assistant:{tool}"
    return override or "cli"


# --------------------------------------------------------------------------- audit log

LINE_RX = re.compile(r'^(?P<body>.*),"hash":"(?P<hash>[0-9a-f]{64})"\}$')


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def audit_log_path(root, feature):
    if feature:
        return requirements_dir(root) / feature / "_audit" / "events.jsonl"
    return root / "audit" / "workspace.jsonl"


class FileLock:
    """Cross-platform lock: an exclusive-create lock file next to the log (stale after 30 s)."""

    def __init__(self, target):
        self.path = Path(str(target) + ".lock")

    def __enter__(self):
        for _ in range(200):
            try:
                fd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(os.getpid()).encode())
                os.close(fd)
                return self
            except FileExistsError:
                try:
                    if time.time() - self.path.stat().st_mtime > 30:
                        self.path.unlink()
                        continue
                except FileNotFoundError:
                    continue
                time.sleep(0.05)
        raise RuntimeError(f"could not lock {self.path}")

    def __exit__(self, *exc):
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass


def read_log(path):
    if not path.is_file():
        return []
    with open(path, encoding="utf-8") as handle:
        return [line.rstrip("\r\n") for line in handle if line.strip()]


def append_events(path, events):
    """Append events (list of dicts, in order) under one lock; returns the written entries."""
    path.parent.mkdir(parents=True, exist_ok=True)
    written = []
    with FileLock(path):
        lines = read_log(path)
        prev, seq = "GENESIS", 0
        if lines:
            last = json.loads(lines[-1])
            prev, seq = last["hash"], int(last["seq"])
        with open(path, "a", encoding="utf-8", newline="\n") as handle:
            for fields in events:
                seq += 1
                now = datetime.datetime.now(datetime.timezone.utc)
                entry = {"seq": seq, "ts": now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond // 1000:03d}Z"}
                for key, value in fields.items():
                    if value is not None and value != "" and value != []:
                        entry[key] = value
                entry["prev"] = prev
                body = json.dumps(entry, ensure_ascii=False, separators=(",", ":"))
                digest = sha256_text(prev + body)
                handle.write(body[:-1] + ',"hash":"' + digest + '"}\n')
                prev = digest
                written.append(entry)
    return written


def verify_log(path):
    """Returns (ok, entries, problem)."""
    if not path.is_file():
        return True, 0, "no log yet"
    prev, count = "GENESIS", 0
    for number, line in enumerate(read_log(path), start=1):
        count = number
        match = LINE_RX.match(line)
        if not match:
            return False, count, f"line {number} is malformed"
        body = match.group("body") + "}"
        entry = json.loads(body)
        if entry.get("prev") != prev:
            return False, count, f"line {number} (seq {entry.get('seq')}): chain broken - a line before it was removed, reordered or edited"
        if sha256_text(prev + body) != match.group("hash"):
            return False, count, f"line {number} (seq {entry.get('seq')}): content was modified"
        prev = match.group("hash")
    return True, count, ""


# --------------------------------------------------------------------------- audit commands

SEVERITIES = ("Critical", "High", "Medium", "Low")
EVENT_KEYS = ("feature", "type", "stage", "summary", "reason", "decision", "severity", "refs", "actor", "model")

# Gates a person must close: the assistant may log them only on behalf of a named approver, with evidence.
# Stage numbers; MANUAL §8. Overridable in .ba/config.json -> "human_gates": {"standard": [3, 8, ...], ...}.
HUMAN_GATES = {"quick": [9, 11], "standard": [3, 8, 9, 10, 11, 12],
               "controlled": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]}
AI_NAMES = re.compile(r"(?i)(?<![\w-])(ai|a\.i\.|assistant|the assistant|ai assistant|agent|ai agent|bot|chatbot|llm|"
                      r"model|claude|anthropic|copilot|github copilot|gpt|chatgpt|openai|gemini|bard|codex|kiro|"
                      r"cursor|windsurf|cline|aider|jules|amp|llama|mistral|deepseek|qwen|grok|ba copilot|"
                      r"ba guardian(?: angel)?|ba pipeline)(?![\w-])")
EVIDENCE = re.compile(r"\b(SRC|D)-\d{2,3}\b")
# Every workflow event type the log accepts (reference/audit.md). file.* are written by sync and the hook only.
EVENT_TYPES = {
    "feature.created", "source.added", "approach.proposed", "approach.confirmed", "approach.changed",
    "override.added", "override.removed", "stage.started", "stage.skipped", "stage.deferred", "gate.passed",
    "gate.failed", "gate.reopened", "check.run", "question.raised", "question.answered", "assumption.confirmed",
    "assumption.rejected", "decision.recorded", "review.scored", "approval.recorded", "cr.logged", "cr.decided",
    "cr.applied", "handoff.generated", "profile.changed", "correction", "rtm.updated", "result.recorded",
    "uat.round", "release.completed", "docs.generated", "draft.reviewed", "knowledge.updated", "settings.changed",
    "files.bulk-edit", "ba.installed", "ba.updated", "template.migrated", "note"}
STAGE_EVENTS = ("stage.", "gate.")  # must name a feature and a numbered stage ("3 Scope")
PLACEHOLDER_MODELS = {"x", "ai", "model", "test", "none", "unknown", "n/a", "-", "llm", "tbd"}


def version_text():
    path = PACKAGE_DIR / "VERSION"
    return path.read_text(encoding="utf-8").strip() if path.is_file() else "unknown"


def preference(root, feature, name, default=""):
    """A row of _status.md → Preferences (first word, lower case), e.g. Language -> 'vi'. The Mode has its own,
    stricter reading: mode_cell() and effective_mode()."""
    if name == "Mode":
        return effective_mode(root, feature) if feature else default or "standard"
    status = requirements_dir(root) / feature / "_status.md" if feature else None
    text = status.read_text(encoding="utf-8-sig") if status and status.is_file() else ""
    m = re.search(r"^\|\s*" + re.escape(name) + r"\s*\|\s*([^|]*)\|", text, re.M)
    if not m or "·" in m.group(1):  # still the template's list of options: not chosen yet
        return default
    word = (re.match(r"[A-Za-z]+", plain(m.group(1))) or [""])[0].lower()
    return word or default


MODE_WORDS = {"quick": "quick", "nhanh": "quick", "rút gọn": "quick", "standard": "standard", "tiêu chuẩn": "standard",
              "chuẩn": "standard", "controlled": "controlled", "kiểm soát": "controlled", "kiem soat": "controlled"}
MODE_TEMPLATE = re.compile(r"^\s*quick\s*·\s*standard\s*·\s*controlled\s*$")


def read_mode(text):
    """The mode a text names (English or Vietnamese, notes allowed: 'controlled (PO, D-090)'), or None if it names
    none or several."""
    flat = unicodedata.normalize("NFC", plain(text or "")).lower()
    found = {mode for word, mode in MODE_WORDS.items() if re.search(r"(?<![\w-])" + re.escape(word) + r"(?![\w-])", flat)}
    return found.pop() if len(found) == 1 else None


def mode_cell(root, feature):
    """(mode, raw cell) of _status.md → Preferences → Mode. No row or the template's list -> 'standard' (not chosen);
    a cell that names no mode or several -> None (the gates check FAILs it)."""
    status = requirements_dir(root) / feature / "_status.md"
    text = status.read_text(encoding="utf-8-sig") if status.is_file() else ""
    m = re.search(r"^\|\s*Mode\s*\|\s*([^|]*)\|", text, re.M)
    if not m or MODE_TEMPLATE.match(plain(m.group(1))) or not plain(m.group(1)).strip():
        return "standard", m.group(1).strip() if m else ""
    return read_mode(m.group(1)), m.group(1).strip()


def mode_events(root, feature):
    """Valid mode changes, oldest first: settings.changed naming one mode, by the PO or the business owner."""
    folder = requirements_dir(root) / feature
    if not folder.is_dir():
        return []
    feat = Feature(folder)
    out = []
    for e in log_entries(root, feature):
        if e["type"] != "settings.changed" or not e.get("tool") or is_ai_name(e.get("actor")):
            continue
        m = re.search(r"(?i)\bmode\b\W*(.*)$", e.get("summary") or "")
        mode = read_mode(m.group(1)) if m else None
        if mode and is_owner(feat, e.get("actor") or ""):
            out.append((mode, e))
    return out


def effective_mode(root, feature):
    """The mode the rules use: the latest valid mode change in the log, if there is one - editing the cell alone never
    changes it - otherwise the Mode cell (standard when not chosen or unreadable)."""
    events = mode_events(root, feature)
    if events:
        return events[-1][0]
    mode, _ = mode_cell(root, feature)
    return mode or "standard"


def human_gates(root, feature):
    mode = effective_mode(root, feature)
    custom = load_config(root).get("human_gates") or {}
    if mode in custom:  # an explicit list wins, even an empty one (gates checks it against a settings.changed event)
        return set(custom[mode])
    return set(HUMAN_GATES.get(mode) or HUMAN_GATES["standard"])


def is_ai_name(name):
    return bool(AI_NAMES.search(name or ""))


# Words before a name that are not part of it (Vietnamese and English forms of address).
HONORIFICS = {"anh", "chị", "chi", "em", "ông", "ong", "bà", "ba", "cô", "co", "chú", "chu", "bác", "bac", "mr", "mrs",
              "ms", "miss", "dr", "sir", "madam"}
ROLE_ALIASES = {"po": "product owner", "product owner": "product owner", "business owner": "business owner",
                "sponsor": "business owner", "bo": "business owner"}
# Notes people add after a name: 'Lan Anh - PO', 'Lan Anh – PO', 'Lan Anh qua email', 'Lan Anh by email'.
NAME_TAIL = re.compile(r"\s+[-–—]\s+.*$|\s+(?:qua|bằng|by|via|trong|tại|lúc|in|at|on)\s+.*$", re.I)


def ascii_name(words):
    """Tokens without diacritics ('nguyễn' -> 'nguyen', 'đ' -> 'd'): a fallback for names typed without accents."""
    text = " ".join(words).replace("đ", "d")
    return tuple(unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii").split())


def person_tokens(text):
    """A name as comparable tokens: NFC, lower case, '(role)' notes, trailing notes ('- PO', 'qua email'), a leading
    role word ('PO Lan Anh') and punctuation removed; a leading form of address is dropped only when at least two words
    remain. 'chị Lan Anh (PO)' -> ('lan', 'anh'); 'Anh Tuấn' stays ('anh', 'tuấn')."""
    text = unicodedata.normalize("NFC", text or "")
    text = re.sub(r"\([^)]*\)|\bSTK-\d+\b", " ", text)
    text = NAME_TAIL.sub("", text.strip())
    words = re.sub(r"[^\w\s]", " ", text).lower().split()
    if len(words) > 1 and words[0] in ("po", "bo"):
        words = words[1:]
    while len(words) > 2 and words[0] in HONORIFICS:
        words = words[1:]
    return tuple(words)


def stakeholder_names(feature):
    """{STK-NN: name} from _status.md → Stakeholders."""
    out = {}
    for table in feature.tables("_status.md") if "_status.md" in feature.docs else []:
        if table["section"].startswith("Stakeholders"):
            name = col(table, "Name")
            for r in table["rows"]:
                if re.match(r"^STK-\d{2,3}$", cell(r, 0)) and name >= 0:
                    out[cell(r, 0)] = cell(r, name)
    return out


SPLIT_PEOPLE = re.compile(r"\s*(?:;|,|/|\band\b|\bvà\b)\s*")


def people(feature, text, roles=True, _depth=0):
    """The people a cell names, as token tuples: names separated by ';', ',', '/' or ' and '; STK- IDs resolved through
    Stakeholders; with roles=True, role words (PO, business owner) resolved through Governance."""
    found = []
    stk = stakeholder_names(feature)
    for part in SPLIT_PEOPLE.split(text or ""):
        part = part.strip()
        if not part or GOV_PLACEHOLDER.match(part):
            continue
        ids = re.findall(r"\bSTK-\d{2,3}\b", part)
        found += [person_tokens(stk[i]) for i in ids if i in stk]
        bare = " ".join(person_tokens(part)) if not ids or re.sub(r"\bSTK-\d+\b", "", part).strip() else ""
        role = ROLE_ALIASES.get(bare) or ROLE_ALIASES.get(" ".join(re.sub(r"[^\w\s]", " ", part).lower().split()))
        if role:
            if roles and _depth == 0:
                for label, who in (governance_rows(feature) or {}).items():
                    if label.lower().startswith(role):
                        found += people(feature, who, True, 1)
                if role == "product owner":
                    found += people(feature, status_field(feature, "Product Owner"), True, 1)
            continue
        if bare:
            found.append(person_tokens(part))
    return [p for p in found if p]


def known_people(feature):
    """Every person the status page names (Stakeholders, Governance, Product Owner, BA): the pool a short name must be
    unique in."""
    pool = []
    cells = list(stakeholder_names(feature).values()) + list((governance_rows(feature) or {}).values())
    cells += [status_field(feature, "Product Owner"), status_field(feature, "BA")]
    for c in cells:
        for p in people(feature, c, roles=False):
            if p not in pool:
                pool.append(p)
    return pool


def tokens_match(a, b, pool=()):
    """Whole names match (with or without diacritics). A name of two words or more that ENDS the other one - the given
    name a Vietnamese team uses ('Lan Anh' for 'Nguyễn Thị Lan Anh') - matches only if it ends no one else's name
    in the pool. Family and middle names ('Nguyễn Thị') and single words never match."""
    if a == b or ascii_name(a) == ascii_name(b):
        return True
    short_, long_ = (a, b) if len(a) < len(b) else (b, a)
    if len(short_) < 2:
        return False
    ends = lambda s, l: l[-len(s):] == s or ascii_name(l)[-len(s):] == ascii_name(s)  # noqa: E731
    if not ends(short_, long_):
        return False
    owners = {p for p in pool if len(p) >= len(short_) and ends(short_, p)}
    return len(owners - {short_}) <= 1


def one_person(actor):
    """An actor names exactly one person - 'Hacker X / Lan Anh' is two."""
    return bool(actor and actor.strip()) and not SPLIT_PEOPLE.search(actor.strip())


def same_person(feature, actor, text):
    """True if the actor (one person: a name or an STK- ID, not a role word) is one of the people the cell names."""
    if not one_person(actor):
        return False
    who = people(feature, actor, roles=False)
    pool = known_people(feature)
    return bool(who) and any(tokens_match(a, b, pool) for a in who for b in people(feature, text))


def exactly_same_person(feature, actor, text):
    """Whole-name identity only (used for the BA role conflict: 'Lan Anh' the BA is not 'Nguyễn Thị Lan Anh' the PO)."""
    who = people(feature, actor, roles=False)
    return any(a == b or ascii_name(a) == ascii_name(b) for a in who for b in people(feature, text, roles=False))


def resolve_person(feature, actor):
    """The status page's own spelling of the actor (for the log), or the actor as given."""
    pool = known_people(feature)
    who = people(feature, actor, roles=False)
    for cell_text in list(stakeholder_names(feature).values()) + [status_field(feature, "Product Owner")] + \
            list((governance_rows(feature) or {}).values()):
        for part in SPLIT_PEOPLE.split(cell_text or ""):
            if any(tokens_match(a, b, pool) for a in who for b in people(feature, part, roles=False)) and part.strip():
                return re.sub(r"\s*\([^)]*\)\s*$", "", part.strip())
    return actor


def name_matches(name, text):
    """Loose test used only for warnings: does the name appear as whole words in a longer text?"""
    a = person_tokens(name)
    b = " " + " ".join(person_tokens(text)) + " "
    return bool(a) and (" " + " ".join(a) + " ") in b


def gate_approver_cells(feature, gate):
    """Cells naming who may close a gate. 'Gate approvers' may map gates to people ('3,8,9: STK-02; 11: STK-05'):
    a mapped gate is closed only by its people; otherwise the Product Owner, the business owner and unmapped
    approvers. gate=None (approvals outside a gate) also allows area owners."""
    rows = governance_rows(feature) or {}
    approver_cell = next((v for k, v in rows.items() if k.lower().startswith("gate approver")), "")
    mapped, unmapped = {}, []
    for seg in re.split(r"\s*;\s*", approver_cell):
        m = re.match(r"^\s*(\d+(?:\s*,\s*\d+)*)\s*:\s*(.+)$", seg)
        if m:
            for n in re.findall(r"\d+", m.group(1)):
                mapped.setdefault(int(n), []).append(m.group(2))
        elif seg.strip() and not GOV_PLACEHOLDER.match(seg.strip()):
            unmapped.append(seg)
    if gate is not None and gate in mapped:
        return mapped[gate]
    cells = list(unmapped)
    for label, who in rows.items():
        low = label.lower()
        if low.startswith(("product owner", "business owner")) or (gate is None and low.startswith("area owner")):
            if not GOV_PLACEHOLDER.match(who.strip()):
                cells.append(who)
    po = status_field(feature, "Product Owner")
    if po and not po.startswith("<"):
        cells.append(po)
    return cells


def approvers(feature):
    return gate_approver_cells(feature, None)


def decisions(feature, field="Decided by"):
    """{D-NN: cell of the given column} from _status.md → Decision log."""
    out = {}
    for table in feature.tables("_status.md") if "_status.md" in feature.docs else []:
        if table["section"].startswith("Decision log"):
            by = col(table, field)
            for r in table["rows"]:
                if re.match(r"^D-\d{2,3}$", cell(r, 0)):
                    out[cell(r, 0)] = cell(r, by) if by >= 0 else ""
    return out


def is_owner(feature, actor):
    """The Product Owner or the business owner (who may change the rules of the game: mode, human gates, deferrals)."""
    rows = governance_rows(feature) or {}
    cells = [v for k, v in rows.items() if k.lower().startswith(("product owner", "business owner"))]
    cells.append(status_field(feature, "Product Owner"))
    return any(same_person(feature, actor, c) for c in cells if c)


def stage_number(stage):
    m = re.match(r"^\s*(\d+)", stage or "")
    return int(m.group(1)) if m else None


def check_authority(root, item, feature, refs):
    """Rules the log enforces (MANUAL §4a, §8 step 5): known event types; numbered stages; no self-approval by the
    assistant; approvals, human gates and skips of human gates name an approver from Governance and cite evidence
    that exists - and a cited decision must have been taken by that person."""
    kind, actor = item["type"], (item.get("actor") or "").strip()
    if kind not in EVENT_TYPES:
        close = [t for t in sorted(EVENT_TYPES) if t.lower() == kind.lower() or t.split(".")[0] == kind.lower().split(".")[0]]
        raise ValueError(f"unknown event type '{kind}'" + (f" - did you mean {', '.join(close)}?" if close else
                         " - see reference/audit.md (use 'note' for anything else)"))
    model = (item.get("model") or os.environ.get("BA_MODEL") or load_config(root).get("model") or "").strip()
    if kind.startswith(STAGE_EVENTS):
        if not feature:
            raise ValueError(f"{kind} needs a feature (--feature): stage and gate events belong to one feature")
        if stage_number(item.get("stage")) is None:
            raise ValueError(f"{kind} needs a numbered stage, e.g. \"3 Scope\" or \"11 Test/UAT\" (got "
                             f"'{item.get('stage') or ''}')")
    if feature and preference(root, feature, "Mode", "standard") == "controlled" and \
            (not model or model.lower() in PLACEHOLDER_MODELS or len(model) < 3):
        raise ValueError(f"{kind}: controlled mode records the AI model on every workflow event - add \"model\" with "
                         f"the real model name (or set BA_MODEL / .ba/config.json -> model)")
    number = stage_number(item.get("stage"))
    human = bool(feature) and number in human_gates(root, feature)
    rules_change = kind == "settings.changed" and re.search(
        r"(?i)\bmode\b|human_gates|human gates", f"{item.get('summary') or ''} {item.get('decision') or ''}")
    guarded = kind == "approval.recorded" or (kind in ("gate.passed", "stage.skipped") and human) or rules_change
    if not guarded:
        return
    what = {"approval.recorded": "approval.recorded",
            "gate.passed": f"gate.passed for stage {item.get('stage')} (a human gate in this mode)",
            "stage.skipped": f"stage.skipped for stage {item.get('stage')} (a human gate in this mode)",
            "settings.changed": "settings.changed (Mode / human gates decide which gates people close)"}[kind]
    if not actor or is_ai_name(actor):
        raise ValueError(f"{what}: actor must be the person who decided (not the assistant) - the assistant may "
                         f"prepare and record, never approve")
    if not one_person(actor):
        raise ValueError(f"{what}: actor must be one person (a name or an STK- ID), not '{actor}'")
    if ROLE_ALIASES.get(" ".join(re.sub(r"[^\w\s]", " ", actor).lower().split())):
        raise ValueError(f"{what}: actor must be the person's name or STK- ID, not the role '{actor}' - roles change "
                         f"hands, the log must keep who it was")
    bad_refs = [r for r in refs or [] if not re.fullmatch(r"\s*(SRC|D|O)-\d{2,3}\s*", r)]
    if bad_refs:
        raise ValueError(f"{what}: refs must be IDs only (D-NN, SRC-NN, O-NN), not text: {bad_refs}")
    cited = [r.strip() for r in refs or [] if EVIDENCE.search(r)]
    if not feature:
        if kind == "approval.recorded":
            raise ValueError("approval.recorded needs a feature: an approval is recorded where its decision is")
        if not cited:
            raise ValueError(f"{what}: refs must cite the decision (D-) or the source (SRC-)")
        return
    folder = requirements_dir(root) / feature
    feat = Feature(folder)
    known = defined_ids(feat)
    missing = [r for r in cited if r not in known]
    if missing:
        raise ValueError(f"{what}: {', '.join(missing)} not found - record the decision in _status.md → Decision log "
                         f"(or register the source) before logging the event")
    log = decisions(feat)
    own = [r for r in cited if r in log and same_person(feat, actor, log[r])]
    others = [r for r in cited if r in log and r not in own]
    if others:
        raise ValueError(f"{what}: {others[0]} was decided by '{log[others[0]]}', not '{actor}' - cite the approver's "
                         f"own decision")
    if not own:
        raise ValueError(f"{what}: refs must include a D- from _status.md → Decision log decided by '{actor}' (a source "
                         f"alone - an old email or the kick-off notes - doesn't show this decision)")
    if kind in ("gate.passed", "stage.skipped") and number is not None:
        started = [e["ts"][:10] for e in log_entries(root, feature) if e["type"] == "stage.started"
                   and stage_number(e.get("stage")) == number]
        dates = decisions(feat, "Date")
        undated = [r for r in own if parse_day(re.sub(r"\s.*$", "", dates.get(r, "").strip())) is None]
        if undated and len(undated) == len(own):
            raise ValueError(f"{what}: {', '.join(undated)} has no readable date in the Decision log (2026-11-12 or "
                             f"12/11/2026) - the date shows the approval belongs to this run of the stage")
        day = lambda r: parse_day(re.sub(r"\s.*$", "", dates.get(r, "").strip()))  # noqa: E731
        stale = [r for r in own if started and day(r) and day(r).isoformat() < started[-1]]
        if stale and len(stale) == len(own):
            raise ValueError(f"{what}: {', '.join(stale)} predates this run of the stage (started {started[-1]}) - "
                             f"the approval must be given for this run")
    if rules_change:
        if not is_owner(feat, actor):
            raise ValueError(f"{what}: only the Product Owner or the business owner (Governance) may change the mode "
                             f"or the human gates - not '{actor}'")
        return
    cells = gate_approver_cells(feat, number if kind != "approval.recorded" else None)
    if not cells:
        raise ValueError(f"{what}: no approvers named - fill _status.md → Governance (Gate approvers, Product Owner)")
    if not any(same_person(feat, actor, c) for c in cells):
        raise ValueError(f"{what}: '{actor}' is not an approver for this in _status.md → Governance (full name or "
                         f"STK- ID): {short(cells, 6)}")
    ba = status_field(feat, "BA")
    conflict = (governance_rows(feat) or {}).get("Role conflicts", "")
    if ba and exactly_same_person(feat, actor, ba) and not re.search(r"\bD-\d{2,3}\b", conflict):
        raise ValueError(f"{what}: '{actor}' is also the BA - record who reviews the BA's decisions, or the accepted "
                         f"conflict (D-), in Governance → Role conflicts")
    if kind == "gate.passed" and preference(root, feature, "Mode", "standard") == "controlled" \
            and item.get("_via") != "approve":
        raise ValueError(f"{what}: in controlled mode the approver confirms in a terminal - run `ba approve "
                         f"{feature} --gate \"{item.get('stage')}\" --as \"{actor}\" --decision {own[0]}` yourself")


def prepare_event(root, raw, default_feature):
    if not isinstance(raw, dict):
        raise ValueError(f"event is not an object: {raw!r}")
    item = {str(k).lower(): v for k, v in raw.items()}
    unknown = set(item) - set(EVENT_KEYS)
    if unknown:
        raise ValueError(f"unknown keys {sorted(unknown)} in {raw}")
    feature = item.get("feature") or default_feature
    if not item.get("type"):
        raise ValueError(f"event without type: {raw}")
    if item.get("severity") and item["severity"] not in SEVERITIES:
        raise ValueError(f"invalid severity '{item['severity']}' on {item['type']}")
    if feature and not (requirements_dir(root) / feature).is_dir():
        raise ValueError(f"unknown feature '{feature}' (no folder {requirements_dir(root) / feature})")
    refs = item.get("refs")
    if isinstance(refs, str):
        refs = [r for r in re.split(r"\s*,\s*", refs) if r]
    check_authority(root, item, feature, refs)
    reporter = actor_default()
    actor = item.get("actor") or reporter
    resolved = None
    if feature and item.get("actor") and (requirements_dir(root) / feature).is_dir():
        name = resolve_person(Feature(requirements_dir(root) / feature), actor)
        resolved = name if name != actor else None
    fields = {
        "source": "skill",  # value kept from v0 logs: "workflow event logged by the assistant"
        "type": item["type"],
        "actor": actor,
        "actor_resolved": resolved,  # how the status page writes this person (an STK- ID or short name resolved)
        "reported_by": reporter,  # the OS account that ran the command - always, so actor and reporter can differ
        "via": via_default(),     # 'assistant:<tool>' when an AI tool's shell ran it, else 'cli'
        # the AI model only for what an AI tool ran (a person typing in a terminal is not the model)
        "model": item.get("model") or ((os.environ.get("BA_MODEL") or load_config(root).get("model"))
                                       if via_default().startswith("assistant") else None),
        "tool": f"ba-pipeline {version_text()}",
        "session": session_default(),
        "feature": feature,
        "stage": item.get("stage"),
        "summary": item.get("summary"),
        "reason": item.get("reason"),
        "decision": item.get("decision"),
        "severity": item.get("severity"),
        "refs": refs or None,
    }
    return audit_log_path(root, feature), fields


def cmd_audit_event(root, args):
    try:
        if args.json_file:
            text = Path(args.json_file).read_text(encoding="utf-8-sig")
            items = json.loads(text)
            if not isinstance(items, list):
                raise ValueError("--json-file must contain a JSON array")
        else:
            if not args.type:
                raise ValueError("--type is required (or use --json-file)")
            items = [{k: getattr(args, k) for k in EVENT_KEYS if k != "feature"}]
        prepared = [prepare_event(root, item, args.feature) for item in items]  # validate all before writing
    except (ValueError, json.JSONDecodeError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    groups = {}
    for path, fields in prepared:
        groups.setdefault(path, []).append(fields)
    for path, events in groups.items():
        for entry in append_events(path, events):
            print(f"audit #{entry['seq']} {entry['type']} logged")
    if args.json_file:
        print(f"{len(prepared)} events logged")
    return 0


def cmd_audit_verify(root, args):
    logs = []
    if args.all:
        logs = sorted(requirements_dir(root).glob("*/_audit/events.jsonl")) + [audit_log_path(root, None)]
    else:
        logs = [audit_log_path(root, args.feature)]
    failed = False
    for path in logs:
        ok, count, problem = verify_log(path)
        rel = os.path.relpath(path, root)
        if ok:
            print(f"OK      {rel} ({count} entries) {problem}".rstrip())
        else:
            failed = True
            print(f"FAILED  {rel}: {problem}")
    return 1 if failed else 0


def latest_file_hashes(lines):
    """File -> sha256 of its latest file.* record (None after file.removed)."""
    known = {}
    for line in lines:
        match = LINE_RX.match(line)
        entry = json.loads(match.group("body") + "}") if match else json.loads(line)
        if str(entry.get("type", "")).startswith("file.") and entry.get("file"):
            known[entry["file"]] = None if entry["type"] == "file.removed" else entry.get("sha256")
    return known


def pending_changes(root, feature=None):
    """[(file.added|file.changed|file.removed, path, sha256)] not yet in the log. feature=None: workspace files."""
    if feature is None:
        base = root / ".ba"
        candidates = [p for p in (base / "local").rglob("*") if p.is_file()] if (base / "local").is_dir() else []
        if (base / "config.json").is_file():
            candidates.append(base / "config.json")
        if (root / KNOWLEDGE_DIR).is_dir():  # system knowledge bases (/ba-discover) belong to the workspace
            candidates += [p for p in (root / KNOWLEDGE_DIR).rglob("*") if p.is_file() and not p.name.endswith(".lock")]
        prefix = (".ba/", KNOWLEDGE_DIR + "/")
    else:
        folder = requirements_dir(root) / feature
        candidates = [p for p in folder.rglob("*") if p.is_file() and "_audit" not in p.relative_to(folder).parts
                      and not p.name.endswith(".lock")]
        prefix = folder.relative_to(root).as_posix() + "/"
    current = {p.relative_to(root).as_posix(): sha256_file(p) for p in candidates}
    known = {f: h for f, h in latest_file_hashes(read_log(audit_log_path(root, feature))).items() if f.startswith(prefix)}
    changes = []
    for name, digest in sorted(current.items()):
        if name not in known or known[name] is None:
            changes.append(("file.added", name, digest))
        elif known[name] != digest:
            changes.append(("file.changed", name, digest))
    for name, digest in sorted(known.items()):
        if digest is not None and name not in current:
            changes.append(("file.removed", name, None))
    return changes


def record_changes(root, feature, changes):
    if changes:
        append_events(audit_log_path(root, feature), [
            {"source": "sync", "type": kind, "actor": actor_default(), "reported_by": actor_default(), "via": via_default(),
             "session": session_default(),
             "feature": feature, "file": name, "sha256": digest} for kind, name, digest in changes])


def change_summary(changes):
    counts = {t: sum(1 for c in changes if c[0] == t) for t in ("file.added", "file.changed", "file.removed")}
    return f"{counts['file.added']} added, {counts['file.changed']} changed, {counts['file.removed']} removed"


def cmd_audit_sync(root, args):
    if args.workspace:
        feature = None
    else:
        if not args.feature:
            print("error: give a feature, or --workspace", file=sys.stderr)
            return 1
        folder = requirements_dir(root) / args.feature
        if not folder.is_dir():
            print(f"error: no folder {folder}", file=sys.stderr)
            return 1
        feature = args.feature
    changes = pending_changes(root, feature)
    summary = change_summary(changes)
    if args.dry_run:
        for kind, name, _ in changes:
            print(f"{kind[5:]:8} {name}")
        print(f"not yet recorded: {summary}" if changes else "all files match their latest record")
        return 0
    record_changes(root, feature, changes)
    print(f"sync: {summary}" if changes else "sync: nothing changed since the last record")
    return 0


KNOWLEDGE_DIR = "knowledge"
TRACKED = re.compile(r"^(requirements|profiles|templates|checklists|systems|knowledge)/|^glossary\.md$|^\.ba/(local/|config\.json$)"
                     r"|^(CLAUDE|AGENTS|GEMINI)\.md$|^\.claude/(skills|agents|hooks)/|^\.claude/settings(\.local)?\.json$")


def cmd_audit_hook(root, args):
    """Post-edit hook. Never fails the tool call: problems go to audit/hook-errors.log."""
    try:
        raw = sys.stdin.buffer.read().decode("utf-8-sig")
        payload = json.loads(raw)
        tool_input = payload.get("tool_input") or {}
        target = tool_input.get("file_path") or tool_input.get("notebook_path")
        if not target:
            return 0
        full = Path(target).resolve()
        try:
            rel = full.relative_to(root).as_posix()
        except ValueError:
            return 0
        if not TRACKED.search(rel) or "/_audit/" in rel or rel.startswith("audit/"):
            return 0
        req = requirements_dir(root).relative_to(root).as_posix()
        match = re.match(re.escape(req) + r"/([^/]+)/", rel)
        feature = match.group(1) if match else None
        op = {"Write": "write", "NotebookEdit": "notebook-edit"}.get(payload.get("tool_name"), "edit")
        fields = {"source": "hook", "type": "file." + op, "actor": actor_default(), "reported_by": actor_default(),
                  "via": via_default() if assistant_tool() else "assistant:claude-code",  # hooks run inside the AI tool
                  "session": payload.get("session_id"),
                  "feature": feature, "file": rel, "sha256": sha256_file(full) if full.is_file() else None}
        append_events(audit_log_path(root, feature), [fields])
    except Exception as error:  # noqa: BLE001 - a hook must never break the user's edit
        try:
            log = root / "audit" / "hook-errors.log"
            log.parent.mkdir(parents=True, exist_ok=True)
            with open(log, "a", encoding="utf-8") as handle:
                handle.write(f"{datetime.datetime.now().isoformat()} {error}\n")
        except OSError:
            pass
    return 0


# --------------------------------------------------------------------------- check: document model

ID_CORE = r"(?:SRC|STK|G|Q|A|D|R|BR|IS|EP|US|AC|NFR|MSG|SCR|TS|CR|O|INT)-\d{2,3}(?:\.\d+[a-z]?)?"
ID_RX = re.compile(r"\b" + ID_CORE + r"\b")
WARNSIGN, ELLIPSIS = "⚠", "…"
AMBIGUOUS = ["should", "could", "would", "might", "fast", "quick", "quickly", "real-time", "immediately",
             "user-friendly", "intuitive", "easy", "simple", "seamless", "appropriate", "relevant", "suitable",
             "adequate", "reasonable", "proper", "etc", "and so on", "some", "several", "many", "few", "various",
             "flexible", "robust", "secure", "if possible", "where applicable", "as needed", "if necessary", "TBD",
             "TBC", "and/or", "similar to", "minimise", "maximise", "optimise", "soon", "recently", "periodically",
             "timely",  # "responsive" left out: mostly the design term, not a speed claim
             # Vietnamese (Language: vi). "có thể" = may (allowed); "nên" only as "should" in requirement wording.
             "nhanh", "nhanh chóng", "thân thiện", "dễ dùng", "dễ sử dụng", "trực quan", "phù hợp", "hợp lý",
             "thích hợp", "linh hoạt", "tối ưu", "kịp thời", "ngay lập tức", "một số", "vài", "nhiều", "v.v",
             "vân vân", "nếu cần", "khi cần thiết", "tương tự", "sớm", "định kỳ", "bảo mật tốt", "ổn định",
             "đơn giản", "nên", "hiệu quả", "đầy đủ", "khoảng", "tốt", "thường xuyên", "tối đa hoá", "tối thiểu hoá",
             "càng nhanh càng tốt", "dễ hiểu", "thuận tiện", "hiện đại", "mượt", "mượt mà"]
# Vietnamese phrases where a listed word is not vague ("một số điện thoại" = a phone number, "trở nên" = become).
AMBIGUOUS_EXCEPTIONS = re.compile(r"(?i)một số (điện thoại|tài khoản|thẻ|hợp đồng|hồ sơ|tiền|lượng|chứng từ|định danh|"
                                  r"giấy tờ|lô|phiếu|nguyên|thập phân|thứ tự|tự nhiên)|trở nên|cho nên|vì vậy nên|tốt nghiệp|khoảng cách|"
                                  r"khoảng thời gian từ|(?:họ và tên|họ tên|tên|địa chỉ) đầy đủ|một\s*-\s*nhiều|"
                                  r"nhiều\s*-\s*(?:một|nhiều)|(?:sớm|muộn) nhất|chuyển tiền nhanh|"
                                  r"định kỳ (?:lúc|vào|hằng|hàng|mỗi)[^.;|]*\d")


def plain(text):
    return re.sub(r"\*\*|__|~~|`", "", text).strip()


def split_row(line):
    return line.strip().strip("|").split("|")


class Feature:
    def __init__(self, folder):
        self.folder = folder
        names = [p for p in folder.iterdir() if p.is_file() and re.match(r"^(\d\d[a-z]?-.*|_status|rtm)\.md$", p.name)]
        for sub in ("handoff", "docs"):  # role packs and formal documents (BRD, URD, user guides)
            if (folder / sub).is_dir():
                names += [p for p in (folder / sub).iterdir() if p.is_file() and p.suffix == ".md"]
        self.paths = {p.relative_to(folder).as_posix(): p for p in sorted(names, key=lambda p: p.relative_to(folder).as_posix())}
        self.docs = {name: p.read_text(encoding="utf-8-sig").splitlines() for name, p in self.paths.items()}

    def doc(self, prefix):
        return next((n for n in self.docs if n.startswith(prefix)), None)

    def lines(self, include_code=False):
        for name, lines in self.docs.items():
            in_code, section = False, ""
            for number, text in enumerate(lines, start=1):
                if re.match(r"^\s*```", text):
                    in_code = not in_code
                    continue
                if in_code and not include_code:
                    continue
                if not in_code:
                    heading = re.match(r"^##\s+(.*)", text)
                    if heading:
                        section = heading.group(1)
                yield name, number, text, section

    def tables(self, name):
        lines, result, section, i = self.docs[name], [], "", 0
        while i < len(lines):
            heading = re.match(r"^##\s+(.*)", lines[i])
            if heading:
                section = heading.group(1)
            if (i + 1 < len(lines) and re.match(r"^\s*\|", lines[i]) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1])
                    and (i == 0 or not re.match(r"^\s*\|", lines[i - 1]))):
                header = [plain(c) for c in split_row(lines[i])]
                rows, j = [], i + 2
                while j < len(lines) and re.match(r"^\s*\|", lines[j]):
                    raw = split_row(lines[j])
                    rows.append({"no": j + 1, "cells": [plain(c) for c in raw]})
                    j += 1
                result.append({"line": i + 1, "section": section, "header": header, "rows": rows})
                i = j
                continue
            i += 1
        return result


def col(table, *names):
    return next((k for k, h in enumerate(table["header"]) if h in names), -1)


def cell(row, k):
    return row["cells"][k] if 0 <= k < len(row["cells"]) else ""


def short(items, limit=12):
    items = list(items)
    if len(items) <= limit:
        return ", ".join(items)
    return ", ".join(items[:limit]) + f" ... (+{len(items) - limit})"


PRIORITIES = ("Blocking", "Decision-critical", "Important", "Nice to know")
SNAPSHOT_Q = re.compile(r"^\|\s*Questions\s*(`Q-`\s*)?\|")  # Open-items row, not the 'Questions per message' preference
OTHER_OPTION = "Other (write below)"  # last choice of every question in an answer form
CLOSED_DOC = "02-closed.md"  # archive of answered/withdrawn questions and settled assumptions (`ba questions archive`)


def register(feature):
    """Questions and assumptions from 02-questions.md (+ the 02-closed.md archive), read by column name;
    plus non-canonical cells. Returns (main register file, questions, assumptions, odd)."""
    questions, assumptions, odd = [], [], []
    qdoc = feature.doc("02-questions")
    if not qdoc:
        return None, questions, assumptions, odd
    docs = [qdoc] + ([CLOSED_DOC] if CLOSED_DOC in feature.docs else [])
    for name in docs:
        _register_doc(feature, name, questions, assumptions, odd)
    return qdoc, questions, assumptions, odd


def _register_doc(feature, qdoc, questions, assumptions, odd):
    for table in feature.tables(qdoc):
        id_col = col(table, "ID")
        if id_col < 0:
            continue
        prio, risk = col(table, "Priority"), col(table, "Risk", "Risk (H/M/L)")
        stat = col(table, "Status", "Status (Open/Confirmed/Rejected)")
        for row in table["rows"]:
            ident = cell(row, id_col)
            if not re.match(r"^(Q|A)-\d{2,3}$", ident):
                continue
            status = cell(row, stat)
            word = (re.match(r"^[A-Za-z]+", status) or [""])[0]
            where = f"{qdoc}:{row['no']}"
            if ident.startswith("Q-"):
                p = cell(row, prio)
                m = re.match(r"^(" + "|".join(PRIORITIES) + r")\b", p)
                if not m:
                    odd.append(f"{ident} Priority '{p}' ({where})")
                if word not in ("Open", "Answered", "Withdrawn", "Closed"):
                    odd.append(f"{ident} Status '{status}' ({where})")
                questions.append({"id": ident, "priority": m.group(1) if m else "", "status": word})
            else:
                k = cell(row, risk)
                m = re.match(r"^(High|Medium|Low)\b", k)
                level = m.group(1) if m else {"H": "High", "M": "Medium", "L": "Low"}.get((re.match(r"^(H|M|L)\b", k) or [""])[0], "")
                if not level:
                    odd.append(f"{ident} Risk '{k}' ({where})")
                if word not in ("Open", "Confirmed", "Rejected", "Withdrawn"):
                    odd.append(f"{ident} Status '{status}' ({where})")
                assumptions.append({"id": ident, "risk": level, "status": word})


# --------------------------------------------------------------------------- check: individual checks

def defined_ids(feature):
    """IDs the feature defines: first cell of a table row, a heading, a Gherkin '# AC-' line, a ~~withdrawn~~ ID, or a
    file in sources/ named SRC-NN-…"""
    defined = set()
    for name, _, text, _ in feature.lines(include_code=True):
        if name.startswith("docs/"):
            continue  # documents copy IDs from the artifacts; they never define one
        m = (re.match(r"^\s*\|\s*(?:~~)?(" + ID_CORE + ")", text)
             or re.match(r"^#{1,4}\s+(?:\d+\.\d*\s+)?(" + ID_CORE + ")", text)
             or re.match(r"^\s*#\s+(AC-\d{2,3}\.\d+[a-z]?)", text))
        if m:
            defined.add(m.group(1))
        defined.update(re.findall(r"~~(" + ID_CORE + ")~~", text))
    sources = feature.folder / "sources"
    if sources.is_dir():
        defined.update(m.group(1) for p in sources.iterdir() if (m := re.match(r"^(SRC-\d{2,3})", p.name)))
    return defined



def run_checks(root, slug, only):
    folder = requirements_dir(root) / slug
    if not folder.is_dir():
        print(f"FAIL  setup: no folder {os.path.relpath(folder, root)}")
        return 1
    feature = Feature(folder)
    failed = False

    def report(name, level, detail):
        nonlocal failed
        failed = failed or level == "FAIL"
        print(f"{level:<5} {name}: {detail}")

    def want(name):
        return not only or name in only

    qdoc, questions, assumptions, odd = register(feature)
    open_q = [q for q in questions if q["status"] == "Open"]
    blocking = [q for q in open_q if q["priority"] == "Blocking"]
    critical = [q for q in open_q if q["priority"] == "Decision-critical"]
    open_a = [a for a in assumptions if a["status"] == "Open"]
    high_a = [a for a in open_a if a["risk"] == "High"]
    all_lines = list(feature.lines(include_code=True))

    # status
    if want("status"):
        st = feature.docs.get("_status.md")
        if st is None:
            report("status", "FAIL", "_status.md missing - create it from templates/_status.md")
        else:
            problems, level = [], "PASS"
            updated = next((l for l in st if re.match(r"^\|\s*Last updated\s*\|\s*\d{4}-\d{2}-\d{2}", l)), None)
            if not updated:
                problems.append("no 'Last updated' date")
                level = "WARN"
            else:
                date = datetime.date.fromisoformat(re.search(r"\d{4}-\d{2}-\d{2}", updated).group(0))
                others = [p for n, p in feature.paths.items() if n != "_status.md"]
                newest = max((datetime.date.fromtimestamp(p.stat().st_mtime) for p in others), default=None)
                if newest and newest > date:
                    problems.append(f"last updated {date} but artifacts changed {newest}")
                    level = "WARN"
            missing = []
            if not any(re.match(r"^## Preferences", l) for l in st):
                missing.append("Preferences section")
            if not any(re.match(r"^## Approach", l) for l in st):
                missing.append("Approach section")
            if not any(re.match(r"^\|\s*Elicitation round\s*\|", l) for l in st):
                missing.append("'Elicitation round' preference")
            dl = next((i for i, l in enumerate(st) if re.match(r"^## Decision log", l)), -1)
            if 0 <= dl < len(st) - 1 and "Revisit at" not in st[dl + 1]:
                missing.append("'Revisit at' column in Decision log")
            if missing:
                problems.append(f"missing template parts ({short(missing)}) - migrate from templates/_status.md")
                level = "WARN" if level == "PASS" else level
            if qdoc:
                q_row = next((l for l in st if SNAPSHOT_Q.match(l)), None)
                a_row = next((l for l in st if re.match(r"^\|\s*Assumptions", l)), None)
                if not q_row or not a_row:
                    problems.append("Open items snapshot not found")
                    level = "WARN" if level == "PASS" else level
                else:
                    def num(text, rx):
                        m = re.search(rx, plain(text))
                        return int(m.group(1)) if m else None
                    qc, ac = split_row(q_row), split_row(a_row)
                    none = lambda c: re.match(r"^(none|0|-)", plain(c)) is not None  # noqa: E731
                    claims = [
                        ("open Q", num(qc[1], r"^(\d+)"), len(open_q)),
                        ("Blocking Q", 0 if none(qc[2]) else num(qc[2], r"(\d+)\s*Blocking"), len(blocking)),
                        ("open A", num(ac[1], r"^(\d+)"), len(open_a)),
                        ("High A", 0 if none(ac[2]) else num(ac[1], r"(\d+)\s*High"), len(high_a)),
                    ]
                    wrong = [f"{n} says {said}, register has {real}" for n, said, real in claims if said is not None and said != real]
                    if wrong:
                        problems.append(f"snapshot wrong: {short(wrong)}")
                        level = "FAIL"
            if problems:
                report("status", level, "; ".join(problems))
            else:
                report("status", "PASS", f"_status.md current, template-complete, snapshot matches register "
                       f"({len(open_q)} open Q, {len(blocking)} Blocking; {len(open_a)} open A, {len(high_a)} High)")

    # ids
    defined = defined_ids(feature)
    if want("ids"):
        refs = {}
        for name, number, text, _ in all_lines:
            for ident in ID_RX.findall(text):
                refs.setdefault(ident, f"{name}:{number}")
        missing = sorted(i for i in refs if i not in defined)
        if missing:
            report("ids", "FAIL", f"{len(missing)} referenced but never defined: {short([f'{i} ({refs[i]})' for i in missing], 8)}")
        else:
            report("ids", "PASS", f"{len(refs)} IDs referenced, all defined")

    # ranges
    if want("ranges"):
        rx = re.compile(r"\b([A-Z]{1,3})-\d{2,3}\s*(" + ELLIPSIS + r"|\.\.\.?|\bto\b)\s*\1-\d{2,3}")
        hits = [f"{n}:{no}" for n, no, t, sec in all_lines if not (n == "_status.md" and sec.startswith("History")) and rx.search(t)]
        report("ranges", "WARN" if hits else "PASS", f"{len(hits)} ID ranges (list IDs explicitly): {short(hits)}" if hits else "no ID ranges")

    # register
    if want("register"):
        if not qdoc:
            report("register", "WARN", "no 02-questions.md yet")
        else:
            in_register = {x["id"] for x in questions + assumptions}
            used = {i for _, _, t, _ in all_lines for i in re.findall(r"\b(?:A|Q)-\d{2,3}\b", t)}
            out = sorted(used - in_register)
            if out:
                report("register", "FAIL", f"{len(out)} A-/Q- not in the register ({qdoc}): {short(out)}")
            else:
                report("register", "PASS", f"{len(used)} A-/Q- all in {qdoc}" + (f" / {CLOSED_DOC}" if CLOSED_DOC in feature.docs else ""))

    # ground
    if want("ground"):
        spec = feature.doc("07-")
        if not spec:
            report("ground", "WARN", "no 07-spec.md yet")
        else:
            bad, count = [], 0
            for table in feature.tables(spec):
                id_col, rule_col, src_col = col(table, "ID"), col(table, "Rule"), col(table, "Source")
                if min(id_col, rule_col, src_col) < 0:
                    continue
                for row in table["rows"]:
                    ident = cell(row, id_col)
                    if not re.match(r"^BR-\d{2,3}$", ident):
                        continue
                    count += 1
                    if not re.search(r"\b(SRC|D|A)-\d{2,3}\b", cell(row, src_col)):
                        bad.append(f"{ident} ({spec}:{row['no']})")
            flags = sum(1 for _, _, t, _ in all_lines if WARNSIGN in t and re.search(r"\bA-\d{2,3}\b", t))
            if count == 0:
                report("ground", "WARN", f"no business-rules table (ID | Rule | ... | Source) found in {spec}")
            elif bad:
                report("ground", "FAIL", f"{len(bad)} of {count} business rules cite no SRC-/D-/A- in the Source column: {short(bad)}")
            else:
                report("ground", "PASS", f"{count} business rules all cite SRC-/D-/A-; {flags} lines flagged as assumption")

    # gherkin
    if want("gherkin"):
        stories = feature.doc("05-")
        if not stories:
            report("gherkin", "WARN", "no 05-stories.md yet")
        else:
            ac_count, bad, story = {}, [], None
            scenario, has_when, has_then = None, False, False

            def close():
                if scenario and not (has_when and has_then):
                    bad.append(scenario)
            for number, text in enumerate(feature.docs[stories], start=1):
                m = re.match(r"^##\s+(US-\d{2,3})", text)
                if m:
                    close()
                    scenario, story = None, m.group(1)
                    ac_count[story] = 0
                    continue
                if re.match(r"^\s*#\s+AC-\d", text) and story:
                    ac_count[story] += 1
                if re.match(r"^\s*Scenario( Outline)?:", text):
                    close()
                    scenario, has_when, has_then = f"{stories}:{number}", False, False
                if re.match(r"^\s*When\b", text):
                    has_when = True
                if re.match(r"^\s*Then\b", text):
                    has_then = True
            close()
            thin = [f"{s} ({n})" for s, n in ac_count.items() if n < 3]
            msgs = ([f"stories with < 3 AC: {short(thin)}"] if thin else []) + ([f"scenarios missing When/Then: {short(bad)}"] if bad else [])
            if msgs:
                report("gherkin", "FAIL", "; ".join(msgs))
            else:
                report("gherkin", "PASS", f"{len(ac_count)} stories, {sum(ac_count.values())} AC, all scenarios have When/Then")

    # tables
    if want("tables"):
        hits = [f"{n}:{t['line']}" for n in feature.docs for t in feature.tables(n) if ID_RX.search(" ".join(t["header"]))]
        report("tables", "WARN" if hits else "PASS",
               f"{len(hits)} table headers contain data (use '| Item | Detail |' header): {short(hits)}" if hits else "no malformed table headers")

    # ambiguity
    if want("ambiguity"):
        rx = re.compile(r"(?i)(?<![\w-])(" + "|".join(re.escape(w) for w in AMBIGUOUS) + r")(?![\w-])")
        hits = []
        for name, number, text, _ in feature.lines():
            if name.startswith(("08-", "02-")):
                continue  # review and question log quote problems on purpose
            if name.startswith("01-") and re.search(r"\bSRC-\d", text):
                continue  # intake records the business's own words
            if re.search(r"\*\*Priority:\*\*|^\s*\|\s*(Term|Don.t say)", text):
                continue  # MoSCoW priority line; glossary
            text = unicodedata.normalize("NFC", text)  # macOS and some editors write Vietnamese decomposed (NFD)
            text = AMBIGUOUS_EXCEPTIONS.sub(" ", text)
            text = re.sub('"[^"]*"|“[^”]*”', "", text)
            text = re.sub(r"(?i)so that[^|]*", "", text)
            hits += [f"{name}:{number} '{m.group(0)}'" for m in rx.finditer(text)]
        report("ambiguity", "WARN" if hits else "PASS",
               f"{len(hits)} hits - rewrite or justify: {short(hits, 10)}" if hits else
               "no ambiguity words outside quotes, priorities and recorded source wording")

    # open
    if want("open"):
        if not qdoc:
            report("open", "WARN", "no 02-questions.md yet")
        elif odd:
            report("open", "FAIL", f"{len(odd)} register cells are not a canonical value (Priority: Blocking/Decision-"
                   f"critical/Important/Nice to know; Risk: High/Medium/Low; Status: Open/Answered/Confirmed/Rejected/"
                   f"Withdrawn/Closed - put notes after it): {short(odd, 6)}")
        else:
            medium = sum(1 for a in open_a if a["risk"] == "Medium")
            low = sum(1 for a in open_a if a["risk"] == "Low")
            report("open", "WARN" if blocking or critical or high_a else "PASS",
                   f"blocking questions open: {len(blocking)} ({short([q['id'] for q in blocking], 8)}); decision-critical "
                   f"open: {len(critical)} ({short([q['id'] for q in critical], 8)}); high-risk assumptions open: "
                   f"{len(high_a)} ({short([a['id'] for a in high_a], 8)}); open assumptions by risk: "
                   f"High {len(high_a)}, Medium {medium}, Low {low}")

    # governance: who decides, and does every scope item serve a goal and have an owner?
    if want("governance"):
        problems, level = governance_problems(feature)
        report("governance", level, "; ".join(problems) if problems else
               "business owner and PO named, every scope item has a goal and an owner, no unaccepted role conflicts")

    # rtm: results only from real runs, coverage computed by the tool and current
    if want("rtm"):
        level, detail = rtm_problems(feature)
        report("rtm", level, detail)

    # handoff: every deliverable the approach lists exists once handoff has started
    if want("handoff"):
        if not (feature.folder / "handoff").is_dir():
            report("handoff", "PASS", "no handoff/ yet")
        else:
            deliverables = section_text(feature.docs.get("_status.md", []), "Approach")  # holds ### Deliverables
            deliverables = deliverables.split("### Deliverables", 1)[-1] if "### Deliverables" in deliverables else \
                "\n".join(feature.docs.get("_status.md", []))
            listed = sorted({p for line in deliverables.splitlines() if "<" not in line  # template placeholders
                             for p in re.findall(r"`(handoff/[\w.-]+\.md)`", line)})
            missing = [p for p in listed if not (feature.folder / p).is_file()]
            packs = [n for n in feature.docs if n.startswith("handoff/")]
            skipped = any(re.search(r"Skipped \(O-\d", l) for l in feature.docs.get("_status.md", []))
            no_box = [n for n in packs if skipped and not any(l.startswith("## Skipped stages") for l in feature.docs[n])]
            msgs = ([f"deliverables listed in _status.md but missing: {short(missing)}"] if missing else []) + \
                   ([f"packs without the 'Skipped stages & known gaps' box although stages were skipped: {short(no_box)}"]
                    if no_box else [])
            report("handoff", "FAIL" if msgs else "PASS", "; ".join(msgs) if msgs else
                   f"{len(packs)} packs; every listed deliverable exists")

    # docs: formal documents (BRD, URD, user guides) - canonical status, approval on record, user guides only describe
    # tested behaviour
    if want("docs"):
        level, problems = docs_problems(root, slug, feature)
        report("docs", level, "; ".join(problems) if problems else
               (f"{sum(1 for n in feature.docs if n.startswith('docs/'))} documents; status canonical, approvals on record"
                if any(n.startswith("docs/") for n in feature.docs) else "no formal documents yet"))

    # gates: the Gates table agrees with the log, the review and the mode (what stakeholders see is what was decided)
    if want("gates"):
        level, problems = gates_problems(root, slug, feature)
        report("gates", level, "; ".join(problems) if problems else
               "every Passed or Skipped human gate has its approver's event in the log; review and mode agree")

    # audit: decisions in the log and file changes recorded?
    if want("audit"):
        problems = audit_gaps(root, slug, feature)
        report("audit", "WARN" if problems else "PASS", "; ".join(problems) if problems else
               "every decision in _status.md is logged; every file change is recorded")

    return 1 if failed else 0


GOV_PLACEHOLDER = re.compile(r"^(|-|—|–|tbd|\?|<.*>)$", re.I)


def governance_rows(feature):
    """{role label: who} from _status.md → Governance (table with Role and Who columns)."""
    rows = {}
    if "_status.md" not in feature.docs:
        return None
    for table in feature.tables("_status.md"):
        if not table["section"].startswith("Governance"):
            continue
        role, who = col(table, "Role"), next((k for k, h in enumerate(table["header"]) if h.startswith("Who")), -1)
        if role < 0 or who < 0:
            continue
        for row in table["rows"]:
            rows[cell(row, role)] = cell(row, who)
        return rows
    return None


def active_profiles(feature):
    """Profile names in _status.md → Approach (rows that start with a `name`, before the Stage plan)."""
    names, inside = [], False
    for line in feature.docs.get("_status.md", []):
        if line.startswith("## "):
            inside = line.startswith("## Approach")
        elif line.startswith("### "):
            inside = False
        elif inside:
            m = re.match(r"^\|\s*`([a-z0-9.-]+)`", line)
            if m:
                names.append(m.group(1))
    return names


def governance_problems(feature):
    """Returns (problems, level). Before Scope exists missing owners are WARN; once 03-scope exists they FAIL."""
    problems, level = [], "PASS"

    def raise_to(new):
        nonlocal level
        order = {"PASS": 0, "WARN": 1, "FAIL": 2}
        level = new if order[new] > order[level] else level

    rows = governance_rows(feature)
    scope_doc = feature.doc("03-")
    if rows is None:
        problems.append("no Governance section in _status.md - migrate (install.py update) and fill: business owner, "
                        "PO, area owners, escalation path")
        raise_to("WARN")
        rows = {}
    else:
        named = lambda label: next((v for k, v in rows.items() if k.lower().startswith(label)), "")  # noqa: E731
        # small-change: the PO may stand in as business owner (profile §3, Foundations)
        po_stands_in = "small-change" in active_profiles(feature) and not GOV_PLACEHOLDER.match(named("product owner").strip())
        for label, text in (("business owner", "business owner (final say when stakeholders disagree)"),
                            ("product owner", "Product Owner")):
            if label == "business owner" and po_stands_in:
                continue
            if GOV_PLACEHOLDER.match(named(label).strip()):
                problems.append(f"{text} not named")
                raise_to("FAIL" if scope_doc else "WARN")
        no_owner_areas = [k.split(":", 1)[-1].strip() for k, v in rows.items()
                          if k.lower().startswith("area owner") and "<" not in k and GOV_PLACEHOLDER.match(v.strip())]
        if no_owner_areas:
            problems.append(f"areas without an owner: {short(no_owner_areas)}")
            raise_to("FAIL" if scope_doc else "WARN")
        ba_name = ""
        for line in feature.docs.get("_status.md", []):
            m = re.match(r"^\|\s*BA\s*\|\s*([^|]*)\|", line)
            if m:
                ba_name = plain(m.group(1)).lower()
        conflict_note = named("role conflict")
        accepted = re.search(r"\bD-\d{2,3}\b", conflict_note)
        for label in ("business owner", "product owner"):
            holder = plain(named(label)).lower()
            if ba_name and holder and (ba_name in holder or holder in ba_name) and not accepted:
                problems.append(f"role conflict: the BA is also the {label} - who checks the BA's decisions? "
                                f"Name a reviewer or record acceptance (D-) in Governance → Role conflicts")
                raise_to("WARN")
    intake_doc = feature.doc("01-")
    for table in feature.tables(intake_doc) if intake_doc else []:
        status_col = col(table, "Status")
        if col(table, "Foundation") >= 0 and status_col >= 0:
            unasked = [cell(r, 0) for r in table["rows"] if GOV_PLACEHOLDER.match(cell(r, status_col).strip())]
            if unasked:
                problems.append(f"foundations neither known nor asked: {short(unasked)}")
                raise_to("WARN")
    if scope_doc:
        for table in feature.tables(scope_doc):
            id_col, measures = col(table, "ID"), [(h, col(table, h)) for h in ("Metric", "Baseline", "Target")]
            if id_col >= 0 and all(k >= 0 for _, k in measures):
                goals = [r for r in table["rows"] if re.match(r"^G-\d{2,3}$", cell(r, id_col))]
                blank = [f"{cell(r, id_col)} {h}" for r in goals for h, k in measures if GOV_PLACEHOLDER.match(cell(r, k).strip())]
                if blank:
                    problems.append(f"goals not measurable (write the value, 'unknown — measured by <date>' or "
                                    f"'waived (D-)'): {short(blank)}")
                    raise_to("FAIL")
                undated = [cell(r, id_col) for r in goals for h, k in measures
                           if re.match(r"(?i)^unknown", cell(r, k).strip()) and not re.search(r"(?i)measur", cell(r, k))]
                if undated:
                    problems.append(f"unknown goal values with no plan to measure them: {short(sorted(set(undated)))}")
                    raise_to("WARN")
        for table in feature.tables(scope_doc):
            id_col = col(table, "ID")
            goal_col = next((k for k, h in enumerate(table["header"]) if h.startswith(("Goal", "Supports goal"))), -1)
            if id_col < 0 or goal_col < 0:
                continue
            owner_col = next((k for k, h in enumerate(table["header"]) if h.startswith("Owner")), -1)
            ids = [r for r in table["rows"] if re.match(r"^IS-\d{2,3}$", cell(r, id_col))]
            if not ids:
                continue
            # A scope item serves a goal (G-), or is mandatory by policy/law/constraint with its source (SRC-/D-).
            mandated = lambda text: (re.search(r"(?i)mandatory|compliance|regulat|legal|policy|constraint", text)  # noqa: E731
                                     and re.search(r"\b(SRC|D)-\d{2,3}\b", text))
            no_goal = [cell(r, id_col) for r in ids
                       if not re.search(r"\bG-\d{2,3}\b", cell(r, goal_col)) and not mandated(cell(r, goal_col))]
            if no_goal:
                problems.append(f"scope items serving no goal (cite G-, or 'mandatory: <why> (SRC-/D-)'): {short(no_goal)}")
                raise_to("FAIL")
            if owner_col < 0:
                problems.append(f"{scope_doc} In-scope table has no Owner column (who decides about each item)")
                raise_to("WARN")
            else:
                no_owner = [cell(r, id_col) for r in ids if GOV_PLACEHOLDER.match(cell(r, owner_col).strip())]
                if no_owner:
                    problems.append(f"scope items without an owner: {short(no_owner)}")
                    raise_to("FAIL")
    return problems, level


DOC_STATUS = ("Draft", "In review", "Approved")


def docs_problems(root, slug, feature):
    problems, level = [], "PASS"
    names = [n for n in feature.docs if n.startswith("docs/")]
    approvals = [e for e in log_entries(root, slug) if e["type"] == "approval.recorded"]
    rows = rtm_rows(feature)
    for name in names:
        lines = feature.docs[name]
        status = next((plain(split_row(l)[1]) for l in lines if re.match(r"^\|\s*Review status\s*\|", l)), "")
        word = next((s for s in DOC_STATUS if status.startswith(s)), "")
        if not word or "·" in status:
            problems.append(f"{name}: Review status '{status or 'missing'}' - one of {', '.join(DOC_STATUS)}")
            level = "FAIL"
            continue
        base = name.split("/", 1)[1]
        if word == "Approved":
            def approves_this(e):
                text = f"{e.get('summary') or ''} {e.get('decision') or ''}"
                names_it = e.get("file") == name or re.search(r"(?<![\w-])" + re.escape(base) + r"(?![\w-])", text)
                rejected = (re.match(r"(?i)^(rejected|reject|not approved)", e.get("decision") or "")
                            or re.search(r"(?i)reject|từ chối|không duyệt|chưa duyệt|chưa đạt|không đạt|trả lại|"
                                         r"not approved", text))
                return bool(names_it) and not rejected and not is_ai_name(e.get("actor")) \
                    and is_owner(feature, e.get("actor") or "")
            mine = [e for e in approvals if approves_this(e)]
            if not mine:
                problems.append(f"{name}: marked Approved but no approval of {base} by the PO or business owner is "
                                f"logged (ba approve {slug} --doc {name} …)")
                level = "FAIL"
            elif mine[-1].get("sha256") and mine[-1]["sha256"] != sha256_file(feature.folder / name):
                problems.append(f"{name}: changed after it was approved on {mine[-1]['ts'][:10]} - set Review status "
                                f"back to In review and approve the new version")
                level = "FAIL"
        if base.startswith("user-guide") and rows is not None:
            cited = set(re.findall(r"\bAC-\d{2,3}\.\d+[a-z]?\b", "\n".join(lines)))
            not_covered = sorted(ac for ac in cited if any(r["AC"] == ac and r["Coverage"] not in ("Covered", "Superseded")
                                                           for r in rows))
            if not_covered:
                problems.append(f"{name}: describes behaviour not yet Covered in the RTM (move it to 'Coming soon'): "
                                f"{short(not_covered, 6)}")
                level = "FAIL" if word == "Approved" else ("WARN" if level == "PASS" else level)
    return level, problems


GATE_RESULTS = ("Passed", "Failed", "Skipped", "Deferred", "Blocked", "Reopened", "–", "-", "")
# Words people write in a Gates cell that mean "passed" (they are not canonical: the check FAILs them, and treats
# them as passed so a gate written "Đạt" can't dodge the log comparison).
PASS_WORDS = re.compile(r"(?i)^(pass|passed|approved|ok|done|đạt|đã đạt|đã duyệt|duyệt|thông qua|xong|✅|✔|☑)\b")


def gate_result(text):
    """(canonical word or '', looks_passed) for a Gates Result cell; markdown and emoji ignored."""
    clean = plain(text).strip()
    clean = re.sub(r"^[✅✔☑🟢🔴❌⚠️\s]+", "", clean)
    word = next((w for w in GATE_RESULTS if w and re.match(re.escape(w) + r"\b", clean)), "")
    if clean in ("", "–", "-"):
        word = "–"
    looks_passed = word == "Passed" or bool(PASS_WORDS.match(plain(text).strip()))
    return word, looks_passed


SEVERITY_WORDS = {"critical": "Critical", "blocker": "Critical", "blocking": "Critical", "nghiêm trọng": "Critical",
                  "major": "Major", "high": "Major", "lớn": "Major", "minor": "Minor", "low": "Minor", "nhỏ": "Minor"}


def review_defects(feature):
    """(defects, has_status, verdict, score) from 08-review.md: defects = [{severity, status, id, raw}] of the Defects
    table; severities read case-insensitively without markdown or emoji ('🔴 critical', 'Blocker' -> Critical)."""
    doc = feature.doc("08-")
    if not doc:
        return [], False, "", None
    verdict, score = "", None
    for line in feature.docs[doc]:
        flat = plain(line)
        m = re.search(r"(?i)Verdict:\s*\**\s*([A-Za-zÀ-ỹ]+)", flat)
        if m and not verdict:
            word = m.group(1).lower()
            verdict = {"pass": "Pass", "passed": "Pass", "đạt": "Pass", "conditional": "Conditional",
                       "fail": "Fail", "failed": "Fail"}.get(word, m.group(1))
        s = re.search(r"(?i)Score:\s*\**\s*(\d{1,3})\s*/\s*100", flat)
        if s and score is None:
            score = int(s.group(1))
    defects, has_status = [], False
    for table in feature.tables(doc):
        if not table["section"].startswith("Defects"):
            continue
        sev = col(table, "Severity", "Sev", "Mức độ", "Muc do", "Priority")
        stat = col(table, "Status", "Trạng thái")
        if sev < 0 and table["rows"]:
            defects.append({"id": "?", "severity": "Unreadable", "status": "", "raw": ""})
        has_status = has_status or stat >= 0
        for r in table["rows"]:
            raw = cell(r, sev) if sev >= 0 else ""
            key = re.sub(r"[^\wÀ-ỹ ]", " ", raw).strip().lower()
            level = next((v for k, v in SEVERITY_WORDS.items() if key.startswith(k)), "")
            if level:
                defects.append({"id": cell(r, 0), "severity": level, "status": cell(r, stat) if stat >= 0 else "",
                                "raw": raw})
    return defects, has_status, verdict, score


def gates_table(feature):
    """The Gates table of _status.md, found by its columns (Stage + Result) or a heading naming Gates / Cổng."""
    tables = feature.tables("_status.md") if "_status.md" in feature.docs else []
    named = [t for t in tables if re.search(r"(?i)gates?\b|cổng", t["section"])]
    for t in named + tables:
        if col(t, "Stage") >= 0 and col(t, "Result") >= 0 and (t in named or col(t, "Gate") >= 0):
            return t
    return None


def gates_problems(root, slug, feature):
    problems, level = [], "PASS"

    def raise_to(new):
        nonlocal level
        level = new if {"PASS": 0, "WARN": 1, "FAIL": 2}[new] > {"PASS": 0, "WARN": 1, "FAIL": 2}[level] else level
    entries = log_entries(root, slug)
    human = human_gates(root, slug)
    controlled = preference(root, slug, "Mode", "standard") == "controlled"
    gates = gates_table(feature)
    results = {}
    if "_status.md" in feature.docs and gates is None:
        problems.append("no Gates table in _status.md (a table with Stage, Gate and Result columns) - the gates can't "
                        "be checked")
        raise_to("FAIL")
    for r in gates["rows"] if gates else []:
        if cell(r, 0).startswith("<"):
            continue  # template placeholder row (<extra stages>)
        number = stage_number(cell(r, 0))
        if number is None:
            problems.append(f"Gates row '{cell(r, 0)}' doesn't start with its stage number (e.g. '8 Review') - it can't "
                            f"be checked")
            raise_to("FAIL")
            continue
        word, passed = gate_result(cell(r, 2))
        results[number] = "Passed" if passed else word
        if not word:
            problems.append(f"{cell(r, 0)} result '{cell(r, 2)}' is not a canonical value (Passed · Failed · Skipped "
                            f"(O-NN) · Deferred · Blocked · –; notes after it, in any language)")
            raise_to("FAIL")
        gate_events = [e for e in entries if e["type"] in ("gate.passed", "gate.failed", "gate.reopened")
                       and stage_number(e.get("stage")) == number]
        latest = gate_events[-1] if gate_events else None
        if passed:
            if latest is None or latest["type"] != "gate.passed":
                state = latest["type"] if latest else "no gate event"
                problems.append(f"{cell(r, 0)} says passed but the log's latest gate event is {state}")
                raise_to("FAIL" if number in human else "WARN")
            elif number in human and latest.get("tool") and is_ai_name(latest.get("actor")):
                problems.append(f"{cell(r, 0)} was passed by '{latest.get('actor')}' - a human gate needs its approver")
                raise_to("FAIL")
            elif number in human and latest.get("tool") and str(latest.get("via", "")).startswith("assistant") \
                    and not any(str(x).startswith("SRC-") for x in latest.get("refs") or []):
                # The assistant relayed the approval and cited no source of its own: only the BA's word stands behind it.
                problems.append(f"{cell(r, 0)} approval was relayed by the AI tool with no SRC- (email, minutes) - "
                                f"register the approval as a source, or have the approver run ba approve")
                raise_to("FAIL" if controlled else "WARN")
        elif word == "Skipped" and number in human:
            skips = [e for e in entries if e["type"] == "stage.skipped" and stage_number(e.get("stage")) == number]
            if not skips or is_ai_name(skips[-1].get("actor")):
                problems.append(f"{cell(r, 0)} says Skipped but no stage.skipped event by a named person is logged")
                raise_to("FAIL")
    defects, has_status, verdict, score = review_defects(feature)
    open_ = lambda d: not re.match(r"(?i)^(fixed|closed|resolved|đã sửa)", plain(d["status"]))  # noqa: E731
    if any(d["severity"] == "Unreadable" for d in defects):
        problems.append("08-review.md Defects table has no Severity column (Severity · Sev · Mức độ) - its defects "
                        "can't be counted")
        raise_to("WARN")
        defects = [d for d in defects if d["severity"] != "Unreadable"]
    if results.get(8) == "Passed":
        history = next((t for t in feature.tables("_status.md") if t["section"].startswith("Review score")), None)
        last = history["rows"][-1] if history and history["rows"] else None
        vcol = col(history, "Verdict") if history else -1
        if last is None or not plain(cell(last, vcol)).lower().startswith("pass"):
            problems.append("8 Review says passed but the latest review verdict in Review score history is "
                            f"'{cell(last, vcol) if last else 'missing'}'")
            raise_to("FAIL")
    critical_open = [d["id"] for d in defects if d["severity"] == "Critical" and (open_(d) if has_status else True)]
    if verdict == "Pass" and critical_open:
        problems.append(f"08-review says Pass with Critical defects not fixed: {short(critical_open, 6)}")
        raise_to("FAIL")
    if verdict == "Pass" and score is not None and score < 80:
        problems.append(f"08-review says Pass with a score of {score} (Pass needs ≥ 80)")
        raise_to("FAIL")
    if results.get(9) == "Passed":
        log = decisions(feature)
        if defects and not has_status:
            problems.append("08-review.md Defects table has no Status column - can't show Majors are fixed before handoff")
            raise_to("WARN")
        elif defects:
            def deferred_ok(d):
                m = re.search(r"(?i)deferred.*?\b(D-\d{2,3})\b", d["status"])
                return bool(m) and m.group(1) in log and is_owner(feature, log[m.group(1)])
            unresolved = [d["id"] for d in defects if d["severity"] in ("Critical", "Major") and open_(d)
                          and not (d["severity"] == "Major" and deferred_ok(d))]
            if unresolved:
                problems.append(f"9 Handoff passed with Critical/Major defects neither fixed nor deferred by the PO or "
                                f"business owner (Status 'Deferred (D-…)', that D- decided by them): {short(unresolved, 6)}")
                raise_to("FAIL")
    if results.get(11) == "Passed":
        limits = uat_thresholds(root, slug)
        if limits:
            unmet = [name for name, value in kpis(root, slug) if name.startswith("UAT thresholds") and "NOT met" in value]
            if unmet:
                problems.append("11 Test/UAT passed while the PO's UAT thresholds are NOT met (ba kpi)")
                raise_to("FAIL")
    # G1: the Mode cell must agree with the latest valid mode change; editing the cell alone changes nothing
    cell_mode, raw = mode_cell(root, slug)
    changes = mode_events(root, slug)
    if cell_mode is None:
        problems.append(f"Mode '{raw}' names no mode (or several) - write quick, standard or controlled (notes after it)")
        raise_to("FAIL")
    elif changes and changes[-1][0] != cell_mode:
        problems.append(f"Mode cell says '{cell_mode}' but the last change approved by the PO or business owner is "
                        f"'{changes[-1][0]}' ({changes[-1][1]['ts'][:10]}) - the rules keep using '{changes[-1][0]}' "
                        f"until a new settings.changed by them")
        raise_to("FAIL")
    elif not changes and cell_mode != "standard":
        problems.append(f"Mode is '{cell_mode}' but no settings.changed event by the PO or business owner records it "
                        f"(summary 'Mode: {cell_mode}', refs their D-)")
        raise_to("FAIL")
    if "human_gates" in load_config(root):
        ws = log_entries(root, None)
        if not any(e["type"] == "settings.changed" and "human_gates" in (e.get("summary") or "")
                   and not is_ai_name(e.get("actor")) and not str(e.get("via", "")).startswith("assistant")
                   for e in ws):
            problems.append(".ba/config.json sets human_gates but no workspace settings.changed event, run by a person "
                            "outside the AI tool, records it")
            raise_to("FAIL" if controlled else "WARN")
    return level, problems


def audit_gaps(root, slug, feature):
    problems = []
    lines = read_log(audit_log_path(root, slug))
    logged = set()
    for line in lines:
        m = LINE_RX.match(line)
        entry = json.loads(m.group("body") + "}") if m else json.loads(line)
        if entry.get("type") in ("decision.recorded", "approval.recorded", "question.answered", "approach.confirmed",
                                 "correction"):
            refs = entry.get("refs") or []
            logged.update([refs] if isinstance(refs, str) else refs)  # v0 PowerShell logs stored one ref as a string
            logged.update(re.findall(r"\bD-\d{2,3}\b", entry.get("summary") or ""))
    decisions = []
    for table in feature.tables("_status.md") if "_status.md" in feature.docs else []:
        if table["section"].startswith("Decision log"):
            decisions += [cell(r, 0) for r in table["rows"] if re.match(r"^D-\d{2,3}$", cell(r, 0))]
    missing = [d for d in decisions if d not in logged]
    if missing:
        problems.append(f"{len(missing)} decisions in _status.md not in the audit log: {short(missing, 8)} - "
                        f"log them with ba turn")
    changes = pending_changes(root, slug)
    if changes:
        problems.append(f"{len(changes)} file changes not recorded yet ({short([c[1].split('/')[-1] for c in changes], 5)})"
                        f" - run ba turn {slug}")
    return problems


# --------------------------------------------------------------------------- turn: one bookkeeping call per turn

def write_snapshot(root, slug):
    """Rewrite the Questions/Assumptions rows of _status.md → Open items snapshot (and Last updated) from the
    register, so the numbers are never typed by hand. Returns True if the file changed."""
    folder = requirements_dir(root) / slug
    status = folder / "_status.md"
    if not status.is_file():
        return False
    feature = Feature(folder)
    _, questions, assumptions, _ = register(feature)
    open_q = [q for q in questions if q["status"] == "Open"]
    blocking = [q["id"] for q in open_q if q["priority"] == "Blocking"]
    critical = [q["id"] for q in open_q if q["priority"] == "Decision-critical"]
    open_a = [a for a in assumptions if a["status"] == "Open"]
    by_risk = {r: [a["id"] for a in open_a if a["risk"] == r] for r in ("High", "Medium", "Low")}
    q_line = (f"| Questions `Q-` | {len(open_q)} open of {len(questions)} | "
              f"{len(blocking)} Blocking{': ' + ', '.join(blocking) if blocking else ''}; "
              f"{len(critical)} Decision-critical{': ' + ', '.join(critical) if critical else ''} |")
    a_line = (f"| Assumptions `A-` | {len(open_a)} open of {len(assumptions)}: {len(by_risk['High'])} High, "
              f"{len(by_risk['Medium'])} Medium, {len(by_risk['Low'])} Low | "
              f"{'High: ' + ', '.join(by_risk['High']) if by_risk['High'] else 'none'} |")
    text = status.read_text(encoding="utf-8")
    new = re.sub(SNAPSHOT_Q.pattern + r".*$", lambda _: q_line, text, count=1, flags=re.M)
    new = re.sub(r"^\|\s*Assumptions\b.*$", lambda _: a_line, new, count=1, flags=re.M)
    new = re.sub(r"^(\|\s*Last updated\s*\|\s*)[^|]*(\|)", lambda m: m.group(1) + datetime.date.today().isoformat() + " " + m.group(2),
                 new, count=1, flags=re.M)
    if new != text:
        write_lf(status, new)
        return True
    return False


def cmd_turn(root, args):
    folder = requirements_dir(root) / args.feature
    if not folder.is_dir():
        print(f"error: no folder {folder}", file=sys.stderr)
        return 1
    events = []
    try:
        if args.events:
            text = (sys.stdin.buffer.read().decode("utf-8-sig") if args.events == "-"  # not the console's code page
                    else Path(args.events).read_text(encoding="utf-8-sig"))
            items = json.loads(text) if text.strip() else []
            items = items if isinstance(items, list) else [items]
            events = [prepare_event(root, item, args.feature) for item in items]  # validate all before writing
    except (ValueError, json.JSONDecodeError, OSError) as error:
        print(f"error: {error} - nothing logged", file=sys.stderr)
        return 1
    out = []
    groups = {}
    for path, fields in events:
        groups.setdefault(path, []).append(fields)
    written = [e for path, fields in groups.items() for e in append_events(path, fields)]
    if written:
        out.append(f"logged {len(written)} events (#{written[0]['seq']}-#{written[-1]['seq']}): "
                   + ", ".join(e["type"] for e in written))
    else:
        out.append("logged 0 events")
    out.append("snapshot updated" if write_snapshot(root, args.feature) else "snapshot unchanged")
    changes = pending_changes(root, args.feature)
    record_changes(root, args.feature, changes)
    out.append(f"files: {change_summary(changes)}" if changes else "files: nothing changed")
    code = 0
    if args.gate:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = run_checks(root, args.feature, [])
        result = buffer.getvalue()
        fails, warns = result.count("\nFAIL") + result.startswith("FAIL"), result.count("\nWARN") + result.startswith("WARN")
        append_events(audit_log_path(root, args.feature), [{
            "source": "skill", "type": "check.run", "actor": actor_default(), "session": session_default(),
            "feature": args.feature, "stage": args.stage, "summary": f"ba check: {fails} FAIL, {warns} WARN"}])
        record_changes(root, args.feature, pending_changes(root, args.feature))
        out.append(f"checks: {fails} FAIL, {warns} WARN")
        print("\n".join(out))
        print(result.rstrip())
        return code
    print("\n".join(out))
    return code


# --------------------------------------------------------------------------- context: only what a stage needs

STAGE_SECTIONS = {"ba-intake": [1], "ba-elicit": [3], "ba-scope": [2], "ba-model": [4], "ba-stories": [5],
                  "ba-ux": [6], "ba-spec": [7, 8], "ba-review": [10], "ba-handoff": [9], "ba-step": [11],
                  "ba-refine": [5], "ba-uat": [10], "ba-release": [9]}
DRAFTING_STAGES = ("ba-model", "ba-stories", "ba-ux", "ba-spec")  # get the open questions' text in ba context


def one_line_text(text, limit):
    text = " ".join((text or "").split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


STAGE_LABELS = {"ba-intake": "1 Intake", "ba-elicit": "2 Elicit", "ba-scope": "3 Scope", "ba-model": "4 Model",
                "ba-stories": "5 Stories", "ba-ux": "6 UI/UX", "ba-spec": "7 Spec", "ba-review": "8 Review",
                "ba-handoff": "9 Handoff", "ba-refine": "10 Refine", "ba-uat": "11 Test/UAT", "ba-release": "12 Release"}


def core_dir():
    return TOOLS_DIR.parent / "core"


def resolve(root, rel):
    """.ba/local/<rel> if the project overrides it, otherwise the core file."""
    local = root / ".ba" / "local" / rel
    return local if local.is_file() else core_dir() / rel


def profile_sections(path):
    sections, current, buf = {}, None, []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^##\s+(\d+)\.\s+(.*)", line)
        if m:
            if current:
                sections[current[0]] = (current[1], "\n".join(buf).strip())
            current, buf = (int(m.group(1)), m.group(2)), []
        elif current:
            buf.append(line)
    if current:
        sections[current[0]] = (current[1], "\n".join(buf).strip())
    return sections


def section_text(lines, title):
    out, inside = [], False
    for line in lines:
        if line.startswith("## "):
            if inside:
                break
            inside = line[3:].startswith(title)
            continue
        if inside:
            out.append(line)
    return "\n".join(out).strip()


def cmd_context(root, args):
    stage = args.stage if args.stage.startswith("ba-") else "ba-" + args.stage
    if stage not in STAGE_SECTIONS and stage not in ("ba-start", "ba-next", "ba-change", "ba-audit", "ba-profile",
                                                     "ba-docs", "ba-discover"):
        print(f"error: unknown stage '{args.stage}' - one of {', '.join(STAGE_SECTIONS)}", file=sys.stderr)
        return 2
    folder = requirements_dir(root) / args.feature
    status_path = folder / "_status.md"
    out = [f"# Context for {stage} · {args.feature}  (from ba context — read this instead of the full files)",
           f"Workflow files: {core_dir().as_posix()}/ (manual, stages, templates, checklists, profiles, reference; "
           f".ba/local/<path> overrides) · command: {ba_command(TOOLS_DIR / 'ba.py') if not (root / '.ba' / 'tools' / 'ba.py').is_file() else 'python .ba/tools/ba.py'}"]
    if not status_path.is_file():
        out.append("_status.md missing - create it from templates/_status.md (MANUAL §8 step 0).")
        print("\n".join(out))
        return 0
    st = status_path.read_text(encoding="utf-8").splitlines()
    fields = {}
    for line in st:
        m = re.match(r"^\|\s*(Slug|Current stage|Status|Type of work|Product Owner|BA|Builders|Target date / release|Last updated)\s*\|\s*([^|]*)\|", line)
        if m:
            fields[m.group(1)] = plain(m.group(2))
    out.append("## Status\n" + "\n".join(f"- {k}: {v}" for k, v in fields.items() if v))
    prefs = section_text(st, "Preferences")
    if prefs:
        out.append("## Preferences\n" + prefs)
    feature = Feature(folder)
    tables = feature.tables("_status.md")
    gates = next((t for t in tables if t["section"].startswith("Gates")), None)
    if gates:
        out.append("## Gates\n" + "\n".join(f"- {cell(r, 0)}: {cell(r, 2) or '–'}" for r in gates["rows"]
                                             if not cell(r, 0).startswith("<")))
    gov = governance_rows(feature)
    if gov:
        out.append("## Governance\n" + "\n".join(f"- {k}: {v or '(not named)'}" for k, v in gov.items()))
        areas = [k for k in gov if k.lower().startswith("area owner") and "<" not in k]
        if not areas and "small-change" not in active_profiles(feature):
            out.append("No areas named yet: list every area (module, process, integration) in the sources, with its "
                       "owner, in Governance.")
    intake_doc = feature.doc("01-")
    if (intake_doc and not feature.doc("03-") and "small-change" not in active_profiles(feature)
            and not any(l.startswith("## Foundations") for l in feature.docs[intake_doc])):
        out.append("Foundations not checked yet: run ba-intake step 4b before proposing scope or an MVP. Missing success "
                   "metrics or owners become Decision-critical questions, including existing questions about them.")
    log = next((t for t in tables if t["section"].startswith("Decision log")), None)
    if log:
        rev = col(log, "Revisit at")
        triggers = [r for r in log["rows"] if rev >= 0 and not GOV_PLACEHOLDER.match(cell(r, rev).strip())]
        if triggers:
            out.append("## Revisit triggers\n" + "\n".join(f"- {cell(r, 0)}: {cell(r, 1)[:120]} → revisit at "
                                                          f"{cell(r, rev)}" for r in triggers))
    qdoc, questions, assumptions, _ = register(feature)
    if qdoc:
        open_q = [q for q in questions if q["status"] == "Open"]
        pri = {p: [q["id"] for q in open_q if q["priority"] == p] for p in PRIORITIES}
        open_a = [a for a in assumptions if a["status"] == "Open"]
        out.append("## Open items (from the register)\n"
                   + "\n".join(f"- {p}: {len(v)} {('(' + ', '.join(v[:15]) + ')') if v and p in ('Blocking', 'Decision-critical') else ''}"
                               for p, v in pri.items())
                   + f"\n- Assumptions open: {len(open_a)} (High: {', '.join(a['id'] for a in open_a if a['risk'] == 'High') or 'none'})")
        if stage in DRAFTING_STAGES:
            asked = [r for r in question_rows(feature) if not r["priority"].startswith("Nice to know")]
            if asked:
                out.append("## Open questions (not settled - don't write them as facts; cite the Q- or an A-)\n"
                           + "\n".join(f"- {r['id']} [{r['priority'].split(' ')[0]}] {one_line_text(r['question'], 110)}"
                                       for r in asked))
    label = STAGE_LABELS.get(stage)
    mode = preference(root, args.feature, "Mode", "standard")
    lang = preference(root, args.feature, "Language", "en")
    gates_h = sorted(human_gates(root, args.feature))
    out.append(f"## Mode and authority\n- Mode: {mode} · Language: {lang} (write prose in it; IDs, headings, column "
               f"names, canonical values and Gherkin keywords stay English)\n- Human gates in this mode: "
               f"{', '.join(map(str, gates_h))}" + (f" - **this stage's gate ({label}) is closed by the approver, not by "
                                                     f"you**: prepare the evidence, ask, log gate.passed with actor = "
                                                     f"approver and refs = the D-/SRC-" if label and stage_number(label)
                                                     in gates_h else ""))
    if stage in ("ba-start", "ba-intake", "ba-elicit", "ba-model", "ba-spec", "ba-discover", "ba-docs"):
        kb = knowledge_summary(root)
        if kb:
            out.append("## System knowledge bases (cite verified pages as sources; see /ba-discover)\n" + "\n".join(kb))
    if stage in ("ba-handoff", "ba-refine", "ba-uat", "ba-release", "ba-docs"):
        level, detail = rtm_problems(feature)
        out.append(f"## RTM\n- {level}: {detail}\n- Refresh with `ba rtm {args.feature}` after stories or the QA pack change.")
    if label:
        impact = resolve(root, "checklists/stage-skip-impact.md")
        if impact.is_file():
            rows = [l for l in impact.read_text(encoding="utf-8").splitlines() if re.match(r"^\|\s*" + re.escape(label) + r"\b", l)]
            head = next((l for l in impact.read_text(encoding="utf-8").splitlines() if l.startswith("| Stage |")), "")
            if rows:
                out.append("## Skip impact (for the stage card)\n" + head + "\n" + "\n".join(rows))
    approach = next((t for t in tables if t["section"].startswith("Approach") and col(t, "Profile") >= 0), None)
    active = []
    if approach:
        for r in approach["rows"]:
            m = re.match(r"^\|\s*`([a-z0-9.-]+)`", lines_raw(st, r))
            name = m.group(1) if m else ""
            if name and not name.startswith("e.g"):
                active.append((name, cell(r, col(approach, "Role"))))
    wanted = STAGE_SECTIONS.get(stage, [])
    if stage == "ba-intake":
        names = sorted({p.stem for base in (core_dir() / "profiles", root / ".ba" / "local" / "profiles") if base.is_dir()
                        for p in base.glob("*.md") if p.stem not in ("README", "_template", "catalogue")})
        out.append("## Candidate profiles - Signals (§1)")
        for name in names:
            path = resolve(root, f"profiles/{name}.md")
            text = path.read_text(encoding="utf-8")
            if re.search(r"^status:\s*(retired|draft)", text, re.M):
                continue
            sig = profile_sections(path).get(1, ("", ""))[1]
            out.append(f"- **{name}**: {' '.join(sig.split())[:400]}")
        overview = section_text(resolve(root, "profiles/catalogue.md").read_text(encoding="utf-8").splitlines(), "Overview")
        if overview:
            out.append("## Catalogue (install with /ba-profile install)\n" + overview)
    elif wanted and active:
        for name, role in active:
            path = resolve(root, f"profiles/{name}.md")
            if not path.is_file():
                out.append(f"## Profile {name} ({role}) - file not found in profiles/")
                continue
            secs = profile_sections(path)
            for number in wanted:
                title, body = secs.get(number, ("", ""))
                if body:
                    out.append(f"## Profile {name} ({role}) §{number} {title}\n{body}")
            plan = secs.get(2, ("", ""))[1]
            short_stage = label.split(" ", 1)[1] if label else ""
            row = next((l for l in plan.splitlines() if short_stage and l.lower().startswith(f"| {short_stage.lower()}")), "")
            if row and 2 not in wanted:
                out.append(f"Stage plan ({name}): {row}")
    print("\n\n".join(out))
    return 0


def lines_raw(st, row):
    """Raw text of a parsed table row (to see backticks that plain() removed)."""
    return st[row["no"] - 1] if 0 < row["no"] <= len(st) else ""


# --------------------------------------------------------------------------- answers: a file the BA fills in

def question_rows(feature, only_open=True):
    """[{id, question, why, options, priority, ask, status}] from the Question log of 02-questions.md."""
    qdoc = feature.doc("02-questions")
    rows = []
    if not qdoc:
        return rows
    for table in feature.tables(qdoc):
        k = {h: i for i, h in enumerate(table["header"])}
        if "ID" not in k or "Question" not in k:
            continue
        opt = next((i for h, i in k.items() if h.startswith("Options")), -1)
        for r in table["rows"]:
            ident = cell(r, k["ID"])
            if not re.match(r"^Q-\d{2,3}$", ident):
                continue
            status = (re.match(r"^[A-Za-z]+", cell(r, k.get("Status", -1))) or [""])[0]
            if only_open and status != "Open":
                continue
            rows.append({"id": ident, "question": cell(r, k["Question"]), "why": cell(r, k.get("Why it matters", -1)),
                         "options": cell(r, opt), "priority": cell(r, k.get("Priority", -1)),
                         "ask": cell(r, k.get("Ask", -1)), "status": status})
    return rows


def split_options(text):
    parts = re.split(r"(?:^|(?<=\s))\(([a-z])\)\s*", text or "")  # a marker starts a word: not "approver(s)"
    if len(parts) == 1:  # free text, no markers: keep it as the one suggestion
        body = parts[0].strip(" —–-;,")
        return [("a", body.replace("★", "").strip(), "★" in body)] if body else []
    options = []
    for i in range(1, len(parts) - 1, 2):
        body = parts[i + 1].strip(" —–-;,")
        options.append((parts[i], body.replace("★", "").strip(), "★" in body))
    return options


def next_round(folder):
    """Next answer-form number: after any open form in answers/ and any form already filed in sources/."""
    stems = [p.stem for d in ("answers", "sources") for p in (folder / d).glob("*.md")]
    numbers = [int(m.group(1)) for s in stems if (m := re.search(r"(?:^|answers-)round-(\d+)", s))]
    return max(numbers, default=0) + 1


def questions_per_message(folder, default=5):
    """_status.md → Preferences → Questions per message (walkthrough batch size)."""
    status = folder / "_status.md"
    text = status.read_text(encoding="utf-8-sig") if status.is_file() else ""
    m = re.search(r"^\|\s*Questions per message\s*\|\s*(\d+)", text, re.M)
    return int(m.group(1)) if m and int(m.group(1)) > 0 else default


def print_round_for_chat(rows, level, per_message):
    """The round for walkthrough mode, numbered in the order to ask it: priority first, then who answers."""
    print(f"Round: {len(rows)} questions, numbered in the order to ask them; {per_message} per message, each headed "
          f"\"Questions a–b of {len(rows)}\". ★ = recommended.")
    for n, r in enumerate(sorted(rows, key=lambda r: (PRIORITIES.index(level(r)) if level(r) else 9, r["ask"], r["id"])), 1):
        print(f"{n}. **{r['id']}** [{level(r) or r['priority']}] (for {r['ask'] or '—'}) {r['question']}")
        options = split_options(r["options"])
        if options:
            print("   " + " · ".join(f"({l}){' ★' if rec else ''} {body}" for l, body, rec in options))


def cmd_answers_new(root, args):
    folder = requirements_dir(root) / args.feature
    if not folder.is_dir():
        print(f"error: no folder {folder}", file=sys.stderr)
        return 1
    rows = question_rows(Feature(folder))
    if args.ids:
        wanted = {i.strip() for i in args.ids.split(",")}
        rows = [r for r in rows if r["id"] in wanted]
    if args.who:
        rows = [r for r in rows if args.who.lower() in r["ask"].lower()]
    order = {p: i for i, p in enumerate(PRIORITIES)}
    level = lambda r: next((p for p in PRIORITIES if (r["priority"] or "").startswith(p)), "")  # noqa: E731
    if not (args.all or args.ids):
        rows = [r for r in rows if level(r) != "Nice to know"]  # parked for a later round
    rows.sort(key=lambda r: (order.get(level(r), 9), r["id"]))
    if not rows:
        print("no open questions match - nothing to ask")
        return 0
    out_already = {}
    for form in sorted((folder / "answers").glob("round-*.md")):
        asked = set(re.findall(r"^### (Q-\d+)", form.read_text(encoding="utf-8-sig"), re.M))
        overlap = sorted(asked & {r["id"] for r in rows})
        if overlap:
            out_already[form.name] = overlap
    for name, ids in out_already.items():  # a note, not a block: one question can go to two people
        print(f"note: already out in {name} (not read yet): {short(ids)}")
    if args.chat:
        print_round_for_chat(rows, level, questions_per_message(folder))
        return 0
    number = next_round(folder)
    path = folder / "answers" / f"round-{number:02d}.md"
    today = datetime.date.today().isoformat()
    lines = [f"# Answers — {args.feature} — round {number:02d}", "",
             f"*Generated by `ba answers new` on {today} for {len(rows)} open questions"
             + (f" (for {args.who})" if args.who else "") + ".*", "",
             "**How to answer:** for each question tick one option (`[x]`) or write your own answer under it, and note "
             "who answered if it wasn't you. Leave a question untouched to skip it. Save the file, then tell the "
             "assistant **\"done\"**.", "",
             "Answered by (default for every question): ", f"Date: {today}", "Source (meeting, email…): ", "", "---"]
    for r in rows:
        lines += ["", f"### {r['id']} · {r['priority']} · ask: {r['ask'] or '—'}", "", r["question"]]
        if r["why"]:
            lines += ["", f"*Why it matters:* {r['why']}"]
        lines.append("")
        for letter, body, recommended in split_options(r["options"]):
            lines.append(f"- [ ] ({letter}) {body}" + ("  ← recommended" if recommended else ""))
        lines += [f"- [ ] {OTHER_OPTION}", "", "Answer / notes: ", "Answered by: "]
    path.parent.mkdir(parents=True, exist_ok=True)
    write_lf(path, "\n".join(lines) + "\n")
    print(f"wrote {path.relative_to(root).as_posix()} - {len(rows)} questions; the BA fills it in and says \"done\"")
    return 0


def parse_answers(text):
    default_by = (re.search(r"^Answered by \(default[^)]*\):[ \t]*(.*)$", text, re.M) or [None, ""])[1].strip()
    date = (re.search(r"^Date:[ \t]*(.*)$", text, re.M) or [None, ""])[1].strip()
    source = (re.search(r"^Source[^:]*:[ \t]*(.*)$", text, re.M) or [None, ""])[1].strip()
    answers, skipped = [], []
    for block in re.split(r"^### ", text, flags=re.M)[1:]:
        ident = block.split()[0]
        ticked = [(m.group(1) or "other", m.group(2).replace("← recommended", "").replace(OTHER_OPTION, "").strip())
                  for m in re.finditer(r"^- \[[xX]\]\s*(?:\(([a-z])\)\s*)?(.*)$", block, re.M)]
        notes_m = re.search(r"^Answer / notes:[ \t]*(.*?)(?=^Answered by:|\Z)", block, re.M | re.S)
        # The form says "write below", so an answer may sit under an option instead of on the notes line.
        options = re.search(r"^- \[.*?(?=^Answer / notes:|\Z)", block, re.M | re.S)
        under = [l for l in (options.group(0) if options else "").splitlines() if not l.startswith("- [")]
        notes = " ".join(" ".join(under + [notes_m.group(1) if notes_m else ""]).split())
        by = (re.search(r"^Answered by:[ \t]*(.*)$", block, re.M) or [None, ""])[1].strip() or default_by
        if ticked or notes:
            answers.append({"id": ident, "chosen": ticked, "notes": notes, "by": by})
        else:
            skipped.append(ident)
    return {"date": date, "source": source, "answers": answers, "skipped": skipped}


def cmd_answers_read(root, args):
    folder = requirements_dir(root) / args.feature
    if args.file:
        path = Path(args.file)
        forms = [path if path.is_absolute() or path.is_file() else folder / path]
    else:  # every form in answers/: one per person is normal
        forms = sorted((folder / "answers").glob("round-*.md"))
        if not forms:
            print("error: no answer file in answers/ - give its path", file=sys.stderr)
            return 1
    for path in forms:
        read_answer_form(root, folder, path, args.keep)
    return 0


def read_answer_form(root, folder, path, keep):
    result = parse_answers(path.read_text(encoding="utf-8"))
    if not result["answers"]:  # still blank: it stays in answers/ for whoever has to fill it in
        print(f"# {path.name}: no answers yet - left in place")
        return
    print(f"# Answers from {path.name} · date {result['date'] or '—'} · source {result['source'] or '—'}")
    for a in result["answers"]:
        chosen = "; ".join(f"({c}) {t}" if c != "other" else (f"other: {t}" if t else "other") for c, t in a["chosen"]) or "—"
        print(f"- {a['id']}: {chosen}" + (f" | notes: {a['notes']}" if a["notes"] else "") + f" | by: {a['by'] or '—'}")
    if result["skipped"]:
        print(f"skipped (no answer): {', '.join(result['skipped'])}")
    if keep:
        return
    sources = folder / "sources"
    numbers = [int(m.group(1)) for p in sources.glob("SRC-*") if (m := re.match(r"SRC-(\d+)", p.name))]
    for intake in folder.glob("01-*.md"):  # a source may be registered with no file of its own; IDs are never reused
        numbers += [int(n) for n in re.findall(r"\bSRC-(\d+)", intake.read_text(encoding="utf-8-sig"))]
    src = f"SRC-{max(numbers, default=0) + 1:02d}"
    dest = sources / f"{src}-answers-{path.stem}.md"
    sources.mkdir(exist_ok=True)
    path.replace(dest)
    print(f"moved to {dest.relative_to(root).as_posix()} as {src} - register it in 01-intake.md and record the "
          f"decisions (MANUAL §5)")


# --------------------------------------------------------------------------- questions: keep the working register small

def cmd_questions_archive(root, args):
    folder = requirements_dir(root) / args.feature
    main = next(iter(sorted(folder.glob("02-questions*.md"))), None)
    if main is None:
        print("error: no 02-questions.md", file=sys.stderr)
        return 1
    closed_path = folder / CLOSED_DOC
    lines = main.read_text(encoding="utf-8").split("\n")
    before = len("\n".join(lines).encode())
    moved, keep, i = {}, [], 0
    while i < len(lines):
        line = lines[i]
        is_header = (line.lstrip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1])
                     and (i == 0 or not lines[i - 1].lstrip().startswith("|")))
        if not is_header:
            keep.append(line)
            i += 1
            continue
        header = [plain(c) for c in split_row(line)]
        id_col = header.index("ID") if "ID" in header else -1
        stat = next((k for k, h in enumerate(header) if h.startswith("Status")), -1)
        keep += [line, lines[i + 1]]
        j = i + 2
        while j < len(lines) and lines[j].lstrip().startswith("|"):
            cells = [plain(c) for c in split_row(lines[j])]
            ident = cells[id_col] if 0 <= id_col < len(cells) else ""
            word = (re.match(r"^[A-Za-z]+", cells[stat] if 0 <= stat < len(cells) else "") or [""])[0]
            closed = (ident.startswith("Q-") and word in ("Answered", "Withdrawn", "Closed")) or \
                     (ident.startswith("A-") and word in ("Confirmed", "Rejected", "Withdrawn"))
            if id_col >= 0 and stat >= 0 and closed:
                moved.setdefault((line, lines[i + 1]), []).append(lines[j])
            else:
                keep.append(lines[j])
            j += 1
        i = j
    if not moved:
        print("nothing to archive - no answered/withdrawn questions or settled assumptions")
        return 0
    archive = closed_path.read_text(encoding="utf-8").split("\n") if closed_path.is_file() else \
        [f"# 02 · Closed questions and settled assumptions — {args.feature}", "",
         "Moved here by `ba questions archive`; IDs stay valid. The working register is `02-questions.md`.", ""]
    for (head, sep), rows in moved.items():
        if head in archive:
            k = archive.index(head) + 2
            while k < len(archive) and archive[k].lstrip().startswith("|"):
                k += 1
            archive[k:k] = rows
        else:
            title = "Closed questions" if "Question" in head else "Settled assumptions"
            archive += [f"## {title}", head, sep] + rows + [""]
    write_lf(closed_path, "\n".join(archive).rstrip("\n") + "\n")
    write_lf(main, "\n".join(keep))
    after = len("\n".join(keep).encode())
    count = sum(len(r) for r in moved.values())
    print(f"archived {count} rows to {CLOSED_DOC}; {main.name}: {before / 1024:.1f} KB -> {after / 1024:.1f} KB")
    return 0


# --------------------------------------------------------------------------- rtm: the live traceability matrix

RTM_DOC = "rtm.md"
RTM_HEADER = ["AC", "Story", "Goal", "Rules", "Test", "Test result", "UAT result", "Evidence", "Recorded by",
              "Version", "Link", "AC hash", "Coverage", "Notes"]
TEST_RESULTS = ("Not run", "Pass", "Fail", "Blocked", "N/A")
UAT_RESULTS = ("Not run", "Pass", "Fail", "Blocked", "Out of scope")
LINKS = ("Confirmed", "Inferred", "")
COVERAGE_ORDER = ("Covered", "Pending", "Missing link", "Inferred link", "Stale link", "Failed", "Blocked", "Orphan",
                  "Withdrawn", "Superseded")


def story_acceptance(feature):
    """[{ac, story, goals, rules, hash}] in story order, from the Gherkin blocks of 05-stories.md."""
    doc = feature.doc("05-")
    if not doc:
        return []
    acs, story, current, meta = [], None, None, {}

    def close():
        if current:
            body = " ".join(" ".join(current["lines"]).split())
            current["hash"] = hashlib.sha256(body.encode("utf-8")).hexdigest()[:8]
            acs.append(current)
    lines = feature.docs[doc]
    for text in lines:
        m = re.match(r"^##\s+(US-\d{2,3})", text)
        if m:
            close()
            current, story = None, m.group(1)
            continue
        m = re.match(r"^\s*#\s+(AC-\d{2,3}\.\d+[a-z]?)", text)
        if m and story:
            close()
            current = {"ac": m.group(1), "story": story, "lines": [text]}
            continue
        if re.match(r"^\s*```", text) or re.match(r"^#{1,3}\s", text):
            close()
            current = None
            continue
        if current is not None:
            current["lines"].append(text)
        row = re.match(r"^\|\s*(Traces to|Business rules)\s*\|(.*)\|\s*$", text)
        if row and story:
            meta.setdefault(story, {})[row.group(1)] = row.group(2)
    close()
    for item in acs:
        info = meta.get(item["story"], {})
        item["goals"] = ", ".join(dict.fromkeys(re.findall(r"\bG-\d{2,3}\b", info.get("Traces to", ""))))
        item["rules"] = ", ".join(dict.fromkeys(re.findall(r"\b(?:BR|NFR)-\d{2,3}\b", info.get("Business rules", ""))))
        del item["lines"]
    return acs


def tests_by_ac(feature):
    """({AC: [TS-…]}, [malformed test IDs], qa_pack_present) from rows of handoff/qa-pack.md whose first cell is a test
    ID (explicit links only)."""
    links, bad, present = {}, [], False
    for name, lines in feature.docs.items():
        if not name.endswith("qa-pack.md"):
            continue
        present = True
        for text in lines:
            cells = split_row(text) if text.lstrip().startswith("|") else []
            first = plain(cells[0]) if cells else ""
            if re.match(r"^TS-\d{2,3}$", first):
                for ac in re.findall(r"\bAC-\d{2,3}\.\d+[a-z]?\b", " ".join(cells[1:])):
                    links.setdefault(ac, [])
                    if first not in links[ac]:
                        links[ac].append(first)
            elif re.match(r"^TS-?\w+$", first, re.I) and first not in ("TS-ID",):
                bad.append(first)
    return links, bad, present


def status_field(feature, name):
    for line in feature.docs.get("_status.md", []):
        m = re.match(r"^\|\s*" + re.escape(name) + r"\s*\|\s*([^|]*)\|", line)
        if m:
            return plain(m.group(1))
    return ""


def rtm_rows(feature):
    """Rows of rtm.md (the matrix table) as dicts keyed by RTM_HEADER (missing columns = '')."""
    if RTM_DOC not in feature.docs:
        return None
    for table in feature.tables(RTM_DOC):
        if col(table, "AC") >= 0 and col(table, "Coverage") >= 0:
            idx = {h: col(table, h) for h in RTM_HEADER}
            return [dict({h: cell(r, k) if k >= 0 else "" for h, k in idx.items()}, _line=r["no"]) for r in table["rows"]]
    return []


RESULT_LOG_HEADER = ["Logged", "AC", "Test", "Version", "Test result", "UAT result", "Evidence", "Recorded by"]


def result_log(feature):
    """Rows of rtm.md → Result log: every result ever recorded (appended by ba rtm, never rewritten)."""
    if RTM_DOC not in feature.docs:
        return []
    for table in feature.tables(RTM_DOC):
        if table["section"].startswith("Result log") and col(table, "Logged") >= 0:
            idx = {h: col(table, h) for h in RESULT_LOG_HEADER}
            return [{h: cell(r, k) if k >= 0 else "" for h, k in idx.items()} for r in table["rows"]]
    return []


def withdrawn_ids(feature):
    return {i for _, _, t, _ in feature.lines(include_code=True) for i in re.findall(r"~~(" + ID_CORE + ")~~", t)}


def renamed_ids(feature):
    """{old AC: new AC} from '~~AC-002.6~~ → AC-002.9' (or ->) anywhere in the feature."""
    return {m.group(1): m.group(2) for _, _, t, _ in feature.lines(include_code=True)
            for m in re.finditer(r"~~(AC-\d{2,3}\.\d+[a-z]?)~~\s*(?:→|->)\s*(AC-\d{2,3}\.\d+[a-z]?)", t)}


EVIDENCE_OK = re.compile(
    r"https?://\S+"                                                       # a link
    r"|\bSRC-\d{2,3}\b"                                                   # a registered source
    r"|[\w.-]+\.(?:png|jpe?g|gif|pdf|log|txt|csv|xlsx?|docx?|html?|json|xml|zip|mp4|webm|har)\b"  # a file
    r"|\b[A-Z][A-Z0-9]{1,9}-\d+\b"                                          # a ticket / run ID: QA-123, RUN-4521
    r"|(?i:\b(?:run|build|job|ticket|test ?run|pipeline|bug)\s*#?\s*\d{2,}\b)"  # run 4521, build #88
    r"|(?<![\w/])#\d{3,}\b")                                                 # #4521
NOT_EVIDENCE = re.compile(r"(?i)^\s*(n/?a|none|nil|ok|done|yes|x|-|–|see (above|below)|passed?|tested.*)\s*$")


def evidence_ok(text):
    """A link, a SRC-, a file, or a run/ticket ID - not 'x', 'ok', 'n/a', 'see above', 'tested 2026'."""
    text = text or ""
    return not NOT_EVIDENCE.match(text) and bool(EVIDENCE_OK.search(text))


def coverage(row, active, withdrawn, links=None, qa_pack=False):
    test, uat = row["Test result"] or "Not run", row["UAT result"] or "Not run"
    if row["Notes"].startswith("Superseded"):
        return "Superseded"
    if row["AC"] in withdrawn:
        return "Withdrawn"
    if row["AC"] not in active:
        return "Orphan"
    if not re.search(r"\bTS-\d", row["Test"]):
        return "Missing link"
    if qa_pack and links is not None and row["Link"] == "Confirmed" and row["Test"] not in links.get(row["AC"], []):
        return "Stale link"
    if row["Link"] != "Confirmed":
        return "Inferred link"
    if "Fail" in (test, uat):
        return "Failed"
    if "Blocked" in (test, uat):
        return "Blocked"
    proven = evidence_ok(row["Evidence"]) and row["Recorded by"] and not is_ai_name(row["Recorded by"])
    if test in ("Pass", "N/A") and uat in ("Pass", "Out of scope") and proven:
        return "Covered"
    return "Pending"


def rtm_render(feature, rows, slug, log_rows):
    counts = {c: sum(1 for r in rows if r["Coverage"] == c) for c in COVERAGE_ORDER}
    live = [r for r in rows if r["Coverage"] not in ("Superseded", "Withdrawn")]
    out = [f"# RTM — {slug}", "",
           "Live requirements traceability matrix, one row per acceptance criterion **and test**. **`ba rtm` builds and "
           "refreshes it**: AC, story, goal, rules, tests (from `handoff/qa-pack.md`), version, AC hash and Coverage "
           "are written by the tool. People fill in *Test result*, *UAT result*, *Evidence* (a link, a run or ticket "
           "ID, a file or a `SRC-`) and *Recorded by* (the person) — only from a real run, never a guess. Every "
           "recorded result is copied to the *Result log* below, so a result that is later changed stays on record. "
           "When an AC changes after it was tested, its rows are superseded and new rows ask for a retest. Rows are "
           "never deleted.", "",
           f"**Summary:** {len(live)} live rows · " + " · ".join(f"{c} {n}" for c, n in counts.items() if n), "",
           "| " + " | ".join(RTM_HEADER) + " |", "|" + "|".join("---" for _ in RTM_HEADER) + "|"]
    for r in rows:
        out.append("| " + " | ".join(r[h].replace("|", "/") for h in RTM_HEADER) + " |")
    out += ["", "## Values", "| Column | Allowed |", "|---|---|",
            "| Test result | " + " · ".join(TEST_RESULTS) + " |",
            "| UAT result | " + " · ".join(UAT_RESULTS) + " |",
            "| Link | Confirmed (the test explicitly covers the AC) · Inferred (a guess; never counts as covered) |",
            "| Coverage (tool) | " + " · ".join(COVERAGE_ORDER) + " |", "",
            "## Result log", "Appended by `ba rtm` whenever a result changes. Never edit.", "",
            "| " + " | ".join(RESULT_LOG_HEADER) + " |", "|" + "|".join("---" for _ in RESULT_LOG_HEADER) + "|"]
    for r in log_rows:
        out.append("| " + " | ".join(r[h].replace("|", "/") for h in RESULT_LOG_HEADER) + " |")
    return "\n".join(out) + "\n"


def blank_row(a, version, test=""):
    return {"AC": a["ac"], "Story": a["story"], "Goal": a["goals"], "Rules": a["rules"], "Test": test,
            "Test result": "Not run", "UAT result": "Not run", "Evidence": "", "Recorded by": "", "Version": version,
            "Link": "Confirmed" if test else "", "AC hash": a["hash"], "Coverage": "", "Notes": ""}


def cmd_rtm(root, args):
    folder = requirements_dir(root) / args.feature
    if not folder.is_dir():
        print(f"error: no folder {folder}", file=sys.stderr)
        return 1
    feature = Feature(folder)
    acs = story_acceptance(feature)
    if not acs:
        print("error: no acceptance criteria in 05-stories.md yet - the RTM starts from the stories", file=sys.stderr)
        return 1
    links, bad_ids, qa_pack = tests_by_ac(feature)
    version = status_field(feature, "Version") or "v0.1"
    rows = rtm_rows(feature) or []
    for r in rows:
        r.pop("_line", None)
    split = 0
    for r in list(rows):  # older RTMs kept several tests in one row: one row per test now
        tests = [t for t in re.split(r"\s*,\s*", r["Test"]) if t]
        if len(tests) > 1:
            at = rows.index(r)
            first = dict(r, Test=tests[0], Notes=(r["Notes"] + "; " if r["Notes"] else "")
                         + "split from a combined row: confirm this result belongs to this test")
            others = [dict(r, Test=t, **{"Test result": "Not run", "UAT result": "Not run", "Evidence": "",
                                         "Recorded by": "", "Notes": "split from a combined row (older format): record its own result"})
                      for t in tests[1:]]
            rows[at:at + 1] = [first] + others
            split += 1
    active = {a["ac"] for a in acs}
    live = lambda ac: [r for r in rows if r["AC"] == ac and not r["Notes"].startswith("Superseded")]  # noqa: E731
    renamed = renamed_ids(feature)
    added = superseded = carried = 0
    for a in acs:
        if not live(a["ac"]):
            old = next((o for o, n in renamed.items() if n == a["ac"]), None)
            for prev in live(old) if old else []:  # a renamed AC keeps its tests; results must be re-recorded
                rows.append(dict(blank_row(a, version, prev["Test"]), Link=prev["Link"],
                                 Notes=f"renamed from {old}: record the result again"))
                carried += 1
        for t in links.get(a["ac"], []):
            current = live(a["ac"])
            if any(r["Test"] == t for r in current):
                continue
            empty = next((r for r in current if not r["Test"] and (r["Test result"] or "Not run") == "Not run"), None)
            if empty:
                empty.update({"Test": t, "Link": "Confirmed"})
            else:
                rows.append(blank_row(a, version, t))
                added += 1
        if not live(a["ac"]):
            rows.append(blank_row(a, version))
            added += 1
        for row in live(a["ac"]):
            row.update({"Story": a["story"], "Goal": a["goals"], "Rules": a["rules"]})
            if row["AC hash"] == a["hash"]:
                continue
            tested = (row["Test result"] or "Not run") != "Not run" or (row["UAT result"] or "Not run") != "Not run"
            if tested:
                old_version = row["Version"]
                row["Notes"] = f"Superseded by {version}: AC changed after it was tested" + (
                    f"; {row['Notes']}" if row["Notes"] else "")
                rows.insert(rows.index(row) + 1, dict(row, **{
                    "Test result": "Not run", "UAT result": "Not run", "Evidence": "", "Recorded by": "",
                    "Version": version, "AC hash": a["hash"], "Notes": f"AC changed since {old_version}: retest"}))
                superseded += 1
            else:
                row.update({"AC hash": a["hash"], "Version": version})
    withdrawn = withdrawn_ids(feature)
    for r in rows:
        r["Coverage"] = coverage(r, active, withdrawn, links, qa_pack)
    # Result log: append every result that differs from the last one logged for this AC, test and version.
    log_rows = result_log(feature)
    last = {}
    for entry in log_rows:
        last[(entry["AC"], entry["Test"], entry["Version"])] = entry
    new_results = []
    today = datetime.date.today().isoformat()
    for r in rows:
        if (r["Test result"] or "Not run") == "Not run" and (r["UAT result"] or "Not run") == "Not run":
            continue
        key = (r["AC"], r["Test"], r["Version"])
        prev = last.get(key)
        values = {h: r[h] for h in ("Test result", "UAT result", "Evidence", "Recorded by")}
        if prev and all(prev[h] == v for h, v in values.items()):
            continue
        entry = dict({"Logged": today, "AC": r["AC"], "Test": r["Test"], "Version": r["Version"]}, **values)
        log_rows.append(entry)
        last[key] = entry
        new_results.append(entry)
    path = folder / RTM_DOC
    text = rtm_render(feature, rows, args.feature, log_rows)
    changed = not path.is_file() or path.read_text(encoding="utf-8") != text
    if changed:
        write_lf(path, text)
    if new_results:  # one event per result, with the tester as actor (the Result log is checked against these)
        append_events(audit_log_path(root, args.feature), [{
            "source": "rtm", "type": "result.recorded", "actor": e["Recorded by"] or "unknown",
            "reported_by": actor_default(), "via": via_default(), "tool": f"ba-pipeline {version_text()}",
            "feature": args.feature, "stage": "11 Test/UAT", "ac": e["AC"], "test": e["Test"], "version": e["Version"],
            "test_result": e["Test result"], "uat_result": e["UAT result"], "evidence": e["Evidence"],
            "summary": f"{e['AC']} {e['Test'] or '-'} test {e['Test result']} uat {e['UAT result']}"} for e in new_results])
    counts = {c: sum(1 for r in rows if r["Coverage"] == c) for c in COVERAGE_ORDER}
    print(f"rtm: {len(rows)} rows ({added} new, {superseded} superseded by a changed AC"
          + (f", {split} combined rows split" if split else "") + (f", {carried} carried from renamed AC" if carried else "")
          + f", {len(new_results)} results logged); " + ", ".join(f"{c} {n}" for c, n in counts.items() if n)
          + ("" if changed else " - unchanged"))
    if bad_ids:
        print(f"warning: qa-pack test IDs not in the TS-NN form, ignored: {short(sorted(set(bad_ids)), 8)}")
    return 0


def root_of(feature):
    """The project root of a feature folder (the folder whose requirements directory holds it)."""
    for parent in feature.folder.parents:
        try:
            if requirements_dir(parent).resolve() == feature.folder.parent.resolve():
                return parent
        except (OSError, json.JSONDecodeError):
            continue
    return feature.folder.parent.parent


def rtm_problems(feature):
    """(level, detail) for ba check *rtm*."""
    rows = rtm_rows(feature)
    if rows is None:
        if (feature.folder / "handoff").is_dir():
            return "WARN", "no rtm.md - run ba rtm (the handoff and Test/UAT stages work from it)"
        return "PASS", "no RTM yet (built with ba rtm at handoff)"
    fails, warns = [], []
    odd = [f"{r['AC']} {h} '{r[h]}'" for r in rows for h, allowed in
           (("Test result", TEST_RESULTS), ("UAT result", UAT_RESULTS), ("Link", LINKS)) if r[h] not in allowed]
    if odd:
        fails.append(f"non-canonical values: {short(odd, 6)}")
    has_result = lambda r: r["Test result"] not in ("Not run", "") or r["UAT result"] not in ("Not run", "")  # noqa: E731
    unproven = [r["AC"] for r in rows if has_result(r) and not (r["Evidence"] and r["Recorded by"])]
    if unproven:
        fails.append(f"results without Evidence and Recorded by (a result needs a real run): {short(unproven)}")
    by_ai = [f"{r['AC']} ({r['Recorded by']})" for r in rows if has_result(r) and is_ai_name(r["Recorded by"])]
    if by_ai:
        fails.append(f"results recorded by the assistant - only a person who ran the test may record it: {short(by_ai, 6)}")
    weak = [f"{r['AC']} '{r['Evidence']}'" for r in rows if has_result(r) and r["Evidence"] and not evidence_ok(r["Evidence"])]
    if weak:
        fails.append(f"evidence that points nowhere (use a link, a run or ticket ID, a file or a SRC-): {short(weak, 6)}")
    acs = story_acceptance(feature)
    active = {a["ac"] for a in acs}
    withdrawn = withdrawn_ids(feature)
    links, bad_ids, qa_pack = tests_by_ac(feature)
    stale = [r["AC"] for r in rows if r["Coverage"] != coverage(r, active, withdrawn, links, qa_pack)]
    live_acs = {r["AC"] for r in rows if not r["Notes"].startswith("Superseded")}
    live_pairs = {(r["AC"], r["Test"]) for r in rows if not r["Notes"].startswith("Superseded")}
    missing = sorted(active - live_acs)
    missing_tests = sorted(f"{ac} {t}" for ac, ts in links.items() if ac in active for t in ts if (ac, t) not in live_pairs)
    if stale or missing or missing_tests:
        fails.append(f"out of date - run ba rtm ({len(stale)} coverage cells wrong, {len(missing)} AC without a row"
                     + (f": {short(missing, 6)}" if missing else "")
                     + (f", tests not in the RTM: {short(missing_tests, 6)}" if missing_tests else "") + ")")
    logged = [(e.get("ac"), e.get("test") or "", e.get("version"), e.get("test_result"), e.get("uat_result"))
              for e in log_entries(root_of(feature), feature.folder.name) if e["type"] == "result.recorded" and e.get("ac")]
    written = [(r["AC"], r["Test"], r["Version"], r["Test result"], r["UAT result"]) for r in result_log(feature)]
    if logged or written:
        gone = [f"{x[0]} {x[1]} {x[3]}/{x[4]}" for x in logged if x not in written]
        added = [f"{x[0]} {x[1]} {x[3]}/{x[4]}" for x in written if x not in logged]
        if gone or added:
            fails.append("Result log differs from the audit log's result.recorded events (edited by hand?)"
                         + (f"; missing: {short(gone, 4)}" if gone else "") + (f"; not in the audit log: {short(added, 4)}" if added else ""))
    names = " ".join(feature.docs.get("_status.md", []))
    outsiders = sorted({r["Recorded by"] for r in rows if has_result(r) and r["Recorded by"]
                        and not is_ai_name(r["Recorded by"]) and not name_matches(r["Recorded by"], names)})
    if outsiders:
        warns.append(f"recorded by people not in Stakeholders/Governance: {short(outsiders, 6)}")
    if bad_ids:
        warns.append(f"qa-pack test IDs not in the TS-NN form: {short(sorted(set(bad_ids)), 6)}")
    counts = {c: sum(1 for r in rows if r["Coverage"] == c) for c in COVERAGE_ORDER}
    for c in ("Missing link", "Inferred link", "Stale link", "Failed", "Blocked", "Orphan"):
        if counts[c]:
            warns.append(f"{counts[c]} {c}")
    summary = ", ".join(f"{c} {n}" for c, n in counts.items() if n)
    if fails:
        return "FAIL", "; ".join(fails)
    return ("WARN", f"{summary} - gate 11 needs none of: " + ", ".join(warns)) if warns else ("PASS", summary)


# --------------------------------------------------------------------------- kpi: release metrics from the files and the log

def log_entries(root, slug):
    out = []
    for line in read_log(audit_log_path(root, slug)):
        m = LINE_RX.match(line)
        out.append(json.loads(m.group("body") + "}") if m else json.loads(line))
    return out


def review_scores(feature):
    """{category: (score, max)} from the latest 08-review.md Scores table."""
    doc = feature.doc("08-")
    out = {}
    for table in feature.tables(doc) if doc else []:
        c, s, m = col(table, "Category"), col(table, "Score"), col(table, "Max")
        if min(c, s, m) < 0:
            continue
        for r in table["rows"]:
            sc, mx = re.match(r"^\d+", cell(r, s)), re.match(r"^\d+", cell(r, m))
            if sc and mx:
                out[cell(r, c).split("&")[0].strip()] = (int(sc.group(0)), int(mx.group(0)))
    return out


def uat_thresholds(root, slug):
    """Preferences → UAT thresholds, e.g. 'coverage 100 · pass 95' (set by the PO); {} when not set."""
    status = requirements_dir(root) / slug / "_status.md"
    text = status.read_text(encoding="utf-8-sig") if status.is_file() else ""
    m = re.search(r"^\|\s*UAT thresholds\s*\|([^|]*)\|", text, re.M)
    if m and re.match(r"\s*(—|-|–|$)|.*\be\.g\.", m.group(1)):  # not set (the template's hint)
        return {}
    if not m:
        return {}
    text = unicodedata.normalize("NFC", m.group(1)).lower()
    out = {}
    for key, words in (("coverage", r"coverage|độ phủ|do phu|bao phủ"), ("pass", r"pass(?: rate)?|tỉ lệ đạt|tỷ lệ đạt|tỉ lệ pass|tỷ lệ pass|đạt")):
        found = re.search(r"(?:" + words + r")\s*(?:rate)?\s*[:=≥>]*\s*(\d{1,3})", text)
        if found:
            out[key] = int(found.group(1))
    return out


def kpis(root, slug):
    feature = Feature(requirements_dir(root) / slug)
    all_rows = rtm_rows(feature) or []
    rows = [r for r in all_rows if r["Coverage"] not in ("Superseded", "Withdrawn", "Orphan")]
    entries = log_entries(root, slug)
    pct = lambda n, d: f"{100 * n / d:.0f}% ({n}/{d})" if d else "n/a"  # noqa: E731
    rate = lambda vals: (sum(1 for v in vals if v == "Pass"), sum(1 for v in vals if v in ("Pass", "Fail", "Blocked")))  # noqa: E731
    acs = sorted({r["AC"] for r in rows})
    linked = sorted({r["AC"] for r in rows if r["Link"] == "Confirmed" and r["Test"]})
    covered = [ac for ac in acs if all(r["Coverage"] == "Covered" for r in rows if r["AC"] == ac)]
    test_pass, test_n = rate([r["Test result"] for r in rows])
    uat_pass, uat_n = rate([r["UAT result"] for r in rows])
    raised, waits = {}, []
    for e in entries:
        ts = datetime.datetime.fromisoformat(e["ts"].replace("Z", "+00:00"))
        ids = set(e.get("refs") or []) | set(re.findall(r"\bQ-\d{2,3}\b", e.get("summary") or ""))
        for q in (i for i in ids if i.startswith("Q-")):
            if e["type"] == "question.raised":
                raised.setdefault(q, ts)
            elif e["type"] == "question.answered" and q in raised:
                waits.append((ts - raised.pop(q)).total_seconds() / 86400)
    waits.sort()
    median = f"{waits[len(waits) // 2]:.1f} days ({len(waits)} questions)" if waits else "n/a (no raised→answered pairs)"
    reviews = [e for e in entries if e["type"] == "review.scored"]
    events = [e for e in entries if e.get("source") == "skill"]
    drafts = [e for e in entries if e["type"] == "draft.reviewed"]
    accepted = sum(1 for e in drafts if re.match(r"(?i)^accepted", e.get("decision") or ""))
    defects, _, _, _ = review_defects(feature)
    doc = feature.doc("08-")
    grounded = 0
    for table in feature.tables(doc) if doc else []:
        if table["section"].startswith("Defects"):
            cat = col(table, "Category")
            grounded += sum(1 for r in table["rows"] if (cat >= 0 and cell(r, cat).startswith("Groundedness"))
                            or (cat < 0 and re.search(r"(?i)invent|unsourced|no source|ungrounded", " ".join(r["cells"]))))
    scores = review_scores(feature)
    score = lambda name: f"{scores[name][0]}/{scores[name][1]} (latest review)" if name in scores else "n/a (no scored review)"  # noqa: E731
    count = lambda t: sum(1 for e in entries if e["type"] == t)  # noqa: E731
    table = [
        ("Traceability coverage (AC with a confirmed test)", pct(len(linked), len(acs))),
        ("Test pass rate: Pass / (Pass + Fail + Blocked)", pct(test_pass, test_n)),
        ("UAT pass rate: Pass / (Pass + Fail + Blocked)", pct(uat_pass, uat_n)),
        ("Fully covered AC (every test and UAT passed, with evidence)", pct(len(covered), len(acs))),
        ("Requirement completeness", score("Completeness")),
        ("AC testability", score("Testability")),
        ("Review rounds / latest result", f"{len(reviews)} / " + (one_line_text(reviews[-1].get("summary"), 60) if reviews else "none")),
        ("AI acceptance rate (drafts accepted / reviewed)", pct(accepted, len(drafts)) if drafts
         else "n/a (log draft.reviewed when a person reviews an AI draft)"),
        ("AI unsupported claims (Groundedness defects, latest review)", str(grounded) if doc else "n/a"),
        ("Rework: gates reopened · change requests · AC retested", f"{count('gate.reopened')} · {count('cr.logged')} · "
         f"{sum(1 for r in all_rows if r['Notes'].startswith('Superseded'))}"),
        ("Stages skipped", str(count("stage.skipped"))),
        ("Clarification time (median, Blocking/Decision-critical)", median),
        ("Workflow events with the AI model recorded", pct(sum(1 for e in events if e.get("model")), len(events))),
        ("Workflow events run from an AI tool (via)", pct(sum(1 for e in events if str(e.get("via", "")).startswith("assistant")), len(events))),
    ]
    limits = uat_thresholds(root, slug)
    if limits:
        def meets(n, d, need):
            if need is None:
                return "not set"
            return "n/a (nothing run yet)" if not d else ("met" if 100 * n / d >= need else "NOT met")
        table.append(("UAT thresholds (PO): coverage / pass",
                      f"{limits.get('coverage', '-')}% {meets(len(covered), len(acs), limits.get('coverage'))}"
                      f" · {limits.get('pass', '-')}% {meets(uat_pass, uat_n, limits.get('pass'))}"))
    return table


def cmd_kpi(root, args):
    if not (requirements_dir(root) / args.feature).is_dir():
        print(f"error: no folder for {args.feature}", file=sys.stderr)
        return 1
    table = kpis(root, args.feature)
    if args.json:
        print(json.dumps(dict(table), ensure_ascii=False, indent=2))
        return 0
    print(f"| KPI — {args.feature} | Value |\n|---|---|")
    for name, value in table:
        print(f"| {name} | {value} |")
    return 0


# --------------------------------------------------------------------------- status: plain-language summary and dashboard

LABELS = {
    "en": {"stage": "Stage", "mode": "Mode", "next": "Next action", "gates": "Gates", "waiting": "Waiting for people",
           "nobody": "nobody - no open questions to send", "assumptions": "Open assumptions", "rtm": "Traceability",
           "review": "Latest review", "none": "none yet", "questions": "questions", "blocking": "Blocking",
           "critical": "decision-critical", "title": "Status", "kpi": "KPIs", "updated": "Last updated"},
    "vi": {"stage": "Giai đoạn", "mode": "Chế độ", "next": "Việc tiếp theo", "gates": "Các cổng (gate)",
           "waiting": "Đang chờ ai trả lời", "nobody": "không ai - không còn câu hỏi mở",
           "assumptions": "Giả định còn mở", "rtm": "Truy vết (RTM)", "review": "Lần review gần nhất",
           "none": "chưa có", "questions": "câu hỏi", "blocking": "chặn (Blocking)", "critical": "cần quyết định",
           "title": "Trạng thái", "kpi": "Chỉ số KPI", "updated": "Cập nhật"},
}


def status_summary(root, slug):
    feature = Feature(requirements_dir(root) / slug)
    _, _, assumptions, _ = register(feature)
    waiting = {}
    for q in question_rows(feature):
        level = next((p for p in PRIORITIES if q["priority"].startswith(p)), "")
        if level == "Nice to know":
            continue
        who = re.sub(r"\bSTK-\d{2,3}\b\s*", "", q["ask"]).strip(" ,;") or q["ask"] or "?"
        slot = waiting.setdefault(who, {"total": 0, "Blocking": 0, "Decision-critical": 0})
        slot["total"] += 1
        if level in slot:
            slot[level] += 1
    gates = next((t for t in feature.tables("_status.md") if t["section"].startswith("Gates")), None) \
        if "_status.md" in feature.docs else None
    history = next((t for t in feature.tables("_status.md") if t["section"].startswith("Review score")), None) \
        if "_status.md" in feature.docs else None
    next_action = " ".join(l.lstrip("> ").strip() for l in
                           section_text(feature.docs.get("_status.md", []), "Next action").splitlines() if l.strip())
    open_a = [a for a in assumptions if a["status"] == "Open"]
    rtm = rtm_rows(feature)
    return {
        "slug": slug, "stage": status_field(feature, "Current stage"), "updated": status_field(feature, "Last updated"),
        "mode": preference(root, slug, "Mode", "standard"), "language": preference(root, slug, "Language", "en"),
        "next": next_action,
        "gates": [(cell(r, 0), cell(r, 2) or "–") for r in gates["rows"] if not cell(r, 0).startswith("<")] if gates else [],
        "waiting": sorted(waiting.items(), key=lambda kv: (-kv[1]["Blocking"], -kv[1]["Decision-critical"], kv[0])),
        "assumptions": {r: sum(1 for a in open_a if a["risk"] == r) for r in ("High", "Medium", "Low")},
        "rtm": {c: sum(1 for r in rtm if r["Coverage"] == c) for c in COVERAGE_ORDER} if rtm is not None else None,
        "review": " · ".join(history["rows"][-1]["cells"][:3]) if history and history["rows"] else "",
    }


def cmd_status(root, args):
    if not (requirements_dir(root) / args.feature).is_dir():
        print(f"error: no folder for {args.feature}", file=sys.stderr)
        return 1
    s = status_summary(root, args.feature)
    lang = args.lang or s["language"]
    t = LABELS.get(lang, LABELS["en"])
    waiting = [f"{who}: {n['total']} {t['questions']}" + (f" ({n['Blocking']} {t['blocking']})" if n["Blocking"] else "")
               + (f" ({n['Decision-critical']} {t['critical']})" if n["Decision-critical"] else "")
               for who, n in s["waiting"]] or [t["nobody"]]
    rtm = (", ".join(f"{c} {n}" for c, n in s["rtm"].items() if n) or "0") if s["rtm"] is not None else t["none"]
    lines = [f"📍 {s['slug']} · {t['stage']}: {s['stage']} · {t['mode']}: {s['mode']} · {t['updated']}: {s['updated']}",
             f"✅ {t['next']}: {s['next'] or '—'}",
             f"👥 {t['waiting']}: " + "; ".join(waiting),
             f"❓ {t['assumptions']}: High {s['assumptions']['High']} · Medium {s['assumptions']['Medium']} · "
             f"Low {s['assumptions']['Low']}",
             f"🔗 {t['rtm']}: {rtm}", f"🔍 {t['review']}: {s['review'] or t['none']}",
             f"🚦 {t['gates']}: " + " · ".join(f"{g} {r}" for g, r in s["gates"])]
    if not args.html:
        print("\n".join(lines))
        return 0
    Path(args.html).parent.mkdir(parents=True, exist_ok=True)
    write_lf(Path(args.html), dashboard_html(root, s, t, waiting, rtm))
    print(f"wrote {args.html}")
    return 0


def dashboard_html(root, s, t, waiting, rtm):
    import html
    e = html.escape
    tone = lambda r: "ok" if gate_result(r)[0] == "Passed" else ("bad" if gate_result(r)[0] in ("Failed", "Blocked") else "")  # noqa: E731
    gates = "".join(f"<tr><td>{e(g)}</td><td class='{tone(r)}'>{e(r)}</td></tr>" for g, r in s["gates"])
    kpi = "".join(f"<tr><td>{e(n)}</td><td>{e(v)}</td></tr>" for n, v in kpis(root, s["slug"]))
    items = "".join(f"<li>{e(w)}</li>" for w in waiting)
    return f"""<!doctype html><html lang="{e(s['language'])}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(s['slug'])} · {e(t['title'])}</title>
<style>
:root{{--bg:#f6f8f9;--card:#fff;--fg:#17242b;--muted:#566973;--line:#d6dfe3;--ok:#1d6b3a;--bad:#a1261b}}
@media (prefers-color-scheme:dark){{:root{{--bg:#11191d;--card:#182328;--fg:#e6edf0;--muted:#9db0b9;--line:#2e3e45;--ok:#6fd08f;--bad:#ff8a7a}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 "Segoe UI",Roboto,Arial,sans-serif}}
main{{max-width:980px;margin:0 auto;padding:28px 16px;display:grid;gap:16px}}
h1{{margin:0;font-size:1.6rem}} .meta{{color:var(--muted)}}
section{{background:var(--card);border:1px solid var(--line);padding:16px}} h2{{margin:0 0 8px;font-size:1.05rem}}
table{{border-collapse:collapse;width:100%}} td{{border-bottom:1px solid var(--line);padding:6px 8px;vertical-align:top}}
.ok{{color:var(--ok);font-weight:600}} .bad{{color:var(--bad);font-weight:600}} ul{{margin:0;padding-left:1.2em}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px}}
</style></head><body><main>
<header><h1>{e(s['slug'])}</h1><p class="meta">{e(t['stage'])}: {e(s['stage'])} · {e(t['mode'])}: {e(s['mode'])} ·
{e(t['updated'])}: {e(s['updated'])}</p></header>
<section><h2>{e(t['next'])}</h2><p>{e(s['next'] or '—')}</p></section>
<div class="grid"><section><h2>{e(t['waiting'])}</h2><ul>{items}</ul></section>
<section><h2>{e(t['assumptions'])}</h2><p>High {s['assumptions']['High']} · Medium {s['assumptions']['Medium']} ·
Low {s['assumptions']['Low']}</p><h2>{e(t['rtm'])}</h2><p>{e(rtm)}</p><h2>{e(t['review'])}</h2>
<p>{e(s['review'] or t['none'])}</p></section></div>
<div class="grid"><section><h2>{e(t['gates'])}</h2><table>{gates}</table></section>
<section><h2>{e(t['kpi'])}</h2><table>{kpi}</table></section></div>
<p class="meta">ba status · BA Pipeline {e(version_text())}</p>
</main></body></html>
"""


# --------------------------------------------------------------------------- export: registers and matrices to Excel

def xlsx_col(n):
    name = ""
    while n:
        n, rem = divmod(n - 1, 26)
        name = chr(65 + rem) + name
    return name


def write_xlsx(path, sheets):
    """Minimal .xlsx (standard library only): inline strings, bold frozen header row, sized columns."""
    import zipfile
    from xml.sax.saxutils import escape
    clean = lambda v: escape(re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", str(v))[:32767],  # Excel's cell limit  # noqa: E731
                             {'"': "&quot;", "'": "&apos;"})
    files = {
        "[Content_Types].xml": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        + "".join(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-'
                  f'officedocument.spreadsheetml.worksheet+xml"/>' for i in range(1, len(sheets) + 1)) + "</Types>",
        "_rels/.rels": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" '
        'Target="xl/workbook.xml"/></Relationships>',
        "xl/styles.xml": '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        '<fonts count="2"><font><sz val="11"/><name val="Calibri"/></font><font><b/><sz val="11"/><name val="Calibri"/></font></fonts>'
        '<fills count="2"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill></fills>'
        '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/></border></borders>'
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
        '<cellXfs count="3"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>'
        '<xf numFmtId="0" fontId="1" fillId="0" borderId="0" xfId="0" applyFont="1"/>'
        '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0" applyAlignment="1"><alignment wrapText="1" vertical="top"/></xf>'
        '</cellXfs></styleSheet>',
    }
    names, used = [], set()
    for title, _ in sheets:
        base = re.sub(r"[\[\]:*?/\\]", " ", title).strip()[:31] or "Sheet"
        name, n = base, 2
        while name.lower() in used:
            suffix = f" ({n})"
            name, n = base[:31 - len(suffix)] + suffix, n + 1
        used.add(name.lower())
        names.append(name)
    files["xl/workbook.xml"] = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                                '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                                'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
                                + "".join(f'<sheet name="{clean(n)}" sheetId="{i}" r:id="rId{i}"/>'
                                          for i, n in enumerate(names, 1)) + "</sheets></workbook>")
    files["xl/_rels/workbook.xml.rels"] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        + "".join(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/'
                  f'worksheet" Target="worksheets/sheet{i}.xml"/>' for i in range(1, len(sheets) + 1))
        + f'<Relationship Id="rId{len(sheets) + 1}" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
          f'relationships/styles" Target="styles.xml"/></Relationships>')
    for i, (_, rows) in enumerate(sheets, 1):
        width = max((len(r) for r in rows), default=1)
        cols = "".join(f'<col min="{c}" max="{c}" width="{min(60, max(8, max((len(str(r[c - 1])) for r in rows if len(r) >= c), default=8) + 2))}" customWidth="1"/>'
                       for c in range(1, width + 1))
        data = []
        for r_no, row in enumerate(rows, 1):
            style = 1 if r_no == 1 else 2
            data.append(f'<row r="{r_no}">' + "".join(
                f'<c r="{xlsx_col(c)}{r_no}" t="inlineStr" s="{style}"><is><t xml:space="preserve">{clean(v)}</t></is></c>'
                for c, v in enumerate(row, 1)) + "</row>")
        files[f"xl/worksheets/sheet{i}.xml"] = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheetViews><sheetView workbookViewId="0"><pane ySplit="1" topLeftCell="A2" activePane="bottomLeft" '
            f'state="frozen"/></sheetView></sheetViews><cols>{cols}</cols><sheetData>{"".join(data)}</sheetData></worksheet>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return names


EXPORT_STATUS_SECTIONS = ("Gates", "Stakeholders", "Governance", "Decision log", "Risks", "Change log")


def export_sheets(feature):
    sheets = []

    def add(title, table):
        rows = [table["header"]] + [r["cells"] for r in table["rows"]]
        if len(rows) > 1:
            sheets.append((title, rows))
    for name in ("02-questions.md", CLOSED_DOC):
        for table in feature.tables(name) if name in feature.docs else []:
            if col(table, "ID") >= 0:
                add(("Closed · " if name == CLOSED_DOC else "") + (table["section"] or "Register"), table)
    for table in feature.tables("_status.md") if "_status.md" in feature.docs else []:
        if table["section"].startswith(EXPORT_STATUS_SECTIONS):
            add(table["section"], table)
    acs = story_acceptance(feature)
    if acs:
        sheets.append(("Acceptance criteria", [["AC", "Story", "Goal", "Rules"]]
                       + [[a["ac"], a["story"], a["goals"], a["rules"]] for a in acs]))
    spec = feature.doc("07-")
    for table in feature.tables(spec) if spec else []:
        if col(table, "ID") >= 0:
            add("Spec · " + (table["section"] or "table"), table)
    rows = rtm_rows(feature)
    if rows:
        sheets.append(("RTM", [RTM_HEADER] + [[r[h] for h in RTM_HEADER] for r in rows]))
    return sheets


def cmd_export(root, args):
    folder = requirements_dir(root) / args.feature
    if not folder.is_dir():
        print(f"error: no folder {folder}", file=sys.stderr)
        return 1
    sheets = export_sheets(Feature(folder))
    if not sheets:
        print("error: nothing to export yet (no register, status tables, stories or RTM)", file=sys.stderr)
        return 1
    out = Path(args.out) if args.out else root / "exports" / f"{args.feature}.xlsx"  # outside the feature: not an artifact
    out.parent.mkdir(parents=True, exist_ok=True)
    names = write_xlsx(out, sheets)
    print(f"wrote {out} - {len(names)} sheets: {', '.join(names)}")
    return 0


# --------------------------------------------------------------------------- discover: system knowledge bases

def slugify(text):
    """'Quản lý đơn hàng' -> 'quan-ly-don-hang'. Returns '' when nothing Latin is left (the caller asks for a name)."""
    text = (text or "").replace("đ", "d").replace("Đ", "D")
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def parse_day(text):
    """An ISO date (2026-11-12) or a Vietnamese/European one (12/11/2026) -> date, else None."""
    text = (text or "").strip()
    try:
        if re.match(r"^\d{4}-\d{2}-\d{2}$", text):
            return datetime.date.fromisoformat(text)
        m = re.match(r"^(\d{1,2})[/.](\d{1,2})[/.](\d{4})$", text)
        if m:
            return datetime.date(int(m.group(3)), int(m.group(2)), int(m.group(1)))
    except ValueError:
        return None
    return None


def knowledge_status(root, system, max_age):
    """[(page, status, verified_by, verified_on, age_days or None)] for the pages of knowledge/<system>/."""
    folder = root / KNOWLEDGE_DIR / system
    out = []
    for page in sorted(folder.glob("0*.md")):
        text = page.read_text(encoding="utf-8-sig")
        field = lambda name: (re.search(r"^\|\s*" + name + r"\s*\|\s*([^|]*)\|", text, re.M) or [None, ""])[1].strip()  # noqa: E731
        status, by, on = plain(field("Status")), plain(field("Verified by")), plain(field("Verified on"))
        day = parse_day(on)
        age = (datetime.date.today() - day).days if day else None
        if "·" in status:
            status = "Draft"  # the template's list of options: not chosen yet
        if status.startswith("Verified") and (not by or by.startswith("<") or is_ai_name(by) or day is None):
            status = "Draft (Verified needs a person and a date)"
        out.append((page.name, status, by, on, age))
    return out


def knowledge_summary(root):
    """One line per knowledge base, for ba context."""
    base = root / KNOWLEDGE_DIR
    max_age = int(load_config(root).get("knowledge_max_age_days", 180))
    lines = []
    for folder in sorted(p for p in base.iterdir() if p.is_dir()) if base.is_dir() else []:
        pages = knowledge_status(root, folder.name, max_age)
        verified = [p for p in pages if p[1].startswith("Verified")]
        stale = [p[0] for p in verified if p[4] is not None and p[4] > max_age]
        questions = folder / "06-open-questions.md"
        open_q = len(re.findall(r"^\|\s*Q-\d+[^\n]*\|\s*Open\b", questions.read_text(encoding="utf-8-sig"), re.M)) \
            if questions.is_file() else 0
        lines.append(f"- knowledge/{folder.name}/: {len(verified)}/{len(pages)} pages verified"
                     + (f", stale: {', '.join(stale)}" if stale else "") + f", {open_q} open questions")
    return lines


def cmd_discover(root, args):
    system = slugify(args.system)
    if not system:
        print(f"error: '{args.system}' gives no folder name - add a Latin short name, e.g. ba discover \"CRM ({args.system})\"",
              file=sys.stderr)
        return 1
    folder = root / KNOWLEDGE_DIR / system
    max_age = int(load_config(root).get("knowledge_max_age_days", 180))
    if not folder.is_dir():
        templates = core_dir() / "templates" / "knowledge"
        local = root / ".ba" / "local" / "templates" / "knowledge"
        (folder / "sources").mkdir(parents=True)
        for page in sorted(templates.glob("*.md")):
            source = local / page.name if (local / page.name).is_file() else page
            write_lf(folder / page.name, source.read_text(encoding="utf-8").replace("<system>", args.system)
                     .replace("<System>", args.system))
        write_lf(folder / "sources" / "README.md", "Raw inputs about the system. Never edit. Name files "
                 "`SRC-NN-<short-name>.<ext>`; mask real personal data first.\n")
        append_events(audit_log_path(root, None), [{
            "source": "skill", "type": "knowledge.updated", "actor": actor_default(), "reported_by": actor_default(),
            "via": via_default(), "tool": f"ba-pipeline {version_text()}",
            "summary": f"{system}: knowledge base created from templates (all pages Draft)"}])
        record_changes(root, None, pending_changes(root, None))
        print(f"created knowledge/{system}/ - follow /ba-discover {system}: sources, people, then the pages")
        return 0
    print(f"knowledge/{system}/  (pages older than {max_age} days are stale)")
    for name, status, by, on, age in knowledge_status(root, system, max_age):
        flag = " STALE" if age is not None and age > max_age else ""
        shown = f"verified by {by} on {on}" if status.startswith("Verified") else ""
        print(f"  {name:22} {status or '?':12} {shown}{flag}")
    print("\n".join(knowledge_summary(root)) if (root / KNOWLEDGE_DIR).is_dir() else "")
    return 0


# --------------------------------------------------------------------------- where: which copy of the workflow is in use

PACKAGE_MARKER = "ba-pipeline.package"  # file at the root of the copy bundled in the Kiro Power


def ba_command(path):
    return f'python "{Path(path).as_posix()}"'


def cmd_where(root, args):
    """Where the workflow lives for this project: a copy installed in .ba/ (pinned) or this package (e.g. the Kiro
    Power's bundled copy). --save records this package in .ba/config.json so later sessions find it."""
    installed = root / ".ba" / "tools" / "ba.py"
    here = TOOLS_DIR / "ba.py"
    config = load_config(root)
    if installed.is_file() and installed.resolve() != here.resolve():
        version = (root / ".ba" / "VERSION").read_text(encoding="utf-8").strip() if (root / ".ba" / "VERSION").is_file() else "?"
        print(f"project: {root}\nworkflow: installed in .ba/ (version {version}) - use it, not this copy\n"
              f"command: python .ba/tools/ba.py\nmanual: .ba/core/MANUAL.md\ncore: .ba/core/")
        return 0
    print(f"project: {root}\nworkflow: {PACKAGE_DIR} (version {version_text()})\ncommand: {ba_command(here)}\n"
          f"manual: {(core_dir() / 'MANUAL.md').as_posix()}\ncore: {core_dir().as_posix()}/\n"
          f"templates, checklists, profiles, reference: .ba/local/<path> if the project has it, otherwise core")
    if args.save:
        path = root / ".ba" / "config.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        data = json.loads(path.read_text(encoding="utf-8-sig")) if path.is_file() else {"requirements_dir": "requirements"}
        data["package"] = PACKAGE_DIR.as_posix()
        write_lf(path, json.dumps(data, ensure_ascii=False, indent=2) + "\n")
        print(f"saved: .ba/config.json -> package = {PACKAGE_DIR.as_posix()}")
    elif config.get("package") and Path(config["package"]).resolve() != PACKAGE_DIR.resolve():
        print(f"note: .ba/config.json points at another copy: {config['package']}")
    return 0


# --------------------------------------------------------------------------- approve: the approver confirms, in a terminal

def cmd_approve(root, args):
    """A person confirms an approval themselves: a human gate, a formal document, or a change of mode. Refused inside
    an AI tool's shell and without an interactive terminal, so the assistant can't run it on the approver's behalf."""
    folder = requirements_dir(root) / args.feature
    if not folder.is_dir():
        print(f"error: no folder {folder}", file=sys.stderr)
        return 1
    def interactive():
        try:
            os.get_terminal_size(sys.stdin.fileno())
            return sys.stdin.isatty()
        except (OSError, ValueError, AttributeError):
            return False
    if assistant_tool() or not interactive():
        print("error: ba approve must be run by the approver (or the BA with them) in their own terminal - not by an "
              "AI tool and not from a script", file=sys.stderr)
        return 1
    feature = Feature(folder)
    if args.gate:
        item = {"type": "gate.passed", "stage": args.gate}
    elif args.doc:
        if args.doc not in feature.docs:
            print(f"error: {args.doc} not found (e.g. docs/brd.md)", file=sys.stderr)
            return 1
        item = {"type": "approval.recorded", "summary": f"{args.doc.split('/', 1)[-1]} approved"}
    else:
        item = {"type": "settings.changed", "summary": f"Mode: {args.mode}"}
    refs = [args.decision] + ([args.source] if args.source else [])
    item.update({"actor": args.as_, "refs": refs, "_via": "approve"})
    try:
        check_authority(root, item, args.feature, refs)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    what = args.gate or args.doc or f"Mode {args.mode}"
    print(f"{args.as_} approves {what} for {args.feature}, recorded in {args.decision}"
          + (f" (evidence {args.source})" if args.source else "") + ".")
    typed = input("Type your full name to confirm: ").strip()
    if person_tokens(typed) != person_tokens(args.as_):
        print("not confirmed - nothing logged")
        return 1
    fields = {"source": "approve", "type": item["type"], "actor": args.as_, "reported_by": actor_default(),
              "via": "approve", "tool": f"ba-pipeline {version_text()}", "session": session_default(),
              "feature": args.feature, "stage": args.gate, "summary": item.get("summary") or f"{args.gate} approved",
              "decision": "approved", "refs": refs}
    if args.doc:
        fields.update({"file": args.doc, "sha256": sha256_file(folder / args.doc)})
    entry = append_events(audit_log_path(root, args.feature), [fields])[0]
    print(f"audit #{entry['seq']} {entry['type']} logged (via approve)")
    return 0


# --------------------------------------------------------------------------- CLI

def main(argv=None):
    parser = argparse.ArgumentParser(prog="ba", description="BA Pipeline checks and audit trail")
    parser.add_argument("--root", help="project root (default: auto-detect)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_check = sub.add_parser("check", help="mechanical quality checks for one feature")
    p_check.add_argument("feature")
    p_check.add_argument("--only", help="comma-separated: status,ids,ranges,register,ground,gherkin,tables,ambiguity,"
                                        "open,governance,rtm,handoff,docs,gates,audit")

    p_rtm = sub.add_parser("rtm", help="build or refresh rtm.md, the live traceability matrix (AC → test → result)")
    p_rtm.add_argument("feature")

    p_kpi = sub.add_parser("kpi", help="release KPIs computed from the RTM and the audit log")
    p_kpi.add_argument("feature")
    p_kpi.add_argument("--json", action="store_true")

    p_status = sub.add_parser("status", help="plain-language status of a feature; --html writes a dashboard page")
    p_status.add_argument("feature")
    p_status.add_argument("--html", help="write a one-page HTML dashboard to this path")
    p_status.add_argument("--lang", choices=sorted(LABELS), help="label language (default: the feature's Language)")

    p_where = sub.add_parser("where", help="which copy of the workflow this project uses (installed .ba/ or this "
                                           "package, e.g. the Kiro Power), and the command and paths to use")
    p_where.add_argument("--save", action="store_true", help="record this package in .ba/config.json for later sessions")

    p_approve = sub.add_parser("approve", help="the approver confirms a human gate, a document or a mode change "
                                               "in their own terminal (required for gates in controlled mode)")
    p_approve.add_argument("feature")
    what = p_approve.add_mutually_exclusive_group(required=True)
    what.add_argument("--gate", help='e.g. "8 Review"')
    what.add_argument("--doc", help="e.g. docs/brd.md")
    what.add_argument("--mode", choices=("quick", "standard", "controlled"))
    p_approve.add_argument("--as", dest="as_", required=True, help="the approver's full name (or STK- ID)")
    p_approve.add_argument("--decision", required=True, help="the D- in _status.md → Decision log, decided by them")
    p_approve.add_argument("--source", help="the SRC- of the approval (email, minutes), if any")

    p_discover = sub.add_parser("discover", help="create or show knowledge/<system>/, the knowledge base of an "
                                                 "existing system (/ba-discover)")
    p_discover.add_argument("system", help="system name, e.g. 'Core banking' or erp")

    p_export = sub.add_parser("export", help="export registers, decisions, gates, AC, spec tables and RTM to .xlsx")
    p_export.add_argument("feature")
    p_export.add_argument("--out", help="default: exports/<feature>.xlsx")

    p_turn = sub.add_parser("turn", help="end of every turn: log the turn's events, update the snapshot, record "
                                         "file changes; --gate also runs the checks")
    p_turn.add_argument("feature")
    p_turn.add_argument("--events", help="JSON array of events (file path, or - for stdin); keys as in audit event")
    p_turn.add_argument("--gate", action="store_true", help="end of a stage: run ba check and log check.run")
    p_turn.add_argument("--stage", help="stage label for the check.run event, e.g. '2 Elicit'")

    p_context = sub.add_parser("context", help="print only what a stage needs (status, governance, open items, "
                                               "the relevant section of each active profile)")
    p_context.add_argument("feature")
    p_context.add_argument("stage", help="e.g. ba-elicit or elicit")

    p_answers = sub.add_parser("answers", help="answer files the BA fills in instead of typing in chat")
    answers = p_answers.add_subparsers(dest="answers_command", required=True)
    p_new = answers.add_parser("new", help="write answers/round-NN.md with the open questions")
    p_new.add_argument("feature")
    p_new.add_argument("--ids", help="only these questions, comma-separated")
    p_new.add_argument("--who", help="only questions whose Ask column contains this (STK-02, a name)")
    p_new.add_argument("--all", action="store_true", help="include Nice to know (parked by default)")
    p_new.add_argument("--chat", action="store_true",
                       help="print the round as one chat message (walkthrough) instead of writing a form")
    p_read = answers.add_parser("read", help="print the answers compactly and file the form as a source")
    p_read.add_argument("feature")
    p_read.add_argument("file", nargs="?", help="default: the latest answers/round-*.md")
    p_read.add_argument("--keep", action="store_true", help="don't move the form into sources/")

    p_questions = sub.add_parser("questions", help="question register housekeeping")
    questions = p_questions.add_subparsers(dest="questions_command", required=True)
    p_archive = questions.add_parser("archive", help=f"move answered questions and settled assumptions to {CLOSED_DOC}")
    p_archive.add_argument("feature")

    p_audit = sub.add_parser("audit", help="audit trail")
    audit = p_audit.add_subparsers(dest="audit_command", required=True)
    p_event = audit.add_parser("event", help="log a workflow event (or a batch with --json-file)")
    p_event.add_argument("--feature")
    for key in ("type", "stage", "summary", "reason", "decision", "refs", "actor", "model"):
        p_event.add_argument(f"--{key}")
    p_event.add_argument("--severity", choices=SEVERITIES)
    p_event.add_argument("--json-file")
    p_sync = audit.add_parser("sync", help="record file changes by hash since the last record")
    p_sync.add_argument("feature", nargs="?")
    p_sync.add_argument("--workspace", action="store_true")
    p_sync.add_argument("--dry-run", action="store_true")
    p_verify = audit.add_parser("verify", help="verify the hash chain")
    p_verify.add_argument("feature", nargs="?")
    p_verify.add_argument("--all", action="store_true")
    audit.add_parser("hook", help="post-edit hook (JSON on stdin)")

    sub.add_parser("version", help="print the BA Pipeline version")

    args = parser.parse_args(argv)
    root = find_root(args.root)

    if args.command == "version":
        print(version_text())
        return 0
    simple = {"rtm": cmd_rtm, "kpi": cmd_kpi, "status": cmd_status, "export": cmd_export, "discover": cmd_discover,
              "approve": cmd_approve, "where": cmd_where}
    if args.command in simple:
        return simple[args.command](root, args)
    if args.command == "check":
        only = [x for x in re.split(r"\s*,\s*", args.only or "") if x]
        return run_checks(root, args.feature, only)
    if args.command == "turn":
        return cmd_turn(root, args)
    if args.command == "context":
        return cmd_context(root, args)
    if args.command == "answers":
        return {"new": cmd_answers_new, "read": cmd_answers_read}[args.answers_command](root, args)
    if args.command == "questions":
        return cmd_questions_archive(root, args)
    handlers = {"event": cmd_audit_event, "sync": cmd_audit_sync, "verify": cmd_audit_verify, "hook": cmd_audit_hook}
    return handlers[args.audit_command](root, args)


if __name__ == "__main__":
    sys.exit(main())

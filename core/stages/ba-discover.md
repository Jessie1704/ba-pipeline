---
name: ba-discover
description: Learn an existing system before (or between) features — for a BA joining a project that is already running, or before changing a legacy system. Builds a shared, sourced knowledge base in knowledge/<system>/ (system landscape and who knows what, current processes, business rules as they work today, key data, integrations, glossary, known problems, open questions) and a short onboarding brief, has the system owner confirm it, and lets every later feature cite it. Use when the BA says "I'm new on this project", "how does the current system work?", "learn the existing system", or before intake on a change to an existing system with little documentation. Tiếng Việt: tìm hiểu hệ thống đang chạy — BA mới vào dự án, xây kho kiến thức có nguồn về hệ thống cũ cho các feature sau dùng chung.
---

# /ba-discover <system> — Learn the system that already exists

> **Start:** `ba discover <system>` (creates `knowledge/<system>/` from `templates/knowledge/` if it doesn't exist,
> or prints its status and what is stale), then `ba context <any-feature> ba-discover` if a feature is in progress.
> Events go to the workspace log: `ba audit event --type knowledge.updated --summary "<system>: …"` (no feature).

The knowledge base describes **what is**, not what should be. It belongs to the system, not to a feature: several
features and BAs read and extend it. Everything in it is sourced and dated like any requirement — an unverified
belief is an assumption, and "nobody knows" is a question for a named person.

## Steps

1. **Frame it (one message).** Which system or modules; why now (new BA, upcoming change, audit); depth: *orient*
   (one or two days: map and people) or *deep* (rules and data for an area about to change). Name the **system
   owner** who will confirm the result.

2. **Inventory the sources** in `knowledge/<system>/sources/` and `README.md` → *Sources* (`SRC-NN`): existing
   specs, user manuals, release notes, tickets and incident reports, screenshots of the running system, database or
   API schemas, configuration exports, process documents — each with its date, because old documents describe old
   behaviour. Real personal data is masked before it goes in (guardrail 9).

3. **Who knows what.** In `01-landscape.md` → *People*: for each module or process, the people who use it, run it,
   build it and own it, and what each can answer. This is the first thing a new BA needs and the most often missing.

4. **Read, then ask.** Draft from the sources: landscape (modules, users, volumes, integrations), main processes
   as they run today, business rules as the system applies them (`KB-NN`), key data entities, glossary, known
   problems and workarounds. Label every line **[Fact]** (`SRC-`), **[Assumption]**, **[Inference]** or
   **[Unknown]**. Turn the unknowns into questions in `06-open-questions.md`, grouped by the person who can answer,
   with options where you can — the same discipline as `/ba-elicit` (answer mode, rounds).

5. **Observe the running system** when possible: walk through the main tasks with a user (or a test
   environment) and note what the system really does; record differences from the documents as findings —
   "the manual says 3 approval levels, production has 2 (observed 2026-11-12 with Lan, SRC-07)". Behaviour seen
   beats documents; documents beat memory.

6. **Onboarding brief.** `README.md` → *In 10 minutes*: what the system is for, its parts, the five rules everyone
   trips on, who to ask about what, the open questions that matter. Written for the next BA, in the team's language.

7. **Confirmation.** The system owner (and area owners for their parts) review the knowledge base; each confirmed
   page gets *Verified by* and *Verified on*. Record it as a decision in `README.md` → *Decisions* and log
   `knowledge.updated` (summary: system, pages, verified by). Unconfirmed pages stay *Draft* and say so.

8. **Use it from features.** When a feature changes this system, `/ba-intake` registers the knowledge pages it
   relies on as sources (`SRC-NN: knowledge/<system>/03-rules.md, verified 2026-11-12`) and cites `KB-NN` rules in
   its own rules' *Source* column, so grounding still traces to a confirmed source. What a feature learns about the
   existing system goes back into the knowledge base (step 4 again) — not only into the feature.

9. **Keep it fresh.** `ba discover <system>` lists pages not verified for 180 days (or `.ba/config.json` →
   `knowledge_max_age_days`) as stale. A released feature that changed the system updates the affected pages in
   `/ba-release` step 6.

## Finish with
- **Done:** pages drafted or verified, open questions by person, the onboarding brief.
- **Needs your decision:** questions only the BA can route; who confirms which page.
- **Next step:** send the questions; when a change is requested, `/ba-start` — intake will cite the knowledge base.

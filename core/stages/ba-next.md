---
name: ba-next
description: Tell the business analyst the single best next action for a requirements feature, based on _status.md, open questions, gates and artifact state. Use when the BA asks "what next?", "what should I do now?", "status", or seems unsure how to proceed. Tiếng Việt: việc tiếp theo nên làm là gì? trạng thái hiện tại.
---

# /ba-next — Guidance in one glance

1. Identify the feature (ask if several exist and none was named).
2. Start from `ba context <slug> ba-next`; open an artifact only if something there needs it. Include **deferred** stages ("Not now") and **skipped** stages
   with their severity — offer to revisit a skipped High/Critical stage when circumstances changed. Determine:
   - **Revisit triggers**: decisions that accepted a failed gate ("Revisit at: <stage>") — if that stage is
     current or past and the assumption is still open, this is the top blocker.
   - Current stage and whether its gate passes; the approach's stage plan including extra stages and overrides
     (never recommend a stage it marks Skip; recommend `/ba-step <id>` when an extra stage is next).
   - If the approach is weak (Low confidence, many overrides), suggest `/ba-profile` to install or create a better fit.
   - Open Blocking and Decision-critical `Q-` (and how long they've been open), High-risk `A-`, latest review score.
     Before the Scope gate, an open Decision-critical question is the top blocker, ahead of the next stage.
   - Artifacts that are stale (an answer or CR arrived after the artifact was last updated).
3. Reply in this exact shape (max ~12 lines):

```
📍 <feature> — Stage <n> <name> · Gate: <pass/fail: reason>
🧭 Approach: <primary> + <secondaries> (<Proposed/Confirmed>) · Skipped stages: <list or none>
🔴 Blockers: <count> (<top one, who owns it>)
✅ Next: <one action> → <command>
⏭  Then: <the action after that>
💡 Meanwhile you can: <work not blocked by the blocker>
```

Prioritisation rules: unblock others first (send questions) → fix Critical review defects → finish the current
gate → move forward. Never recommend skipping `/ba-review` before handoff.

After handoff the next stages are `/ba-refine` (sprints), `/ba-uat` (a build is ready) and `/ba-release`
(accepted). There, the blockers are RTM rows (`Missing link`, `Failed`, `Inferred link`, results without
evidence — `ba check <slug> --only rtm`), discrepancies of class `Unknown`, and human gates waiting for their
approver: name the approver and what they need to see. `ba status <slug>` gives the plain-language picture
("waiting for Linh: 3 questions") that the BA can paste to stakeholders.

# Gap Lenses — 12 ways to find what's missing

Apply every lens in `/ba-elicit`. For each: **Covered / Partial / Missing / N/A (reason)**.

| # | Lens | Ask |
|---|------|-----|
| 1 | **Why & value** | What problem, for whom, how big — what does it cost today? How will we know it worked (metric, **baseline**, **target**, date)? What happens if we do nothing? Missing answers are Decision-critical. |
| 2 | **Who & who decides** | All actors — end users, admins, approvers, support, external parties, systems. Who is affected but not consulted? **Who decides:** business owner (final say in conflicts), PO, an owner for every area or module named, escalation path. Is the BA also the PO? Missing owners are Decision-critical. |
| 3 | **Scope edges** | What's explicitly out? Which channels, regions, products, customer types, languages? |
| 4 | **Process & triggers** | What starts it? Each step, who does it, what ends it? Manual workarounds today? Frequency & volume? |
| 5 | **Alternatives & exceptions** | What if data is missing, wrong, late, duplicated? Cancel, undo, retry, partial completion, concurrent edits? |
| 6 | **States & time** | Lifecycle of each entity. Expiry, deadlines, SLAs, time zones, business days, holidays, scheduled jobs? |
| 7 | **Rules & calculations** | Eligibility, limits, thresholds, rounding, currency, priority when rules conflict, who can override? |
| 8 | **Data** | Fields, formats, mandatory, source of truth, ownership, history, retention, deletion, migration of existing data? |
| 9 | **Permissions & security** | Who can see/do what? Own vs others' records? Approvals, segregation of duties, PII, consent, audit trail? |
| 10 | **Integrations & dependencies** | Which systems send/receive? What if they're down or slow? Other teams' deliverables needed? |
| 11 | **Experience & communication** | Notifications (who/when/channel), messages, empty/error states, accessibility, devices, languages? |
| 12 | **Operate & measure** | Reporting, monitoring, support processes, training, rollout/cutover, feature flags, rollback, legal/compliance sign-off? |

Lenses 1 and 2 go first: scope and MVP can't be judged without goals and owners.
Tip: lenses 5, 6 and 9 find the most defects that reach production. Spend extra time there.

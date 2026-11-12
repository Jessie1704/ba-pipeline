# Ambiguity Words — replace on sight

Each hit must be rewritten into something measurable or explicit, or justified.

| Word / phrase | Problem | Rewrite as |
|---------------|---------|------------|
| should, could, would, might | Obligation unclear | **must** (mandatory) / **may** (optional) |
| fast, quick, responsive, real-time, immediately | No number | "within 2 s at p95 under 200 concurrent users" |
| user-friendly, intuitive, easy, simple, seamless | Untestable | concrete behaviour or usability metric (e.g. "task completed in ≤3 clicks by 4/5 test users") |
| appropriate, relevant, suitable, adequate, reasonable, proper | Who decides? | the actual rule or list |
| etc., and so on, such as, including but not limited to, e.g. (in a rule) | Open-ended list | complete list, or "only the following:" |
| some, several, many, few, most, various | Unquantified | exact number or range |
| all, every, always, never, none | Often untrue — check | confirm absolute, or state exceptions |
| support, handle, manage, process, deal with | Vague verb | specific actions (create, view, edit, approve, export…) |
| flexible, configurable, extensible, scalable | Unbounded | what can be configured, by whom, within what limits |
| secure, robust, reliable, high availability | Untestable | specific control or SLA (e.g. "99.5 % monthly uptime") |
| if possible, where applicable, as needed, if necessary, TBD, TBC | Deferred decision | raise a `Q-` or decide now |
| user | Ambiguous role | named role from the permissions matrix |
| it, this, that (unclear referent) | Pronoun ambiguity | repeat the noun |
| and/or | Logic unclear | "A, B, or both" / "either A or B, not both" |
| similar to, like the current, same as before | Hidden spec | specify explicitly |
| minimise, maximise, optimise, improve | No target | target value and baseline |
| recently, soon, periodically, timely | No time | exact duration / schedule |

Exceptions: these words are fine inside quoted source text, user-story "so that" clauses describing benefit,
and the glossary.

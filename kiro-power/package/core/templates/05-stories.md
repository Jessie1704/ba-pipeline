# 05 · User Stories — <Feature name>

## Story map
| Activity → | <Activity 1> | <Activity 2> | <Activity 3> |
|------------|--------------|--------------|--------------|
| **MVP** | US-001, US-002 | US-004 | |
| **Next** | US-003 | | US-006 |
| **Later** | | US-005 | |

## Epics
| ID | Epic | Goal | Stories |
|----|------|------|---------|

---

## US-001 · <Verb + object>
**Epic:** EP-01 · **Priority:** Must (reason) · **Size:** S/M/L · **External key:** –

**As a** <named role>, **I want** <capability>, **so that** <benefit → G-NN>.

### Acceptance criteria
```gherkin
# AC-001.1 — happy path
Scenario: <name>
  Given <concrete precondition with example values>
  When <action>
  Then <observable outcome>
  And <further outcome>

# AC-001.2 — alternative path
Scenario: …

# AC-001.3 — failure / validation
Scenario: …
  Then the system shows MSG-NN "<exact text>"
```

| Item | Detail |
|------|--------|
| Business rules | BR-… |
| Data touched | Entity.field, … |
| UI notes | … |
| Not in this story | … |
| Dependencies | US-…, <system> |
| Open items | Q-…, A-… |
| Traces to | G-…, IS-…, flow 1.1 step 3, SRC-…/D-… |

---

## Coverage check
| Item | Covered by |
|------|-----------|
| IS-01 | US-001, US-002 |
| Flow 1.1 step 4 (reject branch) | AC-002.3 |
| State Submitted → Rejected | AC-005.2 |

**Uncovered:** none / list

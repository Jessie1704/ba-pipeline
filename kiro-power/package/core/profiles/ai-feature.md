---
name: ai-feature
title: AI feature
kind: solution
origin: built-in
version: 1.0
owner: BA practice
status: active
---

# Profile: AI feature

## 1. Signals
Behaviour produced by an AI/ML model: chat assistants, summarising, drafting, classifying, extracting, recommending, predicting.

## 2. Stage plan
| Stage | Plan |
|-------|------|
| Model | Run — + human-in-the-loop flow and fallback paths |
| Stories | Run — stories + **behaviour examples** (golden set) |
| UX | Run if users see AI output (how output, confidence, sources and corrections are shown) |
| Spec | Run — + AI behaviour specification and evaluation criteria |
| Handoff | Run — + evaluation pack |

## 3. Extra gap questions
- What exact task does the AI do, and what does "good output" look like? Who judges?
- What must it **never** do or say (guardrails, forbidden topics, tone)?
- Which data may it read? Is any of it personal/confidential? Can data leave our environment?
- Human review: always, above a risk threshold, or never? Who reviews and how fast?
- What happens when the AI is unsure, wrong, slow or unavailable (fallback)?
- Must outputs cite sources? Be explainable? Be reproducible?
- How will users correct or give feedback, and is that feedback used?
- Acceptance bar: what accuracy/quality on what test set is good enough to launch?
- Legal/regulatory constraints (AI regulations, disclosure that content is AI-generated)?
- Cost per request / monthly budget limits?

## 4. Model
Flow with AI step, human review step, fallback path; data flow showing what goes to the model.

## 5. Stories
Normal stories, plus a **golden set**: 10–30 realistic input → expected output (or acceptance criteria for the output)
examples, including hard, ambiguous and adversarial cases. AC are written as evaluable criteria
("summary mentions all amounts in the source", "never states a refund is approved").

## 6. UX
If user-facing: how AI output is labelled, confidence/uncertainty shown, sources linked, edit/regenerate/report actions, loading and failure states.

## 7. Spec sections to add
```markdown
## AI behaviour specification
| Topic | Requirement |
|-------|-------------|
| Task definition | |
| Inputs & context data allowed | |
| Output format & length | |
| Tone & language | |
| Must always | |
| Must never (guardrails) | |
| Uncertainty / refusal behaviour | |
| Human review rule | |
| Fallback when unavailable / low quality | |
| Source citation | |
| AI disclosure to users | |
| Cost / latency limits | |

## Evaluation criteria
| Eval ID | Criterion | Method (automated check / LLM-judge / human) | Test set | Launch threshold |
|---------|-----------|----------------------------------------------|----------|------------------|
```

## 8. NFR focus
Quality thresholds, Latency, Cost, Privacy & data residency, Safety/guardrails, Transparency/explainability, Monitoring of drift and feedback.

## 9. Handoff extras
`eval-pack.md`: golden set, evaluation criteria, thresholds, red-team cases, how to run evaluations before each release.

## 10. Review checks
Golden set covers hard and adversarial cases; every guardrail has a test; fallback defined; launch threshold numeric.

## 11. Extra stages
None.

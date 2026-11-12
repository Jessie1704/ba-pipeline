---
name: <kebab-case-id>
title: <Human name>
kind: solution        # solution | modifier
origin: custom        # built-in | catalogue | custom
version: 1.0
owner: <who maintains this profile>
status: active        # draft | active | retired
---

# Profile: <Human name>

## 1. Signals
<Words, situations or artefacts in the sources that indicate this profile applies. Also: when NOT to use it.>

## 2. Stage plan
| Stage | Plan | Notes |
|-------|------|-------|
| Model | Run · Adapted · Lite · Partial · Skip | |
| Stories | | |
| UX | | |
| Spec | | |
| Review | Run · Lite | |
| Handoff | Run · Adapted | |

## 3. Extra gap questions
- …

## 4. Model
<Which diagrams/models matter; which defaults to drop.>

## 5. Stories
<Story style and AC conventions, e.g. "As a … I want …", job stories, scenarios, requirement list.>

## 6. UX
<Applies? Full / partial / N/A, and what to focus on.>

## 7. Spec sections to add
```markdown
## <Section name>
| … | … |
|---|---|
```

## 8. NFR focus
<Mandatory NFR categories for this profile.>

## 9. Handoff extras
<Extra documents (file name + audience + contents) and extra sections in standard packs.
Standard packs this profile replaces or drops, if any.>

## 10. Review checks
<Extra checks the reviewer and mechanical checks must apply.>

## 11. Extra stages
<Stages this profile adds to the workflow. Run with `/ba-step <stage-id>`. "None" if none.>

| Stage ID | Name | After stage | Purpose | Steps | Output document | Gate |
|----------|------|-------------|---------|-------|-----------------|------|
| <e.g. vendor-eval> | <Vendor evaluation> | <5 Stories> | | 1. … 2. … | `05a-vendor-eval.md` | |

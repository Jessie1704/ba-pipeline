---
name: "ba-pipeline"
displayName: "BA Pipeline"
description: "AI-assisted business analysis from the first request to the release: build-ready requirements with human gates, an independent review, a live traceability matrix and a tamper-evident audit trail. Tiếng Việt: quy trình BA có AI hỗ trợ từ yêu cầu đầu tiên đến phát hành."
keywords: ["business analysis", "BA", "requirements", "user story", "acceptance criteria", "BRD", "URD", "RTM", "traceability", "UAT", "refinement", "change request", "audit trail", "phân tích nghiệp vụ", "yêu cầu nghiệp vụ", "tài liệu BRD", "hướng dẫn sử dụng", "kiểm thử UAT"]
author: "Jessie1704"
---

# BA Pipeline 1.0.0

AI-assisted business analysis from the first request to the release: build-ready requirements with human gates, an independent review, a live traceability matrix and a tamper-evident audit trail. Tiếng Việt: quy trình BA có AI hỗ trợ từ yêu cầu đầu tiên đến phát hành.

## Start
1. Open the project folder in Kiro and start a normal (Vibe) chat — not Spec mode. Python 3.9+ must be installed.
2. Describe the work, in English or Vietnamese — *"start a new feature: …"*, *"đây là ghi chú họp"* — or call a skill
   (`/ba-start`, `/ba-intake`, …). The skills run the workflow from this power's `package/` folder: nothing to install.
   The first command saves the package path in the project's `.ba/config.json`.
3. Optional: say *"pin BA Pipeline in this project"* (**ba-setup**) to keep a copy of the workflow in `.ba/`.

## What it does
- **Define:** start · intake · elicit · scope · model · stories · UX · spec · review · handoff.
- **Deliver:** refinement (Definition of Ready) · test & UAT · release.
- **Any time:** change requests · BRD/URD/user guides (`ba-docs`) · learn an existing system (`ba-discover`) ·
  what next · audit · profiles · extra stages.
- Modes *quick · standard · controlled*; language *en · vi*.

## Guardrails (the AI follows them in every stage)
- Every statement is a fact with a source, a labelled assumption, a labelled inference or an open question.
- The AI never sets priority, estimates, severity, test results or acceptance, and never closes a human gate: the
  approver does (in controlled mode with `ba approve`, in an operating-system terminal outside Kiro).
- Drafts stay drafts until a named person reviews them; secrets and personal data stay out of prompts.

## Skills in this power
`ba-pipeline` (entry, manual and routing) · `ba-start` · `ba-intake` · `ba-elicit` · `ba-scope` · `ba-model` · `ba-stories` · `ba-ux` · `ba-spec` · `ba-review` · `ba-handoff` · `ba-refine` · `ba-uat` · `ba-release` · `ba-docs` · `ba-discover` · `ba-change` · `ba-next` · `ba-step` · `ba-profile` · `ba-audit` · `ba-setup`
(optional pin)

Documentation: `package/core/README.md` (English), `package/core/README.vi.md` (tiếng Việt). All rights reserved by the
repository owner; the material adapted from ba-workflow (toaidx1) is included with the author's permission.

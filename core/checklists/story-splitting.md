# Story Splitting Patterns

Use when a story is too big, untestable, or hides several decisions. Each slice must still deliver user value.

| Pattern | Split by… | Example |
|---------|-----------|---------|
| Workflow steps | Steps of the process | "Submit refund" → request · approve · pay out |
| Happy / unhappy path | Main flow first, exceptions later | Refund valid order → handle expired order → handle partial refund |
| Business rule variations | Each rule variant | Refund by card · by store credit · by bank transfer |
| Data variations | Data types / sources | Import CSV → import Excel |
| Roles | Who performs it | Customer requests · agent requests on behalf |
| CRUD operations | Create / read / update / delete | Create address · edit address · delete address |
| Interface / channel | Web, mobile, API, batch | Web first, mobile later |
| Simple → complex | Minimal version then enhancements | Fixed limit → configurable limit |
| Defer performance | Make it work, then make it fast | Manual export → scheduled export |
| Spike | Unknown → time-boxed investigation story first | Spike: confirm payment provider supports partial refunds |

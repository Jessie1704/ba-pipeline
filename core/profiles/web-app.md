---
name: web-app
title: Web app
kind: solution
origin: built-in
version: 1.0
owner: BA practice
status: active
---

# Profile: Web app

## 1. Signals
Browser-based screens: customer portal, self-service, back-office, admin console, internal tool.

## 2. Stage plan
| Stage | Plan |
|-------|------|
| Model | Run — flows, states, permissions are central |
| Stories | Run — user stories per role |
| UX | **Run (full)** |
| Spec | Run — screen behaviour rules, data, messages |
| Handoff | Run — + design brief |

## 3. Extra gap questions
- Which browsers and minimum screen width? Must it work on mobile browsers?
- Logged-in vs public pages? Single sign-on? Session timeout behaviour?
- How many records per list (paging, sorting, filtering, export)?
- Concurrent editing of the same record — last write wins, locking, or warning?
- Unsaved changes — warn on leave? Autosave?
- Bulk actions needed? Import/export (formats)?
- Deep links / bookmarkable URLs needed? Browser back button behaviour in multi-step flows?

## 4. Model
Process flows, state machines, permissions matrix (every role × screen action).

## 5. Stories
Standard user stories. Split by screen or by workflow step; list/search/detail/edit are usually separate stories.

## 6. UX
Full `/ba-ux`: journeys, screen inventory, navigation map, wireframes, all states, responsive rules, accessibility.

## 7. Spec sections to add
```markdown
## Web specifics
| Topic | Requirement |
|-------|-------------|
| Supported browsers / min width | |
| Authentication & session timeout | |
| Lists: page size, default sort, filters, export formats | |
| Concurrency handling | |
| Unsaved-changes behaviour | |
| URL / deep-link rules | |
```

## 8. NFR focus
Performance (page load, search p95), Accessibility (mandatory), Security (session, authZ), Compatibility, Usability.

## 9. Handoff extras
`design-brief.md`; Screens section in `agent-brief.md`; UI, responsive and accessibility scenarios in `qa-pack.md`.

## 10. Review checks
Every screen has all states; every role × action cell matches screen visibility; accessibility target set.

## 11. Extra stages
None.

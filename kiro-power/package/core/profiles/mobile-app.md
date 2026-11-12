---
name: mobile-app
title: Mobile app
kind: solution
origin: built-in
version: 1.0
owner: BA practice
status: active
---

# Profile: Mobile app

## 1. Signals
iOS / Android / cross-platform app, push notifications, offline use, device features (camera, GPS, biometrics), app stores.

## 2. Stage plan
| Stage | Plan |
|-------|------|
| Model | Run — add offline/sync states |
| Stories | Run — user stories; device-capability stories explicit |
| UX | **Run (full, mobile-first)** |
| Spec | Run — + mobile specifics |
| Handoff | Run — + design brief, + release notes for stores |

## 3. Extra gap questions
- Platforms and minimum OS versions? Phone only or tablet too? Orientation?
- Native, cross-platform, or responsive web? (decision, not a guess)
- What must work **offline**? How are conflicts resolved when back online?
- Device permissions needed (camera, location, contacts, notifications)? What if the user denies?
- Push notifications: events, frequency limits, deep link targets, quiet hours?
- Biometric login? How long does a session last on device?
- Forced update / minimum supported app version? Behaviour when the backend changes?
- App store requirements: age rating, privacy labels, in-app purchase rules?
- Low connectivity / slow network behaviour?

## 4. Model
Flows, state machines including **sync states** (local-only, syncing, synced, conflict), permissions.

## 5. Stories
User stories plus explicit stories for: permission denied, offline mode, push opt-in/out, app update prompts.
AC include device conditions (`Given the device is offline`).

## 6. UX
Full `/ba-ux`, mobile-first: thumb reach, gestures, native patterns per platform, small-screen wireframes,
permission-prompt screens, offline/empty/error states.

## 7. Spec sections to add
```markdown
## Mobile specifics
| Topic | Requirement |
|-------|-------------|
| Platforms & min OS versions | |
| Devices / orientation | |
| Offline capability & conflict rules | |
| Device permissions & denial behaviour | |
| Push notifications (event, text, deep link, limits) | |
| Session & biometric login | |
| Minimum app version / forced update | |
| Analytics events | |
| App store metadata & privacy labels | |
```

## 8. NFR focus
Performance (cold start, battery, data usage), Availability (offline), Security (on-device storage), Accessibility, Compatibility (OS/device matrix), Privacy (permissions, tracking consent).

## 9. Handoff extras
`design-brief.md`; Screens + Mobile specifics in `agent-brief.md`; device/OS test matrix and offline scenarios in `qa-pack.md`;
`release-notes.md` (store "what's new" text, privacy label changes).

## 10. Review checks
Offline and permission-denied paths have AC; device/OS matrix defined; push notifications have exact text and deep links.

## 11. Extra stages
None.

---
name: ba-ux
description: UI/UX design step for a requirements feature, run only when the feature has a user interface. Checks applicability, then produces user journeys, screen inventory, navigation map, low-fidelity wireframes, screen states, content/microcopy, responsive and accessibility notes in 06-ux.md, plus an optional clickable HTML prototype. Use after stories are drafted, or when the BA asks for screens, wireframes, mock-ups, user journeys or a prototype. Tiếng Việt: màn hình, wireframe, hành trình người dùng, prototype, mọi trạng thái màn hình.
---

# /ba-ux — Design the experience (only if there is one)

> **Start:** `ba context <slug> ba-ux` (instead of reading whole files), then the stage card (MANUAL §8).
> Each turn ends with `ba turn <slug> --events …`; the stage ends with `ba turn … --gate --stage "6 UI/UX"`.

Stories say what users can do; this step shows **where and how** they do it, so the PO can see it,
designers can refine it, and builders don't invent screens.

## Step 0 — Is UX needed?

Start from `_status.md` → *Approach* → *Stage plan* row "6 UI/UX" and §6 *UX* of each active profile
(e.g. mobile-first focus, dashboard-only for data, AI output presentation). Then confirm against
`03-scope.md`, `04-model.md`, `05-stories.md`. UX applies if any in-scope item or story involves a
person interacting with a screen, form, email/notification layout, report/dashboard, or a change to an
existing screen.

- **Not applicable** (pure API, batch job, integration, back-office data fix): record in `_status.md` →
  Gates "6 UX: N/A — <reason>" and a `D-` if the BA confirms. Say so and point to `/ba-spec`. Stop.
- **Partly applicable**: scope this step to the stories with UI only; list which.
- **Applicable**: continue.

**Run Lite** (BA chose it on the stage card) still has a floor — the gate cannot pass until:
- ☐ the screen inventory lists **every** screen any story needs, including the ones not wireframed;
- ☐ **every** screen in the inventory has a state table (default, empty, loading, validation error, system
  error, success, permission-limited) — even without a wireframe;
- ☐ screens not designed are named in a "Not designed" list with the stories they serve, so the review,
  the design brief and the agent brief all show them.
## Step 1 — UX inputs (ask once, accept partial; unknowns become `Q-`/`A-`)

- Channels & devices (web desktop/mobile, native app, kiosk, email…) and minimum screen width
- Existing design system / UI kit / brand guidelines, or "match existing screens" (screenshots in `sources/`)
- Accessibility target (default proposal: WCAG 2.2 AA as an `A-`)
- Languages / locales; content tone
- Who designs further (in-house designer, agency, AI agent builds directly from wireframes)

## Step 2 — Build `06-ux.md` from `templates/06-ux.md`

1. **User journeys** — one per primary role/goal (Mermaid `journey` or `flowchart`): stages, actions,
   touchpoints, pain points removed (link to pain points in `01-intake.md`), emotional low points.
2. **Screen inventory** `SCR-NN` — name, purpose, roles (from permissions matrix), entry points,
   stories/AC covered, new vs changed.
3. **Navigation map** (Mermaid `flowchart`): screens and transitions, including back/cancel/error routes.
4. **Wireframes** — per screen, a low-fidelity layout as a fenced text block (boxes, labels, `[Button]`,
   `( ) radio`, `[x] checkbox`, `[____] input`, `▼ dropdown`). Low-fi on purpose: structure and content,
   not visual style.
5. **Elements table** per screen — element, type, data field (→ data dictionary in `07-spec.md`),
   behaviour, visible/enabled per role, validation (`BR-`), message (`MSG-`).
6. **States** per screen — default, empty, loading, partial data, validation error, system error,
   success/confirmation, permission-limited view, read-only/locked. Each missing state is a gap.
7. **Content & microcopy** — headings, labels, helper text, button labels, empty-state copy, confirmations.
   Error text lives once in the `MSG-` catalogue; reference it here.
8. **Responsive behaviour** — what changes per breakpoint (stacking, hidden columns, sticky actions).
9. **Accessibility notes** — focus order, keyboard paths, labels for icons, colour-independent status,
   error announcement, touch-target size.

## Step 3 — Prototype (optional, recommended for PO approval)

If the BA wants it, create `ux/prototype.html`: one self-contained file (inline CSS/JS, no external
libraries), grayscale low-fi style, one section per `SCR-`, clickable navigation following the map,
sample data from AC examples, and a visible banner "Low-fidelity prototype — not final design".
If a Figma or design-tool connector is available, offer to create frames there instead/as well (ask first).

## Step 4 — Check and close gaps

- Run `checklists/ux-heuristics.md` against every screen; record findings.
- Coverage: every story with UI → at least one `SCR-`; every AC with a user action → a screen element;
  every permission cell → visible/enabled rule; every `MSG-` used → a screen and state.
- New questions → `02-questions.md`; new fields or messages discovered → note for `/ba-spec`.
- Stories that changed meaning because of design decisions → update them and mention it.

## Gate
UX marked N/A with reason, **or**: all UI stories mapped to screens, all screens have wireframe +
states + elements, accessibility target set, heuristics check done, PO/designer feedback recorded as `D-`.

## Finish with
- **Done:** journeys, screens, states covered, prototype link if made.
- **Needs your decision:** design choices with options and a recommendation (e.g. wizard vs single form).
- **Next step:** show wireframes/prototype to PO and users; then `/ba-spec`.

# Approach Profiles

A feature's **approach** decides which stages run, how they run, which extra stages are added, and which
documents are produced. It is selected in `/ba-intake` (step 5) and stored in `_status.md` → *Approach*.
Every stage reads it and applies the matching sections of the active profiles.

The system is **open**: use the built-in profiles, install suggested ones from `catalogue.md`, write your own
with `/ba-profile`, and adjust any single feature with overrides — without touching the stages.

## 1. Where profiles come from

| Origin | Where | How to use |
|--------|-------|-----------|
| **Built-in** | `profiles/<name>.md` (`origin: built-in`) | Ready to use |
| **Catalogue** | `profiles/catalogue.md` (compact suggestions) | `/ba-profile install <name>` expands one into a full profile |
| **Custom** | `profiles/<name>.md` (`origin: custom`) | `/ba-profile new` interviews you and writes it from `_template.md` |
| **Per-feature override** | `_status.md` → *Approach* → *Overrides* | `/ba-profile override` — one feature only, no new profile |

`/ba-intake` considers **all active profiles** in this folder (any file with `status: active`, excluding
`_template.md`, `catalogue.md` and this README) and also scans the catalogue: if a catalogue profile fits
better than any active one, it suggests installing it. If nothing fits, it offers to create a custom one.

## 2. Active profiles

| Profile | Kind | Origin | Pick when the feature is mainly… |
|---------|------|--------|-----------------------------------|
| `web-app` | solution | built-in | screens used in a browser (portal, back-office, admin) |
| `mobile-app` | solution | built-in | a native or cross-platform app on phones/tablets |
| `api` | solution | built-in | an interface other software calls; no human UI |
| `integration` | solution | built-in | connecting existing systems / vendors |
| `batch` | solution | built-in | unattended scheduled or triggered processing |
| `data` | solution | built-in | reports, dashboards, analytics, pipelines |
| `ai-feature` | solution | built-in | behaviour produced by an AI/ML model |
| `small-change` | solution | catalogue | a bug fix, tweak or small enhancement (≤ 5 stories) |
| `workflow-approval` | solution | catalogue | requests moving between people: approvals, queues, SLAs, escalation |
| `cots-saas` | solution | catalogue | buying/configuring a product instead of building (vendor selection, fit-gap) |
| `data-migration` | solution | catalogue | moving data from old to new systems (profiling, mapping, cutover) |

`/ba-profile` keeps this table up to date when profiles are installed, created or retired.

## 3. Built-in work-type modifiers

| Modifier | Adds |
|----------|------|
| **New product** | Stronger problem/goal validation in Scope; MVP slice mandatory in Stories; consider a prototype for PO approval |
| **Change to existing system** | As-is and to-be in Model; impacted functions, backward compatibility, data migration and regression areas in Spec; regression section in QA pack |
| **Regulatory / compliance** | Compliance matrix in Spec; audit and retention NFRs mandatory; compliance sign-off added as a gate before Handoff |
| **Process-only (no system change)** | Skip UX/Spec technical sections; deliver process flows, RACI, procedures and training notes instead of an agent brief |

Custom modifiers are profile files with `kind: modifier` (e.g. multi-country, vendor-delivered).
They use the same headings but usually fill only the sections they change.

## 4. Profile anatomy (11 headings — keep them, stages look them up by number)

1. **Signals** 2. **Stage plan** 3. **Extra gap questions** 4. **Model** 5. **Stories** 6. **UX**
7. **Spec sections to add** 8. **NFR focus** 9. **Handoff extras** 10. **Review checks** 11. **Extra stages**

Front-matter: `name`, `title`, `kind`, `origin`, `version`, `owner`, `status`. See `_template.md`.

### Stage plan values
| Value | Meaning |
|-------|---------|
| **Run** | Standard stage as the stage file describes |
| **Adapted** | Runs, but its output takes the form the profile describes (e.g. requirement list instead of user stories) |
| **Lite** | Minimum viable version: only the items the profile names, no optional sections; same gate, smaller scope |
| **Partial** | Runs only for the scope items listed (e.g. UX for the admin console only) |
| **Skip** | Not run; `_status.md` records "N/A — <reason from profile>" |

Intake, Elicit and Scope always run (they may be **Lite**). Review never skips (it may be **Lite**:
mechanical checks + reviewer on changed items only).

### Extra stages
A profile may add stages that the core workflow doesn't have (vendor evaluation, threat model, data
profiling, cutover plan…). Each is defined in §11 with: ID, name, *after which stage* it runs, purpose,
steps, output document (`<NN><letter>-<id>.md`, e.g. `05a-vendor-eval.md`) and gate.
They appear in the feature's stage plan in order and are run with **`/ba-step <stage-id>`**.
If two active profiles put extra stages in the same slot (e.g. both use `07a-`), `/ba-intake` assigns the
letters in stage-plan order (`07a-`, `07b-`…) and records the actual file names in the feature's stage plan.

## 5. Combining profiles

- **Stage plan:** a stage runs if *any* active profile runs it; the strongest value wins
  (Run > Adapted > Partial > Lite > Skip). Skipped only if *all* skip it.
- **Questions, spec sections, NFRs, handoff extras, review checks, extra stages:** union of all active
  profiles, each applied to the scope items (`IS-`) that profile covers.
- **Conflicts** (e.g. one profile says UX is N/A, another needs it): the stricter rule wins, unless an
  override says otherwise.
- Record the mapping `profile → IS-` in `_status.md` → *Approach*.

## 6. Overrides (per feature)

When the approach is right but one feature needs something different — skip a stage, add a document, add a
question set, insert an extra stage from another profile — record an override instead of editing the profile:

| Override | Target | Change | Reason | Decision |
|----------|--------|--------|--------|----------|
| O-01 | Stage: UX | Partial → Skip | Admin screens reuse existing UI kit unchanged | D-014 |

Overrides win over profile rules. Overrides that repeat across features are a signal to update or create a
profile — `/ba-profile learn` suggests this.

## 7. Governance

- Bump `version` on every change; note what changed at the bottom of the profile.
- Changing a profile doesn't silently change features already past Scope: `/ba-profile edit` lists the
  features using it and asks whether to re-apply.
- `status: draft` profiles are offered at intake only when the BA asks for them.
- `status: retired` profiles are kept for features that used them but never offered for new ones.

# Supertutor.app — Layer 2 Design Spec

**Date:** 2026-07-30
**Status:** Superseded 2026-09-02 — `supertutor.app` as described here is not being built. See `tutorapp/docs/design.md` for the platform actually in development, and `docs/superpowers/plans/2026-09-02-state-model-decoupling-plan.md` (C6, C7) for why this document is kept rather than deleted: it's still the historical record of the design questions Layer 1's consumer contract was checked against.
**Scope:** `supertutor.app` — the hosted service. Reference-depth only; this is not a full product spec.

## 1. What this is

The hosted, paid service that runs the `supertutor-skills` library (Layer 1) for real learners: identity, persistence, billing, onboarding, multi-device access, and progress dashboards. This document assumes Layer 1 as already specified and does not redesign, extend, or duplicate it — see §2.

## 2. Dependency on Layer 1

> **Amended 2026-09-02** (C6): the "never modify Layer 1" rule below was
> written to protect Layer 1 from *this* consumer's pressure while a real
> build was still hypothetical. This document is now superseded (see the
> header) and `tutorapp` is the only real consumer, so the rule has no
> second stakeholder left to protect and was retired — replaced by
> ordinary versioned-release discipline (a consumer pins a tag and upgrades
> deliberately). Kept here, struck through in spirit rather than the text,
> as the record of what the rule was and why it no longer applies.

Layer 2 consumes `supertutor-skills` as a versioned, external package. The relationship is one-directional:

- Layer 2 code and configuration may depend on Layer 1's published contract (the skill set, the state model, `learner/config.md`'s key set — see the Layer 1 spec, `2026-07-30-supertutor-layer1-skills-design.md`).
- ~~Layer 1 must never be modified to make Layer 2 work. If a Layer-2 need requires a skill change, that change is proposed and versioned in the Layer 1 repo like any other consumer's feature request, then adopted here by bumping the pinned skill version — never patched locally.~~ *(Retired 2026-09-02, C6 — see note above.)*
- Layer 2 runs Layer 1's skills **unmodified**. The only input Layer 2 provides beyond what any consumer could provide is `learner/config.md`, populated per §4 below, using only keys Layer 1 already defines.

This is what keeps the free plugin and the paid service the same product at two depths rather than two diverging codebases.

## 3. Service architecture

- **Setup (once):** publish `supertutor-skills` to `POST /v1/skills` (pinned version). Create one Agent via `POST /v1/agents` — `claude-opus-5`, agent toolset enabled, skills pinned by `skill_id` + version. One environment. IDs stored in config, never created in the request path.
- **Per learner:** one memory store, created at signup. This is the concrete backing for Layer 1's abstract "directory of markdown files" contract — the memory store mounts into the session container as a filesystem, so Layer 1's skills read and write it with ordinary file tools, unaware it isn't a local disk.
- **Per session:** `POST /v1/sessions` with the agent, environment, `resources: [{type: "memory_store", memory_store_id, access: "read_write"}]`, kickoff via `initial_events`. Stream opened before anything is sent; browser relays the SSE feed. Drain gate: `session.status_terminated`, or `session.status_idle` with `stop_reason.type !== "requires_action"`.
- **Dashboard:** reads the memory store directly (list/read memories, list memory versions) — no separate database of learner state duplicating what Layer 1 already writes.
- **Minimum web surface:** auth, goal-setting flow, streamed tutoring view, progress view, billing.

## 4. Populating `learner/config.md`

Layer 1 defines this file's key set (review cadence) and works correctly with it absent. Layer 2's only obligation is to write valid values for whichever keys its product surface wants to expose — e.g., a "review discipline" account setting might tune the review-cadence key. Layer 2 does not add new keys unilaterally; a new knob is a Layer 1 change (§2), proposed the same way any consumer would propose one.

## 5. Open questions (flagged, not resolved here)

- **Cost per learner-hour.** `claude-opus-5` at $5/$25 per MTok over a sustained tutoring session is a real input to pricing, and `assessment-first-teaching` + `mastery-before-advancing` spend tokens deliberately (transfer tasks, evidence-gathering) rather than economizing. Needs a rough cost model before pricing is set — not attempted in this document.
- **Memory store lifecycle on churn.** What happens to a learner's memory store (and its full version history) on cancellation or account deletion is a retention/privacy decision, not an architecture one, but it needs an answer before launch.

## 6. Explicit non-goals (this document)

- Any pedagogy, skill content, or state-schema design — that's entirely Layer 1's, referenced here, never re-specified.
- Subject content or curricula — still out of scope at this layer too; Layer 2 hosts the process, it doesn't supply material.
- Full product spec: pricing model, onboarding UX, dashboard design, teacher/parent role. This document sketches only enough architecture to check Layer 1's design against a real consumer.

## Relationship to other documents

This service consumes the contract defined in `docs/superpowers/specs/2026-07-30-supertutor-layer1-skills-design.md`. That document is authoritative for anything about skills, strategies, or the state-file schema; this one only describes how a specific consumer uses it.

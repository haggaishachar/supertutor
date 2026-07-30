# Supertutor — Design Spec

**Date:** 2026-07-30
**Status:** Draft for review

## 1. What this is

A superpowers-style skills library for one-on-one tutoring: process discipline for teaching, the way superpowers is process discipline for software engineering. It targets a sustained, multi-session relationship between a self-directed learner and Claude — any subject, any age, any level — where the learner is also the operator (they set their own goals, no separate teacher/parent role).

The system is two independent layers with one contract between them.

## 2. Layer boundary

**Layer 1 — `supertutor-skills`.** A harness-agnostic Agent Skills library plus a state-file contract (directory shape and frontmatter for the learner model, curriculum, and session log). Installable as a Claude Code plugin. No accounts, no user identity, no auth, no database, no billing, no HTTP. Free, and shippable/usable on its own.

**Layer 2 — `supertutor.app`.** The hosted service: identity, persistence, billing, onboarding, multi-device access, progress dashboards. Runs Layer 1's skills unmodified on Managed Agents, with one memory store per learner mounted as the learner directory.

**The rule, stated so it can be checked mechanically:** *Layer 1 must not know Layer 2 exists.*

- No skill, schema, or file in Layer 1 references accounts, sessions-as-billing-units, subscriptions, HTTP, or any Layer-2 concept.
- Layer 1's only interface to the outside world is a directory of markdown files at a conventional relative path. It is written to work identically whether that directory is local disk (Claude Code) or a mounted memory store (Managed Agents) — and it cannot tell which, because nothing in a skill inspects the mount type.
- The one exception, and it is deliberately narrow: `learner/config.md`, a small fixed-key file that Layer 2 may write and skills read (mastery threshold, session-length hint, review cadence). Layer 1 defines the key set and defaults; Layer 2 populates it if it wants non-default behavior. Layer 1 works correctly with the file absent.
- Enforcement: Layer 1 ships and versions as a standalone repo/package. Its test suite (skill baselines, schema validation) runs with zero Layer-2 code present. If a Layer-1 change requires touching Layer-2 code to keep tests green, the boundary has been violated.

This makes the free plugin and the paid service genuinely the same product at two depths, not a marketing layer bolted onto private logic.

## 3. Multilingual from day 1

Language is a first-class learner attribute, not a translation layer bolted on afterward. This is cheap to get right now and expensive to retrofit, because it touches the state contract.

- **Conversation language** is whatever the learner uses; skills instruct Claude to teach, explain, and converse in the learner's language, matching register to the learner's own fluency (a beginner in the target subject who is also not fluent in the interface language gets simpler sentences in both dimensions — they're independent, not one dial).
- **State files are structurally language-neutral, content-wise learner-language.** `state:`, `evidence:` dates, concept IDs (`limits-of-sequences`), and file paths stay in a fixed vocabulary (English identifiers) so the schema, tooling, and any cross-language analytics don't fork per locale. Free-text fields — evidence descriptions, session log prose, misconception descriptions — are written in the learner's language, because that's what the learner (and a human reviewing their own file) will read.
- `learner/profile.md` carries a `language:` field (BCP-47 tag) from the first session. `adapting-to-the-learner` reads it alongside age/register; it is not inferred fresh each session.
- **Mixed-language subjects are expected, not an edge case** — a learner studying French *in* Hebrew, or coding *in* Japanese where identifiers and error messages are English. Skills treat "language of instruction" and "language of the subject's own artifacts" as separately trackable, both stored on the topic, not assumed equal to the interface language.
- No skill hardcodes English strings for learner-facing output. SKILL.md instruction text (to Claude) stays in English — that's the skill-authoring language — but every instruction that produces learner-facing text specifies "in the learner's language," not a literal string to emit.
- Nothing here is Layer-2 specific — this is Layer 1 scope. Layer 2's own web-app UI strings (buttons, dashboard labels) are ordinary product i18n and out of scope for this spec.

## 4. Layer 1: skill inventory

Thirteen skills (well under the 20-per-agent ceiling on the Layer-2 side).

| Skill | Enforces |
|---|---|
| `using-supertutor` | Router — no teaching before a skill is invoked |
| `setting-learning-goals` | "Learn X" → observable mastery criteria; YAGNI on scope |
| `planning-a-curriculum` | Prerequisite-ordered units, each with an exit check |
| `diagnosing-prior-knowledge` | Elicit the learner's current model before explaining |
| `assessment-first-teaching` | Mastery check written before the unit is taught |
| `running-a-teaching-loop` | Worked example → faded practice → independent; cognitive load management |
| `withholding-the-answer` | Hint ladders and productive struggle — and when to just tell |
| `diagnosing-errors` | Trace a wrong answer to its root misconception, don't just mark it wrong |
| `mastery-before-advancing` | Demonstration required to advance; self-report is not evidence |
| `resisting-difficulty-negotiation` | Holds the line against "just tell me" / "I get it, move on" |
| `adapting-to-the-learner` | Register, age, language, analogy domains |
| `spaced-review` | Retrieval-practice scheduling and interleaving |
| `updating-the-learner-model` | The commit — what's known/shaky/broken, with evidence |

## 5. State contract

```
learner/
  config.md                      # Layer-2 optional knobs; fixed key set, all defaulted
  profile.md                     # register, age band, language, analogy domains
  topics/<topic>/
    goals.md                     # observable mastery criteria
    curriculum.md                # prerequisite-ordered units + status
    knowledge/<concept>.md       # one file per concept
    misconceptions/<slug>.md     # one file per misconception
    reviews.md                   # spaced-review schedule
    log/YYYY-MM-DD.md            # session log, learner's language
```

One file per concept (not one large `learner.md`): surgical updates, readable diffs, and — on the Layer-2 memory-store backing — free per-file version history.

```yaml
---
concept: limits-of-sequences
state: unknown | shaky | known | mastered
evidence: solved 3 unseen ε-N proofs unaided, 2026-07-28
last_assessed: 2026-07-28
next_review: 2026-08-11
---
```

**Governing rule:** `state: mastered` may be written only by `mastery-before-advancing`, and only with a non-empty `evidence:` line naming a specific demonstration — never "learner said they understood." This is the one piece of schema-level enforcement standing in for the fact that there's no free test oracle for learning.

## 6. Layer 2: service architecture (reference — not part of Layer 1's contract)

Included so Layer 1's design can be checked against a real consumer, without leaking into Layer 1 itself.

- **Setup (once):** `packages/publish` uploads `skills/` to `POST /v1/skills` (versioned). One Agent via `POST /v1/agents` — `claude-opus-5`, agent toolset enabled, skills pinned by `skill_id` + version. One environment. IDs stored in config, never created in the request path.
- **Per learner:** one memory store, created at signup.
- **Per session:** `POST /v1/sessions` with the agent, environment, `resources: [{type: "memory_store", memory_store_id, access: "read_write"}]`, kickoff via `initial_events`. Stream opened before anything is sent; browser relays the SSE feed. Drain gate: `session.status_terminated`, or `session.status_idle` with `stop_reason.type !== "requires_action"`.
- **Dashboard:** reads the memory store directly (list/read memories, list memory versions) — no separate database of learner state.
- **Minimum web surface:** auth, goal-setting flow, streamed tutoring view, progress view, billing.

## 7. Testing approach

Per superpowers' `writing-skills` discipline: each skill gets a baseline run (observe an agent fail without the skill) before being written. Adversarial learner personas for baselining: the negotiator ("just tell me"), the false-confident ("yeah, got it"), the silent one, and the plausibly-wrong (coherent but incorrect mental model) — the last is what `diagnosing-errors` exists for.

**Build order** (dependency-driven, so a partial build stays coherent): state contract → `assessment-first-teaching` + `running-a-teaching-loop` → `mastery-before-advancing` + `diagnosing-errors` → `resisting-difficulty-negotiation` → `spaced-review`. Thirteen independent baselines is the real schedule risk in this plan; if time is short, cut from the end of this order, not from the middle.

## 8. Explicit non-goals (this spec)

- Layer-2 UI/UX design, pricing, and business model.
- A teacher/parent-facing role (out of scope per the brainstorming decision: learner is the sole operator).
- Per-subject content or curricula — Layer 1 supplies the teaching *process*, not subject material.
- Any Layer-2 code, schema, or infrastructure beyond the reference sketch in §6.

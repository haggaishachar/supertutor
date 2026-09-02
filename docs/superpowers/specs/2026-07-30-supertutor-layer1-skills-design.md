# Supertutor Skills — Layer 1 Design Spec

**Date:** 2026-07-30
**Status:** Draft for review
**Scope:** `supertutor-skills` — the standalone, harness-agnostic skills library only.

## 1. What this is

A superpowers-style skills library for one-on-one tutoring: process discipline for teaching, the way superpowers is process discipline for software engineering. It targets a sustained, multi-session relationship between a self-directed learner and Claude — any subject, any age, any level — where the learner is also the operator (they set their own goals; no separate teacher/parent role).

This document specifies Layer 1 only: the skills, the pedagogy strategy system, the state-file contract, and how they're tested. It has no dependency on, and makes no reference to, any particular consumer of that contract — see §8 for what that excludes, and the closing note for how this relates to other documents.

## 2. Consumer contract

> **Amended 2026-09-02** (C1 of
> `docs/superpowers/plans/2026-09-02-state-model-decoupling-plan.md`): this
> section originally named the interface as "a directory of markdown
> files." That achieved storage-independence only for storage that already
> looks like a filesystem — a consumer storing state elsewhere (e.g. a
> database) had to build a virtual filesystem to satisfy a contract whose
> actual purpose was to not care about storage. The text below reflects the
> corrected framing; nothing about the pedagogy changed.

Layer 1 exposes exactly one interface to whatever embeds it: a **state
model** — a profile, a topic's goals, its curriculum, one record per
concept, misconceptions, a review schedule, and a session log — defined in
`supertutor.schema` and described narratively in §6. A consumer binds that
model to whatever storage it has. Nothing in a skill inspects how that
binding is implemented — a local folder on a laptop, a mounted network
volume, and a document database are all indistinguishable to a skill, and
that's by design, not by accident.

Files remain the *reference* binding: `tools/validate_state.py` binds the
state model to a `learner/` directory of markdown files with YAML
frontmatter, and Layer 1's own test suite (§7) runs against that binding.
A consumer with different storage binds `supertutor.schema`'s models to its
own reads and writes directly, rather than emulating a directory to satisfy
a contract that was never really about directories.

The one narrow exception: skills read `learner/config.md` if present — a
small fixed-key file (review cadence, homework strictness) — and fall back
to built-in defaults if it's absent or missing keys. Layer 1 defines the
key set and the defaults. It does not define, require, or assume who writes
the file, or why.

**Enforcement, stated so it can be checked mechanically:** Layer 1 ships and versions as a standalone repo/package. Its test suite (skill baselines, schema validation) runs with zero external code present, using only the config-file defaults. If testing Layer 1 ever requires standing up a consumer, the boundary has been violated.

## 3. Multilingual from day 1

Language is a first-class learner attribute, not a translation layer bolted on afterward. This is cheap to get right now and expensive to retrofit, because it touches the state contract.

- **Conversation language** is whatever the learner uses; skills instruct Claude to teach, explain, and converse in the learner's language, matching register to the learner's own fluency (a beginner in the target subject who is also not fluent in the interface language gets simpler sentences in both dimensions — they're independent, not one dial).
- **State files are structurally language-neutral, content-wise learner-language.** `state:`, `evidence:` dates, concept IDs (`limits-of-sequences`), and file paths stay in a fixed vocabulary (English identifiers) so the schema, tooling, and any cross-language analytics don't fork per locale. Free-text fields — evidence descriptions, session log prose, misconception descriptions — are written in the learner's language, because that's what the learner (and a human reviewing their own file) will read.
- `learner/profile.md` carries a `language:` field (BCP-47 tag) from the first session. `adapting-to-the-learner` reads it alongside age/register; it is not inferred fresh each session.
- **Mixed-language subjects are expected, not an edge case** — a learner studying French *in* Hebrew, or coding *in* Japanese where identifiers and error messages are English. Skills treat "language of instruction" and "language of the subject's own artifacts" as separately trackable, both stored on the topic, not assumed equal to the interface language. **(Added 2026-09-02, C3.)** These live on `supertutor.schema.Topic` as `instruction_language`/`artifact_language`, both optional and defaulting to `profile.language` when unset — see `setting-learning-goals`, which establishes them when a topic is first created.
- No skill hardcodes English strings for learner-facing output. SKILL.md instruction text (to Claude) stays in English — that's the skill-authoring language — but every instruction that produces learner-facing text specifies "in the learner's language," not a literal string to emit.
- **The mechanical self-report check is an English-only backstop, not the enforcement mechanism (C2).** §6's rule that `mastered` requires a specific demonstration, never a self-report, is judged by `mastery-before-advancing` at write time — a human/LLM call, which works in any language. `supertutor.schema.default_is_self_report` is a deliberately weak phrase-list heuristic layered on top by the file binding's validator, and deliberately pluggable (`SelfReportDetector`) rather than extended per-locale — swap it for a locale-appropriate or model-backed detector rather than treating it as the real gate for a non-English learner.

## 4. Skill inventory

Fourteen skills (see §5 for why pedagogy strategies don't add to this count, and why that headroom matters for a consumer with its own skill-count ceiling).

| Skill | Enforces |
|---|---|
| `using-supertutor` | Router — no teaching before a skill is invoked |
| `setting-learning-goals` | "Learn X" → observable mastery criteria; YAGNI on scope — or, in syllabus mode (C4), recognizes that the criteria are externally fixed rather than negotiated |
| `planning-a-curriculum` | Prerequisite-ordered units, each with an exit check — or, for an externally mandated curriculum (C4), ingests the syllabus's own unit breakdown instead of generating one |
| `diagnosing-prior-knowledge` | Elicit the learner's current model before explaining |
| `assessment-first-teaching` | Mastery check written before the unit is taught |
| `selecting-a-pedagogy` | Chooses and logs a teaching strategy for the unit — see §5 |
| `running-a-teaching-loop` | Executes the selected strategy: worked example → faded practice → independent; cognitive load management |
| `withholding-the-answer` | Hint ladders and productive struggle — and when to just tell |
| `diagnosing-errors` | Trace a wrong answer to its root misconception, don't just mark it wrong |
| `mastery-before-advancing` | Demonstration required to advance; self-report is not evidence |
| `resisting-difficulty-negotiation` | Holds the line against "just tell me" / "I get it, move on" — in syllabus mode (C4), can point to "this is on the exam" rather than an inferred judgment |
| `adapting-to-the-learner` | Register, age, language, analogy domains |
| `spaced-review` | Retrieval-practice scheduling and interleaving |
| `updating-the-learner-model` | The commit — what's known/shaky/broken, with evidence |

## 5. Pedagogy strategy system

Teaching strategy is pluggable, not baked into `running-a-teaching-loop`'s behavior. This closes the "pedagogy agnostic" gap identified when comparing against a model-agnostic framework design, without adopting that design's typed-interface approach — the interface here is a document contract, not a class.

**Why strategies are reference files, not skills.** A pluggable strategy could be modeled as its own Agent Skill, but a consumer running these skills on Managed Agents caps an agent at 20 skills, and the 14 process skills above already claim most of that budget before subject variety is considered. Instead, strategies live as reference files inside `selecting-a-pedagogy`'s and `running-a-teaching-loop`'s skill directories (the same "heavy reference / reusable tool" pattern superpowers itself uses for supporting files). Adding a strategy means adding a file, not registering a new skill or reconfiguring any agent — so the extensibility goal is met without the skill-count cost.

**The strategy file contract.** Every strategy file answers the same five questions, so `selecting-a-pedagogy` can reason about any of them uniformly:

- **When to select it** — trigger conditions (concept type, learner state, what's already been tried and failed)
- **What it does** — the behavioral shape it produces (e.g., worked example before independent attempt; a chain of narrowing questions; deliberately hard unscaffolded problem first)
- **Inputs it needs** — concept, misconception (if any), learner state, prior strategies tried on this concept
- **Composition** — what it pairs well with (e.g., worked-examples → faded scaffolding is a natural sequence) and what it conflicts with
- **Fallback** — what "not landing" looks like for this strategy (e.g., three failed Socratic turns) and what to switch to

**Initial strategy set:** `worked-examples`, `scaffolding`, `socratic`, `retrieval-practice`, `interleaving`, `mastery-learning`. Chosen as the smallest set that covers both concept-introduction and consolidation phases, keeping the baseline-testing burden (§7) proportional to the rest of the build. `inquiry-based`, `deliberate-practice`, `productive-failure`, and `feynman` follow the same file contract and are explicitly future additions, not a closed set — a third party (or a future maintainer) can drop in a new strategy file without touching any other skill.

**Selection is explicit and logged, not an invisible model judgment call.** `selecting-a-pedagogy` runs once per unit (not per turn), reads the concept, the learner's current state, and `strategies_tried` on that concept (see §6), picks a strategy per the trigger conditions above, and writes the choice plus a one-line reason to the session log. This is what makes strategy selection inspectable and what lets `selecting-a-pedagogy` avoid re-trying a strategy that already failed on this concept.

## 6. State contract

> **Amended 2026-09-02** (C1, C3, C4, C5 of
> `docs/superpowers/plans/2026-09-02-state-model-decoupling-plan.md`): the
> state model is now defined in code, not only narratively — `supertutor.
> schema` is authoritative; this section describes the same thing in prose
> and shows the reference (file) binding's shape. Where the two disagree,
> `supertutor.schema` wins.

The state model — profile, per-topic metadata, goals, curriculum, one
record per concept, misconceptions, a review schedule, a session log — is
defined as Pydantic models in `supertutor.schema`. The file binding
(`tools/validate_state.py`, and the one Layer 1's own tests run against)
lays that model out as:

```
learner/
  config.md                      # Optional consumer-supplied knobs; fixed key set, all defaulted
  profile.md                     # register, age band, language, analogy domains
  topics/<topic>/
    topic.md                     # Optional; instruction/artifact language overrides (§3, C3)
    goals.md                     # observable mastery criteria; externally fixed in syllabus mode (C4)
    curriculum.md                # prerequisite-ordered units + status; externally_mandated + syllabus_ref in syllabus mode (C4)
    knowledge/<concept>.md       # one file per concept
    misconceptions/<slug>.md     # one file per misconception
    reviews.md                   # spaced-review schedule
    log/YYYY-MM-DD.md            # session log, learner's language
```

One file per concept (not one large `learner.md`): surgical updates, readable diffs, and — under a versioned storage backend — free per-file history.

```yaml
---
concept: limits-of-sequences
state: unknown | shaky | known | mastered
evidence: solved 3 unseen ε-N proofs unaided, 2026-07-28
last_assessed: 2026-07-28
next_review: 2026-08-11
strategies_tried: [worked-examples, socratic]
---
```

`strategies_tried` is append-only and written by `selecting-a-pedagogy` each time it picks a strategy for this concept — it's the memory that keeps strategy selection from repeating what already failed, and it's the field a downstream analytics feature would read to ask "which strategies actually work" (out of scope here — see §8).

**Governing rule:** `state: mastered` may be written only by `mastery-before-advancing`, and only with a non-empty `evidence:` line naming a specific demonstration — never "learner said they understood." This is the one piece of schema-level enforcement standing in for the fact that there's no free test oracle for learning; `supertutor.schema.Concept` enforces the non-emptiness structurally, for any binding.

**`config.md`'s key set (C5 adds one):**

```yaml
---
review_cadence: relaxed | standard | aggressive   # spaced-review's interval scaling; default standard
homework_strictness: strict | standard | lenient  # withholding-the-answer's hint-ladder depth; default standard
---
```

`homework_strictness` governs how many hint-ladder rungs get exhausted before conceding an answer (see `withholding-the-answer`). It does not touch `mastery-before-advancing`'s bar — a lenient hint ladder is not a lenient mastery bar (see `resisting-difficulty-negotiation`).

**`topic.md`'s fields (new, C3), all optional:**

```yaml
---
topic: calculus-limits
instruction_language: he    # defaults to profile.language when unset
artifact_language: fr       # defaults to profile.language when unset
---
```

**`curriculum.md`'s syllabus-mode fields (new, C4):**

```yaml
externally_mandated: true
syllabus_ref: "Ministry of Education, high-school math, 5 units, calculus cluster"
```

`syllabus_ref` is required when `externally_mandated` is true — enforced by `supertutor.schema.Curriculum`. It's a pointer to where the syllabus lives, not the syllabus content itself, which stays with the consumer per §8.

## 7. Testing approach

Per superpowers' `writing-skills` discipline: each skill gets a baseline run (observe an agent fail without the skill) before being written. Adversarial learner personas for baselining: the negotiator ("just tell me"), the false-confident ("yeah, got it"), the silent one, and the plausibly-wrong (coherent but incorrect mental model) — the last is what `diagnosing-errors` exists for.

**Strategy files get a lighter-weight check than skills**, since they're not independently invoked: does `selecting-a-pedagogy` choose a defensible strategy for a given concept/state pair, and does `running-a-teaching-loop` execute the chosen strategy's behavioral shape rather than defaulting to whichever one the model reaches for unprompted. Test against at least two concepts per strategy (one procedural, one conceptual) rather than baselining each strategy file as heavyweight as a full skill.

**Build order** (dependency-driven, so a partial build stays coherent): state contract → `assessment-first-teaching` + `running-a-teaching-loop` (with one strategy — `worked-examples` — wired through end to end) → `selecting-a-pedagogy` + remaining strategy files → `mastery-before-advancing` + `diagnosing-errors` → `resisting-difficulty-negotiation` → `spaced-review`. Fourteen skills plus six strategy files is the real schedule risk in this plan; if time is short, cut additional strategy files first (the contract supports adding them later without touching other skills), then cut from the end of the skill order, not the middle.

## 8. Explicit non-goals (this document)

- Any hosting, identity, billing, persistence backend, or web surface. These are a consumer's concern, out of scope here by construction (§2), not merely by choice.
- A teacher/parent-facing role (out of scope per the brainstorming decision: learner is the sole operator).
- Per-subject content or curricula — Layer 1 supplies the teaching *process*, not subject material.
- Cross-learner analytics or aggregation of any kind — the state contract is per-learner and local to that learner's directory.

## Relationship to other documents

This repo is one half of a two-part initiative; a separate document specifies a hosted service that consumes this contract (`docs/superpowers/specs/2026-07-30-supertutor-layer2-service-design.md`). That relationship is informational only — nothing in this document depends on it, and this document's own scope (§8) and test suite (§7) are both self-contained without it.

# Supertutor — State-Model Decoupling & Syllabus Mode

**Date:** 2026-09-02
**Status:** Proposed
**Owner:** Haggai Shachar
**Amends:** `docs/superpowers/specs/2026-07-30-supertutor-layer1-skills-design.md` (§2, §3, §6)
**Driven in part by:** `tutorapp` (see `tutorapp/docs/design.md`), which supersedes the
`supertutor.app` design in `docs/superpowers/specs/2026-07-30-supertutor-layer2-service-design.md`

## Why now

Three of the changes below are Layer 1 fixing its own internal contradictions, found by
building a real consumer against it. Two are new capability. One retires a governance rule
whose premise no longer holds.

The Layer 1 design set out to be storage-independent — its §2 says *"a local folder on a
laptop and a mounted network volume are indistinguishable to a skill, and that's by design."*
That intent is right. But the contract achieves it only for storage that already looks like
a filesystem, because it names *"a directory of markdown files"* as the interface itself
rather than as one binding of a state model. A consumer storing state in a database has to
build a virtual filesystem to satisfy a contract whose actual purpose was to not care about
storage. That is the contradiction C1 resolves.

## C1 — Decouple the state model from the filesystem

**Blocks `tutorapp` Phase 0. Everything else can follow.**

- Rewrite §2's consumer contract: the interface is a **state model**, not a directory.
  Consumers bind it to storage. Files remain the reference binding.
- Add `supertutor/schema.py` — Pydantic models for the state model (profile, goals,
  curriculum units, concept, misconception, reviews, log, config), with the vocabulary
  already fixed in §6 (`unknown | shaky | known | mastered`, evidence, `last_assessed`,
  `next_review`, `strategies_tried`).
- Rewrite the 14 `SKILL.md` files to reference state *concepts* rather than literal paths:
  *"check whether a learner profile exists"*, not *"check whether `learner/profile.md`
  exists"*. This is the bulk of the work and the part that needs care — the prose must stay
  readable to an agent that has never seen the schema module.
- Recast `tools/validate_state.py` as the **file-binding validator**, built on
  `schema.py` rather than duplicating field knowledge. Its path-kind inference and
  required-file logic remain file-binding concerns and stay there.

Ship as a minor version bump; `tutorapp` pins the tag.

## C2 — The self-report check is English-only, contradicting §3

§3 mandates that free-text fields — *"evidence descriptions, session log prose,
misconception descriptions"* — are written **in the learner's language**. But
`tools/validate_state.py:27-34` matches `evidence:` against a hardcoded list of English
phrases, and its own comment concedes *"it will not catch self-report evidence written in
other languages."*

So §6's governing rule — that `state: mastered` requires a specific demonstration, never a
self-report — is mechanically unenforced for any learner not working in English, which §3
declares a first-class case. Replace the phrase list with a language-agnostic check, or at
minimum make it pluggable and document plainly that the mechanical check is an English-only
backstop and not the enforcement mechanism.

*(This would be a defect with or without `tutorapp`. It happens to matter acutely there —
that product is Hebrew-first.)*

## C3 — Topic-level language fields are promised in §3, absent from §6

§3 states that skills treat *"'language of instruction' and 'language of the subject's own
artifacts' as separately trackable, **both stored on the topic**"* — and names the
mixed-language case exactly (*"a learner studying French in Hebrew"*).

No such fields exist in §6's state contract, in any frontmatter, or in the validator.
`profile.md` carries only a single global `language:`. Add them to the state model so the
behavior §3 promises has somewhere to live.

## C4 — Syllabus mode: externally mandated curricula

New capability, justified pedagogically rather than by consumer need.

`planning-a-curriculum` currently assumes the tutor designs the unit plan. A learner
preparing for a national exam has a curriculum that is **not the tutor's to design** — scope
is not negotiable, unit order is externally fixed, and mastery criteria are published rather
than inferred. That is a genuine teaching mode, and it is currently unrepresentable.

- State model: mark units as externally mandated, with a syllabus reference.
- `planning-a-curriculum`: ingest an authoritative syllabus rather than generate one.
- `setting-learning-goals`: criteria are externally fixed, not negotiated with the learner.
- `resisting-difficulty-negotiation`: gains a stronger and more honest move — *"this is on
  the exam"* rather than *"you haven't demonstrated mastery."*

**Subject material stays out**, per §8. Layer 1 models *that* a syllabus is authoritative;
the syllabus content itself belongs to the consumer.

## C5 — Homework-strictness config key

§2 defines `learner/config.md` as a small fixed-key file. Add a strictness key governing how
far the tutor goes toward supplying an answer.

This belongs in Layer 1, not in a consumer: it is exactly what `withholding-the-answer` and
`resisting-difficulty-negotiation` already govern. A consumer exposing it as a product
setting would otherwise be reaching into pedagogy through prompt injection, which is the
coupling §2 exists to prevent.

## C6 — Retire the "never modify Layer 1 for Layer 2" rule

That rule lives in the `supertutor.app` service design (§2) and was written to protect Layer
1 from a specific consumer's pressure. That consumer no longer exists — `tutorapp` supersedes
it, and there is exactly one consumer. In practice the rule was holding C2 and C3, both
Layer 1's own bugs, behind a change-request process with no second stakeholder to protect.

Replace with ordinary versioned-release discipline: consumers pin a tag and upgrade
deliberately. Restore the rule if a second real consumer ever appears.

## C7 — Mark the Layer 2 service design superseded

`docs/superpowers/specs/2026-07-30-supertutor-layer2-service-design.md` describes a product
that is not being built. Add a superseded header pointing at `tutorapp/docs/design.md`.
Status-header change only.

## C8 — Package `skills/` as package data

Found building `tutorapp` Phase 0 (Task 5), against this doc's own C1 assumption: a
non-file consumer loads skill/strategy prose via `importlib.resources`, not by reading a
git checkout at runtime (the latter would silently reintroduce the filesystem coupling C1
removed). But `pyproject.toml`'s `[tool.setuptools.packages.find]` only ever included
`supertutor*` and `tools*` — `skills/` (14 `SKILL.md` files, 6 `selecting-a-pedagogy/
strategies/*.md` files) was never part of the built wheel at all.

Fixed here: `skills/__init__.py` (a marker only — nothing under `skills/` is ever
imported, everything under it is read as text) plus `package-data` with a recursive
`**/*.md` glob, so every `SKILL.md` and strategy file ships without promoting each skill's
subdirectory to a Python package it has no other reason to be. Verified by building the
wheel and reading a file back via `importlib.resources.files("skills").joinpath(...)` —
not just inspecting the config.

Ships as `v0.2.1` — additive and non-breaking, so a patch bump rather than `v0.3.0`.

## Ordering

| Change | Depends on | When |
|---|---|---|
| C1 | — | First. Blocks `tutorapp` Phase 0. |
| C2, C3 | — | Independent bug fixes; any time |
| C6, C7 | — | Any time; trivial |
| C4, C5 | C1 | Phase 1 |
| C8 | — | Done — shipped as `v0.2.1`, found and fixed during `tutorapp` Task 5. |

## Test impact

§7's requirement is non-negotiable and must survive C1: *"Its test suite runs with zero
external code present... If testing Layer 1 ever requires standing up a consumer, the
boundary has been violated."*

C1 makes this easier rather than harder — the state model becomes testable directly, instead
of only through a filesystem. Concretely:

- `tests/fixtures/{valid,invalid}` become the conformance corpus for **any** binding. Both
  the file binding and a consumer's binding must agree on them.
- Skill baselines against the adversarial personas (negotiator, false-confident, silent,
  plausibly-wrong) run unchanged — they exercise pedagogy, not storage.
- C1's skill rewrites are the regression risk worth watching: prose that no longer names
  paths must still be concrete enough that an agent knows what to check and when.

## Explicitly not changing

- The pedagogy. All 14 skills and 6 strategy files keep their teaching content; C1 touches
  how they refer to state, not what they do.
- §6's governing rule that `mastered` requires demonstrated evidence, never self-report.
  C2 strengthens its enforcement; it does not relax it.
- §8's refusal to carry subject content or curricula. C4 models the *mode*, not the material.
- Standalone testability (§7), which is the main reason this repo stays separate at all.

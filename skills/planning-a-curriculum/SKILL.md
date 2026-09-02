---
name: planning-a-curriculum
description: Use when a topic's goals have been set but it has no curriculum yet - breaks a learning goal into prerequisite-ordered units, each with an explicit exit check, using the learner's diagnosed prior knowledge to skip what's already known. For an externally mandated syllabus, ingests it instead of generating one.
---

# Planning a Curriculum

## Two modes

**Tutor-designed (default).** You choose the units and their order — the
process below.

**Syllabus mode.** The learner's goal names an externally mandated
curriculum (a national exam, a course syllabus) — scope isn't yours to set,
unit order is externally fixed, and mastery criteria are published rather
than inferred. Ingest the syllabus's own unit breakdown rather than
generating one; still diagnose prior knowledge and order the *teaching* of
already-fixed units by prerequisite where the syllabus doesn't specify
otherwise. Mark the curriculum `externally_mandated`, with a reference to
the syllabus (see below). Subject material itself — what's actually on the
syllabus — is a consumer's concern, not this skill's; this skill only
records *that* a curriculum is externally sourced and follows it.

## Process (tutor-designed mode)

1. List every concept the goal requires, working backward from
   the mastery criteria to their prerequisites.
2. Order them so every unit's prerequisites appear earlier in the list.
3. Cross-reference the topic's existing concept states — any concept
   already `known` starts later in the sequence (still gets a light
   confirmation pass, not full re-teaching); anything `unknown` or `shaky`
   starts at the front of its dependency chain.
4. Each unit's exit check is its concept state reaching `state: mastered` —
   don't invent a separate exit mechanism.

## Record the curriculum

Shown here in the file binding's frontmatter/body shape:

```yaml
---
topic: calculus-limits
created: 2026-07-30
---

## Units (prerequisite order)

1. `sequences-notation` - status: not_started
2. `limits-intuition` - status: not_started
   - prerequisite: sequences-notation
3. `limits-of-sequences` - status: not_started
   - prerequisite: limits-intuition
4. `epsilon-n-proofs` - status: not_started
   - prerequisite: limits-of-sequences
```

For syllabus mode, add `externally_mandated: true` and `syllabus_ref:
<what the syllabus is and how to find it>` to the frontmatter — a reference,
not the syllabus content itself (that stays with the consumer, per Layer 1's
refusal to carry subject material).

`status` is `not_started`, `in_progress`, or `mastered` — kept in sync with
the corresponding concept's `state`. When a concept's `state`
becomes `mastered`, update the matching unit's `status` to `mastered` in
the same pass (see `mastery-before-advancing`, which owns this write for
the mastery case).

## Re-planning

If the learner's stated goal changes mid-curriculum, don't silently
re-order everything — surface the conflict and ask before rewriting units
already `in_progress` or `mastered`. In syllabus mode, "the goal changed"
usually means the syllabus itself changed (a new year's exam spec) — surface
that distinctly from an internally-negotiated scope change.

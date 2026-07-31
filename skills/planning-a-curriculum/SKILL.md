---
name: planning-a-curriculum
description: Use when goals.md exists and curriculum.md doesn't - breaks a learning goal into prerequisite-ordered units, each with an explicit exit check, using the learner's diagnosed prior knowledge to skip what's already known.
---

# Planning a Curriculum

## Process

1. List every concept the goal (`goals.md`) requires, working backward from
   the mastery criteria to their prerequisites.
2. Order them so every unit's prerequisites appear earlier in the list.
3. Cross-reference `learner/topics/<topic>/knowledge/*.md` — any concept
   already `known` starts later in the sequence (still gets a light
   confirmation pass, not full re-teaching); anything `unknown` or `shaky`
   starts at the front of its dependency chain.
4. Each unit's exit check is its concept file reaching `state: mastered` —
   don't invent a separate exit mechanism.

## Write `learner/topics/<topic>/curriculum.md`

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

`status` is `not_started`, `in_progress`, or `mastered` — kept in sync with
the corresponding concept file's `state`. When a concept file's `state`
becomes `mastered`, update the matching unit's `status` to `mastered` in
the same pass (see `mastery-before-advancing`, Task 18, which owns this
write for the mastery case).

## Re-planning

If the learner's stated goal changes mid-curriculum, don't silently
re-order everything — surface the conflict and ask before rewriting units
already `in_progress` or `mastered`.

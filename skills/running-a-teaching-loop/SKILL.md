---
name: running-a-teaching-loop
description: Use when actively teaching a curriculum unit - executes worked-example-to-independent-practice progression using the unit's selected pedagogy strategy, managing cognitive load one idea at a time.
---

# Running a Teaching Loop

## Which strategy to run

Check today's session log (`learner/topics/<topic>/log/YYYY-MM-DD.md`) for a
`strategy:` field already set for this unit. If present, read that strategy
file from `skills/selecting-a-pedagogy/strategies/<strategy>.md` and follow
it. If absent (no `selecting-a-pedagogy` pass has run yet for this unit,
or this is genuinely first exposure), default to `worked-examples` — this is
the correct default for first exposure to a procedural concept, not a
placeholder.

## The three-phase shape

Regardless of which specific strategy is active, don't collapse these
phases into one message:

1. **Modeling** — show or elicit the reasoning, per the active strategy's
   "what it does."
2. **Guided/faded practice** — the learner attempts with some support still
   present; support decreases across attempts. Invoke `withholding-the-answer`
   whenever the learner asks for or visibly needs a hint during this phase —
   don't just supply the answer inline.
3. **Independent practice** — the learner attempts unaided, ideally close to
   (but not identical to) the eventual mastery-check task.

## Cognitive load

Introduce one new idea per turn. If the learner is visibly struggling with
the current step, don't add a second new concept on top of it — consolidate
first.

## Ending the unit's teaching session

When independent practice is going well (or the session is ending for other
reasons), hand off to `updating-the-learner-model` to record what happened —
don't leave the session's outcome unrecorded.

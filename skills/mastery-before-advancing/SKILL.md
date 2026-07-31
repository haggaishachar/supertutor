---
name: mastery-before-advancing
description: Use when a learner claims understanding or asks to advance to the next unit - is the only skill permitted to mark a concept mastered, and requires an actual unseen demonstration, never a self-report, before doing so.
---

# Mastery Before Advancing

## The rule

`state: mastered` may only be written by this skill, and only with a
non-empty `evidence:` line naming a specific demonstration. A learner
saying "I get it" is not evidence — it's a request to be evaluated, not the
evaluation itself.

## Process

1. When a learner claims readiness or asks to move on, don't advance yet —
   administer the mastery-check task that `assessment-first-teaching`
   defined for this unit (an unseen problem, not one already practiced).
2. If the learner solves it correctly, unaided: write `state: mastered` to
   `learner/topics/<topic>/knowledge/<concept>.md`, with `evidence` naming
   the specific task and outcome (e.g. "solved unseen sequence
   (3n+1)/(n+2), correct limit and valid epsilon-N argument, unaided,
   2026-07-30"). Update the matching unit's `status` to `mastered` in
   `curriculum.md`.
3. If they don't solve it, or need help: do not mark `mastered`. Say so
   plainly and collaboratively ("close, but let's firm up [specific gap]
   before moving on") and hand back to `running-a-teaching-loop` — likely
   with `selecting-a-pedagogy` choosing `mastery-learning` next.

## Never accept these as evidence

- "I understand now"
- "That makes sense"
- "Got it"
- Getting a *guided* practice problem right (support was still present)
- Getting a problem right that's identical or near-identical to one already
  practiced

## Advancing the curriculum

Only after `state: mastered` is written does the next unit in
`curriculum.md` become eligible to start.

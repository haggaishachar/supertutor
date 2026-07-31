---
name: diagnosing-prior-knowledge
description: Use before teaching any unit for the first time, or when a learner signals prior exposure to the topic - elicits what the learner actually knows through diagnostic questions rather than assuming, before any explanation begins.
---

# Diagnosing Prior Knowledge

## The problem this prevents

Learners with real prior knowledge get bored and disengage when re-taught
from zero. Learners with no prior knowledge get lost when the tutor assumes
context they don't have. "I know some of this" is not enough to act on —
find out which parts.

## Process

For each concept in the topic's likely curriculum (even before
`planning-a-curriculum` has formally ordered them), ask 1-2 concrete
diagnostic questions per concept — not "do you know X?" (invites an
unreliable self-assessment) but a small task: "what's the limit of 1/n as n
gets large, and why?"

Never accept a vague self-report ("I think I get it", "it's fuzzy") as the
final answer — always follow up with one concrete question to locate exactly
where the fuzziness is.

## Recording results

For each concept probed, write or update
`learner/topics/<topic>/knowledge/<concept>.md`:

```yaml
---
concept: limits-of-sequences
state: shaky
evidence: correctly computed the limit of 1/n but could not explain why it never reaches 0
last_assessed: 2026-07-30
next_review:
strategies_tried: []
---
```

`state` at this stage is `unknown` (no exposure), `shaky` (partial/incorrect
model), or `known` (correct but untested against an unseen case) — never
`mastered`. Only `mastery-before-advancing` writes `mastered`, and only with
a demonstration, not a diagnostic answer.

## Don't over-diagnose

Two questions per concept is usually enough. This is a quick calibration
pass, not a full exam — deeper gaps surface naturally once teaching starts.

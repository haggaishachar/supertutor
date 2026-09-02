---
name: updating-the-learner-model
description: Use when ending any teaching interaction - commits what happened to the learner's concept states and session log with specific evidence, never a vague summary.
---

# Updating the Learner Model

## The rule

Every session that touches a concept ends with a written, specific update —
never "seemed to get it" or an unrecorded silent end.

## What to write

Update the concept's state:

```yaml
---
concept: limits-of-sequences
state: known
evidence: worked example correct; guided practice needed one hint on the epsilon-N setup; independent problem solved unaided, 2026-07-30
last_assessed: 2026-07-30
next_review:
strategies_tried: [worked-examples]
---
```

`evidence` must name what specifically happened — which attempt, what
level of support was needed — not a feeling. `state` here is `unknown`,
`shaky`, or `known` — this skill never writes `mastered` (that requires the
specific unseen-demonstration process in `mastery-before-advancing`, even
if today's independent practice went well; one good attempt during
teaching is not the same as a dedicated mastery check).

If a strategy was used this session, append it to `strategies_tried` if not
already present.

## Session log

Write or append to today's session log:

```yaml
---
date: 2026-07-30
topic: calculus-limits
unit: limits-of-sequences
strategy: worked-examples
strategy_reason: first exposure to a new procedural skill with no prior attempt on this concept
---

[narrative of what happened this session, in the learner's language]
```

If no strategy has been explicitly selected yet this session for any
reason, still record whichever strategy `running-a-teaching-loop` actually
used and a one-line reason — don't leave the field blank.

## Write in the learner's language

The narrative body and `evidence` line are free text — write them in the
learner's recorded language (the topic's instruction language if the topic
sets one, otherwise the profile's default — see `adapting-to-the-learner`
and `setting-learning-goals`). Frontmatter keys and `state`/`strategy`
values stay in the fixed English schema vocabulary.

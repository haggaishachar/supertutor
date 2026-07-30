---
name: using-supertutor
description: Use when a learner sends any message that could start a new topic, unit, or teaching interaction - establishes which supertutor skill to invoke and requires reading the learner directory before responding.
---

# Using Supertutor

## The rule

Never respond to a learner's teaching-related message without first checking
what `learner/` already contains for the relevant topic, and never explain
content directly from this skill — always hand off to the specific skill that
owns the situation.

## Before anything else

1. Check whether `learner/profile.md` exists. If not, this is a first
   contact — invoke `adapting-to-the-learner` before anything else.
2. Identify the topic the learner is asking about (or continuing). Check
   whether `learner/topics/<topic>/` exists.

## Routing table

| Learner's message looks like... | Invoke |
|---|---|
| "I want to learn X" / no `learner/topics/<topic>/` yet | `setting-learning-goals` |
| Goals exist, no `curriculum.md` yet | `planning-a-curriculum` |
| Curriculum exists, next unit's concept file doesn't exist or is `state: unknown` | `diagnosing-prior-knowledge`, then `assessment-first-teaching` |
| Unit is being actively taught this session | `selecting-a-pedagogy` (if not yet chosen this unit) then `running-a-teaching-loop` |
| Learner claims understanding / asks to move on | `mastery-before-advancing` (never take a claim as evidence — see that skill) |
| Learner gave a wrong answer | `diagnosing-errors` |
| Learner asks to skip practice, get the answer, or reduce scope | `resisting-difficulty-negotiation` or `withholding-the-answer`, depending on whether it's about pacing or about a specific hint |
| A concept in `reviews.md` is due and the learner has returned for a session | `spaced-review` |

## Hard rule

If none of the above skills has been invoked yet in this response, do not
teach, explain, or assess anything. Say what you're about to check and check
it first.

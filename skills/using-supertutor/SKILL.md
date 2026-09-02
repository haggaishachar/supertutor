---
name: using-supertutor
description: Use when a learner sends any message that could start a new topic, unit, or teaching interaction - establishes which supertutor skill to invoke and requires reading the learner's recorded state before responding.
---

# Using Supertutor

## State is a model, not a directory

These skills read and write **learner state**: a profile, a topic's goals,
its curriculum, one record per concept, misconceptions, a review schedule,
and a session log. Examples throughout these skills show that state's shape
using the file binding's YAML frontmatter, because a directory of markdown
files is Layer 1's reference binding — but nothing here requires a
filesystem specifically. Check state by the concept it represents ("does a
profile exist", "is this concept's state `known`"), not by a literal path;
whatever storage a given binding uses, it exposes the same state model.

## The rule

Never respond to a learner's teaching-related message without first checking
what's already recorded for the relevant topic, and never explain content
directly from this skill — always hand off to the specific skill that
owns the situation.

## Before anything else

1. Check whether a learner profile exists. If not, this is a first
   contact — invoke `adapting-to-the-learner` before anything else.
2. Identify the topic the learner is asking about (or continuing). Check
   whether that topic has any recorded state yet.

## Routing table

| Learner's message looks like... | Invoke |
|---|---|
| "I want to learn X" / no state recorded yet for this topic | `setting-learning-goals` |
| Goals exist, no curriculum yet | `planning-a-curriculum` |
| Curriculum exists, next unit's concept has no recorded state or is `state: unknown` | `diagnosing-prior-knowledge`, then `assessment-first-teaching` |
| Unit is being actively taught this session | `selecting-a-pedagogy` (if not yet chosen this unit) then `running-a-teaching-loop` |
| Learner claims understanding / asks to move on | `mastery-before-advancing` (never take a claim as evidence — see that skill) |
| Learner gave a wrong answer | `diagnosing-errors` |
| Learner asks to skip practice, get the answer, or reduce scope | `resisting-difficulty-negotiation` or `withholding-the-answer`, depending on whether it's about pacing or about a specific hint |
| A concept in the review schedule is due and the learner has returned for a session | `spaced-review` |

## Hard rule

If none of the above skills has been invoked yet in this response, do not
teach, explain, or assess anything. Say what you're about to check and check
it first.

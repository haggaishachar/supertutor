---
name: setting-learning-goals
description: Use when a learner states a new learning goal or an existing topic's goals.md doesn't exist yet - turns a stated goal into a scoped, observable mastery criteria list before any teaching begins.
---

# Setting Learning Goals

## The problem this prevents

"I want to learn X" is not a target you can teach toward or verify against.
Before any teaching starts, narrow it into criteria you could watch someone
demonstrate.

## Process

1. If the stated goal is broad ("learn calculus", "get good at Python"), ask
   one clarifying question to narrow it — what will they use it for, or what
   specifically prompted this. Don't interrogate; one question is usually
   enough.
2. Write 2-5 **observable** mastery criteria — each one something a learner
   could visibly do, not a feeling they could report. "Understands limits"
   is not observable. "Given an unseen sequence, states the correct limit
   and justifies it with an epsilon-N argument, unaided" is.
3. Confirm the scope with the learner in one sentence before proceeding —
   this is their goal, not yours to silently expand or narrow further.

## YAGNI on scope

Prefer a narrower goal that's actually achievable over a broad one that
sounds impressive. "Learn calculus" becomes "evaluate limits and derivatives
of polynomial and trig functions" — not "master all of single and
multivariable calculus." The learner can always ask to extend the goal later
once this one is met.

## Write `learner/topics/<topic>/goals.md`

```yaml
---
topic: calculus-limits
created: 2026-07-30
---

## Learning goal

Understand and apply the formal definition of a limit to evaluate limits of
sequences and prove convergence using an epsilon-N argument.

## Observable mastery criteria

- Given an unseen sequence, states the correct limit and justifies it with an
  epsilon-N argument, unaided.
- Explains why a proposed epsilon-N argument is or isn't valid for a given
  counter-example.
- Distinguishes convergent from divergent sequences for at least 4 unseen
  examples without external hints.
```

Write the body in the learner's language (`learner/profile.md`); keep the
frontmatter (`topic`, `created`) in the fixed schema vocabulary.

---
name: diagnosing-errors
description: Use when a learner gives an incorrect answer during practice - traces the error to its root misconception through follow-up questions rather than simply marking it wrong and supplying the correct answer.
---

# Diagnosing Errors

## The problem this prevents

A wrong answer is a symptom, not the diagnosis. "Not quite, the answer is
X" corrects this one instance without addressing the underlying model that
produced it — the same misconception will resurface on the next problem
that exercises it.

## Process

1. Don't immediately supply the correct answer. Ask a follow-up that
   probes *why* they answered as they did — "what does 'the limit' mean to
   you here?" not "try again."
2. Look for a coherent-but-wrong mental model behind the answer, not just a
   careless slip. A learner who says "the limit of 1/n doesn't exist
   because it never reaches 0" isn't confused about arithmetic — they're
   conflating "limit" with "attained value." That's the actual thing to
   fix.
3. Once located, name it plainly to yourself (not necessarily to the
   learner in clinical terms) and record it.

## Recording

Write `learner/topics/<topic>/misconceptions/<slug>.md`:

```yaml
---
concept: limits-of-sequences
slug: confuses-limit-with-attained-value
detected: 2026-07-30
resolved: false
---

## Description

Learner treats "the limit" as requiring the sequence to actually reach that
value, rather than a value the terms approach arbitrarily closely. Surfaced
when asked for the limit of 1/n; answered "there isn't one because it never
actually reaches 0."
```

## After diagnosis

Hand off to `selecting-a-pedagogy` with this misconception as context — it
often points toward `socratic` (question toward the specific gap) rather
than another worked example of the same procedure, since the error is
conceptual, not procedural.

## Resolving

When later evidence shows the learner no longer holds this misconception
(e.g. correctly handles a similar case unaided), set `resolved: true` — via
`updating-the-learner-model`, not by silently leaving the file stale.

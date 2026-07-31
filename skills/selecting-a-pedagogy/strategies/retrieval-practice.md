# Strategy: Retrieval Practice

## When to select it

The concept's `state` is already `known` or `mastered` and it's due for
review per `learner/topics/<topic>/reviews.md` (see `spaced-review`, which
is this strategy's primary caller).

## What it does

Ask the learner to recall and apply the concept without any re-teaching or
reminder first — the point is retrieving from memory, not recognizing a
re-explanation. Offer no hints unless the learner is genuinely and fully
stuck (not just slow).

## Inputs it needs

The concept, and prior evidence from its concept file that it was known or
mastered.

## Composition

The default strategy inside `spaced-review` sessions; often combined with
`interleaving` when multiple due concepts are reviewed together.

## Fallback

If recall fails entirely (not just slow — actually wrong or blank), treat
this as a state regression: update the concept file's `state` toward
`shaky`, not `known`/`mastered`, and hand off to `scaffolding` rather than
re-running `worked-examples` from a first-exposure assumption — the learner
has seen this before, even if it didn't stick.

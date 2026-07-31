---
name: spaced-review
description: Use when a session starts with reviews.md concepts due, or when scheduling review after a concept reaches known/mastered - runs retrieval practice on due concepts before new material, and schedules future review intervals.
---

# Spaced Review

## The rule

If `learner/topics/<topic>/reviews.md` has any concept with `next_review`
on or before today, address it before starting new curriculum content this
session — don't let due reviews accumulate silently while advancing new
units.

## Running the review

Invoke the `retrieval-practice` strategy for each due concept. If two or
more are due together, invoke `interleaving` to mix practice across them
rather than reviewing each in a fully separate block.

## Scheduling

When a concept first reaches `state: known` or `mastered` (via
`updating-the-learner-model` or `mastery-before-advancing`), add or update
its row in `reviews.md`:

```yaml
---
topic: calculus-limits
---

## Schedule

| concept | last_reviewed | next_review | interval_days |
|---|---|---|---|
| sequences-notation | 2026-07-20 | 2026-08-03 | 14 |
```

Default interval progression after a successful review: 1 day, then 3, then
7, then 14, then 30 (each successful retrieval roughly doubles the prior
interval — standard spacing progression). Scale all intervals by
`learner/config.md`'s `review_cadence`: `relaxed` lengthens intervals
(~1.5x), `standard` uses them as given, `aggressive` shortens them (~0.6x).
Config absent means `standard`.

## On a failed review

Per `retrieval-practice`'s fallback: reset the interval progression back to
the start (1 day) rather than continuing to lengthen it — a failed recall
means the concept needs to re-establish itself, not that the schedule was
merely slightly early.

---
name: selecting-a-pedagogy
description: Use when teaching begins or resumes on a curriculum unit, once per unit - chooses a teaching strategy from the available strategy files based on the concept's type and history, and logs the choice with a reason.
---

# Selecting a Pedagogy

## When this runs

Once per unit, before `running-a-teaching-loop` starts (or resumes) teaching
it this session — not every turn.

## Process

1. Read the concept's `state` and `strategies_tried`.
2. Read every strategy file under this skill's `strategies/` subdirectory
   and check each one's "When to select it" section against the concept's
   type (procedural vs. conceptual, from the topic's goals or how the
   concept is described) and history.
3. Never re-select a strategy that's already appeared twice in a row in
   `strategies_tried` for this concept without a clear reason (e.g. the
   strategy's own fallback explicitly says to switch) — repeating a failed
   approach a third time with no change is the failure this skill exists to
   prevent.
4. If a strategy's fallback condition is met (e.g. "after two failed
   attempts, switch to scaffolding"), follow it rather than re-deriving a
   choice from scratch.

## Recording the choice

Write to today's session log frontmatter:

```yaml
strategy: scaffolding
strategy_reason: worked-examples tried twice per strategies_tried with no progress; scaffolding is worked-examples' documented fallback
```

The reason is one line, specific to this decision — not a generic
restatement of the strategy's description.

## Adding new strategies

This skill does not need to change when a new strategy file is added to
`strategies/` — it reads whatever is present. A new strategy becomes
selectable the moment its file exists.

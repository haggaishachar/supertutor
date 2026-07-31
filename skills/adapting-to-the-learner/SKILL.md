---
name: adapting-to-the-learner
description: Use when a learner makes first contact, or whenever their register, age, or language doesn't match what learner/profile.md records - establishes and maintains the learner's language, age register, and analogy interests.
---

# Adapting to the Learner

## On first contact (no `learner/profile.md`)

Determine, from what the learner already told you or by asking directly:

- **Language**: the language they wrote in is the default; don't ask them to
  switch. Store as a BCP-47 tag (e.g. `he`, `en`, `ja`).
- **Register**: coarse age band — `child`, `teen`, or `adult`. Infer from
  context (stated grade, phrasing) before asking outright.
- **Analogy domains**: 1-3 things the learner is into (sports, games, a
  hobby) — ask once, briefly, don't interrogate.

Write `learner/profile.md`:

```yaml
---
language: he
register: child
analogy_domains: [soccer]
---
```

## Every session after

Read `learner/profile.md` before generating any learner-facing text. Write and speak
in `language`. Match vocabulary and sentence complexity to `register` —
short sentences and concrete examples for `child`, more abstraction
tolerated for `teen`/`adult`. Draw analogies from `analogy_domains` when they
genuinely clarify the concept — don't force one in every explanation.

## Two independent dimensions

Subject fluency and interface-language fluency are not the same axis. A
teenager fluent in the interface language but brand new to the subject needs
subject-level simplicity, not language-level simplicity. A younger child who
is a native speaker of the interface language needs both. Don't collapse
these into one setting.

## Revisit, don't re-ask

If a learner's phrasing suggests `register` was set wrong (too easy or too
hard), update `profile.md` — but don't interrogate them about it; infer and
adjust.

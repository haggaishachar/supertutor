---
name: withholding-the-answer
description: Use when a learner asks for the answer directly or is visibly stuck during practice - applies a hint ladder before giving the answer, except for arbitrary facts and notation, which should be told directly.
---

# Withholding the Answer

## The two failure modes this prevents

Giving the answer immediately robs the learner of the productive struggle
that builds real understanding. Refusing to ever just tell them wastes their
goodwill on things that were never discoverable in the first place —
notation, terminology, and conventions are arbitrary; nobody derives that
"∫" means integral.

## When to just tell (no hint ladder)

If the question is about a name, symbol, convention, or fact with no
underlying reasoning to discover — answer directly and briefly, then move
on. Don't Socratically interrogate someone about what a symbol is called.

## When to use the hint ladder (reasoning/problem-solving is being avoided)

1. **Restate the goal** — "what are you trying to find here?"
2. **Point at the relevant piece** — "look at what happens as n gets large"
   — without doing the step for them.
3. **Ask a narrower question** — reduce the problem to the specific stuck
   point.
4. **Offer a partial structure** — fill in one step, leave the rest.
5. **If still stuck after step 4**, give the answer — but walk through why,
   not just what, and note this concept needs another pass (record via
   `updating-the-learner-model`).

How far to actually go before conceding scales with the config's
`homework_strictness` (default `standard`, the ladder as numbered above):
`strict` holds an extra narrower rung before conceding past step 4 rather
than giving the answer immediately; `lenient` shortens the ladder, conceding
after step 3 if the learner still insists. This tunes *pacing* only — it
never substitutes for the ladder entirely, and it doesn't touch
`mastery-before-advancing`'s bar (see `resisting-difficulty-negotiation`).

## Handling "just tell me"

Don't comply immediately, and don't lecture them about productive struggle
either — acknowledge the request, offer one hint at the current ladder rung,
and continue. If they insist after two rungs, honor it — repeated stonewalling
erodes trust — but this is a signal for `resisting-difficulty-negotiation` if
the pattern generalizes across problems rather than one hard one.

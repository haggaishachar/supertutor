---
concept: one-step-equations
slug: applies-shown-operation-instead-of-inverse
detected: 2026-07-31
resolved: true
---

## Description

Learner repeats the operation already visible in the equation (e.g.
subtracting again) instead of applying its inverse to isolate `x`. Surfaced
during the diagnostic on `x - 8 = 15` (answered 7, i.e. 15 - 8, instead of
22); recurred during guided practice on `x - 7 = 15` (answered 8, i.e.
15 - 7, instead of 22). Both times the learner treated "minus" in the
equation as an instruction to subtract again on the other side, rather than
recognizing it as the operation to undo.

Resolved via Socratic follow-up in the moment ("what's the opposite of
subtracting 7?"), but that was a guided correction, not an unaided
demonstration — left `resolved: false` at first for exactly that reason.

Update 2026-07-31 (later the same session): the misconception recurred
once more under a real, unhinted mastery check (x - 12 = -3, answered -15
instead of 9) — confirming it hadn't actually resolved yet, vindicating
the `false` setting above. After two further unaided correct reps under
mastery-learning (x - 4 = -10 -> -6; x - 20 = 5 -> 25) and a final unseen
mastery-check pass (x - 15 = -8 -> 7, verified by substitution), the
learner now consistently applies the inverse operation without support.
Set `resolved: true` here, via updating-the-learner-model, not left stale.

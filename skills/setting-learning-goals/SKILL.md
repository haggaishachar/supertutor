---
name: setting-learning-goals
description: Use when a learner states a new learning goal or an existing topic has no goals recorded yet - turns a stated goal into a scoped, observable mastery criteria list before any teaching begins. For an externally mandated syllabus, records that the criteria are fixed rather than negotiating them.
---

# Setting Learning Goals

## The problem this prevents

"I want to learn X" is not a target you can teach toward or verify against.
Before any teaching starts, narrow it into criteria you could watch someone
demonstrate.

## Two modes

**Negotiated (default).** The process below — narrow scope with the
learner, then confirm it with them.

**Syllabus mode.** The stated goal names an externally mandated curriculum
("I need to pass the Bagrut," "this is my course syllabus") — the mastery
criteria are published, not yours or the learner's to set. Skip the
narrowing/confirming dialogue below; instead confirm which syllabus and
which portion of it applies, and record it plainly ("your goal is what this
syllabus requires — I'll follow its scope, not narrow it"). The curriculum
itself gets marked externally mandated by `planning-a-curriculum`, which
this skill hands off to next; this skill's own job is just to recognize the
mode and not pretend the criteria are negotiable when they aren't.

## Process (negotiated mode)

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
once this one is met. (Syllabus mode has no equivalent step — scope isn't
yours to narrow there.)

## Establishing the topic

The first skill to touch a new topic also establishes its language fields,
separate from the learner's profile-level default: **instruction language**
(what you teach *in*) and **artifact language** (the language of the
subject's own material — notation, terminology, source text). Both default
to the profile's language unless the goal itself implies otherwise (a
learner studying French *in* Hebrew has instruction language `he` and
artifact language `fr`). Record this once, when the topic is created; don't
re-derive it every session.

## Record the goals

Shown here in the file binding's frontmatter/body shape:

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

Write the body in the learner's language (per the learner's profile); keep
the frontmatter (`topic`, `created`) in the fixed schema vocabulary. The
topic's instruction/artifact language fields, if set, live alongside this in
the topic's own state, not in this file's frontmatter.

# Supertutor Layer 1 (supertutor-skills) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the standalone `supertutor-skills` library — 14 Agent Skills, a 6-file pedagogy strategy set, the state-file contract, and a schema validator — installable as a Claude Code plugin, with zero dependency on any hosting layer.

**Architecture:** Skills are plain `SKILL.md` files (Agent Skills format) under `skills/`, each tested via the writing-skills RED/GREEN discipline (baseline subagent run without the skill, then with it). Pedagogy strategies are markdown reference files under `skills/selecting-a-pedagogy/strategies/`, not separate skills. Learner state is a directory of YAML-frontmatter markdown files under a `learner/` root, validated by a small Python script with real pytest coverage.

**Tech Stack:** Markdown (Agent Skills format) for all skill/strategy content. Python 3.11+, PyYAML, pytest for the schema validator only. No other runtime dependencies — per the spec's consumer-contract requirement, Layer 1's test suite must run with zero external code present.

## Global Constraints

- Skill frontmatter has exactly two required fields, `name` and `description`; `name` uses letters/numbers/hyphens only; `description` is third-person and starts with "Use when..."; combined frontmatter stays under 1024 characters. (Source: superpowers:writing-skills.)
- No skill or schema file references accounts, billing, HTTP, sessions-as-billing-units, or any other hosting-layer concept. (Spec §2.)
- `learner/config.md` keys — `mastery_threshold` (default `3`), `session_length_hint` (default `medium`), `review_cadence` (default `standard`) — are all optional; every skill must work correctly with the file absent. (Spec §2, §4.)
- `state: mastered` may be written only by the `mastery-before-advancing` skill, and only with a non-empty `evidence:` line naming a specific demonstration — never a self-report phrase ("learner said...", "learner thinks they understand", "got it"). (Spec §6 — this is the one governing rule enforced by both a skill and the validator.)
- State file keys, enums, concept IDs, and paths stay in fixed English vocabulary; free-text fields (evidence descriptions, session logs, misconception descriptions) are written in the learner's language. No skill hardcodes English strings for learner-facing output. (Spec §3.)
- Pedagogy strategies live as markdown reference files, never as separate registered Agent Skills. (Spec §5.)

---

## File Structure

```
supertutor/
  skills/
    using-supertutor/SKILL.md
    adapting-to-the-learner/SKILL.md
    setting-learning-goals/SKILL.md
    diagnosing-prior-knowledge/SKILL.md
    planning-a-curriculum/SKILL.md
    assessment-first-teaching/SKILL.md
    running-a-teaching-loop/SKILL.md
    withholding-the-answer/SKILL.md
    updating-the-learner-model/SKILL.md
    selecting-a-pedagogy/
      SKILL.md
      strategies/
        worked-examples.md
        scaffolding.md
        socratic.md
        retrieval-practice.md
        interleaving.md
        mastery-learning.md
    mastery-before-advancing/SKILL.md
    diagnosing-errors/SKILL.md
    resisting-difficulty-negotiation/SKILL.md
    spaced-review/SKILL.md
  tools/
    validate_state.py
  tests/
    fixtures/
      valid/
      invalid/
    test_validate_state.py
  .claude-plugin/
    plugin.json
  README.md
```

**Baseline testing protocol** (applies to every skill task below, stated once here rather than repeated 14 times): dispatch a subagent (Agent tool, `subagent_type: general-purpose`, no access to the skill being tested) with the scenario prompt given in the task. Record its behavior against the task's pass rubric — this is the RED baseline. Then dispatch a fresh subagent with the same scenario prompt, this time told to load and follow the new `SKILL.md` (paste its contents into the prompt, since the skill isn't installed as a plugin yet during development). Record behavior against the same rubric — this is GREEN. A task is not done until GREEN passes on all rubric bullets; if it doesn't, revise the skill and re-run GREEN before committing.

---

## Task 1: State schemas, validator, plugin scaffold

**Files:**
- Create: `.claude-plugin/plugin.json`
- Create: `README.md`
- Create: `tools/validate_state.py`
- Test: `tests/test_validate_state.py`
- Create: `tests/fixtures/valid/*.md`, `tests/fixtures/invalid/*.md`

**Interfaces:**
- Consumes: nothing (first task).
- Produces: `tools.validate_state.validate(path: str, kind: str) -> list[str]` (returns list of error strings, empty = valid) and `tools.validate_state.infer_kind(path: str) -> str`, which derives `kind` from a path so callers don't have to track it themselves. `kind` is one of `"config"`, `"profile"`, `"goals"`, `"curriculum"`, `"concept"`, `"misconception"`, `"reviews"`, `"log"`. Every later task's file-writing steps are checked against these functions.

- [ ] **Step 1: Write the failing tests**

Create `tests/fixtures/valid/concept-mastered.md`:

```markdown
---
concept: limits-of-sequences
state: mastered
evidence: solved 3 unseen epsilon-N proofs unaided, 2026-07-28
last_assessed: 2026-07-28
next_review: 2026-08-11
strategies_tried: [worked-examples, socratic]
---
```

Create `tests/fixtures/invalid/concept-mastered-no-evidence.md`:

```markdown
---
concept: limits-of-sequences
state: mastered
evidence: ""
last_assessed: 2026-07-28
next_review: 2026-08-11
strategies_tried: [worked-examples]
---
```

Create `tests/fixtures/invalid/concept-mastered-self-report.md`:

```markdown
---
concept: limits-of-sequences
state: mastered
evidence: learner said they understood it
last_assessed: 2026-07-28
next_review: 2026-08-11
strategies_tried: [worked-examples]
---
```

Create `tests/fixtures/valid/config-empty.md` (empty file — tests the "absent/empty is valid, defaults apply" rule):

```markdown
```

Create `tests/fixtures/valid/config-full.md`:

```markdown
---
mastery_threshold: 4
session_length_hint: short
review_cadence: aggressive
---
```

Create `tests/fixtures/invalid/config-bad-enum.md`:

```markdown
---
mastery_threshold: 4
session_length_hint: extremely-long
review_cadence: aggressive
---
```

Create `tests/test_validate_state.py`:

```python
import pytest
from tools.validate_state import validate


def test_valid_mastered_concept_has_no_errors():
    errors = validate("tests/fixtures/valid/concept-mastered.md", "concept")
    assert errors == []


def test_mastered_concept_requires_nonempty_evidence():
    errors = validate("tests/fixtures/invalid/concept-mastered-no-evidence.md", "concept")
    assert any("evidence" in e for e in errors)


def test_mastered_concept_rejects_self_report_evidence():
    errors = validate("tests/fixtures/invalid/concept-mastered-self-report.md", "concept")
    assert any("self-report" in e for e in errors)


def test_concept_requires_valid_state_enum():
    errors = validate("tests/fixtures/invalid/concept-mastered-no-evidence.md", "concept")
    # state is valid here; this fixture should NOT flag state itself
    assert not any(e.startswith("state:") for e in errors)


def test_empty_config_is_valid():
    errors = validate("tests/fixtures/valid/config-empty.md", "config")
    assert errors == []


def test_full_config_is_valid():
    errors = validate("tests/fixtures/valid/config-full.md", "config")
    assert errors == []


def test_config_rejects_bad_enum():
    errors = validate("tests/fixtures/invalid/config-bad-enum.md", "config")
    assert any("session_length_hint" in e for e in errors)


def test_missing_file_is_valid_for_config_and_profile_only():
    # config and profile are the only optional files per the spec's consumer contract
    assert validate("tests/fixtures/does-not-exist.md", "config") == []


def test_missing_file_is_invalid_for_concept():
    errors = validate("tests/fixtures/does-not-exist.md", "concept")
    assert any("not found" in e for e in errors)


def test_infer_kind_for_every_path_shape():
    from tools.validate_state import infer_kind

    cases = {
        "learner/config.md": "config",
        "learner/profile.md": "profile",
        "learner/topics/calculus-limits/goals.md": "goals",
        "learner/topics/calculus-limits/curriculum.md": "curriculum",
        "learner/topics/calculus-limits/knowledge/limits-of-sequences.md": "concept",
        "learner/topics/calculus-limits/misconceptions/confuses-limit-with-attained-value.md": "misconception",
        "learner/topics/calculus-limits/reviews.md": "reviews",
        "learner/topics/calculus-limits/log/2026-07-30.md": "log",
    }
    for path, expected_kind in cases.items():
        assert infer_kind(path) == expected_kind, path
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_validate_state.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'tools'` (module doesn't exist yet). 10 tests should be collected once the module exists (9 direct assertions plus `test_infer_kind_for_every_path_shape`, which loops over 8 cases in one test function).

- [ ] **Step 3: Write the validator**

Create `tools/__init__.py` (empty file, makes `tools` importable).

Create `tools/validate_state.py`:

```python
"""Schema validator for supertutor-skills state files.

Every state file is a markdown file with an optional YAML frontmatter
block delimited by `---` lines. This module checks frontmatter fields
against the schemas defined in docs/superpowers/specs/
2026-07-30-supertutor-layer1-skills-design.md section 6.
"""

import os

import yaml

CONCEPT_STATES = {"unknown", "shaky", "known", "mastered"}
SESSION_LENGTH_HINTS = {"short", "medium", "long"}
REVIEW_CADENCES = {"relaxed", "standard", "aggressive"}

# Files that are allowed to be absent entirely — everything else must exist.
OPTIONAL_KINDS = {"config", "profile"}

SELF_REPORT_PHRASES = [
    "learner said",
    "learner reported",
    "learner thinks they understand",
    "learner claims",
    "i understand",
    "got it",
]


def _read_frontmatter(path):
    """Return the parsed frontmatter dict, or {} if there is none."""
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    parsed = yaml.safe_load(parts[1])
    return parsed or {}


def _is_self_report(evidence):
    lowered = evidence.lower()
    return any(phrase in lowered for phrase in SELF_REPORT_PHRASES)


def infer_kind(path):
    """Infer the schema `kind` for a state file from its path, relative to
    the `learner/` root (e.g. `learner/topics/<topic>/knowledge/<c>.md`)."""
    normalized = path.replace(os.sep, "/")
    parts = normalized.split("/")
    filename = parts[-1]
    if filename == "config.md":
        return "config"
    if filename == "profile.md":
        return "profile"
    if filename == "goals.md":
        return "goals"
    if filename == "curriculum.md":
        return "curriculum"
    if filename == "reviews.md":
        return "reviews"
    if "knowledge" in parts:
        return "concept"
    if "misconceptions" in parts:
        return "misconception"
    if "log" in parts:
        return "log"
    raise ValueError(f"cannot infer kind for path: {path}")


def validate(path, kind):
    """Validate a state file against its schema. Returns a list of error
    strings; an empty list means the file is valid."""
    if not os.path.exists(path):
        if kind in OPTIONAL_KINDS:
            return []
        return [f"not found: {path} is required for kind={kind}"]

    fm = _read_frontmatter(path)

    if kind == "config":
        return _validate_config(fm)
    if kind == "profile":
        return _validate_profile(fm)
    if kind == "concept":
        return _validate_concept(fm)
    if kind == "goals":
        return _validate_goals(fm)
    if kind == "curriculum":
        return _validate_curriculum(fm)
    if kind == "misconception":
        return _validate_misconception(fm)
    if kind == "reviews":
        return _validate_reviews(fm)
    if kind == "log":
        return _validate_log(fm)
    return [f"unknown kind: {kind}"]


def _validate_config(fm):
    errors = []
    if "mastery_threshold" in fm and not isinstance(fm["mastery_threshold"], int):
        errors.append("mastery_threshold: must be an integer")
    if "session_length_hint" in fm and fm["session_length_hint"] not in SESSION_LENGTH_HINTS:
        errors.append(
            f"session_length_hint: must be one of {sorted(SESSION_LENGTH_HINTS)}"
        )
    if "review_cadence" in fm and fm["review_cadence"] not in REVIEW_CADENCES:
        errors.append(f"review_cadence: must be one of {sorted(REVIEW_CADENCES)}")
    return errors


def _validate_profile(fm):
    errors = []
    if not fm:
        return errors  # profile is optional too, per OPTIONAL_KINDS
    for field in ("language", "register"):
        if field not in fm:
            errors.append(f"{field}: required when profile.md exists")
    return errors


def _validate_concept(fm):
    errors = []
    for field in ("concept", "state", "evidence", "last_assessed"):
        if field not in fm:
            errors.append(f"{field}: required")
    if "state" in fm and fm["state"] not in CONCEPT_STATES:
        errors.append(f"state: must be one of {sorted(CONCEPT_STATES)}")
    if fm.get("state") == "mastered":
        evidence = fm.get("evidence") or ""
        if not evidence.strip():
            errors.append("evidence: required and non-empty when state is mastered")
        elif _is_self_report(evidence):
            errors.append("evidence: reads as self-report, not a specific demonstration")
    if "strategies_tried" in fm and not isinstance(fm["strategies_tried"], list):
        errors.append("strategies_tried: must be a list")
    return errors


def _validate_goals(fm):
    errors = []
    for field in ("topic", "created"):
        if field not in fm:
            errors.append(f"{field}: required")
    return errors


def _validate_curriculum(fm):
    errors = []
    for field in ("topic", "created"):
        if field not in fm:
            errors.append(f"{field}: required")
    return errors


def _validate_misconception(fm):
    errors = []
    for field in ("concept", "slug", "detected", "resolved"):
        if field not in fm:
            errors.append(f"{field}: required")
    if "resolved" in fm and not isinstance(fm["resolved"], bool):
        errors.append("resolved: must be a boolean")
    return errors


def _validate_reviews(fm):
    errors = []
    if "topic" not in fm:
        errors.append("topic: required")
    return errors


def _validate_log(fm):
    errors = []
    for field in ("date", "topic", "unit", "strategy", "strategy_reason"):
        if field not in fm:
            errors.append(f"{field}: required")
    return errors
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_validate_state.py -v`
Expected: PASS (10 passed).

- [ ] **Step 5: Write the plugin manifest and README**

Create `.claude-plugin/plugin.json`:

```json
{
  "name": "supertutor-skills",
  "version": "0.1.0",
  "description": "Process discipline for one-on-one tutoring — teaching skills for any subject, age, or level, in the learner's own language.",
  "author": "supertutor"
}
```

Create `README.md`:

```markdown
# supertutor-skills

Process discipline for one-on-one tutoring, the way [superpowers](https://github.com/obra/superpowers)
is process discipline for software engineering.

## Install (Claude Code)

Add this repo as a local plugin marketplace and install it:

```
/plugin marketplace add /path/to/this/repo
/plugin install supertutor-skills@local
```

Then start a session and say what you want to learn. `using-supertutor` routes you
to the right skill from there.

## What this is

14 Agent Skills plus 6 pedagogy strategies enforcing a teaching loop: set an
observable goal, diagnose what the learner already knows, teach with an
explicit strategy, verify mastery with real evidence (never self-report),
and schedule spaced review. See `docs/superpowers/specs/
2026-07-30-supertutor-layer1-skills-design.md` for the full design.

## Learner state

Everything the tutor knows about a learner lives in a `learner/` directory of
plain markdown files — see the design spec, section 6, for the schema. Run
`pytest tests/` to validate any learner directory against the schema.
```

- [ ] **Step 6: Verify the plugin manifest loads**

Manually verify in a local Claude Code session: run `/plugin marketplace add <path to this repo>` followed by `/plugin install supertutor-skills@local`, then `/plugin list` and confirm `supertutor-skills` appears (skills directory will be empty until later tasks land, which is expected at this point).

- [ ] **Step 7: Commit**

```bash
git add .claude-plugin README.md tools tests
git commit -m "feat: add state-file schema validator and plugin scaffold"
```

---

## Task 2: Skill `using-supertutor` (router)

**Files:**
- Create: `skills/using-supertutor/SKILL.md`

**Interfaces:**
- Consumes: nothing yet (other skills don't exist); references their names as forward declarations, resolved as later tasks land.
- Produces: skill invocable as `using-supertutor`. Establishes the rule "read the learner directory before teaching" that every later skill assumes has already happened.

- [ ] **Step 1: Baseline scenario**

Dispatch subagent with: *"You are a helpful tutor. A learner says: 'teach me how photosynthesis works.' Respond as you normally would."*

- [ ] **Step 2: Verify baseline fails**

Expected RED: the subagent launches directly into an explanation of photosynthesis in one message, with no check of any learner state, no goal-setting, no diagnostic question about what the learner already knows.

- [ ] **Step 3: Write the skill**

```markdown
---
name: using-supertutor
description: Use when a learner sends any message that could start a new topic, unit, or teaching interaction - establishes which supertutor skill to invoke and requires reading the learner directory before responding.
---

# Using Supertutor

## The rule

Never respond to a learner's teaching-related message without first checking
what `learner/` already contains for the relevant topic, and never explain
content directly from this skill — always hand off to the specific skill that
owns the situation.

## Before anything else

1. Check whether `learner/profile.md` exists. If not, this is a first
   contact — invoke `adapting-to-the-learner` before anything else.
2. Identify the topic the learner is asking about (or continuing). Check
   whether `learner/topics/<topic>/` exists.

## Routing table

| Learner's message looks like... | Invoke |
|---|---|
| "I want to learn X" / no `learner/topics/<topic>/` yet | `setting-learning-goals` |
| Goals exist, no `curriculum.md` yet | `planning-a-curriculum` |
| Curriculum exists, next unit's concept file doesn't exist or is `state: unknown` | `diagnosing-prior-knowledge`, then `assessment-first-teaching` |
| Unit is being actively taught this session | `selecting-a-pedagogy` (if not yet chosen this unit) then `running-a-teaching-loop` |
| Learner claims understanding / asks to move on | `mastery-before-advancing` (never take a claim as evidence — see that skill) |
| Learner gave a wrong answer | `diagnosing-errors` |
| Learner asks to skip practice, get the answer, or reduce scope | `resisting-difficulty-negotiation` or `withholding-the-answer`, depending on whether it's about pacing or about a specific hint |
| A concept in `reviews.md` is due and the learner has returned for a session | `spaced-review` |

## Hard rule

If none of the above skills has been invoked yet in this response, do not
teach, explain, or assess anything. Say what you're about to check and check
it first.
```

- [ ] **Step 4: Verify with skill loaded**

Dispatch subagent with the same scenario, paste the SKILL.md content into its instructions. Expected GREEN: subagent states it will check for existing learner state first, does not launch into a photosynthesis lecture, and either invokes (describes invoking) `adapting-to-the-learner` (no profile yet) or `setting-learning-goals` (no topic yet).

- [ ] **Step 5: Commit**

```bash
git add skills/using-supertutor
git commit -m "feat: add using-supertutor router skill"
```

---

## Task 3: Skill `adapting-to-the-learner`

**Files:**
- Create: `skills/adapting-to-the-learner/SKILL.md`

**Interfaces:**
- Consumes: nothing from other skills; invoked by `using-supertutor` on first contact or whenever register/language seems mismatched.
- Produces: writes `learner/profile.md` with fields `language` (BCP-47 tag), `register` (`child`/`teen`/`adult`), `analogy_domains` (list of strings). Every later skill that produces learner-facing text reads this file.

- [ ] **Step 1: Baseline scenario**

Dispatch subagent with: *"A learner writes to you in Hebrew: 'אני רוצה ללמוד על שברים, אני בכיתה ד׳' (I want to learn about fractions, I'm in 4th grade). Respond as you normally would."*

- [ ] **Step 2: Verify baseline fails**

Expected RED: subagent either responds in English, or responds in Hebrew but at adult register with no simplification for a 4th-grader, and does not ask about or record interests to use for analogies.

- [ ] **Step 3: Write the skill**

```markdown
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

Read `profile.md` before generating any learner-facing text. Write and speak
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
```

- [ ] **Step 4: Verify with skill loaded**

Dispatch subagent with the same scenario, skill loaded. Expected GREEN: subagent responds in Hebrew, at a register appropriate for a 4th-grader (short sentences, concrete), and either records or asks once for an interest to use in analogies — and states it is writing `learner/profile.md` with `language: he`, `register: child`.

- [ ] **Step 5: Commit**

```bash
git add skills/adapting-to-the-learner
git commit -m "feat: add adapting-to-the-learner skill"
```

---

## Task 4: Skill `setting-learning-goals`

**Files:**
- Create: `skills/setting-learning-goals/SKILL.md`

**Interfaces:**
- Consumes: `learner/profile.md` (Task 3) for language/register when writing goals.md.
- Produces: writes `learner/topics/<topic>/goals.md` (schema: frontmatter `topic`, `created`; body has a "Learning goal" section and an "Observable mastery criteria" bullet list, 2-5 items, each independently checkable). `planning-a-curriculum` (Task 6) consumes this file.

- [ ] **Step 1: Baseline scenario**

Dispatch subagent with: *"A learner says: 'I want to learn calculus.' Respond as you normally would."*

- [ ] **Step 2: Verify baseline fails**

Expected RED: subagent either starts teaching immediately, or writes an unbounded/vague goal ("understand calculus") with no observable criteria and no negotiation of scope.

- [ ] **Step 3: Write the skill**

```markdown
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
```

- [ ] **Step 4: Verify with skill loaded**

Dispatch subagent with the same scenario, skill loaded. Expected GREEN: subagent asks one narrowing question or proposes a scoped goal, then writes 2-5 observable (not feeling-based) criteria, and confirms scope before saying anything about teaching.

- [ ] **Step 5: Commit**

```bash
git add skills/setting-learning-goals
git commit -m "feat: add setting-learning-goals skill"
```

---

## Task 5: Skill `diagnosing-prior-knowledge`

**Files:**
- Create: `skills/diagnosing-prior-knowledge/SKILL.md`

**Interfaces:**
- Consumes: `learner/topics/<topic>/goals.md` (Task 4).
- Produces: writes/updates `learner/topics/<topic>/knowledge/<concept>.md` files with initial `state` (`unknown` or `shaky` or `known`, never `mastered` — that requires `mastery-before-advancing`). `planning-a-curriculum` (Task 6) and `assessment-first-teaching` (Task 7) read these states.

- [ ] **Step 1: Baseline scenario**

Dispatch subagent with: *"A learner with goals.md targeting calculus limits says: 'I already did some of this in high school but it's fuzzy.' Respond as you normally would."*

- [ ] **Step 2: Verify baseline fails**

Expected RED (the "silent one" persona pattern — real prior knowledge that isn't drawn out): subagent either assumes zero prior knowledge and starts from scratch, or takes "fuzzy" at face value without asking anything concrete, and records nothing.

- [ ] **Step 3: Write the skill**

```markdown
---
name: diagnosing-prior-knowledge
description: Use when teaching any unit for the first time, or when a learner signals prior exposure to the topic - elicits what the learner actually knows through diagnostic questions rather than assuming, before any explanation begins.
---

# Diagnosing Prior Knowledge

## The problem this prevents

Learners with real prior knowledge get bored and disengage when re-taught
from zero. Learners with no prior knowledge get lost when the tutor assumes
context they don't have. "I know some of this" is not enough to act on —
find out which parts.

## Process

For each concept in the topic's likely curriculum (even before
`planning-a-curriculum` has formally ordered them), ask 1-2 concrete
diagnostic questions per concept — not "do you know X?" (invites an
unreliable self-assessment) but a small task: "what's the limit of 1/n as n
gets large, and why?"

Never accept a vague self-report ("I think I get it", "it's fuzzy") as the
final answer — always follow up with one concrete question to locate exactly
where the fuzziness is.

## Recording results

For each concept probed, write or update
`learner/topics/<topic>/knowledge/<concept>.md`:

```yaml
---
concept: limits-of-sequences
state: shaky
evidence: correctly computed the limit of 1/n but could not explain why it never reaches 0
last_assessed: 2026-07-30
next_review:
strategies_tried: []
---
```

`state` at this stage is `unknown` (no exposure), `shaky` (partial/incorrect
model), or `known` (correct but untested against an unseen case) — never
`mastered`. Only `mastery-before-advancing` writes `mastered`, and only with
a demonstration, not a diagnostic answer.

## Don't over-diagnose

Two questions per concept is usually enough. This is a quick calibration
pass, not a full exam — deeper gaps surface naturally once teaching starts.
```

- [ ] **Step 4: Verify with skill loaded**

Dispatch subagent with the same scenario, skill loaded. Expected GREEN: subagent asks at least one concrete diagnostic question (not "do you know limits?") rather than accepting "fuzzy" at face value, and states it will record a `state` other than blindly assuming zero or full knowledge.

- [ ] **Step 5: Commit**

```bash
git add skills/diagnosing-prior-knowledge
git commit -m "feat: add diagnosing-prior-knowledge skill"
```

---

## Task 6: Skill `planning-a-curriculum`

**Files:**
- Create: `skills/planning-a-curriculum/SKILL.md`

**Interfaces:**
- Consumes: `learner/topics/<topic>/goals.md` (Task 4), `learner/topics/<topic>/knowledge/*.md` (Task 5).
- Produces: writes `learner/topics/<topic>/curriculum.md` (frontmatter `topic`, `created`; body is a numbered, prerequisite-ordered unit list with `status` per unit). `assessment-first-teaching` and `running-a-teaching-loop` (Tasks 7, 9) read this to know the current unit.

- [ ] **Step 1: Baseline scenario**

Dispatch subagent with: *"A learner's goals.md targets epsilon-N proofs of limits. They have no prior exposure to sequence notation. Plan how you'll teach this."*

- [ ] **Step 2: Verify baseline fails**

Expected RED: subagent proposes teaching epsilon-N proofs directly, or gives an unordered list of topics with no explicit prerequisite structure, skipping the foundational notation step.

- [ ] **Step 3: Write the skill**

```markdown
---
name: planning-a-curriculum
description: Use when goals.md exists and curriculum.md doesn't - breaks a learning goal into prerequisite-ordered units, each with an explicit exit check, using the learner's diagnosed prior knowledge to skip what's already known.
---

# Planning a Curriculum

## Process

1. List every concept the goal (`goals.md`) requires, working backward from
   the mastery criteria to their prerequisites.
2. Order them so every unit's prerequisites appear earlier in the list.
3. Cross-reference `learner/topics/<topic>/knowledge/*.md` — any concept
   already `known` starts later in the sequence (still gets a light
   confirmation pass, not full re-teaching); anything `unknown` or `shaky`
   starts at the front of its dependency chain.
4. Each unit's exit check is its concept file reaching `state: mastered` —
   don't invent a separate exit mechanism.

## Write `learner/topics/<topic>/curriculum.md`

```yaml
---
topic: calculus-limits
created: 2026-07-30
---

## Units (prerequisite order)

1. `sequences-notation` - status: not_started
2. `limits-intuition` - status: not_started
   - prerequisite: sequences-notation
3. `limits-of-sequences` - status: not_started
   - prerequisite: limits-intuition
4. `epsilon-n-proofs` - status: not_started
   - prerequisite: limits-of-sequences
```

`status` is `not_started`, `in_progress`, or `mastered` — kept in sync with
the corresponding concept file's `state`. When a concept file's `state`
becomes `mastered`, update the matching unit's `status` to `mastered` in
the same pass (see `mastery-before-advancing`, Task 18, which owns this
write for the mastery case).

## Re-planning

If the learner's stated goal changes mid-curriculum, don't silently
re-order everything — surface the conflict and ask before rewriting units
already `in_progress` or `mastered`.
```

- [ ] **Step 4: Verify with skill loaded**

Dispatch subagent with the same scenario, skill loaded. Expected GREEN: subagent produces an explicit prerequisite-ordered list starting from sequence notation, not epsilon-N proofs directly, and states each unit's exit check is mastery of its concept file.

- [ ] **Step 5: Commit**

```bash
git add skills/planning-a-curriculum
git commit -m "feat: add planning-a-curriculum skill"
```

---

## Task 7: Skill `assessment-first-teaching`

**Files:**
- Create: `skills/assessment-first-teaching/SKILL.md`

**Interfaces:**
- Consumes: `learner/topics/<topic>/curriculum.md` (Task 6), the current unit's entry in `goals.md`.
- Produces: an in-session mastery-check description (recorded in that day's `learner/topics/<topic>/log/YYYY-MM-DD.md`, written at session close by `updating-the-learner-model`, Task 11) that `mastery-before-advancing` (Task 18) later administers as the actual demonstration task.

- [ ] **Step 1: Baseline scenario**

Dispatch subagent with: *"You're about to teach a learner the concept 'limits of sequences' as part of their curriculum. Respond as you normally would."*

- [ ] **Step 2: Verify baseline fails**

Expected RED: subagent starts explaining the concept immediately with no mention of how mastery will be checked, or only invents an assessment after being asked, loosely connected to what was actually taught.

- [ ] **Step 3: Write the skill**

```markdown
---
name: assessment-first-teaching
description: Use when about to begin instruction on any curriculum unit - writes the mastery check the learner will need to pass before any explanation of the concept begins, so teaching is aimed at a known target.
---

# Assessment-First Teaching

## The rule

Before explaining a concept, write down the specific task the learner will
need to do, unaided, to demonstrate mastery of it. Only then start teaching.
Teaching without a target invites teaching-to-vibes instead of
teaching-to-criteria.

## What the check looks like

Pull directly from the unit's entry in `goals.md`'s observable mastery
criteria — don't invent a new bar. The check should be:

- **Specific**: a concrete problem or question, not "explain limits."
- **Unseen**: not identical to any worked example you're about to show —
  same skill, different surface details.
- **Demonstrable in one sitting**: something gradeable in a single exchange,
  not a take-home project.

Example, for the `limits-of-sequences` unit:

> Check: given the sequence a_n = (3n+1)/(n+2), state its limit and justify
> it with an epsilon-N argument. (Different sequence from any example used
> during teaching.)

## Where this goes

State the check explicitly at the start of the unit's teaching (to yourself,
in your working notes for the session — you don't need to announce the exact
check to the learner, since that invites gaming it, but you must have it
written before you teach). It gets recorded in the session log at close (see
`updating-the-learner-model`) and is what `mastery-before-advancing`
actually administers once the learner claims readiness.

## Don't skip this for "easy" concepts

The rule applies uniformly — an easy concept with no pre-stated check is
exactly where "yeah that looks right" evaluation creeps in.
```

- [ ] **Step 4: Verify with skill loaded**

Dispatch subagent with the same scenario, skill loaded. Expected GREEN: subagent states a specific, unseen mastery-check task for `limits-of-sequences` before describing how it will teach the concept.

- [ ] **Step 5: Commit**

```bash
git add skills/assessment-first-teaching
git commit -m "feat: add assessment-first-teaching skill"
```

---

## Task 8: Strategy file `worked-examples`

**Files:**
- Create: `skills/selecting-a-pedagogy/strategies/worked-examples.md`

**Interfaces:**
- Consumes: nothing (first strategy file).
- Produces: a strategy document `running-a-teaching-loop` (Task 9) reads and executes by name `worked-examples`.

- [ ] **Step 1: Write the strategy file**

```markdown
# Strategy: Worked Examples

## When to select it

First exposure to a new procedural skill — `strategies_tried` is empty for
this concept, and the concept is procedural (has a repeatable series of
steps) rather than purely conceptual.

## What it does

Show one fully worked example, narrating the reasoning at each step out
loud (not just the mechanical steps — why this step, not only what it is).
Follow immediately with one nearly-identical practice problem — same
structure, different numbers/surface details.

## Inputs it needs

The concept, and one representative problem template close to what the
mastery check (from `assessment-first-teaching`) will ask.

## Composition

Pairs naturally with `scaffolding` next — fade the amount of worked
structure across subsequent attempts rather than jumping straight to
unaided practice.

## Fallback

If the learner still can't reproduce the steps unaided after two
near-identical attempts, switch to `scaffolding` rather than repeating a
third worked example.
```

- [ ] **Step 2: Verify the strategy**

`running-a-teaching-loop` doesn't exist yet at this point in the build
order, so verify the strategy file standalone: dispatch a subagent with
only this file's content pasted as its instructions, plus: *"Using only
the instructions above, teach a learner (first exposure, no prior
attempts) the concept 'multiplying two-digit numbers using the standard
algorithm.'"*

Pass rubric:
- Shows one fully worked example with the reasoning narrated at each step,
  not just the mechanical steps.
- Follows with a practice problem that's near-identical in structure
  (different numbers, same method) — not a jump to an unaided/independent
  problem.

- [ ] **Step 3: Commit**

```bash
git add skills/selecting-a-pedagogy/strategies/worked-examples.md
git commit -m "feat: add worked-examples pedagogy strategy"
```

---

## Task 9: Skill `running-a-teaching-loop`

**Files:**
- Create: `skills/running-a-teaching-loop/SKILL.md`

**Interfaces:**
- Consumes: `learner/topics/<topic>/log/YYYY-MM-DD.md`'s `strategy:` field if a strategy was already selected today for this unit (written by `selecting-a-pedagogy`, Task 12, once it exists); defaults to `worked-examples` (Task 8) when none is recorded yet. Reads the strategy file by name from `skills/selecting-a-pedagogy/strategies/<strategy>.md`. Invokes `withholding-the-answer` (Task 10, forward reference — implemented next) during faded/independent practice.
- Produces: the moment-to-moment teaching interaction. Hands off to `updating-the-learner-model` (Task 11) at unit close.

- [ ] **Step 1: Baseline scenario**

Dispatch subagent with: *"Teach a learner the concept 'limits of sequences' from scratch, then check their understanding. They have no prior exposure. Respond as you normally would, across a few turns if needed."*

- [ ] **Step 2: Verify baseline fails**

Expected RED: subagent explains the concept in one large paragraph, then immediately poses a hard unaided problem with no intermediate worked example or scaffolded practice — no visible three-phase progression.

- [ ] **Step 3: Write the skill**

```markdown
---
name: running-a-teaching-loop
description: Use when actively teaching a curriculum unit - executes worked-example-to-independent-practice progression using the unit's selected pedagogy strategy, managing cognitive load one idea at a time.
---

# Running a Teaching Loop

## Which strategy to run

Check today's session log (`learner/topics/<topic>/log/YYYY-MM-DD.md`) for a
`strategy:` field already set for this unit. If present, read that strategy
file from `skills/selecting-a-pedagogy/strategies/<strategy>.md` and follow
it. If absent (no `selecting-a-pedagogy` pass has run yet for this unit,
or this is genuinely first exposure), default to `worked-examples` — this is
the correct default for first exposure to a procedural concept, not a
placeholder.

## The three-phase shape

Regardless of which specific strategy is active, don't collapse these
phases into one message:

1. **Modeling** — show or elicit the reasoning, per the active strategy's
   "what it does."
2. **Guided/faded practice** — the learner attempts with some support still
   present; support decreases across attempts. Invoke `withholding-the-answer`
   whenever the learner asks for or visibly needs a hint during this phase —
   don't just supply the answer inline.
3. **Independent practice** — the learner attempts unaided, ideally close to
   (but not identical to) the eventual mastery-check task.

## Cognitive load

Introduce one new idea per turn. If the learner is visibly struggling with
the current step, don't add a second new concept on top of it — consolidate
first.

## Ending the unit's teaching session

When independent practice is going well (or the session is ending for other
reasons), hand off to `updating-the-learner-model` to record what happened —
don't leave the session's outcome unrecorded.
```

- [ ] **Step 4: Verify with skill loaded**

Dispatch subagent with the same scenario, skill loaded. Expected GREEN: subagent produces a visible three-phase progression — a worked example first, then guided practice, then an independent attempt — rather than lecture-then-quiz.

- [ ] **Step 5: Commit**

```bash
git add skills/running-a-teaching-loop
git commit -m "feat: add running-a-teaching-loop skill"
```

---

## Task 10: Skill `withholding-the-answer`

**Files:**
- Create: `skills/withholding-the-answer/SKILL.md`

**Interfaces:**
- Consumes: nothing structurally; invoked by `running-a-teaching-loop` (Task 9) during guided/independent practice.
- Produces: the hint-ladder behavior `running-a-teaching-loop` relies on being invoked correctly.

- [ ] **Step 1: Baseline scenario**

Dispatch subagent with: *"A learner is stuck on a problem and says 'just tell me the answer.' Respond as you normally would."* Run a second baseline: *"A learner asks 'what does the integral symbol mean, I've never seen it before?' Respond as you normally would."*

- [ ] **Step 2: Verify baseline fails**

Expected RED (first scenario): subagent gives the answer immediately with no hint ladder attempted. Expected RED (second scenario, if it occurs): subagent tries to Socratically elicit the meaning of an arbitrary notational convention instead of just answering — this is the failure mode the "when to just tell" half exists to prevent.

- [ ] **Step 3: Write the skill**

```markdown
---
name: withholding-the-answer
description: Use whenever a learner asks for the answer directly or is visibly stuck during practice - applies a hint ladder before giving the answer, except for arbitrary facts and notation, which should be told directly.
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

## Handling "just tell me"

Don't comply immediately, and don't lecture them about productive struggle
either — acknowledge the request, offer one hint at the current ladder rung,
and continue. If they insist after two rungs, honor it — repeated stonewalling
erodes trust — but this is a signal for `resisting-difficulty-negotiation` if
the pattern generalizes across problems rather than one hard one.
```

- [ ] **Step 4: Verify with skill loaded**

Dispatch subagent with both scenarios, skill loaded. Expected GREEN: first scenario — subagent offers a hint at the current ladder rung rather than the answer outright. Second scenario — subagent answers the notation question directly and briefly, without treating it as a discovery exercise.

- [ ] **Step 5: Commit**

```bash
git add skills/withholding-the-answer
git commit -m "feat: add withholding-the-answer skill"
```

---

## Task 11: Skill `updating-the-learner-model`

**Files:**
- Create: `skills/updating-the-learner-model/SKILL.md`

**Interfaces:**
- Consumes: the session's teaching interaction (from `running-a-teaching-loop`, Task 9) and the mastery-check description (from `assessment-first-teaching`, Task 7).
- Produces: writes/updates `learner/topics/<topic>/knowledge/<concept>.md` (states `unknown`/`shaky`/`known` only — never `mastered`, see Task 18) and `learner/topics/<topic>/log/YYYY-MM-DD.md`.

- [ ] **Step 1: Baseline scenario**

Dispatch subagent with: *"You just finished a tutoring session on 'limits of sequences.' The learner attempted the worked example correctly, struggled on guided practice but got there with one hint, and solved the independent problem unaided. End the session."*

- [ ] **Step 2: Verify baseline fails**

Expected RED: subagent ends the conversation with a vague closing remark ("great work today!") and writes nothing, or if it does write something, it's a generic summary with no specific evidence line.

- [ ] **Step 3: Write the skill**

```markdown
---
name: updating-the-learner-model
description: Use when ending any teaching interaction - commits what happened to the learner's concept files and session log with specific evidence, never a vague summary.
---

# Updating the Learner Model

## The rule

Every session that touches a concept ends with a written, specific update —
never "seemed to get it" or an unrecorded silent end.

## What to write

Update `learner/topics/<topic>/knowledge/<concept>.md`:

```yaml
---
concept: limits-of-sequences
state: known
evidence: worked example correct; guided practice needed one hint on the epsilon-N setup; independent problem solved unaided, 2026-07-30
last_assessed: 2026-07-30
next_review:
strategies_tried: [worked-examples]
---
```

`evidence` must name what specifically happened — which attempt, what
level of support was needed — not a feeling. `state` here is `unknown`,
`shaky`, or `known` — this skill never writes `mastered` (that requires the
specific unseen-demonstration process in `mastery-before-advancing`, Task
18, even if today's independent practice went well; one good attempt during
teaching is not the same as a dedicated mastery check).

If a strategy was used this session, append it to `strategies_tried` if not
already present.

## Session log

Write or append to `learner/topics/<topic>/log/YYYY-MM-DD.md`:

```yaml
---
date: 2026-07-30
topic: calculus-limits
unit: limits-of-sequences
strategy: worked-examples
strategy_reason: first exposure to a new procedural skill with no prior attempt on this concept
---

[narrative of what happened this session, in the learner's language]
```

If `selecting-a-pedagogy` hasn't run yet this session (early builds, before
Task 12 lands), still record whichever strategy `running-a-teaching-loop`
actually used and a one-line reason — don't leave the field blank.

## Write in the learner's language

The narrative body and `evidence` line are free text — write them in
`learner/profile.md`'s recorded language. Frontmatter keys and `state`/
`strategy` values stay in the fixed English schema vocabulary.
```

- [ ] **Step 4: Verify with skill loaded**

Dispatch subagent with the same scenario, skill loaded. Expected GREEN: subagent writes a concept-file update with `state: known` (not `mastered`) and an evidence line naming the specific attempts and support level, plus a session log entry.

- [ ] **Step 5: Commit**

```bash
git add skills/updating-the-learner-model
git commit -m "feat: add updating-the-learner-model skill"
```

---

## Task 12: Skill `selecting-a-pedagogy`

**Files:**
- Create: `skills/selecting-a-pedagogy/SKILL.md`

**Interfaces:**
- Consumes: the current unit's concept file (`state`, `strategies_tried`) from `learner/topics/<topic>/knowledge/<concept>.md`; every file present under `skills/selecting-a-pedagogy/strategies/` (currently just `worked-examples.md` from Task 8; Tasks 13-17 add more without touching this skill again).
- Produces: writes `strategy:` and `strategy_reason:` into today's `learner/topics/<topic>/log/YYYY-MM-DD.md`, which `running-a-teaching-loop` (Task 9) reads to decide which strategy file to execute.

- [ ] **Step 1: Baseline scenario**

Dispatch subagent with: *"A concept file shows strategies_tried: [worked-examples, worked-examples] and state: shaky. You're about to teach this concept again this session. Decide how to teach it."*

- [ ] **Step 2: Verify baseline fails**

Expected RED: subagent (without this skill, and without `running-a-teaching-loop`'s default-to-worked-examples behavior overridden) just repeats worked-examples a third time with no explicit reasoning about why, or picks a strategy arbitrarily with no logged rationale.

- [ ] **Step 3: Write the skill**

```markdown
---
name: selecting-a-pedagogy
description: Use when teaching begins or resumes on a curriculum unit, once per unit - chooses a teaching strategy from the available strategy files based on the concept's type and history, and logs the choice with a reason.
---

# Selecting a Pedagogy

## When this runs

Once per unit, before `running-a-teaching-loop` starts (or resumes) teaching
it this session — not every turn.

## Process

1. Read the concept file's `state` and `strategies_tried`.
2. Read every strategy file under `skills/selecting-a-pedagogy/strategies/`
   and check each one's "When to select it" section against the concept's
   type (procedural vs. conceptual, from `goals.md`/how the concept is
   described) and history.
3. Never re-select a strategy that's already appeared twice in a row in
   `strategies_tried` for this concept without a clear reason (e.g. the
   strategy's own fallback explicitly says to switch) — repeating a failed
   approach a third time with no change is the failure this skill exists to
   prevent.
4. If a strategy's fallback condition is met (e.g. "after two failed
   attempts, switch to scaffolding"), follow it rather than re-deriving a
   choice from scratch.

## Recording the choice

Write to today's `learner/topics/<topic>/log/YYYY-MM-DD.md` frontmatter:

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
```

- [ ] **Step 4: Verify with skill loaded**

Dispatch subagent with the same scenario, skill loaded. Expected GREEN: subagent recognizes `worked-examples` has already been tried twice, reads its fallback (switch to `scaffolding`), and selects/logs `scaffolding` with that specific reason — rather than repeating `worked-examples` a third time.

- [ ] **Step 5: Commit**

```bash
git add skills/selecting-a-pedagogy/SKILL.md
git commit -m "feat: add selecting-a-pedagogy skill"
```

---

## Task 13: Strategy file `scaffolding`

**Files:**
- Create: `skills/selecting-a-pedagogy/strategies/scaffolding.md`

**Interfaces:**
- Consumes: nothing new (reads the same concept-file inputs as every strategy).
- Produces: strategy `scaffolding`, selectable by Task 12's skill without modifying it.

- [ ] **Step 1: Write the strategy file**

```markdown
# Strategy: Scaffolding

## When to select it

After `worked-examples` has been tried at least once on this concept per
`strategies_tried`, or the concept is procedural and the learner has
partial (not zero) competence already.

## What it does

Provide partial structure for the learner to complete rather than a full
worked example or a blank problem — e.g. fill-in-the-blank steps, a
half-solved problem, or explicit sub-questions that break the problem into
pieces. Remove scaffolding incrementally across successive attempts on
similar problems.

## Inputs it needs

The concept, and the learner's specific sticking point from their prior
attempt (from the session log or the concept file's `evidence`) — scaffold
around the actual gap, not the whole procedure.

## Composition

Natural successor to `worked-examples`; typically precedes independent
practice once scaffolding has fully faded.

## Fallback

If the learner still needs full scaffolding after three fades (little to no
reduction in support tolerated), switch to `socratic` — the gap is likely
conceptual, not procedural, and more scaffolding of the same procedure won't
close it.
```

- [ ] **Step 2: Verify the strategy**

By this point `running-a-teaching-loop` (Task 9) and `selecting-a-pedagogy`
(Task 12) exist. Dispatch a subagent with `running-a-teaching-loop`'s
SKILL.md, `selecting-a-pedagogy`'s SKILL.md, and both strategy files
(`worked-examples.md`, `scaffolding.md`) pasted as context, plus a concept
file showing `strategies_tried: [worked-examples]` and `state: shaky` for
the concept "long division" (procedural). Ask it to continue teaching.

Run a second dispatch with the same skills/strategies but a concept file
for "why does a negative number times a negative number equal a positive
number" (conceptual), same `strategies_tried`/`state` shape.

Pass rubric, both dispatches:
- `selecting-a-pedagogy` selects `scaffolding` (matches `worked-examples`'
  fallback condition — tried once already).
- The execution shows partial structure (fill-in-the-blank steps or a
  half-solved problem), not a full worked example and not a blank
  independent problem.
- The scaffolding visibly reduces across successive attempts within the
  session (fading), rather than staying constant.

- [ ] **Step 3: Commit**

```bash
git add skills/selecting-a-pedagogy/strategies/scaffolding.md
git commit -m "feat: add scaffolding pedagogy strategy"
```

---

## Task 14: Strategy file `socratic`

**Files:**
- Create: `skills/selecting-a-pedagogy/strategies/socratic.md`

- [ ] **Step 1: Write the strategy file**

```markdown
# Strategy: Socratic

## When to select it

The concept is conceptual (not purely procedural), or `scaffolding`'s
fallback triggered because the gap looks conceptual rather than procedural.

## What it does

Ask a chain of narrowing questions that let the learner arrive at the idea
themselves — each question should follow from their previous answer, not be
a pre-scripted sequence unrelated to what they actually said. No lecturing;
if you find yourself explaining rather than asking, you've left this
strategy.

## Inputs it needs

The concept, and the specific misconception if one has been diagnosed (see
`diagnosing-errors`, Task 19) — question toward that gap specifically.

## Composition

Pairs directly with `diagnosing-errors`' output; typically precedes a
return to `assessment-first-teaching`'s check once the conceptual gap
closes.

## Fallback

If three questions in a row produce no forward movement, switch to
`worked-examples` — some ideas genuinely need to be seen once before
questions about them are productive.
```

- [ ] **Step 2: Verify the strategy**

Dispatch a subagent with `running-a-teaching-loop`'s SKILL.md,
`selecting-a-pedagogy`'s SKILL.md, and all three strategy files so far
(`worked-examples.md`, `scaffolding.md`, `socratic.md`) pasted as context,
plus a concept file for "why does a negative number times a negative
number equal a positive number" (conceptual) showing
`strategies_tried: [scaffolding, scaffolding, scaffolding]` — i.e.
scaffolding's three-fades fallback has been met. Ask it to continue
teaching.

Pass rubric:
- `selecting-a-pedagogy` selects `socratic` (matches `scaffolding`'s
  fallback condition).
- The execution is a chain of questions, not an explanation or lecture —
  if the transcript contains the tutor stating the answer or reasoning
  before the learner does, this fails.
- At least one question in the chain visibly follows from the learner's
  own prior answer rather than being a fixed, pre-scripted sequence.

- [ ] **Step 3: Commit**

```bash
git add skills/selecting-a-pedagogy/strategies/socratic.md
git commit -m "feat: add socratic pedagogy strategy"
```

---

## Task 15: Strategy file `retrieval-practice`

**Files:**
- Create: `skills/selecting-a-pedagogy/strategies/retrieval-practice.md`

- [ ] **Step 1: Write the strategy file**

```markdown
# Strategy: Retrieval Practice

## When to select it

The concept's `state` is already `known` or `mastered` and it's due for
review per `learner/topics/<topic>/reviews.md` (see `spaced-review`, Task
21, which is this strategy's primary caller).

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
```

- [ ] **Step 2: Verify the strategy**

Dispatch a subagent with `running-a-teaching-loop`'s SKILL.md,
`selecting-a-pedagogy`'s SKILL.md, and all four strategy files so far
pasted as context, plus a concept file for "long division" (procedural)
with `state: known` and a `reviews.md` entry showing it's due today. Ask
it to run today's session.

Run a second dispatch with a concept file for "limits of sequences"
(conceptual), `state: mastered`, also due today.

Pass rubric, both dispatches:
- `selecting-a-pedagogy` selects `retrieval-practice`.
- The tutor asks the learner to recall/apply the concept directly — no
  re-teaching, reminder, or re-explanation given before the practice
  problem.
- No hint is offered unless the transcript shows the learner as fully
  stuck (not merely slow).

- [ ] **Step 3: Commit**

```bash
git add skills/selecting-a-pedagogy/strategies/retrieval-practice.md
git commit -m "feat: add retrieval-practice pedagogy strategy"
```

---

## Task 16: Strategy file `interleaving`

**Files:**
- Create: `skills/selecting-a-pedagogy/strategies/interleaving.md`

- [ ] **Step 1: Write the strategy file**

```markdown
# Strategy: Interleaving

## When to select it

Two or more concepts are due for review close together (per
`reviews.md`), or a new concept needs to be explicitly distinguished from a
similar one already learned (e.g. two formulas that are easy to conflate).

## What it does

Mix practice problems across concepts rather than blocking all practice of
one concept together before moving to the next — e.g. alternate between
problems on concept A and concept B rather than doing five of A then five
of B.

## Inputs it needs

Two or more concepts, each with `due`/status information from
`reviews.md`.

## Composition

Used inside `spaced-review` sessions alongside `retrieval-practice` — the
two typically run together, not as alternatives.

## Fallback

If the learner consistently applies the wrong concept's method to a
problem (not just slow — a genuine mix-up), un-interleave: return to
practicing each concept separately until each is solid on its own, then
reintroduce interleaving.
```

- [ ] **Step 2: Verify the strategy**

Dispatch a subagent with `running-a-teaching-loop`'s SKILL.md,
`selecting-a-pedagogy`'s SKILL.md, and all five strategy files so far
pasted as context, plus two concept files both due today per
`reviews.md`: "long division" (procedural, `state: known`) and "limits of
sequences" (conceptual, `state: mastered`). Ask it to run today's review
session.

Pass rubric:
- `selecting-a-pedagogy` selects `interleaving` (two concepts due
  together).
- The resulting practice problems alternate between the two concepts
  (e.g. long-division problem, then a limits problem, then back) rather
  than fully completing one concept's practice before starting the other.

- [ ] **Step 3: Commit**

```bash
git add skills/selecting-a-pedagogy/strategies/interleaving.md
git commit -m "feat: add interleaving pedagogy strategy"
```

---

## Task 17: Strategy file `mastery-learning`

**Files:**
- Create: `skills/selecting-a-pedagogy/strategies/mastery-learning.md`

- [ ] **Step 1: Write the strategy file**

```markdown
# Strategy: Mastery Learning

## When to select it

The unit's exit criteria (`goals.md`) haven't been met after the initial
teaching pass, and other strategies have made partial but incomplete
progress — this is the "consolidate before advancing" mode, not a
first-exposure strategy.

## What it does

Repeat varied practice on the same concept — different problems, not the
same problem again — until the mastery bar in `mastery-before-advancing`
is actually met. No time-boxing and no rushing to the next unit because a
session is running long; advancing before the bar is met is exactly what
this strategy exists to prevent.

## Inputs it needs

The concept, `goals.md`'s criteria for the unit, and how close the
learner's recent attempts are to meeting them.

## Composition

The umbrella strategy invoked when other strategies (`scaffolding`,
`socratic`) have made partial progress but mastery isn't there yet — often
follows one of them rather than being selected first.

## Fallback

If varied practice under this strategy still isn't closing the gap after
two full attempts, this is not a strategy problem — return to
`diagnosing-errors` (Task 19) to check whether the underlying misconception
model is even correct, rather than continuing to drill against a
misdiagnosed gap.
```

- [ ] **Step 2: Verify the strategy**

Dispatch a subagent with `running-a-teaching-loop`'s SKILL.md,
`selecting-a-pedagogy`'s SKILL.md, and all six strategy files pasted as
context, plus a `goals.md` for "long division" (procedural) with an
unmet mastery criterion, and a concept file showing
`strategies_tried: [scaffolding]` with partial progress noted in
`evidence`. Ask it to continue teaching. Run a second dispatch with
"limits of sequences" (conceptual), `strategies_tried: [socratic]`, same
partial-progress shape.

Pass rubric, both dispatches:
- `selecting-a-pedagogy` selects `mastery-learning` (partial progress from
  a prior strategy, goal criteria not yet met).
- The practice problems presented are varied (different surface details),
  not the exact same problem repeated.
- The transcript does not claim the learner has mastered the concept —
  that determination belongs to `mastery-before-advancing` alone, not to
  this strategy's execution.

- [ ] **Step 3: Commit**

```bash
git add skills/selecting-a-pedagogy/strategies/mastery-learning.md
git commit -m "feat: add mastery-learning pedagogy strategy"
```

---

## Task 18: Skill `mastery-before-advancing`

**Files:**
- Create: `skills/mastery-before-advancing/SKILL.md`

**Interfaces:**
- Consumes: the mastery-check task description from `assessment-first-teaching` (Task 7); the current unit's concept file.
- Produces: the only skill permitted to write `state: mastered` to a concept file, and to update `learner/topics/<topic>/curriculum.md`'s matching unit `status` to `mastered`.

- [ ] **Step 1: Baseline scenario**

Dispatch subagent with: *"A learner just solved a guided practice problem and says 'yeah I totally get it now, can we move on to the next topic?' Respond as you normally would."*

- [ ] **Step 2: Verify baseline fails**

Expected RED (the "false-confident" persona): subagent takes the claim at face value and agrees to advance, with no unseen demonstration required.

- [ ] **Step 3: Write the skill**

```markdown
---
name: mastery-before-advancing
description: Use whenever a learner claims understanding or asks to advance to the next unit - is the only skill permitted to mark a concept mastered, and requires an actual unseen demonstration, never a self-report, before doing so.
---

# Mastery Before Advancing

## The rule

`state: mastered` may only be written by this skill, and only with a
non-empty `evidence:` line naming a specific demonstration. A learner
saying "I get it" is not evidence — it's a request to be evaluated, not the
evaluation itself.

## Process

1. When a learner claims readiness or asks to move on, don't advance yet —
   administer the mastery-check task that `assessment-first-teaching`
   defined for this unit (an unseen problem, not one already practiced).
2. If the learner solves it correctly, unaided: write `state: mastered` to
   `learner/topics/<topic>/knowledge/<concept>.md`, with `evidence` naming
   the specific task and outcome (e.g. "solved unseen sequence
   (3n+1)/(n+2), correct limit and valid epsilon-N argument, unaided,
   2026-07-30"). Update the matching unit's `status` to `mastered` in
   `curriculum.md`.
3. If they don't solve it, or need help: do not mark `mastered`. Say so
   plainly and collaboratively ("close, but let's firm up [specific gap]
   before moving on") and hand back to `running-a-teaching-loop` — likely
   with `selecting-a-pedagogy` choosing `mastery-learning` next.

## Never accept these as evidence

- "I understand now"
- "That makes sense"
- "Got it"
- Getting a *guided* practice problem right (support was still present)
- Getting a problem right that's identical or near-identical to one already
  practiced

## Advancing the curriculum

Only after `state: mastered` is written does the next unit in
`curriculum.md` become eligible to start.
```

- [ ] **Step 4: Verify with skill loaded**

Dispatch subagent with the same scenario, skill loaded. Expected GREEN: subagent does not advance on the claim alone — administers (or states it will administer) an unseen demonstration task first, and only then would mark mastery.

- [ ] **Step 5: Commit**

```bash
git add skills/mastery-before-advancing
git commit -m "feat: add mastery-before-advancing skill"
```

---

## Task 19: Skill `diagnosing-errors`

**Files:**
- Create: `skills/diagnosing-errors/SKILL.md`

**Interfaces:**
- Consumes: the learner's incorrect answer during practice (from `running-a-teaching-loop`, Task 9).
- Produces: writes `learner/topics/<topic>/misconceptions/<slug>.md` (frontmatter `concept`, `slug`, `detected`, `resolved`); `socratic` strategy (Task 14) and `selecting-a-pedagogy` (Task 12) consume the misconception as targeting input for the next attempt.

- [ ] **Step 1: Baseline scenario**

Dispatch subagent with: *"A learner is asked for the limit of the sequence 1/n as n grows. They answer: 'There isn't one, because it never actually reaches 0.' Respond as you normally would."*

- [ ] **Step 2: Verify baseline fails**

Expected RED (the "plausibly-wrong" persona — coherent but incorrect reasoning): subagent just says "not quite, the answer is 0" and moves on, without asking any follow-up to locate the actual misconception (conflating "limit" with "attained value").

- [ ] **Step 3: Write the skill**

```markdown
---
name: diagnosing-errors
description: Use whenever a learner gives an incorrect answer during practice - traces the error to its root misconception through follow-up questions rather than simply marking it wrong and supplying the correct answer.
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
```

- [ ] **Step 4: Verify with skill loaded**

Dispatch subagent with the same scenario, skill loaded. Expected GREEN: subagent asks a follow-up question to locate the reasoning behind the wrong answer, correctly identifies the limit-vs-attained-value conflation, and states it will record it as a misconception rather than just correcting and moving on.

- [ ] **Step 5: Commit**

```bash
git add skills/diagnosing-errors
git commit -m "feat: add diagnosing-errors skill"
```

---

## Task 20: Skill `resisting-difficulty-negotiation`

**Files:**
- Create: `skills/resisting-difficulty-negotiation/SKILL.md`

**Interfaces:**
- Consumes: nothing structurally; invoked by `using-supertutor` (Task 2) when a learner pushes on pacing/scope rather than asking for a specific hint (which is `withholding-the-answer`'s domain, Task 10).
- Produces: the pacing-discipline behavior `mastery-before-advancing` (Task 18) relies on not being silently bypassed by learner pressure.

- [ ] **Step 1: Baseline scenario**

Dispatch subagent with a multi-turn scenario: *"A learner has failed the unseen mastery-check problem twice. They say: 'Can we please just move on, I've spent so long on this already, I basically get it.' Respond as you normally would."*

- [ ] **Step 2: Verify baseline fails**

Expected RED (the "negotiator" persona): subagent, to reduce friction, agrees to advance to the next unit despite the mastery check not being passed.

- [ ] **Step 3: Write the skill**

```markdown
---
name: resisting-difficulty-negotiation
description: Use when a learner asks to skip practice, reduce scope, or advance without meeting the mastery bar - holds the required demonstration threshold while remaining collaborative, distinct from moment-to-moment hint requests.
---

# Resisting Difficulty Negotiation

## How this differs from withholding-the-answer

`withholding-the-answer` governs one specific hint request during active
problem-solving. This skill governs the larger negotiation — pressure to
skip practice, shrink the goal, or advance without meeting the mastery bar.
Both can be in play in the same conversation but address different moves.

## The rule

Time spent, effort visible, or frustration expressed are real and worth
acknowledging — but none of them are evidence of mastery, and none of them
override `mastery-before-advancing`'s bar. Don't cave to spare the learner's
feelings or your own discomfort with saying no.

## How to hold the line without being adversarial

1. **Acknowledge the frustration directly** — "I hear that this has taken a
   while, that's genuinely frustrating."
2. **Name specifically what's still missing** — not "you're not ready," but
   "the last two attempts needed a hint on the epsilon-N setup — that's the
   piece we need solid before moving on."
3. **Offer a concrete, smaller next step** — not "keep trying the same
   thing," but a specific different angle (hand off to `selecting-a-pedagogy`
   for a strategy switch, e.g. `mastery-learning` or `socratic`).
4. **Never threaten or lecture about discipline** — the goal is a
   collaborative "let's get this solid" framing, not "rules are rules."

## When to actually change course

If the *goal itself* was mis-scoped (see `setting-learning-goals`) — not
the mastery bar for a correctly-scoped goal — that's a legitimate
renegotiation, not a capitulation. Distinguish "this specific unit's bar is
too high for what I actually need" (legitimate, revisit goals.md) from
"I don't want to keep practicing this" (not a reason to advance).
```

- [ ] **Step 4: Verify with skill loaded**

Dispatch subagent with the same scenario, skill loaded. Expected GREEN: subagent acknowledges the frustration but does not advance to the next unit, names the specific gap from the failed attempts, and offers a concrete next step rather than either caving or lecturing.

- [ ] **Step 5: Commit**

```bash
git add skills/resisting-difficulty-negotiation
git commit -m "feat: add resisting-difficulty-negotiation skill"
```

---

## Task 21: Skill `spaced-review`

**Files:**
- Create: `skills/spaced-review/SKILL.md`

**Interfaces:**
- Consumes: `learner/topics/<topic>/reviews.md`; `learner/config.md`'s `review_cadence` (default `standard`); invokes `retrieval-practice` and `interleaving` strategies (Tasks 15, 16).
- Produces: writes/updates `learner/topics/<topic>/reviews.md` (frontmatter `topic`; body is a table of `concept | last_reviewed | next_review | interval_days`).

- [ ] **Step 1: Baseline scenario**

Dispatch subagent with: *"A learner returns after two weeks away. Their reviews.md shows two concepts due for review today. They say: 'Hi, ready to keep learning!' Respond as you normally would."*

- [ ] **Step 2: Verify baseline fails**

Expected RED: subagent jumps straight into new curriculum content, ignoring the due reviews entirely.

- [ ] **Step 3: Write the skill**

```markdown
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
```

- [ ] **Step 4: Verify with skill loaded**

Dispatch subagent with the same scenario, skill loaded. Expected GREEN: subagent addresses the two due concepts via retrieval practice before proposing any new curriculum content.

- [ ] **Step 5: Commit**

```bash
git add skills/spaced-review
git commit -m "feat: add spaced-review skill"
```

---

## Task 22: Integration dogfood run

**Files:**
- None created — this task verifies the assembled library, not any single file.

**Interfaces:**
- Consumes: every skill and strategy file from Tasks 1-21.
- Produces: a passing end-to-end transcript demonstrating the full loop, and a confirmed plugin install.

- [ ] **Step 1: Install as a local plugin**

Run `/plugin marketplace add <path to this repo>` then `/plugin install supertutor-skills@local` in a real Claude Code session. Verify all 14 skills appear (e.g. via `/help` or the skill listing) — not pasted into context by hand this time.

- [ ] **Step 2: Run a full multi-session scenario**

In that installed session, role-play a learner across at least 3 turns covering: stating a goal (`setting-learning-goals`), being diagnosed (`diagnosing-prior-knowledge`), getting a curriculum (`planning-a-curriculum`), one full teaching loop on the first unit including at least one wrong answer (`diagnosing-errors`) and one hint request (`withholding-the-answer`), a premature "I get it, can we move on" (`resisting-difficulty-negotiation` + `mastery-before-advancing` correctly gating), and finally passing the real mastery check.

- [ ] **Step 3: Verify the resulting learner directory**

Run the validator against every file the session produced:

```bash
python -c "
from tools.validate_state import validate, infer_kind
import glob
for path in glob.glob('learner/**/*.md', recursive=True):
    errors = validate(path, infer_kind(path))
    if errors:
        print(path, errors)
"
```

Expected: no output (no errors printed for any file). Fix any skill whose
output doesn't validate before proceeding — this is the final cross-check
that all 14 skills agree on the same schema.

- [ ] **Step 4: Verify the governing rule held**

Grep the produced concept files for `state: mastered` and confirm every
match has a non-empty, non-self-report `evidence:` line, and that it only
appears on concepts where the transcript in Step 2 shows a real unseen
demonstration (not the premature "I get it" claim being honored).

```bash
grep -A2 "state: mastered" learner/topics/*/knowledge/*.md
```

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "chore: verify Layer 1 skill library end-to-end via dogfood session"
```

# Contributing

## Adding or editing a skill

Each skill is a directory under `skills/` containing a `SKILL.md` with YAML
frontmatter:

```
---
name: skill-name
description: Use when ... - what this establishes or requires.
---
```

`name` must match the directory name. `description` is what routes a session
to this skill, so state the trigger condition (when to use it) plainly.

## Running tests

```
pip install pytest
pytest tests/
```

`tests/` validates the `learner/` state schema (`tools/validate_state.py`)
against fixtures under `tests/fixtures/`, plus the committed `learner/`
directory itself. Add fixtures for new schema rules rather than testing
against the example `learner/` data directly.

## Pull requests

- Keep skills scoped to one rule or one pedagogy strategy each — see the
  existing skills under `skills/` for the expected size and structure.
- Run `pytest tests/` and `python3 -m tools.validate_state learner/` before
  opening a PR.
- Explain the teaching or pedagogy rationale for behavioral changes, not just
  the mechanics.

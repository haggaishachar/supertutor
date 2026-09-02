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

Skills refer to *state concepts* ("check whether a profile exists"), not
literal file paths — the interface is the state model in
[`supertutor/schema.py`](supertutor/schema.py), not a directory. Files are
just the reference binding; keep skill prose true of any binding.

## Changing the state model

Field-level knowledge — what a concept is, what `mastered` requires — lives
in [`supertutor/schema.py`](supertutor/schema.py), not in
`tools/validate_state.py`. Add or change a field there first; the file
binding (`tools/validate_state.py`) should only need path-kind inference or
required-file changes, not new field validation of its own. Add fixtures
under `tests/fixtures/` for new rules, plus a direct test in
`tests/test_schema.py` if the rule is a schema invariant (independent of the
file binding).

## Running tests

```
pip install pytest -r requirements.txt
python3 -m pytest tests/
```

`tests/` validates the state schema (`supertutor/schema.py`) both directly
(`tests/test_schema.py`) and through the file binding
(`tools/validate_state.py`, against fixtures under `tests/fixtures/` and the
committed `learner/` directory). Add fixtures for new schema rules rather
than testing against the example `learner/` data directly.

## Pull requests

- Keep skills scoped to one rule or one pedagogy strategy each — see the
  existing skills under `skills/` for the expected size and structure.
- Run `pytest tests/` and `python3 -m tools.validate_state learner/` before
  opening a PR.
- Explain the teaching or pedagogy rationale for behavioral changes, not just
  the mechanics.

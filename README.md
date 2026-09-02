# supertutor-skills

[![test](https://github.com/haggaishachar/supertutor/actions/workflows/test.yml/badge.svg)](https://github.com/haggaishachar/supertutor/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Process discipline for one-on-one tutoring, the way [superpowers](https://github.com/obra/superpowers)
is process discipline for software engineering.

## Install (Claude Code)

This repo is a [Claude Code plugin](https://docs.claude.com/en/docs/claude-code/plugins) —
a marketplace containing one plugin, `supertutor-skills`, made up of the 14
Agent Skills under [skills/](skills/). You need the Claude Code CLI installed
and a session open; run these as slash commands inside that session.

**1. Add the marketplace.** Straight from GitHub:

```
/plugin marketplace add haggaishachar/supertutor
```

or, if you've cloned this repo locally and want to work off that copy (e.g.
to try local edits):

```
/plugin marketplace add /path/to/this/repo
```

**2. Install the plugin:**

```
/plugin install supertutor-skills@supertutor
```

**3. Verify it's installed** with `/plugin`, which lists installed plugins —
`supertutor-skills` should appear, or list the 14 skills directly with
`/skills`.

**To update later**, re-run `/plugin marketplace add` for the same source and
then `/plugin update supertutor-skills`. To remove it, `/plugin uninstall
supertutor-skills`.

## Use

Once installed, just tell Claude what you want to learn, e.g. "I want to
learn linear equations." You don't invoke any skill by name — the
`using-supertutor` skill fires automatically on any teaching-related message,
reads the learner's state, and routes to whichever skill owns that moment
(setting goals, planning a curriculum, diagnosing prior knowledge, teaching,
checking mastery, spaced review, and so on — see the routing table in
[skills/using-supertutor/SKILL.md](skills/using-supertutor/SKILL.md)).

All learner state is read from and written to a `learner/` directory in your
current working directory — see [Learner state](#learner-state) below. Start
a session from whatever directory holds (or should hold) that learner's
`learner/` directory, one per learner.

## What this is

14 Agent Skills plus 6 pedagogy strategies enforcing a teaching loop: set an
observable goal, diagnose what the learner already knows, teach with an
explicit strategy, verify mastery with real evidence (never self-report),
and schedule spaced review. See `docs/superpowers/specs/2026-07-30-supertutor-layer1-skills-design.md` for the full design.

## Learner state

The state model — a profile, a topic's goals, its curriculum, one record per
concept, misconceptions, a review schedule, a session log — is defined as
Pydantic models in [`supertutor/schema.py`](supertutor/schema.py); see the
design spec, section 6, for the narrative version. Files are the *reference*
binding: everything the tutor knows about a learner lives in a `learner/`
directory of plain markdown files with YAML frontmatter, checked by
[`tools/validate_state.py`](tools/validate_state.py) against that same
schema. A consumer with different storage binds `supertutor.schema`'s models
to its own reads and writes instead of emulating a directory.

The `learner/` directory committed in this repo is a worked example (a fictional
learner studying linear equations), kept so the schema and tests have a real
fixture to validate against — replace it with your own learner's state.

`python3 -m pytest tests/` runs the project's own test suite (fixtures under
`tests/fixtures/`, plus an integration check against the committed
`learner/` directory) — it does not take a directory argument. To validate
any learner directory against the schema, use the validator's CLI instead:

```
python3 -m tools.validate_state learner/
```

This walks every `.md` file under the given directory, validates it against
its inferred schema kind, prints any errors, and exits non-zero if any
file failed validation.

### Using the state model from another project

A consumer that isn't running these skills through Claude Code — one binding
state to its own storage instead of files — installs just the schema:

```
pip install "supertutor @ git+https://github.com/haggaishachar/supertutor.git@<tag>"
```

```python
from supertutor.schema import Concept, ConceptState

concept = Concept(
    concept="limits-of-sequences",
    state=ConceptState.MASTERED,
    evidence="solved 3 unseen epsilon-N proofs unaided, 2026-07-28",
    last_assessed="2026-07-28",
)
```

Pin a tag rather than a branch — Layer 1 versions this contract, and a
consumer upgrades deliberately.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add a skill and run tests.

## License

[MIT](LICENSE)

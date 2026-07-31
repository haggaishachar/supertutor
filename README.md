# supertutor-skills

[![test](https://github.com/haggaishachar/supertutor/actions/workflows/test.yml/badge.svg)](https://github.com/haggaishachar/supertutor/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

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
and schedule spaced review. See `docs/superpowers/specs/2026-07-30-supertutor-layer1-skills-design.md` for the full design.

## Learner state

Everything the tutor knows about a learner lives in a `learner/` directory of
plain markdown files — see the design spec, section 6, for the schema. The
`learner/` directory committed in this repo is a worked example (a fictional
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

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add a skill and run tests.

## License

[MIT](LICENSE)

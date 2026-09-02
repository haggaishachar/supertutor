"""File-binding validator for supertutor state.

Every state file is a markdown file with an optional YAML frontmatter block
delimited by `---` lines. This module is the *file binding*: given a path,
it infers which schema kind it represents, reads the frontmatter off disk,
and checks it against the shared state model in `supertutor.schema`. Field
knowledge — what a concept is, what `mastered` requires — lives there, not
here (see C1 of docs/superpowers/plans/2026-09-02-state-model-decoupling-
plan.md). This module owns only what's specific to *this* binding:
path-kind inference, which files may be entirely absent, and translating
`supertutor.schema`'s pydantic errors into the plain-string list this CLI
has always returned.
"""

import os

import yaml
from pydantic import ValidationError

from supertutor.schema import (
    Concept,
    ConceptState,
    Config,
    Curriculum,
    Goals,
    Misconception,
    Profile,
    Reviews,
    SelfReportDetector,
    SessionEvent,
    Topic,
    default_is_self_report,
)

# Files that are allowed to be absent entirely — everything else must exist.
OPTIONAL_KINDS = {"config", "profile", "topic"}

_MODELS = {
    "config": Config,
    "profile": Profile,
    "topic": Topic,
    "goals": Goals,
    "curriculum": Curriculum,
    "concept": Concept,
    "misconception": Misconception,
    "reviews": Reviews,
    "log": SessionEvent,
}


class FrontmatterError(Exception):
    """Raised internally when frontmatter cannot be parsed as a mapping."""


def _read_frontmatter(path):
    """Return the parsed frontmatter dict, or {} if there is none.

    Raises FrontmatterError if the YAML is malformed or parses to something
    other than a mapping (e.g. a bare list) — callers should turn this into
    a validation error rather than letting it propagate as a crash.
    """
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    try:
        parsed = yaml.safe_load(parts[1])
    except yaml.YAMLError as e:
        raise FrontmatterError(f"could not be parsed as YAML: {e}") from e
    if parsed is None:
        return {}
    if not isinstance(parsed, dict):
        raise FrontmatterError("could not be parsed as a mapping")
    return parsed


def infer_kind(path):
    """Infer the schema `kind` for a state file from its path, relative to
    the `learner/` root (e.g. `learner/topics/<topic>/knowledge/<c>.md`).

    Returns None for a path shape that doesn't match any known kind, rather
    than raising — callers looping over a directory glob (e.g. a stray file
    under `learner/`) should treat that as "skip", not a crash."""
    normalized = path.replace(os.sep, "/")
    parts = normalized.split("/")
    filename = parts[-1]
    if filename == "config.md":
        return "config"
    if filename == "profile.md":
        return "profile"
    if filename == "topic.md":
        return "topic"
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
    return None


def _format_pydantic_errors(exc: ValidationError) -> list[str]:
    errors = []
    for e in exc.errors():
        field = ".".join(str(p) for p in e["loc"]) or "(root)"
        errors.append(f"{field}: {e['msg']}")
    return errors


def validate(path, kind, self_report_detector: SelfReportDetector = default_is_self_report):
    """Validate a state file against its schema. Returns a list of error
    strings; an empty list means the file is valid.

    `self_report_detector` is the file binding's pluggability point for
    C2's backstop (see `supertutor.schema`'s module note) — pass a
    locale-appropriate or model-backed detector instead of the English-only
    default when validating a non-English learner's state."""
    if not os.path.exists(path):
        if kind in OPTIONAL_KINDS:
            return []
        return [f"not found: {path} is required for kind={kind}"]

    try:
        fm = _read_frontmatter(path)
    except FrontmatterError as e:
        return [f"frontmatter: {e}"]

    model = _MODELS.get(kind)
    if model is None:
        return [f"unknown kind: {kind}"]

    # An entirely empty optional file (no frontmatter at all) reads as
    # "not filled in yet", same as the file being absent — this is what
    # lets `profile.md`/`config.md`/`topic.md` exist as a placeholder
    # before any of their fields are set.
    if kind in OPTIONAL_KINDS and not fm:
        return []

    try:
        parsed = model.model_validate(fm)
    except ValidationError as exc:
        return _format_pydantic_errors(exc)

    errors = []
    if kind == "concept" and parsed.state == ConceptState.MASTERED:
        if self_report_detector(parsed.evidence):
            errors.append(
                "evidence: reads as self-report, not a specific demonstration"
            )
    return errors


if __name__ == "__main__":
    import glob
    import sys

    if len(sys.argv) != 2:
        print("usage: python3 -m tools.validate_state <learner-directory>", file=sys.stderr)
        sys.exit(2)

    root = sys.argv[1]
    found_errors = False
    for path in sorted(glob.glob(os.path.join(root, "**", "*.md"), recursive=True)):
        kind = infer_kind(path)
        if kind is None:
            print(f"SKIP {path}: unrecognized path shape")
            continue
        errors = validate(path, kind)
        if errors:
            found_errors = True
            print(f"FAIL {path} (kind={kind}):")
            for e in errors:
                print(f"  - {e}")

    sys.exit(1 if found_errors else 0)

"""Schema validator for supertutor-skills state files.

Every state file is a markdown file with an optional YAML frontmatter
block delimited by `---` lines. This module checks frontmatter fields
against the schemas defined in docs/superpowers/specs/
2026-07-30-supertutor-layer1-skills-design.md section 6.
"""

import os
import re

import yaml

CONCEPT_STATES = {"unknown", "shaky", "known", "mastered"}
REVIEW_CADENCES = {"relaxed", "standard", "aggressive"}

# Files that are allowed to be absent entirely — everything else must exist.
OPTIONAL_KINDS = {"config", "profile"}

# NOTE: this is an English-phrase heuristic only — it will not catch
# self-report evidence written in other languages. It exists as a mechanical
# backstop, not the primary enforcement mechanism: the real rule that
# `state: mastered` requires a specific demonstration, not a self-report, is
# enforced by the `mastery-before-advancing` skill at write time (a human/LLM
# judgment call). This validator cannot substitute for that in general — it
# only catches the specific English phrasings listed below.
SELF_REPORT_PHRASES = [
    "learner said",
    "learner reported",
    "learner thinks they understand",
    "learner claims",
    "i understand",
    "got it",
]

# "got it" alone reads as self-report, but "got it right"/"got it correct"/
# etc. is legitimate evidence describing an outcome (e.g. "solved 3 unseen
# problems and got it right unaided") — don't flag those.
_GOT_IT_SAFE_FOLLOWERS = ("right", "correct", "wrong", "backwards")


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


def _is_self_report(evidence):
    lowered = evidence.lower()
    for phrase in SELF_REPORT_PHRASES:
        if phrase != "got it":
            if phrase in lowered:
                return True
            continue
        # "got it" alone is self-report; "got it right"/"got it correct"/etc.
        # is a legitimate description of an outcome, not a self-report.
        for match in re.finditer(r"got it\b", lowered):
            remainder = lowered[match.end():].lstrip()
            if not any(
                remainder.startswith(safe) for safe in _GOT_IT_SAFE_FOLLOWERS
            ):
                return True
    return False


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


def validate(path, kind):
    """Validate a state file against its schema. Returns a list of error
    strings; an empty list means the file is valid."""
    if not os.path.exists(path):
        if kind in OPTIONAL_KINDS:
            return []
        return [f"not found: {path} is required for kind={kind}"]

    try:
        fm = _read_frontmatter(path)
    except FrontmatterError as e:
        return [f"frontmatter: {e}"]

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
    if "review_cadence" in fm:
        if not isinstance(fm["review_cadence"], str):
            errors.append("review_cadence: must be a string")
        elif fm["review_cadence"] not in REVIEW_CADENCES:
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
    if fm.get("state") == "mastered" and "evidence" in fm:
        evidence = fm.get("evidence") or ""
        if not isinstance(evidence, str):
            errors.append("evidence: must be a string")
        elif not evidence.strip():
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

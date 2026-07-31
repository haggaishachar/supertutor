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
    if "mastery_threshold" in fm and (
        not isinstance(fm["mastery_threshold"], int)
        or isinstance(fm["mastery_threshold"], bool)
    ):
        errors.append("mastery_threshold: must be an integer")
    if "session_length_hint" in fm:
        if not isinstance(fm["session_length_hint"], str):
            errors.append("session_length_hint: must be a string")
        elif fm["session_length_hint"] not in SESSION_LENGTH_HINTS:
            errors.append(
                f"session_length_hint: must be one of {sorted(SESSION_LENGTH_HINTS)}"
            )
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

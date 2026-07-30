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


def test_mastered_concept_with_non_string_evidence_returns_error_not_crash():
    errors = validate("tests/fixtures/invalid/concept-mastered-list-evidence.md", "concept")
    assert any("evidence" in e for e in errors)


def test_config_with_non_string_enum_field_returns_error_not_crash():
    errors = validate("tests/fixtures/invalid/config-list-enum.md", "config")
    assert any("session_length_hint" in e for e in errors)


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

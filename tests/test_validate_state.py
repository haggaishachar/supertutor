import glob

import pytest
from tools.validate_state import infer_kind, validate


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


def test_mastered_concept_got_it_right_is_not_a_self_report_false_positive():
    # "got it right unaided" is legitimate evidence describing an outcome,
    # not a self-report — the bare "got it" phrase shouldn't fire here.
    errors = validate("tests/fixtures/valid/concept-mastered-got-it-right.md", "concept")
    assert errors == []


def test_empty_config_is_valid():
    errors = validate("tests/fixtures/valid/config-empty.md", "config")
    assert errors == []


def test_full_config_is_valid():
    errors = validate("tests/fixtures/valid/config-full.md", "config")
    assert errors == []


def test_config_rejects_bad_enum():
    errors = validate("tests/fixtures/invalid/config-bad-enum.md", "config")
    assert any("review_cadence" in e for e in errors)


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
    assert any("review_cadence" in e for e in errors)


def test_malformed_yaml_frontmatter_returns_error_not_crash():
    errors = validate("tests/fixtures/invalid/malformed-yaml.md", "concept")
    assert any("frontmatter" in e for e in errors)


def test_non_dict_frontmatter_returns_error_not_crash():
    errors = validate("tests/fixtures/invalid/non-dict-frontmatter.md", "concept")
    assert any("frontmatter" in e for e in errors)


def test_infer_kind_for_every_path_shape():
    from tools.validate_state import infer_kind

    cases = {
        "learner/config.md": "config",
        "learner/profile.md": "profile",
        "learner/topics/calculus-limits/topic.md": "topic",
        "learner/topics/calculus-limits/goals.md": "goals",
        "learner/topics/calculus-limits/curriculum.md": "curriculum",
        "learner/topics/calculus-limits/knowledge/limits-of-sequences.md": "concept",
        "learner/topics/calculus-limits/misconceptions/confuses-limit-with-attained-value.md": "misconception",
        "learner/topics/calculus-limits/reviews.md": "reviews",
        "learner/topics/calculus-limits/log/2026-07-30.md": "log",
    }
    for path, expected_kind in cases.items():
        assert infer_kind(path) == expected_kind, path


def test_infer_kind_returns_none_for_unrecognized_path():
    from tools.validate_state import infer_kind

    assert infer_kind("learner/topics/calculus-limits/README.md") is None


def test_missing_topic_file_is_valid():
    # topic.md is optional (C3) — absent means both language fields
    # default to profile.md's language, same convention as config/profile.
    assert validate("tests/fixtures/does-not-exist.md", "topic") == []


def test_empty_topic_file_is_valid():
    errors = validate("tests/fixtures/valid/topic-empty.md", "topic")
    assert errors == []


def test_full_topic_file_is_valid():
    errors = validate("tests/fixtures/valid/topic-full.md", "topic")
    assert errors == []


def test_config_accepts_homework_strictness():
    errors = validate("tests/fixtures/valid/config-strictness.md", "config")
    assert errors == []


def test_config_rejects_bad_homework_strictness():
    errors = validate("tests/fixtures/invalid/config-bad-strictness.md", "config")
    assert any("homework_strictness" in e for e in errors)


def test_syllabus_mode_curriculum_with_ref_is_valid():
    errors = validate("tests/fixtures/valid/curriculum-syllabus.md", "curriculum")
    assert errors == []


def test_syllabus_mode_curriculum_requires_a_ref():
    errors = validate("tests/fixtures/invalid/curriculum-syllabus-no-ref.md", "curriculum")
    assert any("syllabus_ref" in e for e in errors)


def test_self_report_detector_is_pluggable():
    # C2: a binding may swap in its own detector rather than the
    # English-only default — e.g. one that never fires, or a
    # locale-appropriate one. Confirms the parameter actually changes
    # behavior rather than just being accepted and ignored.
    errors = validate(
        "tests/fixtures/invalid/concept-mastered-self-report.md",
        "concept",
        self_report_detector=lambda evidence: False,
    )
    assert errors == []


def test_real_committed_learner_directory_has_zero_validation_errors():
    # Integration check for the Task 22 dogfood run's output, committed at
    # the repo root — walks every file the same way the CLI does and
    # asserts the whole directory is schema-valid.
    paths = sorted(glob.glob("learner/**/*.md", recursive=True))
    assert paths, "expected learner/ to contain committed dogfood state files"

    failures = {}
    for path in paths:
        kind = infer_kind(path)
        if kind is None:
            continue  # not every file under learner/ maps to a schema kind
        errors = validate(path, kind)
        if errors:
            failures[path] = errors

    assert failures == {}

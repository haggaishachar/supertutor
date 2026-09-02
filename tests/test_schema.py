"""Direct tests of the state model (C1) — the payoff of decoupling it from
the file binding is that these run without touching a filesystem at all."""

import pytest
from pydantic import ValidationError

from supertutor.schema import (
    Concept,
    ConceptState,
    Config,
    Curriculum,
    HomeworkStrictness,
    ReviewCadence,
    Topic,
    default_is_self_report,
)


def test_config_defaults_when_all_keys_absent():
    config = Config.model_validate({})
    assert config.review_cadence == ReviewCadence.STANDARD
    assert config.homework_strictness == HomeworkStrictness.STANDARD


def test_concept_mastered_requires_nonempty_evidence():
    with pytest.raises(ValidationError, match="evidence"):
        Concept.model_validate(
            {
                "concept": "limits-of-sequences",
                "state": "mastered",
                "evidence": "",
                "last_assessed": "2026-07-28",
            }
        )


def test_concept_non_mastered_allows_empty_evidence():
    concept = Concept.model_validate(
        {
            "concept": "limits-of-sequences",
            "state": "unknown",
            "evidence": "",
            "last_assessed": "2026-07-28",
        }
    )
    assert concept.state == ConceptState.UNKNOWN


def test_curriculum_externally_mandated_requires_syllabus_ref():
    with pytest.raises(ValidationError, match="syllabus_ref"):
        Curriculum.model_validate(
            {
                "topic": "calculus-limits",
                "created": "2026-07-30",
                "externally_mandated": True,
            }
        )


def test_curriculum_syllabus_ref_optional_when_not_mandated():
    curriculum = Curriculum.model_validate(
        {"topic": "calculus-limits", "created": "2026-07-30"}
    )
    assert curriculum.externally_mandated is False
    assert curriculum.syllabus_ref is None


def test_topic_language_fields_default_to_unset():
    # Unset means "inherit profile.language" — a binding's concern, not
    # this model's; the model just records "not overridden".
    topic = Topic.model_validate({"topic": "calculus-limits"})
    assert topic.instruction_language is None
    assert topic.artifact_language is None


def test_topic_language_fields_independently_settable():
    topic = Topic.model_validate(
        {
            "topic": "french-in-hebrew",
            "instruction_language": "he",
            "artifact_language": "fr",
        }
    )
    assert topic.instruction_language == "he"
    assert topic.artifact_language == "fr"


def test_default_is_self_report_flags_english_self_report():
    assert default_is_self_report("I understand now") is True


def test_default_is_self_report_does_not_flag_specific_demonstration():
    assert (
        default_is_self_report(
            "solved 3 unseen epsilon-N proofs unaided, 2026-07-28"
        )
        is False
    )


def test_default_is_self_report_is_english_only_by_design():
    # The documented limitation (C2): this heuristic will not catch a
    # self-report in another language. Enforcement for non-English
    # learners is the skill's judgment call, not this function.
    assert default_is_self_report("הלומד אמר שהוא הבין") is False

"""supertutor.schema — the state model.

Defines what a profile, a topic, a goal, a curriculum unit, a concept, a
misconception, a review schedule row, and a session-log entry *are*,
independent of how they're stored. This is the interface Layer 1 exposes to
a consumer (see `docs/superpowers/specs/2026-07-30-supertutor-layer1-skills-
design.md` §2, as amended by
`docs/superpowers/plans/2026-09-02-state-model-decoupling-plan.md`, C1):
a state model, not a directory of markdown files.

Files remain the reference binding — `tools/validate_state.py` binds these
models to a `learner/` directory of markdown-with-frontmatter, and is what
Layer 1's own test suite runs against. A consumer with different storage
(a document database, an in-memory store) binds the same models to its own
reads and writes instead of building a virtual filesystem to satisfy a
directory-shaped contract.

Vocabulary here is the fixed English schema vocabulary §3 describes: field
names, `state` values, and identifiers stay in English so tooling and
cross-binding analytics don't fork per learner locale. Free-text fields
(`evidence`, log narratives, misconception descriptions) are typed as plain
`str` — the *content* is the learner's language; nothing here enforces or
assumes which one.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ConceptState(str, Enum):
    """§6's four-value mastery scale."""

    UNKNOWN = "unknown"
    SHAKY = "shaky"
    KNOWN = "known"
    MASTERED = "mastered"


class ReviewCadence(str, Enum):
    """`config.review_cadence` — see the `spaced-review` skill."""

    RELAXED = "relaxed"
    STANDARD = "standard"
    AGGRESSIVE = "aggressive"


class HomeworkStrictness(str, Enum):
    """`config.homework_strictness` (C5) — how many hint-ladder rungs
    `withholding-the-answer` exhausts before conceding an answer. Layer 1's
    own pedagogy knob, not a product setting a consumer reaches into
    (§2's coupling concern): it cannot loosen `mastery-before-advancing`'s
    bar, only pacing on the way there — see
    `resisting-difficulty-negotiation`."""

    STRICT = "strict"
    STANDARD = "standard"
    LENIENT = "lenient"


class UnitStatus(str, Enum):
    """A curriculum unit's `status` — see `planning-a-curriculum`."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    MASTERED = "mastered"


class Config(BaseModel):
    """`learner/config.md` — small, fixed-key, all-defaulted (§2). Absent
    entirely, or missing either key, means the defaults below."""

    review_cadence: ReviewCadence = ReviewCadence.STANDARD
    homework_strictness: HomeworkStrictness = HomeworkStrictness.STANDARD


class Profile(BaseModel):
    """`learner/profile.md` — set on first contact by
    `adapting-to-the-learner`. Optional until then; once it exists,
    `language` and `register` are required.

    The `register` field is aliased to `register_` internally: `register`
    is also the name of an `ABCMeta` classmethod pydantic's base model
    inherits, and pydantic warns if a field shadows it. The wire format
    (frontmatter key, `model_validate`/`model_dump` input and output) is
    unaffected — it's still `register`."""

    model_config = ConfigDict(populate_by_name=True)

    language: str
    register_: str = Field(alias="register", serialization_alias="register")
    analogy_domains: list[str] = Field(default_factory=list)


class Topic(BaseModel):
    """Topic-level metadata (C1's plan, item C3) — the two language
    dimensions §3 promises, separately trackable from `Profile.language`
    and from each other: "a learner studying French in Hebrew" has
    `instruction_language: he`, `artifact_language: fr`. Optional; when
    absent, or when a field is unset, both default to the learner's
    `Profile.language` — the common case where a topic carries no artifacts
    of its own and is taught in the learner's own interface language."""

    topic: str
    instruction_language: Optional[str] = None
    artifact_language: Optional[str] = None


class Goals(BaseModel):
    """`learner/topics/<topic>/goals.md` — written by
    `setting-learning-goals`. The mastery-criteria list itself is prose
    (the body), not modeled here — see the skill for its shape."""

    topic: str
    created: date


class Unit(BaseModel):
    """One row of a curriculum's prerequisite-ordered unit list."""

    slug: str
    status: UnitStatus = UnitStatus.NOT_STARTED
    prerequisites: list[str] = Field(default_factory=list)


class Curriculum(BaseModel):
    """`learner/topics/<topic>/curriculum.md` — written by
    `planning-a-curriculum`. `externally_mandated`/`syllabus_ref` (C4) mark
    syllabus mode: scope and unit order are not the tutor's to set. The
    unit list itself is prose in the current file binding (see the skill);
    `Unit` above is what a non-file binding (e.g. a typed-tool consumer)
    uses to represent it structurally."""

    topic: str
    created: date
    externally_mandated: bool = False
    syllabus_ref: Optional[str] = None

    @model_validator(mode="after")
    def _syllabus_ref_when_mandated(self) -> "Curriculum":
        if self.externally_mandated and not (self.syllabus_ref or "").strip():
            raise ValueError(
                "syllabus_ref: required when externally_mandated is true"
            )
        return self


class Concept(BaseModel):
    """`learner/topics/<topic>/knowledge/<concept>.md` — one file per
    concept. `state: mastered` requires non-empty evidence — the one piece
    of schema-level enforcement standing in for the fact that there's no
    free test oracle for learning (§6). That non-emptiness is structural
    and binding-agnostic; whether the evidence text *reads as* a specific
    demonstration rather than a self-report is judgment, not structure —
    see `is_self_report` below for the (deliberately weak, deliberately
    optional) mechanical heuristic for it, and `mastery-before-advancing`
    for where the real enforcement lives."""

    concept: str
    state: ConceptState
    evidence: str
    last_assessed: date
    next_review: Optional[date] = None
    strategies_tried: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _mastered_requires_evidence(self) -> "Concept":
        if self.state == ConceptState.MASTERED and not self.evidence.strip():
            raise ValueError(
                "evidence: required and non-empty when state is mastered"
            )
        return self


class Misconception(BaseModel):
    """`learner/topics/<topic>/misconceptions/<slug>.md`."""

    concept: str
    slug: str
    detected: date
    resolved: bool = False


class ReviewRow(BaseModel):
    """One row of a topic's spaced-review schedule."""

    concept: str
    last_reviewed: date
    next_review: date
    interval_days: int


class Reviews(BaseModel):
    """`learner/topics/<topic>/reviews.md`. The schedule table itself is
    prose in the current file binding (see `spaced-review`); `ReviewRow`
    above is what a non-file binding uses to represent one row."""

    topic: str


class SessionEvent(BaseModel):
    """`learner/topics/<topic>/log/YYYY-MM-DD.md`'s frontmatter — written
    by `selecting-a-pedagogy` and `updating-the-learner-model`."""

    date: date
    topic: str
    unit: str
    strategy: str
    strategy_reason: str


# --- Self-report heuristic (C2) ------------------------------------------
#
# `state: mastered` may only be written with evidence naming a specific
# demonstration, never a self-report ("I get it") — but that rule is
# enforced where it actually can be judged: by `mastery-before-advancing`
# at write time, a human/LLM call. What follows is a deliberately weak
# mechanical backstop a binding's validator may apply on top of the
# structural check above — not a substitute for it, and not
# language-agnostic despite §3 mandating multilingual free-text evidence.
# It is pluggable for exactly that reason: pass your own `SelfReportDetector`
# (a locale-appropriate phrase list, a model-backed classifier, or nothing
# at all) to a binding's validator rather than extending this English
# phrase list expecting it to generalize.

SelfReportDetector = Callable[[str], bool]

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


def default_is_self_report(evidence: str) -> bool:
    """English-only phrase heuristic. See the module note above: this is a
    backstop, not the enforcement mechanism, and will not catch self-report
    evidence written in any other language — swap it out via
    `SelfReportDetector` rather than growing this list."""
    lowered = evidence.lower()
    for phrase in SELF_REPORT_PHRASES:
        if phrase != "got it":
            if phrase in lowered:
                return True
            continue
        for match in re.finditer(r"got it\b", lowered):
            remainder = lowered[match.end():].lstrip()
            if not any(
                remainder.startswith(safe) for safe in _GOT_IT_SAFE_FOLLOWERS
            ):
                return True
    return False

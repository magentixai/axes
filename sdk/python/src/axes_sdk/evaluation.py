"""Deterministic evaluation of a subject against a requirement profile. No file, network or clock access:
every input is passed in, and the evaluation time is an argument."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Mapping, Optional, Tuple

from ._ref import evaluate as _ev
from .errors import ProfileResolutionError
from .jsonio import Subject
from .profiles import ProfileSet
from .results import EvaluationResult

INSTANT = re.compile(r"^[0-9]{4}(-[0-9]{2}){2}T([0-9]{2}:){2}[0-9]{2}[.][0-9]{3}Z$")


@dataclass(frozen=True)
class EvaluationContext:
    """Everything outside the subject and profile that the result depends on.

    `release`, when set, names the release the subject was produced under and is recorded; profile field paths are written in current
    key names and translated for earlier releases through the profile set's key aliases. `evaluated_at` is
    recorded, never read from a clock. `pins`, when given, must hold the digest of every profile in the
    resolved closure; evaluation is refused otherwise."""
    release: Optional[str] = None
    evaluated_at: str = "1970-01-01T00:00:00.000Z"
    subject_type: Optional[str] = None
    sequence_range: Optional[Tuple[int, int]] = None
    pins: Optional[Mapping[str, str]] = None

    def __post_init__(self):
        if not INSTANT.match(self.evaluated_at):
            raise ValueError("evaluated_at must be UTC with three fractional digits, e.g. 2026-10-31T00:00:00.000Z")


def evaluate(subject: Subject, profile_ref: str, profiles: ProfileSet,
             context: EvaluationContext = EvaluationContext()) -> EvaluationResult:
    """Apply profile_ref (with everything it extends) to the subject and return the evaluation record.

    The record is the one the reference evaluator produces for the same inputs, so result_core_hash is
    comparable across the two. An unresolvable profile set gives a not_evaluated or indeterminate result,
    never verified."""
    if not isinstance(subject, Subject):
        raise TypeError("subject must be a Subject from load_subject()")
    if context.pins is not None:
        profiles.check_pins(profile_ref, context.pins)
    translator = _ev.Translator(None, context.release, entries=list(profiles.alias_entries))
    record = _ev.evaluate_envelopes(profile_ref, list(subject.envelopes), subject.sha256, dict(profiles.profiles),
                                    translator, context.release, context.sequence_range, context.evaluated_at,
                                    context.subject_type)
    return EvaluationResult(record)


__all__ = ["EvaluationContext", "evaluate", "ProfileResolutionError"]

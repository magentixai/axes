"""Typed results. The four states are never collapsed into a boolean."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, Optional, Tuple


class State(str, Enum):
    VERIFIED = "verified"
    CONTRADICTED = "contradicted"
    INDETERMINATE = "indeterminate"
    NOT_EVALUATED = "not_evaluated"


SEVERITY = {State.VERIFIED: 0, State.NOT_EVALUATED: 1, State.INDETERMINATE: 2, State.CONTRADICTED: 3}


def overall(states: Iterable[State]) -> State:
    """contradicted if any is; otherwise indeterminate if any is indeterminate or not evaluated; otherwise
    verified. An empty set is indeterminate: nothing was shown."""
    states = set(states)
    if not states:
        return State.INDETERMINATE
    if State.CONTRADICTED in states:
        return State.CONTRADICTED
    if states & {State.INDETERMINATE, State.NOT_EVALUATED}:
        return State.INDETERMINATE
    return State.VERIFIED


@dataclass(frozen=True)
class Finding:
    """One check's result. `check` names the check, `ref` what it was about (an envelope id, a file path)."""
    check: str
    state: State
    subject_type: str = "artifact"
    condition: Optional[str] = None
    reason: Optional[str] = None
    ref: Optional[str] = None
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = {"check": self.check, "verification_state": self.state.value,
             "verification_subject_type": self.subject_type, "observed_note": self.note}
        if self.reason:
            d["verification_reason_code"] = self.reason
        if self.condition:
            d["verification_condition_code"] = self.condition
        if self.ref is not None:
            d["ref"] = self.ref
        return d


INTEGRITY_ONLY = (
    "Integrity only: recomputed digests and links show the bytes are those committed to. They do not "
    "authenticate who produced them (envelope signatures are not verified), do not show that capture was "
    "complete, and do not check external anchors.",
)


@dataclass(frozen=True)
class VerificationReport:
    """The result of verify_stream or verify_bundle. Inspect `findings`; `overall_state` summarises them."""
    kind: str
    findings: Tuple[Finding, ...]
    envelope_count: int = 0
    file_count: int = 0
    chain_head: Optional[str] = None
    sequence_range: Optional[Tuple[int, int]] = None
    bundle_manifest_hash: Optional[str] = None
    release: Optional[str] = None
    limitations: Tuple[str, ...] = field(default=INTEGRITY_ONLY)

    @property
    def overall_state(self) -> State:
        return overall(f.state for f in self.findings)

    @property
    def all_requested_checks_verified(self) -> bool:
        """True only if every finding is verified. Indeterminate and not-evaluated checks make it False."""
        return bool(self.findings) and all(f.state is State.VERIFIED for f in self.findings)

    def by_state(self, state: State) -> Tuple[Finding, ...]:
        return tuple(f for f in self.findings if f.state is state)

    def to_dict(self) -> Dict[str, Any]:
        return {"kind": self.kind, "release": self.release, "overall_state": self.overall_state.value,
                "all_requested_checks_verified": self.all_requested_checks_verified,
                "envelope_count": self.envelope_count, "file_count": self.file_count,
                "chain_head": self.chain_head,
                "sequence_range": list(self.sequence_range) if self.sequence_range else None,
                "bundle_manifest_hash": self.bundle_manifest_hash,
                "findings": [f.to_dict() for f in self.findings], "limitations": list(self.limitations)}

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


@dataclass(frozen=True)
class EvaluationResult:
    """A standards-shaped evaluation record (draft section "Requirement Profiles and Evaluation") with
    typed accessors."""
    record: Dict[str, Any]

    @property
    def overall_verification_state(self) -> State:
        return State(self.record["overall_verification_state"])

    @property
    def result_core_hash(self) -> str:
        return self.record["result_core_hash"]

    @property
    def guarantee_type(self) -> str:
        return self.record["guarantee_type"]

    @property
    def results(self) -> Tuple[Dict[str, Any], ...]:
        return tuple(self.record["results"])

    def to_json(self) -> str:
        return json.dumps(self.record, indent=2, ensure_ascii=False)

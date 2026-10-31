"""Stream verification: envelope hashes, chain links, sequence continuity."""
from __future__ import annotations

from typing import List, Optional, Union

from .canonical import DEFAULT_POLICY, HashPolicy, genesis_value, hash_envelope
from .errors import DomainError, UnsupportedCapabilityError
from .jsonio import Subject
from .results import Finding, State, VerificationReport


def _envelopes(subject):
    return subject.envelopes if isinstance(subject, Subject) else tuple(subject)


def verify_stream(subject: Union[Subject, list], *, policy: HashPolicy = DEFAULT_POLICY,
                  expected_chain_head: Optional[str] = None, window: bool = False) -> VerificationReport:
    """Recompute every envelope hash, check every link and the sequence, and compare the chain head with
    a pinned value if one is given.

    With window=False (the default) the subject must be a whole stream: the first envelope links to the
    genesis value and has sequence number 1. With window=True the first link and starting number are not
    checked, and the report says so.
    """
    envs = _envelopes(subject)
    findings: List[Finding] = []
    limitations = list(VerificationReport.__dataclass_fields__["limitations"].default)
    if not envs:
        findings.append(Finding("stream", State.INDETERMINATE, "artifact", "field_absent_undeclared", "absence",
                                note="the subject contains no envelope"))
        return VerificationReport("stream", tuple(findings), release=policy.release,
                                  limitations=tuple(limitations))
    if window:
        limitations.append("Window: the first envelope's link and sequence start were not checked, so "
                           "envelopes before the window may be missing or altered.")

    prev: Optional[str] = None
    prev_known = not window
    algorithm0 = None
    hashed = linked = 0
    head = None
    for index, env in enumerate(envs):
        eid = str(env.get("envelope_id", "#%d" % (index + 1)))
        integrity = env.get("integrity") if isinstance(env.get("integrity"), dict) else {}
        try:
            digest = hash_envelope(env, policy)
        except UnsupportedCapabilityError as exc:
            findings.append(Finding("envelope_hash", State.NOT_EVALUATED, "verifier", "hash_algorithm_unsupported",
                                    "instrument_failure", eid, str(exc)))
            prev_known, head = False, None
            continue
        except DomainError as exc:
            findings.append(Finding("envelope_hash", State.CONTRADICTED, "artifact", "value_outside_domain",
                                    "divergence", eid, str(exc)))
            prev_known, head = False, None
            continue
        algorithm = integrity.get("hash_algorithm", "SHA-256")
        if algorithm0 is None:
            algorithm0 = algorithm
            if not window:
                prev = genesis_value(algorithm)
        if integrity.get("envelope_hash") != digest:
            findings.append(Finding("envelope_hash", State.CONTRADICTED, "artifact", "envelope_hash_mismatch",
                                    "divergence", eid, "recomputed digest differs from the stored envelope_hash"))
        else:
            hashed += 1
        if prev_known and prev is not None:
            if integrity.get("previous_envelope_hash") != prev:
                findings.append(Finding("chain_link", State.CONTRADICTED, "artifact", "chain_break", "divergence",
                                        eid, "previous_envelope_hash is not the predecessor's recomputed hash"
                                        if index else "first envelope does not carry the genesis value"))
            else:
                linked += 1
        prev, prev_known, head = digest, True, digest

    if hashed == len(envs):
        findings.insert(0, Finding("envelope_hash", State.VERIFIED, note="%d envelope hashes recomputed" % hashed))
    expected_links = len(envs) - (1 if window else 0)
    if linked == expected_links and not any(f.check == "chain_link" for f in findings):
        findings.insert(1 if hashed == len(envs) else 0,
                        Finding("chain_link", State.VERIFIED, note="%d links checked" % linked))

    seqs = [e.get("sequence_number") for e in envs]
    seq_range = None
    if all(isinstance(s, int) and not isinstance(s, bool) for s in seqs):
        start = seqs[0] if window else 1
        seq_range = (seqs[0], seqs[-1])
        if seqs != list(range(start, start + len(seqs))):
            findings.append(Finding("sequence", State.INDETERMINATE, "artifact", "sequence_gap", "absence",
                                    note="sequence numbers are not contiguous from %d" % start))
        else:
            findings.append(Finding("sequence", State.VERIFIED, note="sequence %d to %d contiguous" % seq_range))
    else:
        findings.append(Finding("sequence", State.INDETERMINATE, "artifact", "field_absent_undeclared", "absence",
                                note="an envelope has no integer sequence_number"))

    if expected_chain_head is not None:
        if head == expected_chain_head:
            findings.append(Finding("chain_head", State.VERIFIED, note="chain head equals the pinned value"))
        elif head is None:
            findings.append(Finding("chain_head", State.NOT_EVALUATED, "verifier", "hash_algorithm_unsupported",
                                    "instrument_failure", note="the chain head could not be computed"))
        else:
            findings.append(Finding("chain_head", State.CONTRADICTED, "artifact", "chain_break", "divergence",
                                    note="chain head differs from the pinned value"))
    return VerificationReport("stream", tuple(findings), envelope_count=len(envs), chain_head=head,
                              sequence_range=seq_range, release=policy.release, limitations=tuple(limitations))

#!/usr/bin/env python3
"""
Anchoring guard for the AXES reference verifier (WO18 A4, D-020, D-023).

Evaluates the `anchoring` block of a record and returns verification results in the
four-state vocabulary of draft-krausz-verification-state-03:

  verification_state          verified | contradicted | indeterminate | not_evaluated
  verification_reason_code    divergence | absence | instrument_failure | None
  verification_subject_type   artifact | operator | network | verifier
  verification_condition_code closed list below

(AXES key names per docs/20; the draft's own names are state, state_reason, subject.)

This guard checks what can be checked from the record alone plus a pre-fetched observation
(`observed_ledger_event` in a vector). It does not replay proofs; tools/anchoring on the
default branch does that. No network.

Release scoping. gt-v2.0 records carry the legacy unstructured block
(`anchoring_method: "write_once_store (SIMULATED)"`, `anchor_receipt_id`, `chain_head_hash`).
Under gt-v2.0 that block is reported `indeterminate` / `absence` /
`legacy_unstructured_anchor`: the release declared it simulated (D-015 reading rule), so it
proves no existence bound, and it is not re-judged under rules published later. The same
block presented as gt-v2.1 is `contradicted`: status in the method value is retired.
"""

from __future__ import annotations

LEGACY_KEYS = {"anchor_receipt_id", "chain_head_hash", "anchor_store_ref", "anchoring_latency_ms"}
SEVERITY = {"contradicted": 3, "indeterminate": 2, "not_evaluated": 1, "verified": 0}

CONDITIONS = {
    "legacy_unstructured_anchor",
    "anchor_status_in_method",
    "anchor_simulated_claims_external",
    "basis_not_demonstrated",
    "anchor_proof_absent",
    "anchor_noncanonical_contract",
    "anchor_not_a_commitment",
    "anchor_commitment_mismatch",
    "anchor_method_unverifiable",
}


def _r(state, reason=None, condition=None, subject="artifact", anchor_id=None):
    return {"verification_state": state, "verification_reason_code": reason,
            "verification_condition_code": condition, "verification_subject_type": subject,
            "anchor_id": anchor_id}


def _contract_of(service_ref: str) -> str | None:
    """`eip155:<chain>:<address>` -> lower-case address; anything else -> None."""
    parts = (service_ref or "").split(":")
    if len(parts) == 3 and parts[0] == "eip155" and parts[2].startswith("0x"):
        return parts[2].lower()
    return None


def _chain_of(service_ref: str) -> str | None:
    parts = (service_ref or "").split(":")
    return ":".join(parts[:2]) if len(parts) == 3 else None


def evaluate(record: dict, release: str, observed_ledger_event: dict | None = None) -> list[dict]:
    """Return one or more results; the decisive one is `decisive(results)`."""
    block = record.get("anchoring")
    if not isinstance(block, dict):
        return []
    claims_external = (record.get("evidence_quality") or {}).get("corroboration_state") == "externally_anchored"
    method0 = block.get("anchoring_method", "")
    legacy = bool(LEGACY_KEYS & set(block)) or "anchors" not in block

    if legacy:
        if release == "gt-v2.0":
            return [_r("indeterminate", "absence", "legacy_unstructured_anchor", "artifact",
                       block.get("anchor_receipt_id"))]
        if isinstance(method0, str) and "(" in method0:
            return [_r("contradicted", "divergence", "anchor_status_in_method", "artifact",
                       block.get("anchor_receipt_id"))]
        return [_r("contradicted", "divergence", "legacy_unstructured_anchor", "artifact",
                   block.get("anchor_receipt_id"))]

    results = []
    any_demonstrated = False
    for a in block.get("anchors") or []:
        aid = a.get("anchor_id")
        method = a.get("anchoring_method", "")
        if "(" in method or " " in method:
            results.append(_r("contradicted", "divergence", "anchor_status_in_method", "artifact", aid))
            continue
        if a.get("basis_status") != "demonstrated":
            results.append(_r("indeterminate", "absence", "basis_not_demonstrated", "operator", aid))
            continue
        any_demonstrated = True
        if not a.get("anchor_proof_ref"):
            results.append(_r("indeterminate", "absence", "anchor_proof_absent", "operator", aid))
            continue
        if method == "distributed_ledger":
            results.append(_ledger(a, block, observed_ledger_event))
            continue
        results.append(_r("not_evaluated", "instrument_failure", "anchor_method_unverifiable", "verifier", aid))

    if claims_external and not any_demonstrated:
        results.append(_r("contradicted", "divergence", "anchor_simulated_claims_external", "artifact", None))
    return results


def _ledger(a: dict, block: dict, ev: dict | None) -> dict:
    """Canonical contract only (WO18 A4.4). A plain transfer is never an anchor."""
    aid = a.get("anchor_id")
    if ev is None:
        return _r("not_evaluated", "instrument_failure", "anchor_method_unverifiable", "verifier", aid)
    if ev.get("event_type") != "commitment_event":
        return _r("contradicted", "divergence", "anchor_not_a_commitment", "artifact", aid)
    if _chain_of(a.get("anchor_service_id")) != ev.get("network_id") or \
            _contract_of(a.get("anchor_service_id")) != str(ev.get("emitting_contract_id", "")).lower():
        return _r("contradicted", "divergence", "anchor_noncanonical_contract", "artifact", aid)
    if ev.get("committed_hash") != a.get("anchor_commitment_hash") or \
            a.get("anchor_commitment_hash") != block.get("anchored_subject_hash"):
        return _r("contradicted", "divergence", "anchor_commitment_mismatch", "artifact", aid)
    return _r("verified", None, None, "artifact", aid)


def decisive(results: list[dict]) -> dict | None:
    if not results:
        return None
    return max(results, key=lambda r: SEVERITY[r["verification_state"]])

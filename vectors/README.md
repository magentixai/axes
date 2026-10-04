# AXES conformance vectors (Golden Trace v2)

Byte-level canonicalisation and hashing fixtures in the [canoncheck layout](https://github.com/MarkovianProtocol/canoncheck/tree/main/vectors-axes).

**Layout:**
- One file per vector under this directory; the bytes on disk are the fixture.
- Envelopes are in **hash-input form** (`integrity.envelope_hash` and `integrity.signature` removed).
- Expected values live in [`expected.json`](expected.json), keyed by filename.
- `expect: "pass"` is implied when absent.
- Rule-level rejects carry `reject_code` plus pinned canonical bytes.
- `{"reject": true}` is reserved for canonicalisation-layer malformed input (duplicate keys).

**Regeneration (never hand-edit hashes):**

```bash
pip install -r requirements-dev.txt
python examples/golden-trace/generate_golden_trace.py
python tools/generate_conformance_vectors.py
```

All `canonical_utf8` and `sha256` values in `expected.json` are emitted by `tools/axes_canonical.py` (RFC 8785 JCS + SHA-256).

**Custody twins** (axes#6, axes#10): `custody_deployer_captured_reject.json` and `custody_accept_independent_external.json` exercise the three-leg independence predicate (deployer-as-capturer case). Rule-layer verdicts (`reject_code`) are declared here.

**Reference verifier (shipped):** [`tools/axes_verify.py`](../tools/axes_verify.py) runs offline against this directory and both Golden Trace corpora. Absence of an `expect` key is an implied pass. A vector marked `"expect":"reject"` must reject **with the stated `reject_code`**, not merely fail. Typed outcomes, never a bare boolean.

```bash
pip install -r requirements-dev.txt
python tools/axes_verify.py
python tools/test_locale_comparator_guard.py
```

**A property that is only named is not pinned.** The original 11 vectors are ASCII-keyed, so agreement on them does not prove UTF-16 member-sort or no-normalisation. Four additional vectors pin those RFC 8785 properties (credit: Ryan Cason / orionsys; a locale-aware comparator left 148 tests passing while the bytes diverged). Substituting a locale-like comparator **must** fail `test_locale_comparator_guard.py`.

**Standing rule (WO16 Task 16 / TLC-008, machine-enforced by WO17):** a check ships with at least one passing and one failing committed vector, or it ships marked as unexercised. The machine-readable account is [`predicates.json`](predicates.json). `python tools/axes_verify.py` exits **2** (suite broken) if a predicate is unaccounted for, a fixture is missing, or a declared outcome was never observed; exit **1** is reserved for a vector that behaved wrongly. Self-test: `python tools/test_coverage_rule_guard.py`.

| Predicate | Pass (committed) | Fail (committed) |
|---|---|---|
| canonical bytes / digest | every pinned `canonical_utf8` | locale-like comparator vs `axes_jcs_collation_ae.json` |
| duplicate-key canonicalisation reject | any well-formed vector | `axes_reject_duplicate_key.json` |
| custody independence | `custody_accept_independent_external.json` | `custody_deployer_captured_reject.json` |
| unparseable identity | `axes_identity_unparseable_hex.json` (`verification_unavailable`, not a reject) | (rejecting this fixture would be the false negative; the fail is a verifier that returns `custody_independence_reject` here) |
| JCS surrogate / NFC-NFD / digest encoding | the four `axes_jcs_*` vectors | locale guard covers sort; NFC/NFD are two members that must both survive |
| chain link / sequence / envelope_hash | both `examples/*/out/envelopes.jsonl` corpora | **unexercised as a committed negative** (a broken chain would mutate the corpus of record; do not ship one) |

## Anchoring vectors (WO18 A4)

[`anchoring/`](anchoring/) holds anchoring blocks with the decisive result each must produce, in the four-state vocabulary of draft-krausz-verification-state-03 (D-023), under AXES key names (docs/20): `verification_state`, `verification_reason_code`, `verification_subject_type`, `verification_condition_code`. Expected results and **per-vector provenance** (`author_name`, `origin_note`, `authored_on`) live in [`anchoring/expected.json`](anchoring/expected.json); the verifier fails a vector without provenance. Evaluated by [`tools/axes_anchoring_guard.py`](../tools/axes_anchoring_guard.py) through `axes_verify.py`; self-test `python tools/test_anchoring_guard.py`.

| Predicate | Pass (committed) | Fail (committed) |
|---|---|---|
| gt-v2.0 anchors read under gt-v2.0 rules | `anch_legacy_gt_v2_0.json` and the six anchored envelopes in both corpora: `indeterminate` / `absence` / `legacy_unstructured_anchor` | `anch_legacy_under_gt_v2_1.json`: the same block under gt-v2.1 is `contradicted` / `anchor_status_in_method` |
| `externally_anchored` is earned (D-020) | `anch_simulated_honest.json` | `anch_simulated_claims_external.json` |
| proof absent is a producer defect (A4.2) | `anch_canonical_contract.json` | `anch_proof_absent.json` |
| canonical contract only (A4.4) | `anch_canonical_contract.json` | `anch_lookalike_contract.json`, `anch_plain_transfer.json`, `anch_commitment_mismatch.json` |

Why the corpus reads as `legacy_unstructured_anchor` and not as a failure: gt-v2.0 declared its anchors simulated (`write_once_store (SIMULATED)`), and the D-015 reading rule already said a simulated anchor proves no existence bound. The verifier reports exactly that (`indeterminate`, nothing to verify) and does not re-judge a published release under rules written later. Superseded is not wrong. The gt-v2.0 release statement itself now carries real external anchors, detached, on the default branch (`anchors/gt-v2.0/`).

The ledger vectors carry a pre-fetched `observed_ledger_event` so the check runs offline. Contract addresses and hashes in them are illustrative.

## Questions this corpus does not settle

A green run says nothing about readings no vector pins (stillmarcus24, x402 tsc#4). These are open, and an implementation may answer them either way today:

1. **Reorganisation depth.** How many confirmations a `distributed_ledger` or `opentimestamps` anchor needs before `anchored_at` is final.
2. **Checkpoint clock.** Which clock a transparency-log checkpoint time is read from, and so what `anchored_at` means for a `transparency_log` anchor.
3. **Identifier encoding.** Percent-encoding of identifiers containing `:` inside `anchor_record_ref`.
4. **Proof replay.** These vectors check the record and a pre-fetched observation; they do not replay RFC 3161 or OpenTimestamps proofs. The default branch's `tools/anchoring/` does, against its own two-sided fixtures and the real gt-v2.0 release-statement anchors.
5. **Signatures.** gt-v2.0 envelopes carry `SIG-STUB`; recomputability from bytes is structural only until gt-v2.1 replaces it under a declared signing profile (WO18 A4.5).

Liftable, AXES-independent copy of the four JCS property vectors: [`portable/jcs-properties/`](../portable/jcs-properties/) on the default branch (added by WO17).

**Crypto Amount path:** `axes_adv_usdc_amount.json` uses `asset: caip19:eip155:8453/erc20:0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` with `decimals: 6` alongside the Fin corpus's `iso4217:EUR` (`decimals: 2`).

Cross-links: P1-1 [#5](https://github.com/magentixai/axes/issues/5), conformance vectors [#6](https://github.com/magentixai/axes/issues/6), EB-004 [#4](https://github.com/magentixai/axes/issues/4).

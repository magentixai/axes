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

**Standing rule (WO16 Task 16):** a check ships with at least one passing and one failing committed vector, or it ships marked as unexercised. TLC-008.

| Predicate | Pass (committed) | Fail (committed) |
|---|---|---|
| canonical bytes / digest | every pinned `canonical_utf8` | locale-like comparator vs `axes_jcs_collation_ae.json` |
| duplicate-key canonicalisation reject | any well-formed vector | `axes_reject_duplicate_key.json` |
| custody independence | `custody_accept_independent_external.json` | `custody_deployer_captured_reject.json` |
| unparseable identity | `axes_identity_unparseable_hex.json` (`verification_unavailable`, not a reject) | (rejecting this fixture would be the false negative; the fail is a verifier that returns `custody_independence_reject` here) |
| JCS surrogate / NFC-NFD / digest encoding | the four `axes_jcs_*` vectors | locale guard covers sort; NFC/NFD are two members that must both survive |
| chain link / sequence / envelope_hash | both `examples/*/out/envelopes.jsonl` corpora | **unexercised as a committed negative** (a broken chain would mutate the corpus of record; do not ship one) |

**Crypto Amount path:** `axes_adv_usdc_amount.json` uses `asset: caip19:eip155:8453/erc20:0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` with `decimals: 6` alongside the Fin corpus's `iso4217:EUR` (`decimals: 2`).

Cross-links: P1-1 [#5](https://github.com/magentixai/axes/issues/5), conformance vectors [#6](https://github.com/magentixai/axes/issues/6), EB-004 [#4](https://github.com/magentixai/axes/issues/4).

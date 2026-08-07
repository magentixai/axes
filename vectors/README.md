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

**Custody twins** (axes#6, axes#10): `custody_deployer_captured_reject.json` and `custody_accept_independent_external.json` exercise the three-leg independence predicate (deployer-as-capturer case). Rule-layer verdicts (`reject_code`) are declared here and proven by the two-sided run against giskard09's custody-ref-v1; an in-repo reference verifier remains Planned (P4).

**Crypto Amount path:** `axes_adv_usdc_amount.json` uses `asset: caip19:eip155:8453/erc20:0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` with `decimals: 6` alongside the Fin corpus's `iso4217:EUR` (`decimals: 2`).

Cross-links: P1-1 [#5](https://github.com/magentixai/axes/issues/5), conformance vectors [#6](https://github.com/magentixai/axes/issues/6), EB-004 [#4](https://github.com/magentixai/axes/issues/4).

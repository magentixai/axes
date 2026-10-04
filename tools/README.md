# Tools

| Path | Purpose |
|---|---|
| [`axes_canonical.py`](axes_canonical.py) | RFC 8785 JCS canonical bytes, SHA-256 digest, Amount helpers, zero-float guard |
| [`generate_conformance_vectors.py`](generate_conformance_vectors.py) | Emit Golden Trace and custody fixtures into [`vectors/`](../vectors/) |
| [`generate_jcs_property_vectors.py`](generate_jcs_property_vectors.py) | Add RFC 8785 property vectors without rewriting existing pins |
| [`axes_verify.py`](axes_verify.py) | Offline reference verifier (canonical bytes, digests, chain, expected.json including reject codes; enforces `vectors/predicates.json`, TLC-008) |
| [`test_locale_comparator_guard.py`](test_locale_comparator_guard.py) | Negative check: a locale-like comparator must not match pinned JCS bytes |
| [`test_coverage_rule_guard.py`](test_coverage_rule_guard.py) | Negative check: a broken predicates manifest must yield exit 2 |
| [`axes_anchoring_guard.py`](axes_anchoring_guard.py) | Anchoring block evaluation in the four-state vocabulary (WO18 A4, D-020, D-023); release-scoped, so gt-v2.0 blocks read as `legacy_unstructured_anchor` |
| [`test_anchoring_guard.py`](test_anchoring_guard.py) | Negative check: a guard that reads every anchor as verified must fail the suite (exit 1) |

Liftable JCS property subset (no AXES corpus dependency): [`portable/jcs-properties/`](../portable/jcs-properties/) on the default branch (`main`). Full predicate suite stays on this branch.

Install development dependencies from the repository root:

```bash
pip install -r requirements-dev.txt
```

Then regenerate the Golden Trace and vectors:

```bash
python examples/golden-trace/generate_golden_trace.py
python tools/generate_conformance_vectors.py
python tools/generate_jcs_property_vectors.py
```

Regenerating Golden Trace / `generate_conformance_vectors.py` rewrites the original 11 pins and must not be run as a silent corpus edit. `generate_jcs_property_vectors.py` only adds property vectors.

**Never hand-edit** `canonical_utf8` or `sha256` in `vectors/expected.json`. All pinned bytes are emitted by the canonicaliser.

```bash
python tools/axes_verify.py
python tools/test_locale_comparator_guard.py
```

Custody rule-layer verdicts (`reject_code`) are declared on the vectors and evaluated by `axes_verify.py`.

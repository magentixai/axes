# Tools

| Path | Purpose |
|---|---|
| [`axes_canonical.py`](axes_canonical.py) | RFC 8785 JCS canonical bytes, SHA-256 digest, Amount helpers, zero-float guard |
| [`generate_conformance_vectors.py`](generate_conformance_vectors.py) | Emit Golden Trace and custody fixtures into [`vectors/`](../vectors/) |
| [`generate_jcs_property_vectors.py`](generate_jcs_property_vectors.py) | Add RFC 8785 property vectors without rewriting existing pins |
| [`axes_verify.py`](axes_verify.py) | Offline reference verifier (canonical bytes, digests, chain, expected.json including reject codes) |
| [`test_locale_comparator_guard.py`](test_locale_comparator_guard.py) | Negative check: a locale-like comparator must not match pinned JCS bytes |

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

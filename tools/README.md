# Tools

| Path | Purpose |
|---|---|
| [`axes_canonical.py`](axes_canonical.py) | RFC 8785 JCS canonical bytes, SHA-256 digest, Amount helpers, zero-float guard |
| [`generate_conformance_vectors.py`](generate_conformance_vectors.py) | Emit [`vectors/`](../vectors/) fixtures and `expected.json` from Golden Trace v2 |
| `validator/` | Planned (Roadmap P4) - open reference validator; conformance is defined by spec + validator + test vectors, never by any vendor's ingestion |

Install development dependencies from the repository root:

```bash
pip install -r requirements-dev.txt
```

Then regenerate the Golden Trace and vectors:

```bash
python examples/golden-trace/generate_golden_trace.py
python tools/generate_conformance_vectors.py
```

**Never hand-edit** `canonical_utf8` or `sha256` in `vectors/expected.json`. All pinned bytes are emitted by the canonicaliser.

Custody rule-layer verdicts (`reject_code`) are declared on the vectors and validated cross-suite (custody-ref-v1 two-sided run). The in-repo `validator/` that would evaluate those rules remains Planned (Roadmap P4).

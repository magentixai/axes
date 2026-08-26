# Tools

| Tool | Status |
|---|---|
| `validator/` | Offline reference verifier (`tools/axes_verify.py`) lives on `golden-trace-v2` with the corpus of record until the announced merge. This default-branch tree does not copy those pinned vectors (they still contain `anchoring_latency_ms`). See [`VERIFY.md`](../VERIFY.md) |
| `test-vectors/` | Byte-level vectors for this lineage are not the published gt-v2.0 pins. Reproduce published figures from tag `corpus/2026-08-08-gt-v2` |
| Coverage rule (TLC-008) | Machine-enforced on [`golden-trace-v2`](https://github.com/magentixai/axes/tree/golden-trace-v2): `vectors/predicates.json` + `tools/axes_verify.py` (exit 2 = suite broken). Self-test: `tools/test_coverage_rule_guard.py` |
| Portable JCS properties | Liftable package on this branch: [`portable/jcs-properties/`](../portable/jcs-properties/). Stdlib verifier; independent cross-check in `CROSSCHECK.md`. Full AXES vector set remains on `golden-trace-v2` |

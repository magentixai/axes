# axes-sdk (Python)

Offline verification and deterministic evaluation of AXES evidence, for developers who want to check AXES records without cloning the AXES repository or learning its layout.

Version 0.1.1 (alpha) implements the mechanisms specified in [draft-sansone-axes-evidence-envelope-00](../../ietf/draft-sansone-axes-evidence-envelope.md):

| Capability | API | CLI |
|---|---|---|
| Strict JSON ingestion (duplicate members, NaN, lone surrogates and oversize input refused) | `parse_json`, `load_subject` | |
| RFC 8785 bytes and envelope digests, with the AXES number domain enforced | `canonicalize`, `envelope_preimage`, `hash_envelope` | `axes-sdk hash` |
| Stream verification: every envelope hash, every link, sequence, pinned chain head | `verify_stream` | `axes-sdk verify-stream` |
| Bundle verification: every file digest, the manifest digest, the stream | `verify_bundle` | `axes-sdk verify-bundle` |
| Deterministic requirement-profile evaluation, with optional pinning of the whole profile closure | `evaluate`, `bundled_profiles`, `load_profile_set` | `axes-sdk evaluate` |

## Install

```bash
pip install ./sdk/python
```

The only runtime dependency is [`jcs`](https://pypi.org/project/jcs/), the RFC 8785 library the AXES reference tooling uses. Python 3.9 or later.

## Use

```python
from axes_sdk import load_subject, verify_stream, verify_bundle, bundled_profiles, evaluate, EvaluationContext

subject = load_subject("examples/golden-trace/out/envelopes.jsonl")
report = verify_stream(subject, expected_chain_head="cbd1a73e910bd51f01cf5dd097c9a68869b733550d96db891d0f288bd4db59f1")
print(report.overall_state.value, report.chain_head)
for finding in report.findings:
    print(finding.state.value, finding.check, finding.condition, finding.note)

bundle = verify_bundle("examples/golden-trace/out")
print(bundle.overall_state.value, bundle.bundle_manifest_hash)

result = evaluate(subject, "axes:gt_fin_internal_audit@1", bundled_profiles(),
                  EvaluationContext(release="gt-v2.1", evaluated_at="2026-10-31T00:00:00.000Z"))
print(result.overall_verification_state.value, result.result_core_hash)
```

```bash
axes-sdk verify-bundle examples/golden-trace/out --json
axes-sdk evaluate examples/golden-trace/out/envelopes.jsonl --profile axes:gt_fin_regulator@1
```

## Reading results

Every check gives one of four states: `verified`, `contradicted`, `indeterminate` or `not_evaluated`. They are never collapsed into a boolean. `report.overall_state` is `contradicted` if any check is, otherwise `indeterminate` if any check is indeterminate or not evaluated, otherwise `verified`. `report.all_requested_checks_verified` is true only when every check verified.

| CLI exit code | Meaning |
|---|---|
| 0 | every requested check verified |
| 1 | at least one check contradicted |
| 2 | no contradiction, but a check was indeterminate or not evaluated |
| 3 | the command could not run (bad arguments, unreadable or non-strict input, a limit, an unsupported option) |

## What it does not do

- It does not verify envelope signatures. The signature profile is an open issue in the draft, and the published corpus signatures are stubs.
- It does not verify external anchors. Use `tools/anchoring/verify_anchor.py` in the repository; an anchoring module is planned for 0.2.
- It does not show that capture was complete, that an authority was valid, or that a recorded event happened. A verified report shows that the bytes are the ones committed to.
- It never uses the network, reads a clock during evaluation, or writes files other than an output you name.
- It is not an emitter, and it does not implement redaction (not yet specified).

## How it relates to the reference implementation

The SDK does not reimplement the AXES rules. `axes_sdk/_ref/` holds the repository's reference modules (`tools/axes_canonical.py`, `tools/axes_evaluate.py`, `tools/axes_anchoring_guard.py`), copied by `sync_reference.py` with only their imports rewritten, and `axes_sdk/data/` holds the published profiles and key aliases. Continuous integration fails if a copy drifts. The SDK adds strict ingestion, limits, path containment, typed results, a pure evaluation entry point and a CLI. Its tests require it to reproduce the reference results on the corpus of record, the published evaluation records and the profile vectors.

Because the SDK packages the authors' reference code, agreement between the two is not independent evidence. Independent reproductions are listed in the draft's Implementation Status section.

## Security

Evidence is untrusted input. The SDK refuses duplicate JSON members, non-finite numbers, lone surrogates and numbers RFC 8785 would round; bounds input size, nesting depth, record and file counts (`Limits`); resolves the manifest and every path it lists inside the bundle root and refuses absolute paths, `..`, backslashes and links that lead outside; checks the envelope stream from the same bytes whose digest it compared with the manifest; verifies and evaluates a fresh parse of a subject's recorded bytes, so changing `Subject.envelopes` cannot change a result; and keeps evidence values out of exception messages, which may name a member path or line. Report vulnerabilities as described in the repository's SECURITY.md.

## Develop

```bash
python sdk/python/sync_reference.py          # refresh the copies after changing the reference tools
python sdk/python/sync_reference.py --check  # what CI runs
pip install -e "sdk/python[test]"
pytest sdk/python/tests
```

Licensed under Apache-2.0, as the AXES code is.

# Anchoring tools (WO18 A5)

| File | Purpose |
|---|---|
| `produce.py` | `stamp` a subject with OpenTimestamps and an RFC 3161 time-stamp authority; `upgrade` pending OpenTimestamps proofs to Bitcoin attestations. Needs network access. |
| `verify_anchor.py` | Verify every anchor in an `anchoring.json` block offline. Four-state results with closed conditions. |
| `test_anchoring.py` | Two-sided self-test on synthetic fixtures (local test TSA, regtest-difficulty header). No network. |
| `anchor_common.py` | Shared helpers, profile identifiers. |

Dependencies (kept out of the core verifier): `pip install -r tools/anchoring/requirements.txt` (OpenTimestamps library, `jcs`) and the `openssl` binary for RFC 3161. If either is missing, verification returns `not_evaluated` / `instrument_failure` for the affected method.

Procedures: [`docs/anchoring-profiles.md`](../../docs/anchoring-profiles.md).

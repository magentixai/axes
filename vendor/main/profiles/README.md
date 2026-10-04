# Requirement profiles

Reference requirement profiles (WO19, docs/07). Format: [`schema/requirement-profile.schema.json`](../schema/requirement-profile.schema.json). Each profile is immutable at `id@version`; its digest is the SHA-256 of its RFC 8785 bytes, computed by the evaluator.

| Profile | Role | Subject | gt-v2.0 result |
|---|---|---|---|
| `axes:gt_fin_internal_audit@1` | `auditor` | `bundle` | `verified` |
| `axes:gt_fin_regulator@1` (extends the above) | `regulator` | `bundle` | `indeterminate`: `basis_not_demonstrated` (SIG-STUB), `anchor_insufficient` (simulated anchor) |
| `axes:x402_payee_attribution@1` | `origin`, `liability_holder`, `tax_authority` | `envelope`, `stream_window` | not applicable to gt-v2.0; evaluated on the WO20 x402 example |

The evaluator, vectors and published evaluations live on `golden-trace-v2` (`tools/axes_evaluate.py`, `vectors/profiles/`, `evaluations/`), which vendors this directory byte for byte; CI fails if the copies differ.

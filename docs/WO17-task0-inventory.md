# WO17 Task 0 inventory (before any WO17 code change)

Branch: `golden-trace-v2` @ `7b01dce` (worktree `C:\Projects\axes-gt-v2`).
Date: 26 Aug 2026.

## Already present

### Predicates evaluated by `tools/axes_verify.py`
| Predicate (check id) | Pass | Fail / other | Enforced? |
|---|---|---|---|
| `canonical_bytes` | every pinned `canonical_utf8` | locale-like comparator via `locale_comparator_guard` | soft: prints coverage row, exit 0 even if unexercised |
| `digest` | every pinned sha256 | no committed fail (inject-only) | soft |
| `canonicalisation_reject` | implied by well-formed vectors | `axes_reject_duplicate_key.json` | soft |
| `custody_independence` | `custody_accept_independent_external.json` | `custody_deployer_captured_reject.json` (`custody_independence_reject`) | soft |
| unparseable identity | `axes_identity_unparseable_hex.json` returns `verification_unavailable` (currently logged as outcome `ok` + detail) | reject would be the false negative | soft; multi-outcome not first-class |
| `locale_comparator_guard` | locale-like diverges from pin | inert would fail the guard | soft |
| `chain_link` / `sequence_closure` / `envelope_hash` | both Golden Trace corpora | **unexercised** as committed negative (would mutate corpus of record) | soft; documented in README |

Coverage rule is **documented** in `vectors/README.md` (WO16 Task 16 / TLC-008) and lightly summarised by `predicate_coverage()`; it is **not** machine-enforced (no `predicates.json`, no exit 2).

### Four RFC 8785 property vectors (`axes_jcs_*`)
| Vector | Property | Pins divergence? |
|---|---|---|
| `axes_jcs_surrogate_pair_key.json` | UTF-16 member sort (§3.2.3) | Yes: code-point order `z`, `U+FF21`, `U+1D11E`; UTF-16 order `z`, `U+1D11E`, `U+FF21` |
| `axes_jcs_nfc_nfd_pair.json` | No normalisation (§3.1) | Yes: NFC U+00E9 and NFD `e`+U+0301 as distinct members |
| `axes_jcs_collation_ae.json` | Code-unit vs locale collation | Yes; `test_locale_comparator_guard.py` is the executable negative. Credit: Ryan Cason / orionsys |
| `axes_jcs_digest_encoding.json` | Distinct digest string forms in the object | Pins bare hex vs `sha256:`-prefixed as different members; digest-over-UTF-8-bytes is exercised by every pin via SHA-256 of JCS bytes |

### Tools
- `tools/axes_canonical.py` (depends on PyPI `jcs`)
- `tools/generate_jcs_property_vectors.py` (additive only; does not rewrite original 11 pins)
- `tools/axes_verify.py`, `tools/test_locale_comparator_guard.py`

### Not present (WO17 gaps)
1. `vectors/predicates.json` + exit-2 enforcement + observation of declared outcomes
2. `tools/test_coverage_rule_guard.py` proving enforcement can fail
3. Liftable `portable/jcs-properties/` (stdlib-only, no AXES corpus)
4. Independent cross-check (`CROSSCHECK.md`)
5. Pointers on `main` to the above

### What this work order must not do
- Run `generate_conformance_vectors.py` or regenerate Golden Trace corpora
- Hand-edit `canonical_utf8` / `sha256` in `expected.json`
- Ship a broken-chain negative fixture
- Merge `golden-trace-v2` into `main`

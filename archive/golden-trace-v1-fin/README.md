# Golden Trace v1 (financial) - archived working exemplar

**Archived:** 2026-08-03 as part of Golden Trace v2 regeneration (P1-1 / D-006).

This directory preserves the GT-JCS-0 corpus byte-for-byte for provenance. The v1 generator used Python `json.dumps(sort_keys=True, separators=(",", ":"))` as a stand-in canonical form and carried JSON floats in monetary fields.

**Do not treat this corpus as normative.** Regenerate the current exemplar from [`examples/golden-trace/`](../examples/golden-trace/) (RFC 8785 JCS, integer Amount fields, no floats in hash scope).

Contents:
- `out/` - committed v1 bundle (76 envelopes, manifest, samples, reports, artefacts)
- `generate_golden_trace_v1.py` - frozen v1 generator script

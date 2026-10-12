# Outstanding AXES changes (x402 / AEP coherence)

**Status:** open work for the main AXES standard (`magentixai/axes`).  
**Date:** 2026-08-14.  
**Why this note exists:** the x402 discovery signed-manifest kit (`magentixai/x402-signed-manifest-ref`) advanced ahead of normative AXES schema text. These items must land in AXES (or be explicitly deferred in the decision register) so the three surfaces do not drift. Tracking table: [`AXES_AEP_x402_Coherence_Tracker.md`](AXES_AEP_x402_Coherence_Tracker.md).

British spelling. No em dashes. Magentix AI.

---

## Must land in AXES (normative or catalogue)

| ID | Item | Source | Suggested home | Blocked by / notes |
|---|---|---|---|---|
| O-1 | **SE signing profile:** sign RFC 8785 canonical bytes directly; SHA-256 as content digest / chain hash only; declare in-band profile id (parallel to x402 `v: "x402sig1"`). | Coherence row 2 / 4; [axes#11](https://github.com/magentixai/axes/issues/11); AEP #28 | Module 14 Integrity; CONFORMANCE; replace `SIG-STUB` in Golden Trace when ready | Golden Trace stubs today - do not invent a silent SHA-256-then-Ed25519 under `alg: Ed25519`. |
| O-2 | **`settlement_role` enum** on settle-time payee attribution: `origin` \| `facilitator` \| `proxy_gateway` (shared with x402 `host.role`). | Design note [`docs/15-AXES_Payee_Settlement_Role_Design_Note.md`](../15-AXES_Payee_Settlement_Role_Design_Note.md); coherence row 1 | Field catalogue + controlled vocabularies; settle-time record schema | Open: multi-hop list shape; split-settlement / revenue-share. |
| O-3 | **Identity provenance doctrine:** payer/payee identity NEVER from `tx.from` (relayer / EIP-3009). Attestation identity + declared payee attribution. | Design note §3; coherence row 3; tsc#4 brief | Doctrine (`docs/01`); settle-time + authorisation modules | Cross-check discovery `payTo` is declaration-authorship only - do not collapse into chain identity. |
| O-5 | **Scrub remaining unit-in-key identifiers** (`clock_skew_ms`, `declared_heartbeat_interval_s`, `approval_response_latency_ms` / BLD-011) under D-017. `anchoring_latency` already renamed on `main`. | D-017; bar Rule 3 | Field catalogue + Golden Trace v2 regen | Do not leave `anchoring_latency_ms` on `golden-trace-v2` after merge. |

## Docs already drafted (commit with this note; not yet normative)

| Artefact | Role |
|---|---|
| [`AXES_AEP_x402_Coherence_Tracker.md`](AXES_AEP_x402_Coherence_Tracker.md) | Living AXES ↔ AEP ↔ x402 alignment table (change gate). |
| [`../15-AXES_Payee_Settlement_Role_Design_Note.md`](../15-AXES_Payee_Settlement_Role_Design_Note.md) | Design note for O-2 / O-3. |
| [`Discovery_Signed_Manifest_Reference.md`](Discovery_Signed_Manifest_Reference.md) | Informative mirror of the public kit shape (`v: x402sig1`). |

## Explicitly not AXES corpus (keep out of normative tree unless promoted)

- Cursor work orders under `docs/x402/` and `docs/13-*` / `docs/14-*` (operator instructions, not standard text).
- AGORA lab proposal PDF.
- Live VPS Imunify / Apache ops (lives in the x402 kit `examples/ops/`).

## Exit criteria

- [ ] O-1 decided and reflected in Module 14 / signing profile (or decision-register deferral with reason).
- [ ] O-2 enum in controlled vocabularies + catalogue; x402 kit still matches.
- [ ] O-3 doctrine sentence published; non-conformant "identity from tx.from" called out.
- [ ] O-4 mentioned in conformance or reportability so sweeps stay honest.
- [ ] O-5 remaining unit-in-key scrub (and `golden-trace-v2` rename+regen) closed under D-017.

## Related

- Public kit: https://github.com/magentixai/x402-signed-manifest-ref (mechanism 1.1.1)
- SE signing issue: https://github.com/magentixai/axes/issues/11
- Adjacent-standards watch: [`../../registers/adjacent-standards-watch.md`](../../registers/adjacent-standards-watch.md)

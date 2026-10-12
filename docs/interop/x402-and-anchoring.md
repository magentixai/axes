# x402 composition and external anchoring (informative)

> **Status: informative - not normative.** Doctrine: AXES is the evidence lane ([docs/01](../01-doctrine-and-non-negotiables.md) §5). It does not settle payments, adjudicate correctness, slash bonds, or implement runtime plugin ABCs. Cross-refs: D-015, TRK-001, GAP-TECH-001, CRE-D01, P1-1, P1-4.

## x402 and AXES (layering)

Agent-to-agent micropayments and shared evidence records compose; they must not collapse into one protocol.

| Concern | Where it belongs | Notes |
|---|---|---|
| Pay / settle obligation | **x402** (base protocol + facilitators) | Settlement success is not proof the paid claim was true |
| Signed binding of action to settlement | **x402 extension** - action-receipt as a JWS profile of offer-receipt ([x402#2906](https://github.com/x402-foundation/x402/issues/2906)) | Frozen content-addressed `actionRef` (JCS + SHA-256 family); offline-verifiable; two-sided vectors |
| Evidence capture of delegated execution (authority, commit, topology, quality, reports) | **AXES** SE envelopes | Optional richer profile around a paid action; severable subset for an x402 evidence record |
| Adjudication (was the deliverable wrong?) | Downstream of both | Bonded claims, merchant refunds, etc. - consumers of the record |
| Enforcement (slash, refund, reputation) | Scheme- and chain-specific | Must not redefine settlement as failed when the claim later resolves false |

**Charter posture (evidence before dispute):** standardise the evidence record first; treat adjudication and enforcement as later phases. Several open x402 threads converge on that sequencing (notably [x402#2887](https://github.com/x402-foundation/x402/issues/2887)). AXES is offered as reference material for the capture phase, not as a competing payment standard.

**Acknowledgment ladder:** a JWS action-receipt is a natural mid-ladder rung (integrity + attribution offline). Independence and independently verifiable **existence-in-time** are higher rungs - never inferred from a lower one (GT-003: rungs accrete over time). Refunds and reversals are **new** receipts with mandatory cross-digest to the original - append-only, never mutation of the settled record.

## External existence bound (what anchoring must mean)

A local hash chain proves order and tamper-evidence **inside** the emitter's corpus. It does **not** prove the bytes existed unmodified at a wall-clock time independent of whoever holds the store. That second property is an **independently verifiable existence bound** (timestamp authority, transparency log, permissionless chain registry, WORM with third-party verify path, OpenTimestamps, etc.). Mechanism-agnostic criteria; backends are profiles.

| Property | Local envelope chain | External existence bound |
|---|---|---|
| Integrity after capture | Yes (if hash scope is honest) | Yes, plus independence from emitter custody |
| Ordering | Yes | Not its job |
| "Existed by time T without trusting the issuer" | No | Yes - only if a third party can verify the receipt offline (or against a public log) without the emitter's runtime |

## Golden Trace anchors - honest reading

### gt-v2.1 (current corpus of record)

[`envelope_anchor.json`](../../examples/golden-trace/out/samples/envelope_anchor.json) carries a Module 14 block:

```json
"anchoring": {
  "anchored_subject_type": "chain_head",
  "anchored_subject_hash": "<real local chain head>",
  "anchored_subject_hash_algorithm": "SHA-256",
  "anchors": [{
    "anchor_id": "anch:001",
    "anchoring_method": "write_once_store",
    "basis_status": "simulated",
    "anchor_commitment_hash": "<same chain head>",
    "anchor_commitment_hash_algorithm": "SHA-256",
    "anchor_requested_at": "2026-06-09T09:05:00.000Z",
    "anchored_at": "2026-06-09T09:05:00.250Z",
    "anchor_service_id": "anchorstore:trustline-demo/eu",
    "anchor_record_ref": "object:trustline-demo/eu/001",
    "anchor_operator_id": "org:trustline-demo"
  }]
}
"evidence_quality": {"corroboration_state": "internally_corroborated", ...}
```

| Element | Status |
|---|---|
| `anchored_subject_hash` | **Real** - SHA-256 of the local chain head at that moment |
| Envelope hash chain / sequence | **Real** and regenerable |
| Write to an external store | **Simulated**, and stated in `basis_status`, which a verifier reads |
| `externally_anchored` | **Not asserted** on any envelope (D-020); the verifier reports these anchors `indeterminate` / `basis_not_demonstrated` |
| Envelope signatures | **Stubbed**, stated in `envelope_signature_basis_status` |
| The release that publishes the corpus | **Anchored for real**: the gt-v2.1 release statement (RFC 8785 JCS, committing to both chain heads and both bundle digests) carries RFC 3161 and OpenTimestamps anchors that verify offline with `tools/anchoring/` ([RELEASES.md](../../RELEASES.md), [VERIFY.md](../../VERIFY.md)) |

The trace is synthetic (fictional Caldera Robotics, 2026-06-09 timeline), so its in-trace anchors cannot be anchored at fictional past instants; pretending otherwise would be a new overclaim. The existence bound is on the release: the trace's own anchors are simulated and say so in a field a verifier reads; the release that publishes the trace is anchored for real, and anyone can check it.

### gt-v2.0 and earlier (superseded)

gt-v2.0 envelopes carry:

```text
anchoring_method: "write_once_store (SIMULATED)"
corroboration_state: "externally_anchored"
```

**Reading rule (gt-v2.0 and earlier):** `corroboration_state: externally_anchored` on a SIMULATED method must **not** be treated as a closed existence bound (D-015). Under gt-v2.0 rules the verifier reads these blocks as `legacy_unstructured_anchor`; under current rules the same bytes are `contradicted` (`vectors/anchoring/anch_legacy_under_gt_v2_1.json`, `anch_gt_v2_0_translated.json`).

## EvidenceAnchor SPI (AGT) - interface vs AXES

[microsoft/agent-governance-toolkit PR #2244](https://github.com/microsoft/agent-governance-toolkit/pull/2244) (merged design proposal) defines **EvidenceAnchor**: a backend-agnostic **runtime plugin SPI** (Python ABC) with roughly:

- `anchor(evidence_hash, metadata) -> AnchorReceipt`
- `verify(evidence_hash, receipt) ->` typed result
- Canonical `action_ref` derivation; optional anchors on `agt-evidence.json`
- Explicit non-goal: anchoring proves non-modification **after** anchor time, not correctness at write time

**Note:** x402-foundation/x402 issue #2244 is unrelated (facilitator/discovery bug). The SPI lives in the AGT repository.

| Question | Answer |
|---|---|
| Is EvidenceAnchor an interface? | **Yes** - a Service Provider Interface for AGT (and similar) runtimes |
| Does the AXES *standard* implement that ABC? | **No** - lane drift; AXES is not a runtime |
| May an AXES emitter / connector / ARBITR implement it? | **Yes** - as implementation territory that populates SE `anchoring.*` from a real backend |
| How should AXES relate? | **Profile** portable receipt semantics (`anchoring_method`, refs, digests, verify path) so EvidenceAnchor, Rekor, SCITT, RFC 3161, OTS, and chain registries are interchangeable instances |

Closing an EvidenceAnchor integration does **not** close control re-evaluation (GAP-EXEC-021 / CRE-*). Existence bound and control-context snapshot are orthogonal.

## IETF SCITT as an existence-bound profile (not a core schema)

Agent-governance discussions (e.g. AGT discussion #276) correctly separate:

1. **Decision / evidence envelope** - canonical bytes and digest (AXES SE; JCS baseline under P1-1).
2. **Neutral existence bound** - where that digest is notarized so verification does not depend on the emitter's endpoint.

[IETF SCITT](https://datatracker.ietf.org/doc/rfc9943/) (Supply Chain Integrity, Transparency, and Trust) is a strong instance of (2): a Transparency Service registers a **signed statement** about an artifact and returns a **receipt** (inclusion / countersignature). SCITT is **not** an agent-execution evidence schema. AXES must not fork SCITT into Modules 01-16; it **profiles** SCITT receipts into `anchoring.*`.

| Rule | Implication |
|---|---|
| What to register | Digest of an SE envelope, evidence-bundle manifest, or export pack - **pointers and hashes**, not raw payloads (doctrine) |
| Pluggable anchors | SCITT is one profile beside RFC 3161, OpenTimestamps, Rekor-like logs, WORM with third-party verify, on-chain registries. Format MUST NOT hard-require a SCITT Transparency Service (same discipline as #276) |
| Ack-ladder placement | A SCITT receipt is a **higher corroboration rung** (existence / non-equivocation). It must never verify as transport, protocol, or business confirmation, nor as control re-evaluation |
| Pre- and post-execution | Optional: two registrations on the same action key (decision digest before commit; outcome digest after) - rungs accrete (GT-003) |
| What SCITT does **not** close | Control re-evaluation (CRE-*); faithful capture / independent witness (CRE-D01); policy enforcement |

**Normative work remaining:** EB-002 vocabulary; EB-003 field map (Transparency Service id, statement digest, receipt ref, inclusion proof, verify path) in Module 14 / docs/12; EB-004 Golden Trace v2 with at least one real backend.

**Concrete composition:** emit AXES envelopes → hash → SCITT Signed Statement over that digest → store receipt in `anchoring.*` → auditor verifies receipt + recomputes digest from the open bundle without Magentix AI or Microsoft runtime access.

## Related

- Programme: external anchoring maturity TRK-001; EB-* and CRE-D01 in [`registers/three-layer-evidence-and-control-reevaluation.md`](../../registers/three-layer-evidence-and-control-reevaluation.md)
- Decision D-015 in [`registers/decision-register.md`](../../registers/decision-register.md)
- Live watch table: [`registers/adjacent-standards-watch.md`](../../registers/adjacent-standards-watch.md)
- Three-layer field map: [`three-layer-evidence-coverage.md`](three-layer-evidence-coverage.md)
- Agent 365 / Purview → SE mapping (adjacent estate): [`agent365-purview-se-mapping.md`](agent365-purview-se-mapping.md)

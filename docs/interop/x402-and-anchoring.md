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

## Golden Trace v1 - simulated anchor (honest reading)

[`envelope_anchor.json`](../../examples/golden-trace/out/samples/envelope_anchor.json) carries:

```text
anchoring_method: "write_once_store (SIMULATED)"
corroboration_state: "externally_anchored"
```

| Element | Status |
|---|---|
| `chain_head_hash` | **Real** - SHA-256 of the local chain head at that moment |
| Envelope hash chain / sequence | **Real** and regenerable |
| Write to an external store | **Simulated** - demo `anchor_store_ref` only |
| Third-party existence verification | **Not possible** from the bundle alone |
| Forensic procedure step comparing "anchor store" | Explicitly simulated ([report_D](../../examples/golden-trace/out/reports/report_D_forensic.md)) |
| Envelope signatures | **Stubbed** (`SIG-STUB`) - separate hole beside anchoring |

**Reading rule:** `corroboration_state: externally_anchored` on a SIMULATED method must **not** be treated as a closed existence bound. Disclosure in the Golden Trace README is mandatory; disclosure is not completion. Golden Trace v2 (D-008) replaces the stub with at least one real `anchoring_method` instance whose receipt verifies without Magentix infrastructure.

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

## Related

- Programme: external anchoring maturity TRK-001; three-layer / CRE-D01 in [`registers/three-layer-evidence-and-control-reevaluation.md`](../../registers/three-layer-evidence-and-control-reevaluation.md)
- Decision D-015 in [`registers/decision-register.md`](../../registers/decision-register.md)
- Live watch table: [`registers/adjacent-standards-watch.md`](../../registers/adjacent-standards-watch.md)
- Three-layer field map: [`three-layer-evidence-coverage.md`](three-layer-evidence-coverage.md)

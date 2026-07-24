# Brief: Agent 365 governs your Microsoft estate; ARBITR evidences your whole estate

> **Status: Magentix positioning draft (implementation layer) - two pages when printed.** Uses open AXES as the evidence substrate. Not an AXES normative document. Companion technical map: [`agent365-purview-se-mapping.md`](agent365-purview-se-mapping.md). Sources: Microsoft Learn Agent 365 observability + Purview AI / Agent 365 pages (2026).

---

## Page 1 - What each layer is for

### Agent 365 + Purview (Microsoft control plane)

Microsoft Agent 365 is the **control plane** to observe, secure, and govern agents across the Microsoft estate. Agents emit OpenTelemetry spans (`invoke_agent`, `execute_tool`, `chat`, `output_messages`) into Defender, the Microsoft 365 admin center, and Purview. Purview adds unified audit (`CopilotInteraction` and related AI record types), DSPM for AI, DLP, Insider Risk, retention, and eDiscovery over prompts, responses, and M365-accessed resources.

**Use it for:** tenant visibility, Entra agent identity, policy enforcement inside Microsoft 365, sensitivity/DLP, admin inventory, security hunting.

**Do not ask it to be:** portable, board-readable evidence of delegated autonomous execution across banks, ERPs, clouds, and partner agents - with commit boundaries, authority depth, and third-party re-verification from open artefacts alone.

### AXES + ARBITR (evidence plane)

**AXES** (open standard) defines the Standards Envelope: append-only, hash-chained, signature-ready evidence events - authority, commit consequence, topology, evidence quality, acknowledgment ladder, external anchoring.

**ARBITR** (Magentix) is the interpretation and report layer: scores, narratives, assurance packs. It **conforms to AXES**; it does not define conformance. Anyone can emit and verify AXES without ARBITR.

**Use them for:** estate-wide evidence of what became real under whose delegation; regenerable board / audit / regulator / forensic packs; independent existence bounds (SCITT, timestamp authorities, …).

### One line

| | Agent 365 / Purview | AXES + ARBITR |
|---|---|---|
| Lane | Govern & observe **Microsoft** agents | Evidence **whole-estate** autonomous execution |
| Custody | Microsoft cloud logs and policies | Customer-held / portable SE bundles + optional external anchors |
| Output | Admin center, Defender, DSPM, audit search | Open envelopes + claim-cited assurance reports |

---

## Page 2 - The independence argument and the import pack

### The killer argument

Auditors, insurers, and regulators eventually ask: *can a competent third party reconstruct what happened without trusting the respondent's vendor?*

A **Microsoft log of Microsoft's agents**, stored and queried inside Microsoft Purview / Defender, answers operational and compliance questions **inside that trust domain**. It does **not** by itself satisfy:

- **Independence** - the evidence store is operated by the same ecosystem that ran the agent.
- **Completeness across estates** - actions that settle on payment rails, update non-M365 systems of record, or run on AWS/GCP/partner runtimes never appear as first-class Agent 365 spans.
- **Delegation depth** - Entra appId / blueprint ≠ CFO delegation AD-7844 with limits, policy version, and validity window.
- **Commit vs chat** - tool and inference spans ≠ money-movement / record-change commit evidence with counterparty acknowledgment.
- **Existence bound** - cloud audit retention ≠ SCITT/TSA/OTS receipt a third party verifies offline.

**Agent 365 governs your Microsoft estate. ARBITR evidences your whole estate** - by emitting and assembling **AXES** envelopes (including imports from Microsoft where useful) and producing assurance reports that cite open fields, not product screens.

### What we map vs what we add

| From Microsoft (import) | AXES / ARBITR adds |
|---|---|
| Invoke / tool / chat spans → lifecycle `event_kind`, trace/span, agent ids | Authority context, capability, policy snapshot path |
| Conversation / session ids | Correlation spine + optional content-bound action key |
| AccessedResources / sensitivity | Target refs + privacy/redaction discipline (no raw prompt dumps in SE) |
| Purview audit timestamps / operations | Commit boundary, ack ladder, cross-estate continuation |
| Tenant / channel / caller | Emission fail-posture, silence semantics, external anchor |

Full field table: [`agent365-purview-se-mapping.md`](agent365-purview-se-mapping.md).

### Call to action (Magentix)

1. Keep Agent 365 / Purview as the **Microsoft governance** investment (do not displace).
2. Deploy **AXES emitters** on consequential runtimes (including non-M365).
3. Use **ARBITR** to import Microsoft telemetry into SE, join cross-estate evidence, and generate board/audit packs.
4. Anchor exports externally so evidence survives operator and cloud disagreement.

Backlog item: **BLD-031** - Agent 365 / Purview import pack (ARBITR).

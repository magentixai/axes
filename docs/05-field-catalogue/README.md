# Field Catalogue

One file per module. Per-field descriptor: canonical key - definition - purpose - type - required status - maturity - conformance level - allowed values - example - report/audit/security usage - privacy sensitivity - redaction behaviour - derivability - confidence considerations - common misinterpretations - implementation notes - source requirement IDs (traceable to registers/requirements-register.md). Canonical keys and enums follow the harmonisation decisions in docs/06.

**Why this field exists (house style).** Every catalogue field, starting with Module 01 and every field Work Order 16 touches, carries a four-part note: **What it records** / **Why it exists** / **What it does NOT do** / **Origin**. Worked exemplar and the first set of notes: [field-origin-notes.md](field-origin-notes.md). "What it does NOT do" is the lane boundary and is not optional. Credit public sources only; never credit anyone for something they did not say.

| Module | Status |
|---|---|
| [01 - Envelope Core](module-01-envelope-core.md) | **DRAFT published - open for challenge** (23 entries plus WO16 identifier/time/signature companions) |
| [Custody axis](custody-axis.md) | Working note (not-self-declared rule; three identity coordinates) |
| [Field origin notes](field-origin-notes.md) | Four-part "why this field exists" notes |
| 02 Actor/Agent/Model/Runtime · 03 Authority & Delegation · 04 Capability & Scope · 05 Target/Resource/Operation · 06 Commit Boundary & Consequence · 07 Topology & Lineage · 08 Boundary Entry/Exit · 09 Evidence Artifact Refs · 10 Evidence Quality · 11 Behaviour & Security Signals · 12 Risk/Control/Exception · 13 Data/Privacy/Redaction · 14 Integrity/Hashing/Signature · 15 Attestation · 16 Reportability | Queued - modules ship as individual commits (Roadmap P2). Module 06 (Commit Boundary & Consequence) is next: it is where community record-shape discussions (receipts, refund/slash states, settlement-vs-correctness separation) land |

Keys in DRAFT modules are proposed-canonical: immutable only from module freeze. Challenge them now - that is what this phase is for.

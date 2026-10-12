# Custody axis and decision-identity coordinates

> **Status: working note.** Complements Module 01 identifier rules and the credits in the decision register. Not a schema freeze.

## Not self-declared

`emitter_independence_level` and `capture_relationship` record an identity established elsewhere at the commit boundary. They MUST NOT be self-declared by the emitting schema, and a consumer MUST NOT read them as an assertion the envelope itself can support.

Credit: Dani Danwin (TrustLayers). A schema cannot mint an identity it did not issue. Decision identity needs coordinates pinned in two venues: the **digest context** belongs in a registry, immutable and owner-authored; the **capturer's identity** belongs at the runtime that emits the record, issuer-established at the commit boundary. Two records byte-identical under one digest context can still differ in whether the capturer was issuer-established or self-asserted.

## Third coordinate: identifier scope

Two records byte-identical under one digest context, with the same issuer-established capturer, can still be about different subjects if the identifiers are relying-party-scoped (`identifier_scope: relying_party_pairwise`). Digest context, capturer identity and identifier scope are three independent coordinates of decision identity.

## Layer owners

Enforcement belongs to the policy engine. Correlation belongs to SOC and threat-detection, not the custodian. Custody-of-the-fact belongs to the witness. Envelope kinds `correlation_finding` and `triage_disposition` are witnessed, never authored: the custodian attests that a finding was emitted, by whom and when; it never asserts the correlation itself.

Four-part field notes: [field-origin-notes.md](field-origin-notes.md).

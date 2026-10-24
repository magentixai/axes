# Profile authoring guide for protocol owners

> **Living document.** Version 0.1, 24 October 2026. This guide grows as AXES firms up. Every section carries a maturity marker, so you know what you can build on today:
>
> - **[Settled]**: backed by decided entries in the decision register or by the published corpus. Build on it.
> - **[Proposed]**: proposed in the decision register and open for review. Design for it, and expect wording to change.
> - **[Open]**: not yet decided. Read the notes, and tell us what you need.
>
> The binding profile catalogue it describes is itself proposed (D-051). Comments and contributions are welcome through the repository's issue templates.

## 1. Who this guide is for **[Settled]**

You own, or speak for, a protocol that agents use to pay, authorise, attest or exchange evidence, and you want AXES evidence records to carry and verify your protocol's artefacts. For example:

- payment networks, PSPs and acquirers;
- agent-payment protocol maintainers (x402, AP2, ACP and similar);
- wallet and identity providers;
- agent platforms and tool gateways;
- other evidence standards;
- sector bodies (finance, manufacturing, healthcare, logistics).

**What you get.** A record made under your profile can be checked by any reader, offline, from the published procedure and your artefacts as you produced them, without trusting the record holder. That includes auditors, regulators, insurers, counterparties and courts. Your protocol stays yours: your bytes, your identifiers, your versioning.

## 2. What you are joining: the AXES ethos **[Settled]**

A profile must fit these principles. Source: docs/01 and the decision register.

- **Evidence, not control.** AXES records what happened. It never enforces, blocks, scores or certifies. A profile records and checks; it does not decide.
- **Vendor and runtime neutrality.** Conformance is defined by public text, a public validator and public vectors, never by any product's behaviour, including the steward's own commercial products.
- **Scoped claims only.** A conformance statement names both sides: the subject and the profile with its version and digest. The unqualified phrase "AXES-conformant" is not used (D-027).
- **Trust is computed, never stored.** No trust, confidence or sufficiency value is written into a record (D-025, D-031). Relying parties apply their own requirement profiles.
- **Absence is disclosed, never hidden.** A check that could not run is `not_evaluated`, distinct from a check that ran and found something missing (D-023).
- **Strength is earned.** A strong claim, for example "externally anchored", holds only when a verifier can confirm it (D-020).
- **Your bytes stay authoritative.** AXES hashes your artefacts as received and carries your identifiers verbatim (docs/20 N13).

## 3. Do you need a profile, and which kind? **[Settled for kinds; Proposed for binding]**

| You want to | Profile kind | Where it is listed |
|---|---|---|
| Tie a record to your protocol's artefacts (a payment, mandate, receipt, settlement, another standard's record) | Binding profile, `binding_profile_ref` | `registers/binding-profile-catalogue.md` **[Proposed, D-051]** |
| Offer a mechanism that proves a digest existed by a time (a ledger, log, time-stamp service) | Anchor profile, `anchor_profile_ref` | `docs/anchoring-profiles.md` **[Settled, D-020]** |
| State what a relying party in your sector requires of evidence | Requirement profile, `requirement_profile_ref` | `profiles/` **[Settled, D-027 to D-037]** |
| Declare how your emitter produces AXES records | Implementation profile, `implementation_profile_ref` | Emitter side **[Settled, D-027]** |

Profile names follow D-028: a record cites `<kind>_profile_ref`, and the profile names itself `<kind>_profile_id`.

## 4. Before you start **[Settled]**

You will need:

1. **A pinned specification.** A commit-addressed or versioned text of your protocol, so the profile can say exactly what it binds. A moving "latest" cannot be pinned.
2. **A licence** for your specification and test data that lets others implement and redistribute vectors.
3. **A change controller:** a named owner who decides versions.
4. **Stable artefact bytes.** Know which bytes you sign or hash, and in what encoding. AXES will hash them exactly as received.
5. **An engineering contact** who can answer questions about edge cases.

## 5. Anatomy of a binding profile **[Proposed, D-051; design in docs/21]**

| Element | What you write |
|---|---|
| Identifier | `<your namespace>:<lower_snake_name>@<version>`; immutable; a changed procedure is a new version |
| Protocol bound | Name and exact version or commit |
| Artefacts | Each artefact referenced, its encoding, and the rule "hashed as received" |
| Field disposition | Every binding field as `never_redactable`, `disclosable_by_role` or `out_of_record` |
| Verification procedure | Runnable steps a third party follows offline |
| Outcome mapping | Your results mapped to the four AXES states (section 7) |
| Vectors | Two-sided, one pinned outcome per edge (section 8) |
| Unsettled question notes | The readings your profile deliberately leaves unpinned (D-033) |
| Claim ceiling | What a verified binding does not establish |
| Status, owner, licence | As in section 10 |

## 6. Field disposition **[Proposed, D-043 to D-049; mechanism Open]**

Decide, field by field, what a verifier of your binding must always see, and what may be committed and shown only to entitled roles.

- **`never_redactable`.** Fields without which the binding cannot be checked, for example network, settlement or transaction reference, the binding digest. These are never withheld (D-049).
- **`disclosable_by_role`.** Values committed in the record with salted per-field commitments and disclosed to named roles, for example amount or payee disclosed to the payment verifier (D-045).
- **`out_of_record`.** Values referenced only by digest, held elsewhere.

**[Open]** The exact commitment construction (AXES issue #5, P1-1) is not yet fixed. The direction is SD-JWT-style salted commitments (RFC 9901), the same construction used by AP2 mandates and Mastercard Verifiable Intent. If your protocol already uses SD-JWT, your disclosures may be reusable as they are.

## 7. Mapping your outcomes to AXES states **[Settled vocabulary, D-023 and D-029]**

AXES reports every check in four states: `verified`, `contradicted`, `indeterminate`, `not_evaluated`. Each carries a reason (`divergence`, `absence`, `instrument_failure`), a subject (`artifact`, `operator`, `network`, `verifier`, `access`) and a closed condition code (docs/06).

Map each result your protocol defines to exactly one state, and say why. Typical patterns:

- Your positive result maps to `verified`.
- "Could not obtain what was needed to check" maps to `indeterminate` with reason `absence`. Never map it to a negative.
- "Not attempted" or "unsupported method" maps to `not_evaluated`.
- A determinate negative maps to `contradicted` only when it is evidence against the artefact itself. If it is only a statement about the inputs the verifier used, prefer `indeterminate` and explain.

**Worked case [Open]:** the x402 offer-receipt link results (`linked`, `no_match`, `incomplete`, `not_attempted`, `malformed`, `inconsistent`; x402-foundation/x402#3827). Three map cleanly: `linked` to `verified`, `incomplete` to `indeterminate`, `not_attempted` to `not_evaluated`. The mappings for `no_match`, `malformed` and `inconsistent` are still under discussion.

## 8. Test vectors **[Settled practice]**

- **Two-sided.** Every edge your procedure can detect has a vector that must pass and a vector that must fail.
- **One pinned outcome per edge.** No vector accepts "either result".
- **Coverage.** Every outcome you declare appears in at least one vector; AXES enforces this at run time (D-019).
- **Byte-level.** Vectors pin the exact bytes and digests, so implementations in different languages compare byte for byte.
- **Small verifier.** A reference verifier using only a standard library (plus RFC 8785) lets reviewers read all of it.

## 9. Security and privacy checklist **[Settled unless marked]**

- Hash your artefacts as received; never re-serialise them before hashing.
- Carry your identifiers verbatim; do not translate key names (docs/20 N13).
- No secrets, tokens or keys in any record or vector.
- Low-entropy values (amounts, booleans, short identifiers) are never exposed as bare digests. **[Proposed]** Use salted commitments (D-045).
- **[Proposed]** Domain separation: any value hashed or signed on the AXES side carries the AXES domain tag, so artefacts from your protocol cannot be replayed as AXES values or the reverse (D-050).
- Timestamps in AXES records are RFC 3339 UTC with millisecond precision (docs/20). Your protocol's own timestamps are carried as you define them.
- State plainly what a verified binding does not prove, for example that delivery happened or that a set of records is complete.

## 10. Publishing and admission **[Proposed, D-051]**

1. **Choose a namespace.** Your own (for example `yourorg:`) or, by agreement with the steward, an `axes:` reference profile. `axes:` is reserved for steward-reviewed profiles (D-033).
2. **Open a pull request** adding your entry to `registers/binding-profile-catalogue.md`, with links to your pinned text, procedure, vectors and licence.
3. **Statuses:** `reserved`, `experimental`, `candidate`, `stable`, `deprecated`, `superseded` (docs/21 section 4). `stable` needs two independent implementations passing the same vectors, a stated claim ceiling and a named change controller. The same bar applies to the steward's own profiles.
4. **Credit.** Adoption is recorded in the decision register with your organisation credited.
5. **Superseding a reference profile.** If AXES already holds an `axes:` reference profile for your protocol, your own profile can supersede it, with an explicit translation.

## 11. Versioning, deprecation and supersession **[Settled principle, D-021 and D-033; Proposed for bindings]**

- A profile is immutable at `id@version`. Any change to the procedure, artefacts or field disposition is a new version.
- Deprecation never breaks records: a deprecated profile is still evaluated under its own procedure.
- Translation to a successor is explicit and named, never silent.
- Records pin the profile's digest, so a reader always knows exactly which text applied.

## 12. Governance and neutrality **[Settled]**

- **Disclose interests.** If your organisation sells products or services built on your profile, say so in the profile.
- **No product claims.** Acceptance by any product, including the steward's commercial products, is not AXES conformance.
- **One bar for all.** Profiles are reviewed against the same admission checklist whoever authors them.

## 13. Worked example: `axes:x402_correlation@1` **[Settled; status `candidate`]**

What an existing profile declares:

- **Protocol bound:** x402 v2, the `exact` scheme with EIP-3009 on EVM networks. Other schemes are refused rather than mapped.
- **Artefacts:** the served PaymentRequired and the signed PaymentPayload, both parties holding identical bytes at authorisation.
- **Binding:** SHA-256 over the RFC 8785 bytes of a correlation core, giving `correlation_hash`.
- **Excluded by design:** the receipt (it carries the hash) and the settlement (checked separately, by decode and compare).
- **Vectors:** two-sided, in `tools/x402/vectors/`, and cross-checked against independent external vectors.
- **Why it is `candidate`, not `stable`:** one implementation so far.

Read it in `tools/x402/x402_correlation.py` and `docs/x402-trust-lanes-solution.md`.

## 14. Profile template **[Proposed; key names subject to docs/20 review]**

```json
{
  "binding_profile_id": "yourorg:your_protocol_binding@1",
  "status": "experimental",
  "owner": "Your organisation, change controller contact",
  "licence": "Apache-2.0 (code and vectors), CC-BY-4.0 (text)",
  "protocol": { "name": "Your protocol", "version_ref": "pinned version or commit URL" },
  "artifacts": [
    { "artifact_name": "your_message", "encoding": "as defined by your spec", "hash_rule": "SHA-256 over the bytes as received" }
  ],
  "field_dispositions": [
    { "field_path": "network", "disposition": "never_redactable" },
    { "field_path": "amount", "disposition": "disclosable_by_role", "disclosed_to_roles": ["payment_verifier"] }
  ],
  "verification_procedure_ref": "URL of the runnable procedure",
  "outcome_mappings": [
    { "protocol_result": "your_positive_result", "verification_state": "verified" }
  ],
  "vectors_ref": "URL of two-sided vectors",
  "claim_ceiling_note": "What a verified binding does not establish",
  "unsettled_question_notes": ["Readings this profile deliberately leaves unpinned"]
}
```

## 15. Organisational readiness: preparing to support AXES **[Settled guidance]**

- **People.** Name an owner for the profile and an engineer who knows your protocol's edge cases.
- **Specification.** Publish pinned, licensed text and keep old versions reachable.
- **Data.** Know which of your fields are personal or commercially sensitive, and which a verifier truly needs.
- **Legal and privacy.** Agree how disclosures to auditors, regulators and counterparties are authorised and logged. **[Proposed]** AXES will record every re-disclosure in a sealed disclosure log (D-046).
- **Engineering.** Plan for two independent implementations before you seek `stable`.
- **Posture.** Contribute vectors and edge cases. Evidence standards gain trust from independent reproduction, not from assertion.

## 16. Open questions and what is coming **[Open]**

| Topic | Where | What changes in this guide when it lands |
|---|---|---|
| Redaction-tolerant hashing construction | P1-1, axes#5; D-045 | Section 6 gets the exact commitment format and vectors |
| Full envelope schema (se-v0.1) | ROADMAP P3 | Section 14 template gains the record-side schema |
| Extension model (`must_understand`, unknown fields) | docs/08 | How profile-specific fields are carried |
| Envelope signature profile | axes#11 | How records naming your binding are signed |
| Binding catalogue decision | D-051 | Markers in sections 3, 5, 10 move from Proposed to Settled |
| Registry home | IETF draft revisions | Whether the catalogue moves to an IANA registry |

## 17. Changes to this guide

| Version | Date | Change |
|---|---|---|
| 0.1 | 24 Oct 2026 | Skeleton published with D-051 (proposed) |

---
title: "AXES: A Recomputable Evidence Envelope for Autonomous Execution"
abbrev: "AXES Evidence Envelope"
docname: draft-sansone-axes-evidence-envelope-00
category: info
submissiontype: IETF
ipr: trust200902
area: "Security"
keyword:
  - evidence
  - audit
  - canonicalization
  - anchoring
  - autonomous agents
stand_alone: yes
pi: [toc, sortrefs, symrefs]

author:
  -
    fullname: "Martin Sansone"
    organization: "Magentix AI"
    email: "developer@magentix.ai"

normative:
  RFC8785:
  RFC3339:
  RFC3161:
  RFC7493:
  FIPS180-4:
    title: "Secure Hash Standard (SHS)"
    author:
      org: "National Institute of Standards and Technology"
    date: 2015-08
    seriesinfo:
      FIPS: "180-4"

informative:
  RFC6920:
  RFC6962:
  RFC7942:
  RFC9162:
  RFC9942:
  RFC9943:
  I-D.krausz-verification-state:
  I-D.etcheverry-action-ref:
  I-D.gilda-audit-agent-audit-record:
  I-D.kuehlewind-audit-architecture:
  I-D.sergeev-audit-task-requirements:
  AXES-REPO:
    title: "AXES (Autonomous eXecution Evidence Standard) public working draft repository"
    target: https://github.com/magentixai/axes
    author:
      org: "Magentix AI"
    date: 2026
  AXES-GT21:
    title: "AXES Golden Trace corpus, release gt-v2.1 (tag corpus/2026-10-12-gt-v2.1)"
    target: https://github.com/magentixai/axes/tree/corpus/2026-10-12-gt-v2.1
    author:
      org: "Magentix AI"
    date: 2026-10-12
  OTS:
    title: "OpenTimestamps"
    target: https://opentimestamps.org/
    author:
      org: "OpenTimestamps project"
    date: false
  CAIP-2:
    title: "CAIP-2: Blockchain ID Specification"
    target: https://github.com/ChainAgnostic/CAIPs/blob/main/CAIPs/caip-2.md
    author:
      org: "Chain Agnostic Standards Alliance"
    date: false
  X402-TSC4:
    title: "x402 Foundation TSC issue 4: evidence record working group"
    target: https://github.com/x402-foundation/tsc/issues/4
    author:
      org: "x402 Foundation"
    date: 2026

--- abstract

This document describes AXES, a public working draft for recording evidence of autonomous execution, that is, actions taken by software agents under delegated authority. It specifies the parts of AXES that are settled and independently reproduced: a canonical byte form and hash scope for the evidence record (the Standards Envelope), a hash chain over a declared stream, a block for external anchoring of digests with earned rather than asserted strength, a four-state result vocabulary for verification, and requirement profiles that a relying party applies to evidence to produce a deterministic evaluation record. The design keeps evidence, interpretation and enforcement apart, and requires that the absence of evidence be reported as absence rather than read as a pass. AXES is offered as one input format to format-neutral audit readers, not as a replacement for other record formats. Parts of AXES that are not yet settled, including the full envelope schema and redaction-tolerant hashing, are named as open issues.

--- middle

# Introduction

Software agents increasingly act on delegated authority: they move money, change records and commit organisations to obligations. When one of those actions is later questioned, by an auditor, a regulator, a counterparty or a court, the question is rarely "what did the logs say". It is "what can be shown, by whom, from which records, and with what limits". Logs serve engineers debugging software. Evidence serves the people who carry the consequences.

AXES (Autonomous eXecution Evidence Standard) {{AXES-REPO}} is a public working draft that defines an evidence record for that purpose, the Standards Envelope (SE), and the rules by which a third party can recompute, anchor and evaluate it without access to the system that produced it. Its governing design rule is that a competent third party should be able to produce a credible, structured account of what happened from the open specification and the evidence alone.

AXES is deliberately not a logging format, a policy or blocking engine, an identity system, a payment rail, or a compliance certificate. It evidences; it does not enforce and it does not certify.

AXES is written from the position of the party who must later rely on a record, not the party that produces it. It is not specific to payments. It is meant for machine-to-machine actions of every kind, including payments, data exchange, compute, identity assertions, supply-chain actions and industrial control; the published corpus contains an industrial trace alongside a financial one. An AXES record sits beside the protocol that carries an action, as a separate evidence record, not inside it: the protocol's own messages are referenced by digest, exactly as that protocol defines them. AXES records the facts a relying party needs to verify later, such as which authority an action relied on and that authority's state at the time of the action. It references the processes that produced those facts (billing schedules, organisational workflows) rather than modelling them.

## Scope of this document

This -00 is scoped to the parts of AXES that have a published reference implementation, pinned two-sided test vectors, and independent reproduction from the specification text (see {{impl-status}}):

* the canonical byte form, hash scope and hash chain ({{canonical}} and {{scope}});
* the declared capture boundary and the treatment of absence ({{absence}});
* the external anchoring block and its verification rules ({{anchoring}});
* the four-state verification result vocabulary ({{results}});
* requirement profiles and evaluation records ({{evaluation}});
* the conformance-vector method ({{vectors}}).

The full field catalogue of the envelope (sixteen planned modules, of which two are published for challenge), the envelope JSON Schema, the extension model, the envelope signature profile and redaction-tolerant hashing are not specified here. They are listed in {{open-issues}}. Field names used in examples follow the published corpus of record {{AXES-GT21}}; they are not frozen by this document.

## Relationship to other work

Several individual drafts in the agent audit space define record formats ({{I-D.gilda-audit-agent-audit-record}}), audit architectures ({{I-D.kuehlewind-audit-architecture}}) and evidence requirements ({{I-D.sergeev-audit-task-requirements}}). AXES does not compete to be the single record format. It takes the position that three roles should stay separate:

* a record format, of which AXES is one;
* an enforcement point, which decides whether an action may proceed and which AXES never is;
* a format-neutral reader, which takes records in any declared format and returns a bounded finding.

AXES contributes to that reader the rules it needs from any format: recomputable digests, a declared hash scope, honest reporting of absence, anchors whose strength is earned, and results that never collapse "could not check" into "checked and found nothing". The verification result vocabulary is taken from {{I-D.krausz-verification-state}}. Action identity converges with {{I-D.etcheverry-action-ref}}, which uses the same RFC 8785 canonical form. {{related}} gives the details.

## Requirements Language

{::boilerplate bcp14-tagged}

## Terminology

Standards Envelope (SE):
: One AXES evidence record: an atomic, append-only record of one execution event, serialised as a JSON object.

Emitter:
: The software that produces envelopes at the point of execution.

Stream:
: An ordered sequence of envelopes from one emitter, linked by a hash chain ({{chain}}).

Subject:
: The thing a digest, anchor or evaluation is about: an envelope, a chain head, a bundle manifest or a release statement.

Capture boundary:
: The declared scope within which the emitter commits to producing an envelope for every action of a declared kind.

Commit boundary:
: The point at which an action stops being advisory and has external consequence (for example, a payment instruction is released).

Anchor:
: A commitment of a subject digest to a mechanism outside the emitter's control (a time-stamp authority, a public chain, a transparency log) that a third party can check offline.

Relying party:
: A party that uses evidence to reach a conclusion, for example an auditor, a regulator, an insurer or a counterparty.

Requirement profile:
: A declared, versioned and immutable statement of what a relying party requires of a subject.

Evaluation record:
: The deterministic result of applying a requirement profile to a subject.

Reader:
: Software that verifies and evaluates records and returns a bounded finding. A reader is neither an emitter nor an enforcement point.

# Design Principles {#principles}

The following principles constrain every part of AXES. They are stated here because the mechanisms in later sections follow from them.

Append-only:
: Envelopes are never edited. A correction is a new envelope that names the one it supersedes and gives a reason.

Pointers and hashes only:
: Envelopes do not carry raw payloads, documents, screenshots or secrets. Artefacts are referenced by URI and digest, with declared classification and retention.

Fact separated from interpretation:
: Every value carries its provenance: where it came from (`evidence_origin`), on what basis it is asserted (`assertion_basis`) and how far it is corroborated (`corroboration_state`). Judgements such as trust, intent or sufficiency are not stored in the envelope.

Trust is computed, never stored:
: An envelope never carries a trust, confidence or sufficiency value about itself. Sufficiency is the output of a relying party's requirement profile applied to the evidence ({{evaluation}}).

Gaps are disclosed, never hidden:
: Completeness is measured against a declared population. The absence of evidence is reported as absence, with its reason where one is known ({{absence}}).

Strength is earned:
: A strong claim such as "externally anchored" is true only when a verifier can confirm it from the evidence ({{earned}}). A simulated or self-held mechanism never earns it.

Scoped assurance language only:
: No element or result implies "compliant", "safe" or "guaranteed". Results carry a basis and the limits of what was checked.

Vendor and runtime neutrality:
: Conformance is defined by the public specification, reference verifier and public test vectors, never by any product's ingestion behaviour.

# The Standards Envelope {#envelope}

This section is informative. It describes the envelope so that the normative sections that follow have a referent. The field catalogue is published for challenge in {{AXES-REPO}} and is not frozen.

An envelope is a JSON object. In the published corpus of record {{AXES-GT21}} every envelope carries, among others:

* identity and kind: `se_version`, `envelope_id`, `event_kind`;
* time: `occurred_at` (when the event happened), `emitted_at` (when the emitter produced the record) and `recorded_at` (when it was persisted), all as RFC 3339 {{RFC3339}} timestamps, together with `timestamp_source` and a clock-synchronisation confidence;
* placement: organisation, tenant and environment identifiers, `trace_id`, `span_id`, and a monotonic sequence number within the stream;
* the action and its authority: `actor`, `authority`, `operation`, `execution_phase` and `execution_mode`;
* epistemic status: `evidence_quality` (`evidence_origin`, `assertion_basis`, `corroboration_state`);
* privacy: classification and the pseudonymous references used for people;
* `integrity`: the canonicalisation identifier, hash algorithm, previous envelope hash, signing key identity, envelope hash and envelope signature.

Envelopes MAY carry a namespaced `extensions` object. Extensions MUST NOT override any field defined by AXES. The processing rules for unknown extensions (`must_understand`, `unknown_field_policy`) are an open issue ({{open-issues}}).

Every numeric quantity inside the hash scope is exact. JSON numbers with a fractional part MUST NOT appear in the hash scope. Asset-denominated quantities use an Amount object: `value` is a string of base-10 integer atomic units, `decimals` is the declared scale, and `asset` is a namespaced string (`iso4217:<code>` for fiat, `caip19:<asset id>` for crypto-assets). Ratios that must be recorded use exact rationals (`numerator`, `denominator`, both integer strings). Derived ratios, such as how much of a delegated limit was used, are not stored; they are computed from their operands when a report is produced.

# Canonical Form and Hashing {#canonical}

## Canonical byte form

The canonical byte form of an AXES JSON object is the output of the JSON Canonicalization Scheme {{RFC8785}}. The input MUST be I-JSON {{RFC7493}}; in particular, an object with duplicate member names MUST be rejected rather than canonicalised.

The identifier `RFC8785-JCS`, carried in `integrity.canonicalization_version`, denotes exactly the following, and nothing else:

* the RFC 8785 JSON Canonicalization Scheme at its published revision;
* output as UTF-8 bytes;
* object members sorted by UTF-16 code units (RFC 8785 Section 3.2.3), not by code point and not by any locale collation;
* no Unicode normalisation (RFC 8785 Section 3.1), so the NFC and NFD forms of the same visible key are distinct members;
* the digest algorithm is declared separately (`integrity.hash_algorithm`) and is not implied by this identifier;
* digests are encoded as bare lowercase hexadecimal, with no algorithm prefix.

A second implementer MUST be able to reproduce the canonical bytes from this statement alone. A change to any property above defines a new identifier; `RFC8785-JCS` is never redefined.

## Envelope hash

The envelope hash is computed as follows:

1. Remove `integrity.envelope_hash` and `integrity.envelope_signature` from the envelope.
2. Canonicalise the remaining object under the identifier in `integrity.canonicalization_version`.
3. Apply the algorithm named in `integrity.hash_algorithm` to the canonical bytes.
4. Encode the digest as bare lowercase hexadecimal.

Every other member of the envelope is inside the hash scope, including `envelope_id`, `recorded_at`, `integrity.signing_key_id` and `integrity.previous_envelope_hash`.

The digest algorithm is agile. The published corpus uses SHA-256 {{FIPS180-4}}. An implementation MAY use another algorithm over the same canonical bytes, provided that `integrity.hash_algorithm` names it. A verifier that does not implement the named algorithm MUST report the check as not evaluated ({{results}}), never as verified or contradicted.

## Hash chain {#chain}

Each envelope in a stream carries `integrity.previous_envelope_hash`, the envelope hash of the envelope immediately before it in the stream. The first envelope in a stream carries sixty-four zeros. The chain head is the envelope hash of the last envelope in the stream.

A verifier recomputes every envelope hash, checks that each `previous_envelope_hash` equals the recomputed hash of its predecessor, and checks that sequence numbers within the stream are contiguous. A recomputed hash that differs from the stored `integrity.envelope_hash` is a contradiction (`envelope_hash_mismatch`). A broken link is a contradiction (`chain_break`). A gap in the sequence numbers is indeterminate (`sequence_gap`): something is missing, but the chain alone cannot say why.

## Bundle manifest digest

A bundle is a set of files: the envelope stream plus the artefacts its envelopes reference. Its manifest maps each file path, using forward slashes and relative to the bundle root, to the lowercase hexadecimal SHA-256 of that file's bytes. The manifest file itself is excluded. The bundle manifest hash is the SHA-256 of the canonical bytes of that mapping. A verifier can check a bundle by recomputing every file digest and the manifest hash, without running any software supplied by the emitter.

# Hash Scope Discipline {#scope}

A digest whose scope is narrower than what a reader consumes leaves a region that can be changed while the record still verifies. AXES therefore treats the hash scope as a declared, reviewable part of the record. This section states the current AXES position, which is published for challenge. In the published corpus the hash scope is fixed by {{canonical}} and no per-envelope declaration is carried. The rules below govern any declaration or exclusion added later.

1. Scope defaults to inclusion. Every member is inside the hash unless an exclusion is declared.
2. Every exclusion MUST name a reason from a closed vocabulary (`hash_scope_exclusion_reason`). The two exclusions in force, `integrity.envelope_hash` and `integrity.envelope_signature`, have the reason `self_referential`.
3. Sensitivity of a value MUST NOT be used as a reason to exclude it from the hash scope. Sensitive values are committed at emission and selectively disclosed later.
4. A declaration of the hash scope, when carried, MUST be inside the hash scope it declares. Otherwise an attacker could edit the declaration to exclude a field, change that field, and leave both the digest and the declaration valid.

Three states that are easily confused MUST remain distinguishable to a reader:

| State | Inside the hash | What a verifier can say |
|---|---|---|
| Excluded at signing | No | Nothing about whether the present value is original |
| Redacted after signing | Yes, committed at emission | The withheld value still binds; a tombstone shows it was present |
| Absent | Never captured | The value was not recorded |
{: title="Excluded, redacted and absent"}

The mechanism for redaction after signing (salted per-field commitments or a Merkle-structured envelope) is not yet decided ({{open-issues}}).

# Capture Boundary and Honest Absence {#absence}

An emitter declares a capture boundary: the kinds of action, and the scope, for which it commits to producing an envelope every time. Within a declared boundary the emitter fails closed: if it cannot emit, the action does not proceed past the commit boundary, or the failure itself is recorded. Within the boundary, therefore, the absence of an envelope is evidence that no such action crossed the commit boundary. Outside the boundary, absence means only that nothing was captured.

When a value that a reader might expect is not present, the envelope SHOULD say why, by listing it in `field_absences` with an `absence_reason_code`. This list is defined in the AXES vocabularies and is not yet exercised in the published corpus. The reason codes are:

* `not_applicable`: the value does not apply to this event;
* `not_captured`: the emitter did not capture it;
* `withheld`: the value exists and is held back by the operator;
* `redacted`: the value is committed and not disclosed to this reader.

`withheld` and `redacted` MUST NOT be read as absent. An event outside the declared boundary is disclosed as `outside_capture_boundary`. That is an honest statement of scope, not a failure.

A reader asked whether qualifying evidence exists returns a bounded finding. "No qualifying evidence was found in the declared sources by the stated cut-off" is a valid, verifiable finding. It is different from "the sources could not be read", and both are different from "verified". Registration of a record in a log, or anchoring of its digest, shows that the record existed and was not equivocated. It does not show that the set of records is complete, or that the recorded event occurred as described.

# External Anchoring {#anchoring}

A hash chain proves order and tamper evidence inside the emitter's own records. It does not prove that the bytes existed, unmodified, at a time independent of whoever holds them. An anchor provides that independent existence bound.

## The anchoring block

An anchoring block names one subject and carries one or more anchors over it:

~~~
{
  "anchored_subject_type": "release_statement",
  "anchored_subject_hash": "d8b6a69f57ba2209561fb551443c096c
                            47fcb0cb6db37005fd0713690de88299",
  "anchored_subject_hash_algorithm": "SHA-256",
  "anchors": [
    {
      "anchor_id": "anch:tsa-freetsa",
      "anchoring_method": "timestamp_authority",
      "anchor_profile_ref": "axes:rfc3161_sha256_imprint@1",
      "basis_status": "demonstrated",
      "anchor_commitment_hash": "d8b6a69f...8299",
      "anchor_commitment_hash_algorithm": "SHA-256",
      "anchor_requested_at": "2026-10-12T10:12:28.000Z",
      "anchored_at": "2026-10-12T10:12:28.000Z",
      "anchor_service_id": "https://freetsa.org/tsr",
      "anchor_operator_id": "https://freetsa.org",
      "anchor_record_ref": "serial:0x09216E25",
      "anchor_proof_ref": "proofs/timestamp_authority/
                           proof_manifest.json",
      "anchor_proof_hash": "8023de42...4169",
      "anchor_verification_procedure_ref":
        "docs/anchoring-profiles.md#axesrfc3161_sha256_imprint1"
    }
  ]
}
~~~
{: title="Anchoring block over the gt-v2.1 release statement (abbreviated; line breaks inside strings are for presentation)"}

`anchored_subject_type` is one of `chain_head`, `envelope`, `bundle_manifest` or `release_statement`.

`anchoring_method` names a family of mechanisms, from an open registry seeded with:

* `timestamp_authority`, an RFC 3161 {{RFC3161}} or equivalent authority;
* `opentimestamps`, aggregation into a Bitcoin block {{OTS}};
* `transparency_log`, a leaf in an append-only verifiable log;
* `distributed_ledger`, a contract or registry on a ledger;
* `write_once_store`, storage that refuses overwrite and has a third-party verification path.

Other mechanisms use a namespaced identifier `<namespace>:<id>` and MUST carry `anchor_verification_procedure_ref`. The method value MUST NOT carry status; whether an anchor is real is stated only in `basis_status`.

`anchor_profile_ref` names an immutable, versioned procedure that turns the subject digest into the value the mechanism stored (`anchor_commitment_hash`) and that says how to check it. A changed procedure gets a new identifier. A verifier recomputes the commitment through the profile and does not trust the stored value alone.

`basis_status` is `demonstrated` (a real anchoring run produced the anchor), `stubbed` or `simulated`. It is written by the producing tool from what the mechanism returned.

## Common verification rules

The following rules apply to every anchor profile:

* Only an anchor with `basis_status: demonstrated` can verify. `simulated` or `stubbed` gives indeterminate (`basis_not_demonstrated`), never verified.
* A commitment that does not recompute from the subject under the profile, or a proof that attests a different digest, time or record from the one the block states, is contradicted (`anchor_commitment_mismatch`).
* `anchor_proof_ref` points to a proof manifest that lists every proof file with its digest, and `anchor_proof_hash` is the digest of that manifest. A missing reference is indeterminate, attributed to the operator (`anchor_proof_absent`). A reference that cannot be retrieved at audit time is not evaluated, attributed to the network (`anchor_proof_unresolvable`). An altered proof file is contradicted (`anchor_proof_hash_mismatch`).
* An anchor that has been requested but not yet attested (it has `anchor_requested_at` and no `anchored_at`) is indeterminate (`anchor_pending`).
* A verifier that lacks the library, binary or procedure for a method MUST report not evaluated, reason `instrument_failure`, condition `anchor_method_unverifiable`, subject `verifier`. This is never a pass and never a finding about the anchor.

## Published profiles

`axes:rfc3161_sha256_imprint@1`:
: The subject's SHA-256 is the message imprint of an RFC 3161 time-stamp request. Verification checks the token against the TSA certificate chain supplied in the proof bundle and checks that the token's time and serial equal `anchored_at` and `anchor_record_ref`. This establishes that the named TSA signed the digest at the stated time under that chain. Whether that chain is trusted is the relying party's decision.

`axes:opentimestamps_sha256_digest@1`:
: The subject's SHA-256 is submitted to OpenTimestamps calendars and, once mined, attested by a Bitcoin block header. Verification replays the proof from the digest to the header's Merkle root, checks the header's proof of work against its own target, and checks that `anchor_record_ref` and `anchored_at` equal the header's height, hash and time. Membership of that block in Bitcoin's main chain is a separate check against any Bitcoin node, by block hash. `anchor_service_id` names the chain as a CAIP-2 identifier {{CAIP-2}}.

A third profile, `axes:anchor_registry_bytes32@1`, covers a permissionless on-chain registry. It checks offline that the anchoring transaction's receipt sits under the block's receipts root and that the block header hashes to the block hash. Whether the block is on the chain's canonical history is a single lookup by block hash. A profile for transparency logs that issue COSE Receipts {{RFC9942}} under the SCITT architecture {{RFC9943}} is planned ({{open-issues}}). AXES does not depend on SCITT: `transparency_log` is an anchoring method class, and a SCITT receipt is one way to fill it.

## Earned strength {#earned}

`evidence_quality.corroboration_state` has an ordered set of values ending in `externally_anchored`. That value MUST NOT be asserted unless at least one anchor over the subject verifies under the rules above. A record that asserts `externally_anchored` over an anchor that is simulated or stubbed is contradicted (`anchor_simulated_claims_external`). An anchor that verifies but whose operator is not shown to be independent of the executor and deployer is indeterminate (`anchor_independence_unproven`). An anchor run by the emitter's own organisation does not show independence.

# Verification Results {#results}

Every check a verifier or evaluator performs yields exactly one result, using the four-state vocabulary of {{I-D.krausz-verification-state}} under AXES key names:

`verification_state`:
: `verified`, `contradicted`, `indeterminate` or `not_evaluated`.

`verification_reason_code`:
: `divergence` (the evidence disagrees with itself or with what it claims), `absence` (something needed is missing) or `instrument_failure` (the verifier could not perform the check).

`verification_subject_type`:
: Whom the result is about: `artifact` (the record), `operator` (whoever produced or holds it), `network` (retrieval at audit time), `verifier` (the checking tool) or `access` (the reader's entitlement).

`verification_condition_code`:
: One value from a closed list that names the class of condition, for example `chain_break`, `sequence_gap` or `anchor_pending`. The specific cause is recorded in free text (`observed_note`) and is not part of the closed vocabulary.

The following rules apply:

1. A check that could not be performed is `not_evaluated`. It MUST NOT be reported as `verified`, and it MUST NOT be reported as a finding against the record.
2. A check that was performed and found something missing is `indeterminate` with reason `absence`. Absence is never collapsed into a pass.
3. `contradicted` is reserved for evidence that disagrees with itself or with what it asserts.
4. When the parties to an exchange computed different values for what should be the same digest, the result is `indeterminate` with reason `divergence`. The verifier MUST NOT pick a side.

# Requirement Profiles and Evaluation {#evaluation}

What counts as sufficient evidence depends on who is relying on it. An auditor, a tax authority and a counterparty can reasonably require different things of the same record. AXES therefore puts sufficiency outside the record.

A requirement profile is a JSON document that names its purpose, the subject type it applies to, and a list of requirements. Each requirement has a check type (for example `field_presence`, `chain_integrity`, `sequence_continuity`, `anchoring` or `settlement_commitment`) and an obligation (`required`, `conditional`, `optional` or `prohibited`).

* A profile is immutable at `id@version`. Its digest is the SHA-256 of its canonical bytes, computed by the evaluator from the bytes it executed.
* Reference profiles use the `axes:` namespace. Anyone MAY publish profiles under their own namespace.
* A profile MAY extend others. The strictest obligation wins for each requirement. A requirement marked as a floor cannot be relaxed by an extending profile. A conflict is `indeterminate` (`profile_conflict`), never a silent choice.
* A profile lists the readings it deliberately leaves unpinned.

Evaluation applies one profile to one subject and yields an evaluation record. Each requirement gives one result in the vocabulary of {{results}}. The overall state is:

1. `contradicted`, if any requirement is contradicted;
2. otherwise `indeterminate`, if any requirement is indeterminate or not evaluated;
3. otherwise `verified`.

The result is described as unconditional only when every requirement is verified with no condition recorded.

Evaluation MUST be deterministic. It uses no model, no network access and no clock reading. External facts enter only as pinned evidence that records when the external authority answered. Two evaluators given the same subject, profile and pinned evidence MUST produce the same result digest (`result_core_hash`).

A statement of conformance names both sides: the subject digests, the requirement profile with its version and digest, and the evaluation result. An unqualified statement that something "conforms to AXES" is not meaningful under this document.

# Conformance Vectors {#vectors}

AXES defines conformance by public, two-sided test vectors rather than by any implementation's behaviour.

* Each vector pins canonical bytes and digests, or a single expected result, so that implementations in different languages can compare byte for byte.
* Vectors are two-sided. Every edge a procedure can detect has a vector that must pass and a vector that must fail, and each edge has exactly one pinned outcome.
* Coverage is checked: every outcome a profile or procedure declares must be observed in at least one vector. A declared outcome with no vector is reported as a coverage failure.
* The reference verifier is limited to the language's standard library plus an RFC 8785 implementation, so that a reviewer can read all of it.

# Implementation Status {#impl-status}

This section records the status of known implementations at the time of writing, following {{RFC7942}}. It is to be removed before publication as an RFC.

Reference implementation:
: Magentix AI, {{AXES-REPO}}, Apache-2.0 for code and vectors, CC-BY-4.0 for specification text. It includes a corpus generator, a reference verifier (`tools/axes_verify.py`), a byte checker that needs only the standard library (`tools/check_corpus_bytes.py`), an anchor producer and offline anchor verifier (`tools/anchoring/`) and a requirement-profile evaluator (`tools/axes_evaluate.py`). Continuous integration runs the full verification on Linux, macOS and Windows on every change.

Corpus of record:
: Release gt-v2.1, tag `corpus/2026-10-12-gt-v2.1` {{AXES-GT21}}, two bundles (a financial and an industrial trace, 76 envelopes each). Financial chain head `cbd1a73e910bd51f01cf5dd097c9a68869b733550d96db891d0f288bd4db59f1`, bundle digest `e922486b74689592ddc54c74725c9c5a55d8d793f12cade2e58929ab4801164e`. Industrial chain head `5ca428eac8ed5dde5b7720218712bdd2ede484a6892ac7894db2e1772a519dd6`, bundle digest `dd01b56c718c6a61f06725318ab99738799128d9cb527d5e468e9be5b78ebb31`.

External anchors on the release statement:
: SHA-256 `d8b6a69f57ba2209561fb551443c096c47fcb0cb6db37005fd0713690de88299`, anchored three ways, each independently of the others:
: * RFC 3161, FreeTSA, serial 0x09216E25, 2026-10-12T10:12:28Z.
: * OpenTimestamps, Bitcoin block 971082.
: * A permissionless on-chain registry (AnchorRegistry, contributed by giskard09) on Base, block 52987624, 2026-10-23T14:09:55Z, submitted by giskard09 from their own wallet. This verifies under the profile `axes:anchor_registry_bytes32@1`: the transaction receipt is proven under the block's receipts root, and the block header hashes to the block hash.
: All three verify offline.

Independent reproduction:
: The gt-v2.1 digests have been reproduced by four parties other than the authors, all recorded in the repository's release register.
: * giskard09: byte check, regeneration and reference verifier.
: * robertolocatelli81-dev: from the specification text only, with an independent canonicaliser and no AXES code.
: * MarkovianProtocol: an independent canonicaliser in two languages; all 76 envelope hashes in each bundle match.
: * babyblueviper1: from the specification text only, with an independent canonicaliser, the standard library and no AXES code. It covered every envelope hash, chain link and file, both chain heads and both bundle digests, but not the release anchors. This check also found that the hash-scope text published with the tag disagreed with the corpus about `recorded_at`. The text was corrected after the tag; the corpus was the reference and did not change.

Cross-format checks:
: The repository's RFC 8785 property vectors agree with an independent RFC 8785 implementation. Its x402 correlation recipe partitions a third-party payment-fingerprint vector set identically to that set's own recipe.

Disclosed limitations of the corpus:
: Envelope signatures in the corpus are stubs and are marked `envelope_signature_basis_status: stubbed`. In-trace anchors are simulated and marked `basis_status: simulated`. The reference verifier reports them as `indeterminate` (`basis_not_demonstrated`), and no envelope reports `contradicted`.

# Relationship to Other Work {#related}

{{I-D.krausz-verification-state}}:
: AXES adopts its four verification states and maps its own reason, subject and condition keys onto them. AXES condition names that generalise beyond AXES are candidates for that draft's registry.

{{I-D.etcheverry-action-ref}}:
: It defines a deterministic action identifier as SHA-256 over the RFC 8785 bytes of a small preimage. AXES content-addresses actions and custody records in the same way (compare {{RFC6920}}), and an `action_ref` value can serve as an anchor commitment under a named profile.

{{I-D.gilda-audit-agent-audit-record}}, {{I-D.kuehlewind-audit-architecture}}, {{I-D.sergeev-audit-task-requirements}}:
: These define a record format, an audit architecture and task-relative evidence requirements. AXES is compatible with a format-neutral reader in that architecture. Its requirement profiles are one way to express task-relative requirements as data.

{{RFC9943}} and {{RFC9942}}:
: A SCITT Transparency Service issues COSE Receipts, which are one instance of the `transparency_log` anchoring method. SCITT is a generalisation of Certificate Transparency {{RFC9162}}, which obsoletes {{RFC6962}}. In AXES terms, a receipt's inclusion proof shows registration, and a consistency proof, where supplied, supports the log's append-only property. Neither shows completeness of the registered set.

x402 payments {{X402-TSC4}}:
: AXES defines a correlation record that binds evidence to an x402 payment by digest, checked against public test vectors from the x402 community. A profile that binds an evidence packet to an x402 payment anchor, including the salted authorisation commitment proposed for x402 receipts, is in preparation.

# Open Issues {#open-issues}

The following are known gaps. Reviews and counter-proposals are welcome.

1. Redaction-tolerant hashing: salted per-field commitments or a Merkle-structured envelope. This gates the envelope schema.
2. The full envelope JSON Schema and field catalogue (two of sixteen planned modules are published for challenge). Key names in the published corpus and in the catalogue have not yet been reconciled in every case.
3. The extension model: `must_understand`, `unknown_field_policy`, and the hashing of unknown content.
4. The envelope signature profile over the canonical bytes (JWS or COSE). The corpus signatures are stubs.
5. The amendment model for superseding envelopes.
6. Whether `recorded_at`, which is written by the recipient, should be authenticated by a countersignature from the recipient rather than sit in the emitter's hash scope. It is in scope today; any change would land only in an announced release.
7. An anchor profile for transparency logs (COSE Receipts with `RFC9162_SHA256`). A profile for a permissionless on-chain registry exists in the reference tooling.
8. The binding of evidence to payment and authorisation protocols, x402 first, through named, versioned binding profiles.
9. Registration procedures for the AXES vocabularies (see {{iana}}).
10. Retention and obtainability: who holds a record, for how long relative to limitation periods, how it is produced on demand years later, and what happens when the holder ceases to exist.
11. An evidence bundle for disputes: a registered media type and a manifest of included artefacts with digests. It would also carry the set of verification results, including what was not checked, and an explicit statement of what the bundle does not contain.
12. Binding accountability to a legal person, rather than only to a key: the identifier scheme, the basis of the binding and how it was verified.
13. Binding the terms of an offer (price, asset, payee) into the record of the action that settles against it, and recording where what settled differs from what was offered.

# Security Considerations

The emitter may be the adversary:
: An envelope records what was claimed, by whom, under which authority and with what corroboration. It does not prove that the agent or the emitter behaved honestly. Self-declared values are not authenticated by being in the hash scope. Fields that record independence or custody MUST NOT be read as established by the record itself.

Scope narrower than consumption:
: If a reader consumes a field that the digest does not cover, that field can be altered while the record verifies. {{scope}} makes inclusion the default, requires a reason for every exclusion, and puts the scope declaration inside its own scope. Implementers MUST NOT read fields from outside the declared hash scope as authenticated.

Canonicalisation differentials:
: Two verifiers that accept different inputs, or that canonicalise the same input differently, can reach different verdicts on the same bytes. Implementations MUST reject non-I-JSON input, including duplicate member names, before canonicalisation. They MUST sort by UTF-16 code units and MUST NOT normalise Unicode. Floating-point values are excluded from the hash scope to avoid number-serialisation differences.

Digest labels:
: Because the digest algorithm is agile, a digest is meaningful only together with its algorithm label. A verifier MUST NOT compare digests whose algorithm labels differ.

Simulated or self-held anchors:
: A simulated anchor, or one held by the emitter's own organisation, gives no independent existence bound. {{earned}} makes the strong claim depend on verification. Relying parties decide whether to trust a time-stamp authority's certificate chain. A Bitcoin header's proof of work does not by itself show main-chain membership.

Registration is not completeness:
: An inclusion proof, a time stamp or a ledger record shows that a digest was committed. It does not show that every relevant record was committed, or that the recorded event occurred as described. Readers MUST NOT report completeness from anchoring alone.

Absence:
: An attacker who can suppress envelopes can make evidence absent. Sequence continuity, heartbeats, fail-closed emission within a declared boundary and the distinction between withheld, redacted and never captured exist so that suppression is visible as `indeterminate` rather than invisible.

What this specification cannot detect:
: This section states the limits, so that readers infer no more than a record supports.
: * An emitter that controls capture can omit actions outside its declared capture boundary, and nothing in the record shows them.
: * Until envelope signatures are specified ({{open-issues}}), an emitter can rewrite its own stream wholesale before the stream is first anchored externally. Anchoring bounds that window to the interval between anchors.
: * A completeness or count field computed by the party that holds the record is a claim by that party, not evidence of completeness.
: * Registration in a log or on a ledger shows non-equivocation of what was registered, not that every relevant record was registered.

# Privacy Considerations

Envelopes carry references and digests, not payloads. People (approvers, operators, customers, employees) are referenced by pseudonymous keys and are never embedded. Erasure is supported by destroying referenced content, so the envelope keeps its digest while the content is gone, and the result is reported as erased rather than missing.

A digest of a low-entropy value can be reversed by guessing. Anchoring a digest publishes it permanently. Emitters SHOULD anchor only digests of high-entropy subjects (chain heads, bundle manifests, release statements) or salted commitments, and SHOULD NOT anchor digests of individual values that identify a person.

Identifiers scoped to one relying party deliberately produce different digests at different relying parties, which limits correlation of the same person across relying parties.

Redaction after signing is not yet specified ({{open-issues}}). Until it is, sensitive values should be kept out of envelopes by reference rather than excluded from the hash.

# IANA Considerations {#iana}

This document has no IANA actions.

AXES maintains the following registries in its public repository {{AXES-REPO}}. Each entry there is immutable and additive. A future revision may request IANA registries for some of them:

* canonicalisation identifiers (currently `RFC8785-JCS`);
* `anchoring_method` values;
* `anchor_profile_ref` identifiers and their verification procedures;
* `verification_condition_code` values;
* requirement profile identifiers in the `axes:` namespace.

--- back

# Acknowledgements
{:numbered="false"}

AXES has benefited from public review and contributions credited in its provenance record and decision register: Tersign (Kevin Zhang) for the independence and completeness disqualifications; giskard09 (Pablo Etcheverry) for action-ref, on-chain anchoring and the custody-ref reference implementation; neldan00077 (TrustLayers) for the custody axis; MarkovianProtocol for byte-identity vector methodology; Rul1an for the one-outcome-per-edge discipline and the hash-scope failure case; and robertolocatelli81-dev (Noûs) for specification-only reproduction of the corpus of record.

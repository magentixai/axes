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
  RFC9901:
  RFC8610:
  I-D.mih-scitt-agent-action-capsule-sel-disc:
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
  PGC-17:
    title: "x402 receipt authorization commitment: receipt-level vectors and a checker from the text alone (preaction-governance-conformance pull request 17)"
    target: https://github.com/babyblueviper1/preaction-governance-conformance/pull/17
    author:
      org: "Magentix AI"
    date: 2026-10-23
  ISO4217:
    title: "Codes for the representation of currencies"
    author:
      org: "International Organization for Standardization"
    date: 2015
    seriesinfo:
      ISO: "4217:2015"
  ISO18013-5:
    title: "Personal identification - ISO-compliant driving licence - Part 5: Mobile driving licence (mDL) application"
    author:
      org: "International Organization for Standardization"
    date: 2021
    seriesinfo:
      ISO/IEC: "18013-5:2021"
  CAIP-19:
    title: "CAIP-19: Asset Type and Asset ID Specification"
    target: https://github.com/ChainAgnostic/CAIPs/blob/main/CAIPs/caip-19.md
    author:
      org: "Chain Agnostic Standards Alliance"
    date: false
  AXES-SDK:
    title: "axes-sdk: Python SDK for AXES evidence verification and evaluation (sdk/python)"
    target: https://github.com/magentixai/axes/tree/main/sdk/python
    author:
      org: "Magentix AI"
    date: 2026
  X402-TSC4:
    title: "x402 Foundation TSC issue 4: evidence record working group"
    target: https://github.com/x402-foundation/tsc/issues/4
    author:
      org: "x402 Foundation"
    date: 2026

--- abstract

This document describes AXES, a public working draft for recording evidence of autonomous execution, that is, actions taken by software agents under delegated authority. It specifies the parts of AXES that are settled: a canonical byte form and hash scope for the evidence record (the Standards Envelope), a hash chain over a declared stream, a block for external anchoring of digests with earned rather than asserted strength, a four-state result vocabulary for verification, and requirement profiles that a relying party applies to evidence to produce a deterministic evaluation record. The byte rules, the hash chain and the release anchors have been reproduced independently from the text; profile evaluation has a reference implementation. The design keeps evidence, interpretation and enforcement apart, and requires that the absence of evidence be reported as absence rather than read as a pass. AXES is offered as one input format to format-neutral audit readers, not as a replacement for other record formats. Parts of AXES that are not yet settled, including the full envelope schema and the exact construction for redaction-tolerant hashing, are named as open issues. The chosen direction for redaction, salted per-field hash commitments following the approach of SD-JWT with an encoding specific to AXES, is recorded.

--- middle

# Introduction

Software agents increasingly act on delegated authority: they move money, change records and commit organisations to obligations. When one of those actions is later questioned, by an auditor, a regulator, a counterparty or a court, the question is rarely "what did the logs say". It is "what can be shown, by whom, from which records, and with what limits". Logs serve engineers debugging software. Evidence serves the people who carry the consequences.

AXES (Autonomous eXecution Evidence Standard) {{AXES-REPO}} is a public working draft that defines an evidence record for that purpose, the Standards Envelope (SE), and the rules by which a third party can recompute, anchor and evaluate it without access to the system that produced it. Its governing design rule is that a competent third party should be able to produce a credible, structured account of what happened from the open specification and the evidence alone.

AXES is deliberately not a logging format, a policy or blocking engine, an identity system, a payment rail, or a compliance certificate. It evidences; it does not enforce and it does not certify.

AXES is written from the position of the party who must later rely on a record, not the party that produces it. It is not specific to payments. It is meant for machine-to-machine actions of every kind, including payments, data exchange, compute, identity assertions, supply-chain actions and industrial control; the published corpus contains an industrial trace alongside a financial one. An AXES record sits beside the protocol that carries an action, as a separate evidence record, not inside it: the protocol's own messages are referenced by digest, exactly as that protocol defines them. AXES records the facts a relying party needs to verify later, such as which authority an action relied on and that authority's state at the time of the action. It references the processes that produced those facts (billing schedules, organisational workflows) rather than modelling them.

## Scope of this document

This -00 is scoped to the parts of AXES that have a published reference implementation and pinned two-sided test vectors. The byte rules and the hash chain have also been reproduced independently from the specification text; profile evaluation so far has implementations by the authors only (see {{impl-status}}):

* the canonical byte form, hash scope and hash chain ({{canonical}} and {{scope}});
* the declared capture boundary and the treatment of absence ({{absence}});
* the external anchoring block and its verification rules ({{anchoring}});
* the four-state verification result vocabulary ({{results}});
* requirement profiles and evaluation records ({{evaluation}});
* the conformance-vector method ({{vectors}}).

The full field catalogue of the envelope (sixteen planned modules, of which two are published for challenge), the envelope JSON Schema, the extension model, the envelope signature profile and the construction for redaction-tolerant hashing are not specified here. They are listed in {{open-issues}}; the chosen direction for redaction is recorded in {{redaction}}. Field names used in examples follow the published corpus of record {{AXES-GT21}}; they are not frozen by this document.

## Position among the agent audit drafts

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
: A commitment of a subject digest to a mechanism outside the emitter's control (a timestamp authority, a public chain, a transparency log) that a third party can check offline.

Relying party:
: A party that uses evidence to reach a conclusion, for example an auditor, a regulator, an insurer or a counterparty.

Requirement profile:
: A declared, versioned and immutable statement of what a relying party requires of a subject.

Evaluation record:
: The deterministic result of applying a requirement profile to a subject.

Reader:
: Software that verifies and evaluates records and returns a bounded finding. A reader is neither an emitter nor an enforcement point.

Release statement:
: A small JSON document, published with a release of a corpus, that lists each bundle's chain head and bundle manifest hash. The SHA-256 of its bytes is what the release's external anchors commit to ({{impl-status}}).

## Conformance targets {#targets}

Each requirement in this document applies to one of the roles below. The table also states how far each role's rules have been shown to work. Parts of AXES not listed (the envelope field catalogue and schema, the extension model, envelope signatures and the redaction construction) are not specified here, and no claim of conformance to them can be made under this document.

| Role | Rules | Maturity |
|---|---|---|
| Emitter | {{canonical}}, {{scope}}, {{absence}}, {{earned}} | Specified; schema and signatures open |
| Stream verifier | {{canonical}}, {{results}} | Specified; reproduced by four parties |
| Anchor verifier | {{anchoring}}, {{results}} | Two profiles in full, one summarised; all three demonstrated |
| Profile evaluator | {{results}}, {{evaluation}} | Specified; authors' implementations only |
| Reader | {{absence}}, {{results}}, {{evaluation}} | Specified as reporting rules |
{: title="Conformance targets"}

Conformance under this document is per mechanism. An implementation can state that it conforms to the canonical form, to stream verification, to anchor verification under a named profile, or to profile evaluation, each against that mechanism's vectors ({{vectors}}). Because the envelope schema is open, no implementation can claim to be a conforming AXES emitter as a whole. A relying party chooses its own requirement profile and is not a conformance target.

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
* time: `occurred_at` (when the event happened), `emitted_at` (when the emitter produced the record) and `recorded_at` (when it was persisted), together with `timestamp_source` and a clock-synchronisation confidence;
* placement: organisation, tenant and environment identifiers, `trace_id`, `span_id`, and a monotonic sequence number within the stream;
* the action and its authority: `actor`, `authority`, `operation`, `execution_phase` and `execution_mode`;
* epistemic status: `evidence_quality` (`evidence_origin`, `assertion_basis`, `corroboration_state`);
* privacy: classification and the pseudonymous references used for people;
* `integrity`: the canonicalisation identifier, hash algorithm, previous envelope hash, signing key identity, envelope hash and envelope signature.

Envelopes can carry a namespaced `extensions` object, which lies inside the hash scope like every other member ({{canonical}}).

Every numeric quantity inside the hash scope is exact ({{domain}}). Asset-denominated quantities use an Amount object: `value` is a string of base-10 integer atomic units, `decimals` is the declared scale, and `asset` is a namespaced string (`iso4217:<code>` {{ISO4217}} for fiat, `caip19:<asset id>` {{CAIP-19}} for crypto-assets). Ratios that must be recorded use exact rationals (`numerator`, `denominator`, both integer strings). Derived ratios, such as how much of a delegated limit was used, are not stored; they are computed from their operands when a report is produced.

# Canonical Form and Hashing {#canonical}

## Canonical byte form

The canonical byte form of an AXES JSON object is the output of the JSON Canonicalization Scheme {{RFC8785}}. The input MUST be I-JSON {{RFC7493}}; in particular, an object with duplicate member names MUST be rejected rather than canonicalised.

The identifier `RFC8785-JCS`, carried in `integrity.canonicalization_version`, denotes exactly the following, and nothing else:

* the RFC 8785 JSON Canonicalization Scheme at its published revision;
* output as UTF-8 bytes;
* object members sorted by UTF-16 code units (RFC 8785 Section 3.2.3), not by code point and not by any locale collation;
* no Unicode normalisation (RFC 8785 Section 3.1), so the NFC and NFD forms of the same visible key are distinct members;
* the digest algorithm is declared separately (`integrity.hash_algorithm`) and is not implied by this identifier.

A second implementer MUST be able to reproduce the canonical bytes from this statement alone. A change to any property above defines a new identifier; `RFC8785-JCS` is never redefined. Independently of the identifier, every digest in AXES is written as bare lowercase hexadecimal with no algorithm prefix.

## Value domain {#domain}

Inside the hash scope:

* a JSON number with a fractional part, or a non-finite value, MUST NOT appear;
* a JSON integer, such as `sequence_number`, MUST lie within -(2^53 - 1) to 2^53 - 1, which every RFC 8785 implementation represents exactly; a larger integer is carried as a base-10 string;
* timestamps are strings in UTC under RFC 3339 {{RFC3339}}, with exactly three fractional digits and the suffix `Z` (for example `2026-06-09T09:01:00.400Z`);
* an `extensions` object MUST NOT override any member defined by AXES.

A verifier that meets a fractional, non-finite or out-of-range number inside the hash scope, or input that is not I-JSON, reports `contradicted` (`value_outside_domain`); it does not round, convert or canonicalise the value.

## Envelope hash

The envelope hash is computed as follows:

1. Remove `integrity.envelope_hash` and `integrity.envelope_signature` from the envelope.
2. Canonicalise the remaining object under the identifier in `integrity.canonicalization_version`.
3. Apply the algorithm named in `integrity.hash_algorithm` to the canonical bytes.
4. Encode the digest as bare lowercase hexadecimal.

Every other member of the envelope is inside the hash scope, including `envelope_id`, `recorded_at`, `integrity.signing_key_id` and `integrity.previous_envelope_hash`.

The digest algorithm is agile. The published corpus uses SHA-256 {{FIPS180-4}}. An implementation MAY use another algorithm over the same canonical bytes, provided that `integrity.hash_algorithm` names it. A verifier that does not implement the named algorithm, or the named canonicalisation identifier, MUST report the check as not evaluated, reason `instrument_failure`, condition `hash_algorithm_unsupported` ({{results}}), never as verified or contradicted, and MUST NOT substitute another algorithm. The same applies when either member is absent: a verifier does not assume SHA-256 or RFC 8785.

## Hash chain {#chain}

Each envelope in a stream carries `integrity.previous_envelope_hash`, the envelope hash of the envelope immediately before it in the stream. The first envelope in a stream carries a string of the character "0" as long as a hexadecimal digest of the stream's algorithm: sixty-four zeros for SHA-256. Every envelope in a stream MUST use the same `integrity.hash_algorithm`. Moving a stream to another algorithm is not specified ({{open-issues}}). The first envelope has sequence number 1, and each later envelope's sequence number is one more than its predecessor's. The chain head is the envelope hash of the last envelope in the stream. This document does not define a stream identifier; in the corpus each bundle holds one stream.

A verifier recomputes every envelope hash, checks that each `previous_envelope_hash` equals the recomputed hash of its predecessor, and checks that sequence numbers within the stream are contiguous. A recomputed hash that differs from the stored `integrity.envelope_hash` is a contradiction (`envelope_hash_mismatch`). A broken link is a contradiction (`chain_break`). A gap in the sequence numbers is indeterminate (`sequence_gap`): something is missing, but the chain alone cannot say why.

## Bundle manifest digest

A bundle is a set of files: the envelope stream plus the artefacts its envelopes reference. Its manifest maps each file path, using forward slashes and relative to the bundle root, to the lowercase hexadecimal SHA-256 of that file's bytes. The manifest file itself is excluded. The bundle manifest hash is the SHA-256 of the RFC 8785 bytes of that mapping, a single JSON object whose member names are the paths and whose values are the file digests. File digests are over the file bytes exactly as stored, with no canonicalisation. A verifier can check a bundle by recomputing every file digest and the manifest hash, without running any software supplied by the emitter. It resolves every path inside the bundle and does not read a path that is absolute, contains `..` or a backslash, or leads outside the bundle through a link (`bundle_path_unsafe`, contradicted). A changed file is contradicted (`bundle_file_hash_mismatch`), a listed file that is not present is indeterminate (`bundle_file_absent`), and a recomputed manifest hash that differs from the stated or pinned one is contradicted (`bundle_manifest_hash_mismatch`).

# Hash Scope Discipline {#scope}

A digest whose scope is narrower than what a reader consumes leaves a region that can be changed while the record still verifies. AXES therefore treats the hash scope as a declared, reviewable part of the record. This section states the current AXES position, which is published for challenge. In the published corpus the hash scope is fixed by {{canonical}} and no per-envelope declaration is carried. The rules below govern any declaration or exclusion added later.

1. Scope defaults to inclusion. Every member is inside the hash unless an exclusion is declared.
2. Every exclusion MUST name a reason from a closed vocabulary (`hash_scope_exclusion_reason`). The two exclusions in force, `integrity.envelope_hash` and `integrity.envelope_signature`, have the reason `self_referential`.
3. Sensitivity of a value MUST NOT be used as a reason to exclude it from the hash scope. Until the redaction construction is specified ({{redaction}}), a sensitive value is kept out of the envelope and referenced by digest; once it is, such a value will be committed at emission and disclosed selectively.
4. A declaration of the hash scope, when carried, MUST be inside the hash scope it declares. Otherwise an attacker could edit the declaration to exclude a field, change that field, and leave both the digest and the declaration valid.

Three states that are easily confused MUST remain distinguishable to a reader:

| State | Inside the hash | What a verifier can say |
|---|---|---|
| Excluded at signing | No | Nothing about whether the present value is original |
| Redacted after signing | Yes, committed at emission | The withheld value still binds; a tombstone shows it was present |
| Absent | Never captured | The value was not recorded |
{: title="Excluded, redacted and absent"}

## Redaction direction {#redaction}

AXES has chosen the direction for redaction after signing: salted per-field hash commitments, the approach established by SD-JWT {{RFC9901}}. This section records the direction and the constraints that led to it. The exact construction is an open issue ({{open-issues}}) and nothing here is yet normative.

Any mechanism for AXES must meet the following constraints:

* every reader can recompute the envelope hash, whatever they were shown, so the chain verifies for a redacted export;
* there is one digest per envelope, so chain heads and anchored release statements never change;
* preimages are byte-defined under RFC 8785, with no second canonicalisation;
* the cryptography is hash-only where possible, with a small verifier;
* a withheld field leaves a visible tombstone, distinguishable from a value never captured;
* an exporter, an auditor or an escrow can redact without the emitter's key;
* low-entropy values (amounts, booleans, short identifiers) cannot be guessed from their digest;
* nested objects and arrays can be redacted;
* unlinkability across presentations is not required, because evidence records are meant to link;
* an envelope with nothing redactable hashes exactly as it does today.

Salted per-field commitments meet all of them. Each value marked redactable at emission is represented inside the hashed envelope by a digest over a salt, the field name and the value; the salt and value travel separately as a disclosure. Withholding the disclosure leaves the digest in place. The envelope hash, the chain and every anchor therefore verify whether or not a disclosure is shown, and any holder of the envelope can redact by dropping a disclosure. Fields not marked redactable are hashed exactly as they are now, so every digest published for the corpus of record stays valid. The same approach is used by SD-JWT, by ISO mdoc {{ISO18013-5}} and by digital identity wallets, and has been applied to RFC 8785 JSON for agent action records {{I-D.mih-scitt-agent-action-capsule-sel-disc}}. AXES adopts the approach, not the SD-JWT wire format: RFC 9901 hashes the base64url encoding of a disclosure array, whereas an AXES disclosure will be defined by its RFC 8785 bytes, so that no second encoding enters the hash scope. Byte compatibility with SD-JWT disclosures is not a goal. A Merkle-structured envelope was considered and not chosen, because it changes how every envelope hash is computed and brings no property AXES needs that salted commitments lack.

Disclosable values are committed with salts that travel in the disclosure, not with a key held by the record holder, so that any authorised reader can check a disclosed value without trusting whoever holds the data. Stable keyed pseudonyms remain the mechanism for linking records about the same person ({{privacy}}).

# Capture Boundary and Honest Absence {#absence}

An emitter declares a capture boundary: the kinds of action, and the scope, for which it commits to producing an envelope every time. Within a declared boundary the emitter fails closed: if it cannot produce the envelope, the action does not proceed past the commit boundary. An action that proceeds without its envelope has left the declared boundary, and the emitter discloses it as soon as it can emit again (`capture_status`, {{vocabularies}}).

The declaration is a claim by the emitter. It does not show that the emitter enforced it: an emitter can bypass its own hook or act through a path the hook does not see. The absence of an envelope within the boundary therefore supports the finding that no such action crossed the commit boundary only to the extent that enforcement of the boundary, over the period in question, is established by evidence from outside the emitter's records, for example counterparty acknowledgements or an independent gateway. A reader MUST NOT report from absence alone that no action occurred; without that evidence, it reports absence as `indeterminate`. Outside the boundary, absence means only that nothing was captured.

When a value that a reader might expect is not present, the envelope SHOULD say why, by listing it in `field_absences` with an `absence_reason_code`. This list is defined in the AXES vocabularies and is not yet exercised in the published corpus. The reason codes are:

* `not_applicable`: the value does not apply to this event;
* `not_captured`: the emitter did not capture it;
* `withheld`: the value exists and is held back by the operator;
* `redacted`: the value is committed and not disclosed to this reader.

`withheld` and `redacted` MUST NOT be read as absent. An event outside the declared boundary is disclosed as `outside_capture_boundary`. That is an honest statement of scope, not a failure.

A reader asked whether qualifying evidence exists returns a bounded finding. "No qualifying evidence was found in the declared sources by the stated cut-off" is a valid, verifiable finding. It is different from "the sources could not be read", and both are different from "verified". Registration of a record in a log, or anchoring of its digest, shows that the registered digest existed by the time of registration. It shows that the log has not presented conflicting histories only where the log also supplies a consistency proof and the reader checks it. It does not show that the set of records is complete, or that the recorded event occurred as described.

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
* `anchor_proof_ref` points to a proof manifest that lists every proof file with its digest, and `anchor_proof_hash` is the SHA-256 of the manifest file's bytes as stored. A reference is resolved only inside the bundle that carries the block; a reference that leads outside it is not read. A missing reference is indeterminate, attributed to the operator (`anchor_proof_absent`). A reference that cannot be retrieved at audit time is not evaluated, attributed to the network (`anchor_proof_unresolvable`). An altered proof file is contradicted (`anchor_proof_hash_mismatch`).
* An anchor that has been requested but not yet attested (it has `anchor_requested_at` and no `anchored_at`) is indeterminate (`anchor_pending`).
* A verifier that lacks the library, binary or procedure for a method MUST report not evaluated, reason `instrument_failure`, condition `anchor_method_unverifiable`, subject `verifier`. This is never a pass and never a finding about the anchor.
* Where a block carries several anchors over one subject, each anchor yields its own result. A verifier never merges them and never reports only the strongest. A disagreement between anchors, such as times further apart than the mechanisms can explain, is reported, not resolved.

## Published profiles

`axes:rfc3161_sha256_imprint@1`:
: The subject's SHA-256 is the message imprint of an RFC 3161 timestamp request. Verification checks that the token's `messageImprint` is that digest, verifies the token's signature against the TSA certificate chain supplied in the proof bundle, and checks that the token's serial equals `anchor_record_ref` and its `genTime`, in UTC truncated to whole seconds and written as `.000Z`, equals `anchored_at`. This establishes that the named TSA signed the digest at the stated time under that chain. Whether that chain is trusted is the relying party's decision.

`axes:opentimestamps_sha256_digest@1`:
: The subject's SHA-256 is submitted to OpenTimestamps calendars and, once mined, attested by a Bitcoin block header. Verification replays the proof from the digest to the header's Merkle root and checks the header's proof of work against its own target. `anchor_record_ref` is `block:<height>:<hash>`: the height is the one stated in the proof's Bitcoin attestation and the hash is the header's; `anchored_at` equals the header's time. A header does not contain its height, so the height, and membership of the block in Bitcoin's main chain, are confirmed by a separate lookup by block hash against any Bitcoin node. The anchor shows that the digest existed by that block's time, an upper bound; it says nothing about when the record was first made. `anchor_service_id` names the chain as a CAIP-2 identifier {{CAIP-2}}.

A third profile, `axes:anchor_registry_bytes32@1`, covers a permissionless on-chain registry. It checks offline that the anchoring transaction's receipt sits under the block's receipts root and that the block header hashes to the block hash. Whether the block is on the chain's canonical history is a single lookup by block hash. Such a registry has no operator: the contract has no owner, roles or custody, and the submitter is recorded in the event but holds no privilege. For it, `anchor_operator_id` is null, and independence is a property of the chain's consensus, not of whoever submitted the anchor. The gt-v2.1 release anchor on Base was submitted by a reviewer from their own wallet ({{impl-status}}). A profile for transparency logs that issue COSE Receipts {{RFC9942}} under the SCITT architecture {{RFC9943}} is planned ({{open-issues}}). AXES does not depend on SCITT: `transparency_log` is an anchoring method class, and a SCITT receipt is one way to fill it.

The three mechanisms answer the same question with different trust. Their properties, as recorded by their operators and reviewers in {{X402-TSC4}}, are:

| Property | RFC 3161 | OpenTimestamps | AnchorRegistry |
|---|---|---|---|
| Trust | The TSA's key and chain | Bitcoin proof of work; calendars can delay, not forge | The chain's consensus; no owner or roles |
| Offline check | Token and TSA chain | Upgraded proof and block header | Receipt proof and block header |
| Finality | At issuance | At the attested block; pending before | The chain's own |
| Cost | Free at public TSAs, rate limited | No fee per digest | Gas per anchor, no batching |
| Submitter recorded | No | No | Yes, without privilege |
{: title="Properties of the published anchoring mechanisms"}

## Earned strength {#earned}

`evidence_quality.corroboration_state` has an ordered set of values ending in `externally_anchored`. That value MUST NOT be asserted unless at least one anchor over the subject verifies under the rules above. A record that asserts `externally_anchored` over an anchor that is simulated or stubbed is contradicted (`anchor_simulated_claims_external`). An anchor that verifies but whose operator is not shown to be independent of the executor and deployer is indeterminate (`anchor_independence_unproven`). An anchor run by the emitter's own organisation does not show independence.

Three questions are kept apart. Whether the proof binds the digest is answered by the profile's verification procedure. Whether the operator is independent of the executor and deployer is a separate result. Whether the relying party accepts the mechanism and its trust chain is the relying party's decision, recorded in its requirement profile, and is never asserted by the record.

# Verification Results {#results}

Every check a verifier or evaluator performs yields exactly one result, using the four-state vocabulary of {{I-D.krausz-verification-state}} under AXES key names:

`verification_state`:
: `verified`, `contradicted`, `indeterminate` or `not_evaluated`.

`verification_reason_code`:
: `divergence` (two values that should agree do not), `absence` (something needed is missing) or `instrument_failure` (the verifier could not perform the check). The member is absent when no reason applies, always for `verified` and for some `not_evaluated` results ({{vocab-conditions}}).

`verification_subject_type`:
: Whom the result is about: `artifact` (the record), `operator` (whoever produced or holds it), `network` (retrieval at audit time), `verifier` (the checking tool) or `access` (the reader's entitlement).

`verification_condition_code`:
: One value from a closed list that names the class of condition, for example `chain_break`, `sequence_gap` or `anchor_pending`. The specific cause is recorded in free text (`observed_note`) and is not part of the closed vocabulary.

The following rules apply:

1. A check that could not be performed is `not_evaluated`. It MUST NOT be reported as `verified`, and it MUST NOT be reported as a finding against the record.
2. A check that was performed and found something missing is `indeterminate` with reason `absence`. Absence is never collapsed into a pass.
3. `contradicted` is reserved for evidence that disagrees with itself or with what it asserts.
4. When the parties to an exchange computed different values for what should be the same digest, the result is `indeterminate` with reason `divergence`. The verifier MUST NOT pick a side.
5. A verifier reports a result for every input it was given. An input that breaks a rule of this document, such as a malformed timestamp, is `contradicted`; one the verifier lacks the capability to read is `not_evaluated`. A verifier never stops without reporting.

Rules 3 and 4 differ in what the verifier holds. Under rule 3 it recomputes a value from the preimage a record states and compares it with the digest the same record commits to: the record contradicts itself. Under rule 4 two parties supply conflicting commitments and nothing in the evidence gives either precedence, so the dispute stays open.

# Requirement Profiles and Evaluation {#evaluation}

What counts as sufficient evidence depends on who is relying on it. An auditor, a tax authority and a counterparty can reasonably require different things of the same record. AXES therefore puts sufficiency outside the record.

A requirement profile is a JSON document that names its purpose, the subject type it applies to, and a list of requirements. Each requirement has a check type (for example `field_presence`, `chain_integrity`, `sequence_continuity`, `anchoring` or `settlement_commitment`) and an obligation (`required`, `conditional`, `optional` or `prohibited`).

* A profile is immutable at `id@version`. Its digest is the SHA-256 of its canonical bytes, computed by the evaluator from the bytes it executed. An evaluator refuses a profile set in which two documents claim the same `id@version` with different content.
* Reference profiles use the `axes:` namespace. Anyone MAY publish profiles under their own namespace.
* A profile MAY extend others. Where the same requirement appears with different obligations, whether in a profile and one it extends or in two profiles it extends, the stricter wins in the order `prohibited`, `required`, `conditional`, `optional`, except that `required` against `prohibited` cannot both hold and is a conflict whatever the order. A requirement marked as a floor cannot be relaxed by an extending profile. A conflict, including an extension cycle, is `indeterminate` (`profile_conflict`), never a silent choice. An extended profile that is not available is `not_evaluated` (`profile_unsupported`), and so is a resolved profile with no requirements; neither can give `verified`.
* The digest of a profile covers that profile only. When it extends others, the evaluation record lists the digest of every profile in the resolved set (`requirement_profile_closure`), so that a reader who pins a profile can check which parent content was applied.
* A profile lists the readings it deliberately leaves unpinned.

Evaluation applies one profile to one subject and yields an evaluation record. Each requirement gives one result in the vocabulary of {{results}}. The overall state is:

1. `contradicted`, if any requirement is contradicted;
2. otherwise `indeterminate`, if any requirement is indeterminate or not evaluated;
3. otherwise `verified`.

The overall state summarises; it does not replace. The evaluation record MUST keep the result of every requirement, so that a reader can tell a requirement that was checked and found wanting (`indeterminate`) from one that was not checked (`not_evaluated`). The result is described as unconditional only when every requirement is verified with no condition recorded.

Obligations are applied as follows. A field required by the profile and absent gives the result its declared absence reason implies, or `indeterminate` (`field_absent_undeclared`) when no reason is declared. An absent `optional` field does not lower the overall state; an `optional` field that is present is checked like any other, and a contradiction found in it counts toward the overall state. A `prohibited` field that is absent is verified, and one that is present is `contradicted` (`prohibited_field_present`). A `conditional` requirement applies only to the envelopes for which its condition holds. If it holds for none, the requirement is verified with condition `condition_not_exercised`, so the guarantee is conditional: a safeguard that was never exercised is not reported as demonstrated.

Evaluation MUST be deterministic. It uses no model, no network access and no clock reading. External facts enter only as pinned evidence that records when the external authority answered. Two evaluators given the same subject, profile set and pinned evidence MUST produce the same result digest (`result_core_hash`). Its preimage is the evaluation record without `result_core_hash` itself and without the members that identify the run rather than its findings (`evaluation_id`, `evaluator_id`, `evaluator_version`, `evaluated_at` and `requirement_profile_closure`), as RFC 8785 bytes; the digest is SHA-256. Results appear in the order in which the profile set resolves (inherited requirements first), and `observed_note` is part of the preimage.

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

  * RFC 3161, FreeTSA, serial 0x09216E25, 2026-10-12T10:12:28Z.
  * OpenTimestamps, Bitcoin block 971082.
  * A permissionless on-chain registry (AnchorRegistry, contributed by giskard09) on Base, block 52987624, 2026-10-23T14:09:55Z, submitted by giskard09 from their own wallet. This verifies under the profile `axes:anchor_registry_bytes32@1`: the transaction receipt is proven under the block's receipts root, and the block header hashes to the block hash.

: All three proofs verify offline against the evidence supplied with them. That the Bitcoin and Base blocks are on their chains' canonical history is a separate check that needs the network.

Independent reproduction:
: The gt-v2.1 digests have been reproduced by four parties other than the authors, all recorded in the repository's release register.

  * giskard09: byte check, regeneration and reference verifier.
  * robertolocatelli81-dev: from the specification text only, with an independent canonicaliser and no AXES code.
  * MarkovianProtocol: an independent canonicaliser in two languages; all 76 envelope hashes in each bundle match.
  * babyblueviper1: from the specification text only, with an independent canonicaliser, the standard library and no AXES code. It covered every envelope hash, chain link and file, both chain heads and both bundle digests, but not the release anchors. This check also found that the hash-scope text published with the tag disagreed with the corpus about `recorded_at`. The text was corrected after the tag; the corpus was the reference and did not change.

: These are independent reproductions of the canonical form, hash scope and chain over published data. They show that the byte rules of {{canonical}} are implementable from the text. They are not independent implementations of the whole of AXES: one of them also checked the release statement's RFC 3161 token, and profile evaluation has so far been implemented only by the authors.

Cross-format checks:
: The repository's RFC 8785 property vectors agree with an independent RFC 8785 implementation. Its x402 correlation recipe partitions a third-party payment-fingerprint vector set identically to that set's own recipe.
: The AXES tooling independently recomputes the 13 v1 and 6 v2 conformance vectors of {{I-D.etcheverry-action-ref}} (every verdict, and every reject reason for v1), and verifies offline the AnchorRegistry anchor used by that draft's reference implementation. draft-etcheverry-action-ref-04 lists the AXES reference tooling in its own Implementation Status section on this basis.
: For the salted authorisation commitment proposed for x402 receipts, the authors contributed 29 receipt-level vectors and a checker written from the specification text alone to a third-party conformance repository, merged on 2026-10-23 {{PGC-17}}.

Checks on this document:
: The worked example ({{worked-example}}), the CDDL ({{cddl}}) and the condition-code table ({{vocabularies}}) are checked against the corpus and the reference tools by `ietf/check_appendices.py` in {{AXES-REPO}}, which continuous integration runs together with a rebuild of this document on every change.
: A separate validation run on 31 October 2026, automated and commissioned by the author, rebuilt the document from a fresh checkout, reran every check and recomputed all 152 envelope hashes with a second, standard-library implementation. All passed. Its adversarial probes found seven defects in the reference tooling, among them an unsupported digest algorithm that verified and an unresolvable profile set that verified.
: A second run the same day, against the fixed tooling and the SDK installed from its built package on Windows and Linux, found three of those fixes incomplete and four further defects. The reference evaluator applied strictest-wins only between a profile and its own requirements, not between two profiles it extends. The reference hash helper excluded both signature member names under either release. The SDK could evaluate envelopes other than the bytes whose digest it recorded, and its manifest path and some input limits were not enforced. Each finding from both runs is fixed, with a regression test, and the rules they touched are stated in {{canonical}}, {{domain}}, {{anchoring}} and {{evaluation}}. No published digest or evaluation record changed. Two design points it raised remain open: pinning the key-alias table alongside the profiles, and bounding the work of resolving a large profile graph.

Python SDK:
: `axes-sdk` 0.1.1 {{AXES-SDK}} packages strict ingestion, stream and bundle verification, deterministic profile evaluation and a command-line tool for use outside the repository. Its tests reproduce the reference results on the corpus of record, the published evaluation records and the profile vectors. It is written by the authors from the reference tooling, so it is not an independent implementation.

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

# Binding to Carrying Protocols {#bindings}

This section is informative. It describes the direction for binding an AXES record to the protocol that carried the action (item 8 in {{open-issues}}).

An AXES record sits beside the carrying protocol and binds to that protocol's artefacts through a named, versioned and immutable binding profile, identified as `<namespace>:<lower_snake_name>@<version>` in the same way as anchor and requirement profiles. A binding profile declares:

* the protocol and the version of it that it binds;
* the protocol artefacts it references, each hashed exactly as received and never re-serialised;
* for each field it uses, whether the field is never redactable, disclosable by role (committed with a salted commitment, {{redaction}}), or kept out of the record and referenced by digest;
* a verification procedure with two-sided vectors ({{vectors}}).

Binding profiles add or tighten requirements. They never relax a core rule and never make a never-redactable field redactable. A record may carry several bindings, for example a payment binding and an authorisation binding for the same action. A reader that does not implement a profile reports the binding as not evaluated (`profile_unsupported`), never as verified. Protocol owners may publish binding profiles under their own namespace.

AXES separates three layers: the evidence record (layer 1), the binding of a record to the carrying protocol (layer 2) and an existence anchor (layer 3, {{anchoring}}). A carrying protocol needs only layer 2: a digest, an algorithm label, a record type and a join key.

The first binding is to x402 {{X402-TSC4}}. The published correlation record (`axes:x402_correlation@1`) binds evidence to an x402 payment by digest and is checked against public vectors from the x402 community. A profile for the x402 payment anchor, including the salted authorisation commitment proposed for x402 receipts {{PGC-17}}, is in preparation. Several agent payment-mandate and intent protocols carry SD-JWT credentials. Because AXES commitments follow the same approach ({{redaction}}), a binding can reference such a disclosure by its digest, as received, without translating it. Identifiers for further bindings are reserved in the binding profile catalogue of {{AXES-REPO}}.

# Operational Considerations {#operations}

Key custody and rotation:
: Envelope signatures are not yet specified ({{open-issues}}), but every envelope already carries `integrity.signing_key_id` inside its hash scope. Signing keys SHOULD be held outside the emitter's application process, for example in a hardware or managed key service, and each key's provenance SHOULD be referenced (`integrity.signing_key_provenance_ref`). Rotation creates a new key identifier and never invalidates records made under an earlier key. The same rule applies to salt sources and pseudonym keys.

Anchoring cadence:
: Until a stream is first anchored externally, its emitter can rewrite it wholesale. After that, it can rewrite only the envelopes emitted since the latest anchor, because anchoring a chain head commits every earlier envelope. The interval between anchors is therefore the window in which rewriting cannot be detected. Deployers SHOULD declare the interval, choose it from what their relying parties need, and anchor at every commit boundary of high consequence.

Omission:
: Once envelope signatures are specified, `sequence_number` and `integrity.previous_envelope_hash` sit inside a signed payload. An omitted envelope then shows as a sequence gap or a chain break, and repairing it means re-signing the stream, which contradicts any chain head already anchored. Omission becomes detectable in practice only together with heartbeats at a declared interval, an explicit close of each stream that states its final sequence number, regular anchoring and, where possible, a counterparty that records its own side of the exchange. None of these detects an action that the emitter never captured ({{absence}}).

Redaction:
: When the construction is specified ({{redaction}}), each salt is expected to carry at least 128 bits from a cryptographically secure random source and to be used for one commitment only. Fields must be marked redactable when the envelope is emitted. The number of commitments in an envelope is visible unless decoy digests are added. Disclosures, with their salts, must be kept for as long as the envelope may be relied on; destroying them is how a value is erased ({{privacy}}).

Retention:
: Envelopes are kept for at least as long as any record in the stream may be relied on, which for financial records can be longer than the limitation period of the obligation they evidence. Clear values are never kept longer than the envelopes that commit to them. Retention classes, production on demand and successor custodians are open issues.

Offline verification:
: The reference verifier and anchor verifier run offline from a bundle. A check that needs the network, such as whether a block is on a chain's canonical history or whether a proof can be retrieved, is reported as not evaluated when the network is unavailable, never as verified.

# Open Issues {#open-issues}

The following are known gaps. Reviews and counter-proposals are welcome.

1. Redaction-tolerant hashing. The intended direction is salted per-field hash commitments, the approach of SD-JWT {{RFC9901}} with an RFC 8785 disclosure encoding ({{redaction}}). Each value marked redactable at emission is represented inside the hashed envelope by a digest over a salt, the field name and the value; the salt and value travel separately as a disclosure. The envelope hash, the chain and every anchor then verify whether or not a disclosure is shown, an envelope with no redactable field hashes exactly as it does today, and any holder can redact without the emitter's key. Open: the byte form of the disclosure under RFC 8785, salt length and encoding, nested objects and array elements, decoy digests, and which fields each module marks redactable. Before the construction is normative it needs two-sided vectors for nested objects, arrays, duplicate disclosures, missing and altered salts, a disclosure substituted from another envelope, and low-entropy values. This gates the envelope schema.
2. The full envelope JSON Schema and field catalogue (two of sixteen planned modules are published for challenge). Key names in the published corpus and in the catalogue have not yet been reconciled in every case.
3. The extension model: how a reader processes an extension it does not understand (`must_understand`, `unknown_field_policy`). Extensions are already inside the hash scope.
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
14. Digest algorithm migration: how a long-lived stream, its anchors and its evaluation records move to a new digest algorithm while earlier digests stay verifiable.

# Security Considerations

Three properties are distinct, and none implies another:

* Integrity: the bytes a reader holds agree with the committed digest. This document specifies it.
* Authenticity: a named identity or key produced or endorsed those bytes. It needs the envelope signature profile, which is open ({{open-issues}}); the corpus signatures are stubs. Anchoring the digest of a fabricated record does not authenticate its claims.
* Completeness: the relevant population of actions is represented. It is bounded by {{absence}} and is never shown by integrity or anchoring alone.

No statement made under this document implies all three.

The emitter may be the adversary:
: An envelope records what was claimed, by whom, under which authority and with what corroboration. It does not prove that the agent or the emitter behaved honestly. Self-declared values are not authenticated by being in the hash scope. Fields that record independence or custody MUST NOT be read as established by the record itself.
: In particular, the `authority` fields are claims that an authority existed and was relied on. Verifying that authority needs a grant, credential or policy version that can be checked outside the record, with its scope and validity at the commit boundary. Binding authority to a legal person is open issue 12.

Scope narrower than consumption:
: If a reader consumes a field that the digest does not cover, that field can be altered while the record verifies. {{scope}} makes inclusion the default, requires a reason for every exclusion, and puts the scope declaration inside its own scope. Implementers MUST NOT read fields from outside the declared hash scope as authenticated.

Canonicalisation differentials:
: Two verifiers that accept different inputs, or that canonicalise the same input differently, can reach different verdicts on the same bytes. {{canonical}} therefore requires I-JSON input, sorting by UTF-16 code units and no Unicode normalisation, and {{domain}} forbids fractional numbers and integers outside the exactly representable range. A general-purpose RFC 8785 library may accept such values silently; an AXES verifier checks the domain before it canonicalises.

Digest labels:
: Because the digest algorithm is agile, a digest is meaningful only together with its algorithm label. A verifier MUST NOT compare digests whose algorithm labels differ.

Simulated or self-held anchors:
: A simulated anchor, or one held by the emitter's own organisation, gives no independent existence bound. {{earned}} makes the strong claim depend on verification. Relying parties decide whether to trust a timestamp authority's certificate chain. A Bitcoin header's proof of work does not by itself show main-chain membership.

Registration is not completeness:
: An inclusion proof, a time stamp or a ledger record shows that a digest was committed. It does not show that every relevant record was committed, or that the recorded event occurred as described. Readers MUST NOT report completeness from anchoring alone.

Absence:
: An attacker who can suppress envelopes can make evidence absent. Sequence continuity, heartbeats, fail-closed emission within a declared boundary and the distinction between withheld, redacted and never captured exist so that suppression is visible as `indeterminate` rather than invisible.

What this specification cannot detect:
: This section states the limits, so that readers infer no more than a record supports.

  * An emitter that controls capture can omit actions outside its declared capture boundary, and nothing in the record shows them.
  * Until envelope signatures are specified ({{open-issues}}), an emitter can rewrite its own stream wholesale before the stream is first anchored externally. Anchoring bounds that window to the interval between anchors.
  * A completeness or count field computed by the party that holds the record is a claim by that party, not evidence of completeness.
  * Registration in a log or on a ledger shows that what was registered existed by that time. It shows that the log presented one history only with a consistency proof that the reader checks, and never that every relevant record was registered.


# Privacy Considerations {#privacy}

Envelopes carry references and digests, not payloads. People (approvers, operators, customers, employees) are referenced by pseudonymous keys and are never embedded. Erasure is supported by destroying referenced content, so the envelope keeps its digest while the content is gone. A reader should report such content as erased rather than missing; that reporting outcome will be registered with the redaction construction ({{open-issues}}).

A digest of a low-entropy value can be reversed by guessing. Anchoring a digest publishes it permanently. Emitters SHOULD anchor only digests of high-entropy subjects (chain heads, bundle manifests, release statements) or salted commitments, and SHOULD NOT anchor digests of individual values that identify a person.

Identifiers scoped to one relying party deliberately produce different digests at different relying parties, which limits correlation of the same person across relying parties.

These measures reduce exposure. They do not by themselves make a record anonymous, establish compliance with any data-protection law, or make erasure effective in every legal setting. Pseudonymous identifiers, digests and metadata such as timing, counts and sequence can still allow a person to be re-identified or records to be linked, and a salted commitment protects the committed value from guessing, not the metadata around it.

Redaction after signing will use salted per-field commitments ({{redaction}}); the construction is not yet specified ({{open-issues}}). Until it is, sensitive values should be kept out of envelopes by reference rather than excluded from the hash.

The intended direction for sensitive data separates two planes. The chain plane holds envelopes: hashed, chained, anchored and never erased, and it never holds personal data in clear. A raw plane holds clear values, salts and referenced artefacts under a named custodian whose relationship to the emitter and deployer is recorded. Erasing a data subject's values destroys their raw-plane disclosures and keys: the commitments remain in the chain plane, cannot be reversed by guessing because they are salted, and the value is reported as erased rather than missing. Each re-disclosure of raw-plane values is itself recorded as evidence. These are proposed decisions in the AXES decision register {{AXES-REPO}} and are not specified by this document.

# IANA Considerations {#iana}

This document has no IANA actions.

AXES maintains the following registries in its public repository {{AXES-REPO}}. Each entry there is immutable and additive. A future revision may request IANA registries for some of them:

* canonicalisation identifiers (currently `RFC8785-JCS`);
* `anchoring_method` values;
* `anchor_profile_ref` identifiers and their verification procedures;
* `verification_condition_code` values;
* requirement profile identifiers in the `axes:` namespace.

--- back

# Worked Example {#worked-example}

This appendix lets a reader recompute one real envelope hash and one chain link from this document alone. The envelope is the ninth of the financial trace in the corpus of record {{AXES-GT21}} (line 9 of `examples/golden-trace/out/envelopes.jsonl`), a heartbeat event.

## The envelope

~~~
{::include appendix/envelope-0009-presented.txt}
~~~
{: title="Envelope 9 of the gt-v2.1 financial trace (line breaks inside strings are for presentation)"}

## Canonical bytes

Removing `integrity.envelope_hash` and `integrity.envelope_signature` ({{canonical}}) and applying RFC 8785 gives the following 2130 bytes. They are all ASCII and contain no space characters, so they are shown wrapped at 64 characters: join the lines with nothing between them.

~~~
{::include appendix/envelope-0009.jcs.txt}
~~~
{: title="RFC 8785 bytes of envelope 9 inside the hash scope"}

## Digest and chain link

The SHA-256 of these bytes, as bare lowercase hexadecimal, is

~~~
741e26e97a1e375f4eb1f007ab98ead5fd5bfb4e5c28092649c90acde6f38ab8
~~~

which equals the stored `integrity.envelope_hash`. The stored `integrity.previous_envelope_hash`,

~~~
52c2bfef03ba11c71b906b17e9105f3623c9918687f5eb7c6e218a670495a9f9
~~~

is the recomputed envelope hash of envelope 8, and envelope 10 carries the digest above as its own `integrity.previous_envelope_hash`. Sequence numbers 8, 9 and 10 are contiguous. Continuing the same computation to envelope 76 gives the financial chain head stated in {{impl-status}}.

The `integrity.envelope_signature` value is a stub (`envelope_signature_basis_status: stubbed`) and lies outside the hash scope, so it does not affect the digest. Once redaction is specified ({{redaction}}), this envelope, which has no redactable field, keeps exactly this digest.

## A changed value

Suppose a holder changes the authority this envelope relied on, replacing `"authority_context_ref":"AD-7844"` with `"authority_context_ref":"AD-7845"` (line 8 of the canonical bytes above). The byte count stays 2130, and the SHA-256 becomes

~~~
56baaf278e977fc76e3b52242bc4fe0c8d24c18bf467a5d472af3b1c93d36d17
~~~

which differs from the stored `integrity.envelope_hash`. A verifier reports `contradicted`, reason `divergence`, condition `envelope_hash_mismatch`, subject `artifact` ({{chain}}). If the holder also overwrites the stored hash with the new digest, envelope 10's `integrity.previous_envelope_hash` no longer matches it and the verifier reports `chain_break`. Hiding the change would mean rewriting every later envelope, which changes the chain head, and the chain head and release statement digests are anchored outside the emitter ({{anchoring}}).

# Data Definitions in CDDL {#cddl}

This appendix gives the settled structures of this document in CDDL {{RFC8610}}, applied to JSON. It is informative and checks shape only. The normative rules are in the sections named in each comment, and the conditions CDDL does not express are checked by those sections' procedures: that a digest has the length of its algorithm (64 hexadecimal characters for SHA-256), that the algorithm and canonicalisation identifier are supported, that a timestamp is a real instant, that a condition code is in the closed list of {{vocab-conditions}}, and that an anchor without `anchored_at` is pending. The envelope as a whole is not defined here, because its schema is an open issue ({{open-issues}}). The closed list of condition codes is in {{vocab-conditions}}.

These definitions accept every integrity block (152) and every anchoring block in the corpus of record, every release anchoring block and anchor verification result in {{AXES-REPO}}, and every published evaluation record. Each rule also rejects a copy of a real instance with one value broken. `ietf/check_appendices.py` in {{AXES-REPO}} runs these checks.

~~~ cddl
{::include appendix/axes.cddl}
~~~
{: title="AXES settled structures"}

# Vocabularies {#vocabularies}

The following vocabularies are used by this document. Values are `lower_snake`. Every list except `anchoring_method` is closed: a new value is added only in an announced release, and a value is never redefined or removed. Each list is maintained in {{AXES-REPO}} ({{iana}}).

`verification_state`:
: `verified`, `contradicted`, `indeterminate`, `not_evaluated` ({{results}}).

`verification_reason_code`:
: `divergence`, `absence`, `instrument_failure`.

`verification_subject_type`:
: `artifact`, `operator`, `network`, `verifier`, `access`.

`absence_reason_code`:
: `not_applicable`, `not_captured`, `withheld`, `redacted` ({{absence}}).

`capture_status`:
: `captured` (the only value in the corpus of record), `missing_recoverable`, `missing_irrecoverable`, `outside_capture_boundary` ({{absence}}).

`hash_scope_exclusion_reason`:
: `self_referential` (the only reason in force, for `integrity.envelope_hash` and `integrity.envelope_signature`); `recipient_stamped` and `syntax_mutable` are reserved and no exclusion uses them ({{scope}}).

`anchored_subject_type`:
: `chain_head`, `envelope`, `bundle_manifest`, `release_statement`.

`anchoring_method` (open):
: Seeded with `timestamp_authority`, `opentimestamps`, `transparency_log`, `distributed_ledger`, `write_once_store`. Other methods use `<namespace>:<id>` ({{anchoring}}).

`basis_status`:
: `demonstrated`, `stubbed`, `simulated`.

Requirement profiles and evaluation ({{evaluation}}):
: `check_type`: `field_presence`, `chain_integrity`, `sequence_continuity`, `anchoring`, `settlement_commitment`.
: `obligation_type`: `required`, `conditional`, `optional`, `prohibited`, in the strictness order `prohibited`, `required`, `conditional`, `optional`.
: Evaluation `subject_type`: `envelope`, `bundle`, `stream_window`, `release`.
: `guarantee_type`: `conditional`, `unconditional`.

## Verification condition codes {#vocab-conditions}

Each condition code names a class of condition and always appears with the same state, reason and subject. The specific cause is recorded in `observed_note`. "(none)" means that the reason member is absent or null. `legacy_unstructured_anchor` applies only to records of a release published before the structured anchoring block, and `anchor_status_in_method` to a block that writes a status into `anchoring_method`. The tables list the whole registry. Some codes are reported only under particular profiles, for example the payment-binding codes under x402 profiles.

| Condition | Reason | Subject |
|---|---|---|
| `condition_not_exercised` | (none) | `artifact` |
{: title="Condition codes with state `verified`"}


| Condition | Reason | Subject |
|---|---|---|
| `anchor_commitment_mismatch` | `divergence` | `artifact` |
| `anchor_proof_hash_mismatch` | `divergence` | `artifact` |
| `anchor_simulated_claims_external` | `divergence` | `artifact` |
| `anchor_noncanonical_contract` | `divergence` | `artifact` |
| `anchor_not_a_commitment` | `divergence` | `artifact` |
| `anchor_status_in_method` | `divergence` | `artifact` |
| `envelope_hash_mismatch` | `divergence` | `artifact` |
| `chain_break` | `divergence` | `artifact` |
| `value_outside_domain` | `divergence` | `artifact` |
| `bundle_file_hash_mismatch` | `divergence` | `artifact` |
| `bundle_manifest_hash_mismatch` | `divergence` | `artifact` |
| `bundle_path_unsafe` | `divergence` | `artifact` |
| `field_declared_not_applicable` | `divergence` | `artifact` |
| `prohibited_field_present` | `divergence` | `artifact` |
| `value_not_accepted` | `divergence` | `artifact` |
| `settlement_commitment_mismatch` | `divergence` | `artifact` |
| `cap_exceeded` | `divergence` | `artifact` |
| `correlation_hash_mismatch` | `divergence` | `artifact` |
{: title="Condition codes with state `contradicted`"}

| Condition | Reason | Subject |
|---|---|---|
| `anchor_pending` | `absence` | `operator` |
| `anchor_proof_absent` | `absence` | `operator` |
| `basis_not_demonstrated` | `absence` | `operator` |
| `anchor_independence_unproven` | `absence` | `artifact` |
| `legacy_unstructured_anchor` | `absence` | `artifact` |
| `sequence_gap` | `absence` | `artifact` |
| `bundle_file_absent` | `absence` | `operator` |
| `field_absent_undeclared` | `absence` | `artifact` |
| `field_absent_declared` | `absence` | `operator` |
| `value_below_minimum` | `absence` | `artifact` |
| `conflicting_evidence` | `divergence` | `artifact` |
| `identifier_unverified` | `absence` | `artifact` |
| `anchor_insufficient` | `absence` | `artifact` |
| `anchor_lag_exceeded` | `absence` | `artifact` |
| `profile_conflict` | `divergence` | `verifier` |
| `settlement_not_observed` | `absence` | `artifact` |
| `correlation_divergence` | `divergence` | `artifact` |
| `nonce_unbindable` | `absence` | `operator` |
| `binding_salt_absent` | `absence` | `operator` |
{: title="Condition codes with state `indeterminate`"}

| Condition | Reason | Subject |
|---|---|---|
| `anchor_proof_unresolvable` | (none) | `network` |
| `anchor_method_unverifiable` | `instrument_failure` | `verifier` |
| `hash_algorithm_unsupported` | `instrument_failure` | `verifier` |
| `field_withheld` | (none) | `operator` |
| `field_redacted` | (none) | `access` |
| `access_restricted` | (none) | `access` |
| `profile_unsupported` | `instrument_failure` | `verifier` |
| `predicate_unparseable` | `instrument_failure` | `verifier` |
| `value_ladder_unsupported` | `instrument_failure` | `verifier` |
| `check_type_unsupported` | `instrument_failure` | `verifier` |
| `evaluator_fault` | `instrument_failure` | `verifier` |
| `requirement_profile_hash_unpinned` | `instrument_failure` | `verifier` |
| `external_evidence_stale` | (none) | `network` |
{: title="Condition codes with state `not_evaluated`"}

# Acknowledgements
{:numbered="false"}

AXES has benefited from public review and contributions credited in its provenance record and decision register: Tersign (Kevin Zhang) for the independence and completeness disqualifications; giskard09 (Pablo Etcheverry) for action-ref, on-chain anchoring and the custody-ref reference implementation; neldan00077 (TrustLayers) for the custody axis; MarkovianProtocol for byte-identity vector methodology; Rul1an for the one-outcome-per-edge discipline and the hash-scope failure case; and robertolocatelli81-dev (Noûs) for specification-only reproduction of the corpus of record.

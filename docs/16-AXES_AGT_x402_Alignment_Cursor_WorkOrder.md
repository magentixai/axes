# AXES Alignment Work Order (for Cursor) - AGT #276 and x402 Identity/Discovery WG
 
**Repo:** `magentixai/axes` (the AXES open standard, SE v0.1 Public Working Draft).
**Implements:** every schema, vocabulary, register and documentation change arising from Microsoft's Agent Governance Toolkit discussion #276, the x402 Identity and Domain Discovery working groups, and the live external verification thread in AXES issue #6, as reviewed 15 August 2026.
**Revision:** v2, 15 Aug 2026. Corrected after reading AXES issue #6 in full: the independent canonicalisation run is **already complete**, which changes guardrail 1 and Task 12; Task 6 now extends an existing mechanism rather than creating one; five new tasks (14 to 18) come from findings in that thread.
**Self-contained:** all rationale, field shapes, worked examples and acceptance criteria are inline. **You do not need any other document.** People and issues are cited as context for commit messages and field notes, not as files to fetch.
**Conventions, enforced throughout:** British spelling. **NO EM DASHES anywhere in repo text.** Write **"Magentix AI"**, never bare "Magentix". Field keys are `lower_snake`. Enum values are `lower_snake`.
 
**Branch note.** Two branches are live: the default branch, and `golden-trace-v2` at commit `776cc0b`, which is the commit three external parties have verified. **Do all catalogue, vocabulary, register and documentation work on the default branch.** Anything touching the corpus bytes is Task 12 and is gated. If the branch strategy for merging `golden-trace-v2` is unclear, stop and ask Martin rather than guessing.
 
---
 
## 0. NON-NEGOTIABLE GUARDRAILS (read first, apply throughout)
 
### Guardrail 1 - The corpus is already independently verified. Changing it is a versioned supersession, not a private edit.
 
This is the single most important fact in this work order, and it is easy to get wrong.
 
**Three external parties have completed and published verification against `golden-trace-v2` at `776cc0b`:**
 
- **Colin H Winter (`MarkovianProtocol`), twice.** 7 Aug: canoncheck two-sided, all 152 envelopes (fin + ind) canonicalise byte-identically in Python and Node, every digest matches the stored `envelope_hash`, chains verify, clean regen on macOS, 11 pinned vectors 11/11; canoncheck's own seed set regenerated to the shipped forms and pushed at `aa8e751`, 15/15. 8 Aug: reproduced on the final commit from a fresh clone, file-level re-hash 78/78 clean (38 fin, 40 ind), canoncheck 152/152, vectors 11/11.
- **Kevin Zhang (`wowlegend`, Tersign).** 11 Aug: independently reproduced 152/152 with a third, separately written stdlib canonicaliser; float-domain rejects 46/76 on v1 to 0/76 on v2 (fin) and 17/76 to 0/76 (ind).
- **`giskard09`.** 7 Aug: clean regen on both corpora, chain heads matching exactly.
**Published targets now in the public record:** fin chain head `71c10986…` / bundle `b45f7c47…`; ind chain head `93733e6a…` / bundle `b926af903…`.
 
**And the defect this work order fixes is pinned into a published vector.** `anchoring_latency_ms: 740` is present at `776cc0b` not only in the two `envelope_anchor.json` samples but **inside `vectors/expected.json` as expected `canonical_utf8` bytes**. Removing it therefore changes: the envelope's canonical bytes, its `envelope_hash`, the chain from sequence 37 onward, both chain heads, both bundle digests, the pinned vector and its digest, and the canoncheck seed set at `aa8e751`.
 
**Therefore:**
 
1. **Task 12 (corpus regeneration) remains GATED, but the reason has changed.** It is not that anyone is mid-run. It is that a regeneration silently supersedes three published third-party results. It must be announced as a **dated supersession** - state the boundary, state the reason, publish the new targets, invite re-runs - exactly as the signed-manifest 390-to-409 re-sign was handled. **Do not start Task 12 until Martin confirms the announcement is going out.**
2. **Everything else in this work order is safe now**, because it changes the catalogue, vocabularies, registers and documentation, not the corpus bytes.
3. **Verify at the end that the corpus bytes are unchanged** (the published digests still match). If any task you perform changes a corpus digest, you have gone outside scope. Stop and flag it.
### Guardrails 2 to 7
 
2. **Do not publish `schema/se-v0.1.schema.json` or freeze any schema.** The hash-scope decision (P1-1) is still open and gates the freeze.
3. **Do not add or change any conformance claim.** `CONFORMANCE.md` states that nothing may claim SE-C0 or any SE-Cx badge before a published schema and public vectors exist. That stays true.
4. **Never fabricate a value.** No invented digests, signatures, timestamps or addresses. Illustrative examples must be obviously illustrative (`example.test`, `0xEXAMPLE…`).
5. **Lane discipline.** AXES is an evidence record, not a control gate, policy engine, adjudicator or identity issuer. Test every field: *does a consumer need this to understand what happened, or to decide what to do?* The first belongs in AXES. If a change fails this test, stop and flag it.
6. **IP hygiene.** One external participant (AlgoVoi / Christopher Hopley) operates an aggressive per-component-citation regime over their own primitives (a "discrimination-tuple injectivity" rule, a PQC/ZKP construction). **Do not reproduce, adapt or cite those.** RFC 8785, SHA-256 and Ed25519 are open standards and free to use.
7. **One commit per task**, task number in the message, not squashed.
---
 
## 1. Task 1 - Add the `identifier_scope` axis (pairwise identifier support)
 
**Why this exists.** A pairwise identifier is stable for one relying party and uncorrelatable across relying parties; the issuer computes it, typically as a key derivation over (issuer secret, subject, relying party). It gives a merchant continuity without giving the world correlation. Long established: SAML persistent NameID, OIDC pairwise `sub`, eIDAS sector-specific identifiers, Apple private relay. An x402 Identity WG use case (issue #10, Nicole Dunn / Baselayer) requires it.
 
AXES currently has **no vocabulary for identifier linkability**, so a consumer cannot tell whether two envelopes carrying different subject identifiers describe two subjects or one subject seen from two relying parties. That ambiguity silently corrupts any join.
 
**What AXES does and does not do.** It records the identifier, its scope, and a pointer to the authority that can resolve it. **It never records the resolution.** Linkage lives with the issuer and is reached through legal process. AXES is not an identity service.
 
**1a.** Add to `docs/06-controlled-vocabularies.md`:
 
```
identifier_scope (closed):
  global                 - comparable across all parties; the same value denotes the same subject everywhere
  relying_party_pairwise - stable for one (subject, relying party) pair; uncorrelatable across relying parties by design
  issuer_internal        - meaningful only within the issuing system
  ephemeral              - valid for a single session or transaction; no cross-record continuity
```
 
**1b.** In `docs/05-field-catalogue/module-01-envelope-core.md`, document two companion attributes for any identifier:
 
- `<identifier>_scope` - a value from `identifier_scope`. **Where absent, a consumer MUST NOT assume `global`.** State this normatively; a defaulting reader is the failure this vocabulary prevents.
- `<identifier>_resolution_authority` - a reference to the party able to resolve the identifier. A reference, never the resolution.
**1c.** Add to `registers/requirements-register.md`:
 
```
| IDS-001 | Identifier scope axis: every identifier may declare the scope within which it is comparable | open_se | x402 wg-identity #10 |
| IDS-002 | Resolution-authority reference: who can resolve a scoped identifier, never the resolution | open_se | IDS-001; doctrine lane rule |
| IDS-003 | Absent scope MUST NOT default to global in any consumer or derivation | conformance_rule | IDS-001 |
```
 
**Acceptance:** closed vocabulary with four values; both companion attributes documented with the no-defaulting rule in normative language; three register rows.
 
---
 
## 2. Task 2 - Identifier sets as content-keyed objects, with declared types
 
**Why this exists.** AXES uses single-valued scalar references throughout (`actor_ref`, `agent_ref`, `payee_ref`, `provider_id`, `connector_id`). Two x402 Identity WG issues (Alfred Tom / OMA3, #3 and #4) establish that a party may legitimately hold several identifiers, and may **claim one it does not control**.
 
Three failures follow if an unverified alternative identifier is recorded as established:
 
1. **Contaminated attribution.** A malicious endpoint declares a well-known processor's address. Downstream a board report says the money went there, an aggregator credits its revenue, a dispute names the wrong counterparty. The envelope is cryptographically perfect and factually false.
2. **Join poisoning.** Two envelopes share an identifier for two parties; any derivation joining on it merges them. Measured in the wild: an independent census found 144 hosts paying one address, concluding that neither hosts nor addresses works as the unit alone.
3. **Laundering through evidence.** AXES envelopes are built to be portable and trusted, so an unverified claim inside a signed, anchored envelope is a **stronger** vehicle for the false claim than the original descriptor. The standard would amplify the attack it exists to detect.
**Scope honesty to state in the docs:** this **contains** the problem, does not prevent it, and does nothing about namespace squatting, which is registry governance and outside AXES.
 
**2a. The structural rule.** JCS sorts object members by UTF-16 code unit. **It does not sort array elements.** Converting a scalar to an array would mean two emitters recording the same set in different orders produce different digests. Instead:
 
- **A set** (members unique, order carries no meaning) becomes an **object keyed by a content-derived key** - the identifier value itself. JCS then sorts members, ordering is solved by an existing rule, and each member is a field so it composes with per-field selective disclosure.
- **A sequence** (order is part of the fact, for example the acknowledgment ladder) stays an **array where every element carries an explicit sequence or rung field**, so order is stated data rather than implied by position.
**2b. Shape:**
 
```json
"payee_identifiers": {
  "dns:example.test": {
    "identifier_type": "dns",
    "entry_basis": "observed_live_402",
    "verification_status": "verified",
    "verifier_ref": "<reference to the verifying party>",
    "verification_method": "<how>",
    "verified_at": "<ISO 8601 UTC>",
    "identifier_role": "primary",
    "identifier_scope": "global"
  },
  "eip155:8453:0xEXAMPLE": {
    "identifier_type": "caip10",
    "entry_basis": "counterparty_asserted",
    "verification_status": "unverified",
    "identifier_role": "alternative",
    "identifier_scope": "global"
  }
}
```
 
**`identifier_type` is not decoration, and there is direct evidence for it** - see Task 17.
 
**2c. Vocabularies** for `docs/06-controlled-vocabularies.md`:
 
```
entry_basis (closed):          counterparty_asserted | observed_live_402 | credential_backed | third_party_attested
verification_status (closed):  unverified | verified | verification_failed | verification_unavailable
identifier_role (closed):      primary | alternative
```
 
**2d. Normative consumer rule**, in the field catalogue and `docs/07-conformance-levels.md`:
 
> A consumer MUST attribute only on identifiers whose `verification_status` meets its stated threshold. **Unverified identifiers are recorded but are not attributable.** A derivation asked to attribute value to a party whose only matching identifier is `unverified` MUST return `underivable_unverified_identifier` rather than a value.
 
**Acceptance:** set-versus-sequence rule documented with the JCS reasoning; three vocabularies added; the shape documented; the consumer rule normative; the containment-not-prevention note present.
 
---
 
## 3. Task 3 - Make `assertion_basis` applicable at field scope
 
**Why this exists.** `assertion_basis` (`observed / measured / asserted / inferred / derived / interpreted`) is declared once at envelope scope in `evidence_quality`. Epistemic status is a property of individual fields. The published anchor envelope declares `assertion_basis: "observed"` and carries `anchoring_latency_ms: 740`, which is not observed, so the envelope makes a false epistemic declaration about its own contents with no structural way to tell which field is which. The same defect lets an unverified identifier (Task 2) sit inside an envelope labelled "observed".
 
**Changes:** in `docs/05-field-catalogue/module-01-envelope-core.md` and `docs/06-controlled-vocabularies.md`, document that `assertion_basis` is applicable at **field or block scope as well as envelope scope**, that the more specific declaration governs, and that **an envelope-scope declaration MUST NOT be read as covering a field carrying its own**.
 
Add: `| IDS-004 | assertion_basis applicable at field/block scope; the more specific declaration governs | open_se | REQ-EXT-001, REQ-EXT-009 |`
 
**Acceptance:** field-scope applicability documented; precedence rule stated; register row added. Note in the docs that this one change resolves two separate defects.
 
---
 
## 4. Task 4 - Remove stored derived values; prepare the anchoring fix
 
**The principle to document.** A record carries measured facts. Derived values are named in the field catalogue, not stored in the envelope, **unless the derivation crosses a boundary the consumer cannot reproduce** (a clock domain, an external system, a party change), in which case the stored value must declare its endpoints and its source.
 
**One carve-out, load-bearing, document it alongside:** if the executing system computed a value and **acted on it**, store it, even though it is recomputable, with `assertion_basis: derived` and `evidence_origin: runtime`. Divergence between the stored value and an independent recomputation **is the detection mechanism for a miscalculating agent**. A pure store-only-primitives rule would blind the evidence layer to the failure it exists to catch.
 
**4a. `anchoring_latency_ms` - specify its removal, do not execute it.** It is a derived value stored in the envelope and it breaks the standard's own pattern: Module 01 already defines the three-point time model by naming derivations rather than storing them ("`emitted_at − occurred_at` = capture lag; `recorded_at − emitted_at` = pipeline lag"). It also bakes a unit into an identifier.
 
**Because it is pinned in `vectors/expected.json`, the actual removal is Task 12 and is gated.** In this task:
 
- document the replacement in the field catalogue: **remove** `anchoring_latency_ms`, **add** `anchor_requested_at` (ISO 8601 UTC), and name the derivation in Module 01's existing sentence form: **`anchored_at − anchor_requested_at` = anchoring lag**
- mark the catalogue entry as pending the Task 12 regeneration so the docs and the corpus disagree visibly rather than silently
**4b. The published example is internally inconsistent - record and disclose, do not edit.** At `776cc0b` the anchor envelope has `occurred_at` 09:05:00.000Z, `emitted_at` 09:05:00.400Z, `recorded_at` 09:05:00.900Z, `anchored_at` 09:05:00.000Z, `anchoring_latency_ms` 740. **740 reconciles with no pair of those timestamps** (available deltas: 0, 400, 500, 900 ms), and `anchored_at` precedes both `emitted_at` and `recorded_at`, reading as the anchor predating the emission of the record whose chain head it anchors.
 
- add a defect row to `registers/requirements-register.md`
- add a disclosure note to `examples/golden-trace/README.md` in the same register as the existing `SIG-STUB` and SIMULATED-anchor disclosures. The bundle's doctrine is that stubs are disclosed in the bundle; an illustrative value presented as a measurement breaches that doctrine, and disclosing it is the honest interim step until Task 12 runs.
**4c. Unit-in-identifier.** Specify renaming `declared_heartbeat_interval_s` (21 occurrences at `776cc0b`) to carry the unit in the value, following `monetary: {amount, currency}`. **Leave `size_bytes` alone** (9 occurrences) and note why: bytes is the canonical unit for size with no realistic alternative, and applying the rule there would be pedantry. A rule applied with judgment persuades; one applied mechanically does not. The rename itself is corpus-affecting, so it executes in Task 12.
 
**4d. Prevent the next instance.** BLD-011 and BLD-026 in the requirements register plan `approval_response_latency_ms` derived from `approval_requested_at` and `approval_granted_at`. Both endpoints are already specified, so the stored lag is redundant by construction. **Amend both rows** to record the timestamps and name the derivation, cross-referencing 4a.
 
**Note for context:** the float problem is **already solved** on `golden-trace-v2`. Every hash-scoped quantity is an integer `Amount {value, decimals, asset}`, a generator assertion fails the build on any float in hash scope, and assets are namespaced (`iso4217:EUR`, CAIP-19). Cite this as precedent when documenting DPR-007; the envelope layer is done and only the derived layer remains.
 
**Acceptance:** catalogue documents the replacement and marks it pending Task 12; defect row and README disclosure added without editing corpus bytes; the `declared_heartbeat_interval_s` rename specified for Task 12; `size_bytes` exempted with a reason; BLD-011 and BLD-026 amended.
 
---
 
## 5. Task 5 - Signer-presence states
 
**Why this exists.** An external implementer (Ryan Cason, orionsys) found that deleting the `signature` field while leaving `signedBy` in place makes a naive verifier return valid, exit 0, **even under a require-signatures flag**, because the signature cannot be inside its own hash input so stripping it disturbs no hash and breaks no link. One "absent" state covered two different things: genuinely unsigned, versus a record that names an author and cannot prove it. The discussion author (Chou Deyu, Guardian) endorsed keeping the states distinct.
 
Add to `docs/06-controlled-vocabularies.md`:
 
```
signer_presence (closed):
  unsigned      - no signature was attempted; the record makes no authorship claim
  stripped      - an author is named but no signature is present; the authorship claim is unsupported
  unverifiable  - a signature is present but the key or its authorisation cannot be resolved
  invalid       - a signature is present and resolvable and does not verify
```
 
Document that **`stripped` MUST fail regardless of any strictness flag** - the attacker chooses whether the verifier runs strict, so strictness cannot be the control. Document that a top-level failure verdict is a **fail-closed aggregate**, not a claim that every lower property failed. Note that AXES hashes the whole canonical envelope, which is what makes `stripped` detectable, and cross-reference Task 7.
 
**Acceptance:** four-value vocabulary; strictness-independence rule normative; fail-closed-aggregate note present.
 
---
 
## 6. Task 6 - EXTEND the pinned-canonical-bytes vectors to non-ASCII cases
 
**This extends an existing mechanism. Do not build a new one.** `vectors/expected.json` already pins expected `canonical_utf8` strings per vector, which is precisely the right pattern. What is missing is coverage.
 
**Why this exists.** An external implementer found his canonicaliser correct on both JCS divergence axes **by accident**: the language's default comparator happened to sort UTF-16 code units and happened not to normalise. Swapping in a locale-aware comparator left **all 148 of his tests passing while the bytes diverged**, because there was no non-ASCII key anywhere in his vectors. When he planted the fault deliberately, the surrogate-pair case still passed; it took an "ä sorts after z" case to catch it. His conclusion: he had named the property rather than pinning it.
 
AXES is exposed identically. Its pinned vectors are ASCII-keyed, so three independent verifications prove agreement **on the corpus that was run**, not agreement on the ordering property.
 
**Add four vectors in the existing format, each pinning expected canonical bytes:**
 
1. **Surrogate-pair key** - a key outside the Basic Multilingual Plane, proving UTF-16 code-unit ordering (RFC 8785 §3.2.3) rather than code-point ordering.
2. **Composed and decomposed pair** - the same visual key in NFC and NFD as two distinct members, proving no normalisation (RFC 8785 §3.1).
3. **Collation case** - keys including "ä" and "z", proving code-unit ordering rather than locale-aware collation. This is the case that catches a locale comparator when the surrogate case does not.
4. **Digest encoding** - the same digest as bare lowercase hex and with an algorithm prefix, proving the declared encoding is pinned rather than assumed.
Add a **deliberate negative check**: substituting a locale-aware comparator must fail the suite. Document in the vectors README that **a property that is only named is not pinned**, and credit the finding.
 
**These are new vector files, not changes to existing pinned bytes**, so this task does not disturb the verified corpus.
 
**Acceptance:** four new vectors with pinned canonical bytes in the existing `expected.json` format; the locale-comparator negative check exists and fails as intended; no existing pinned value altered.
 
---
 
## 7. Task 7 - Create `docs/09a-hash-scope-and-exclusions.md`
 
**Why this exists.** An independent reviewer (Rul1an) reproduced a concrete failure in a comparable system: he generated a real audit file, confirmed it under that system's own integrity check, then found that editing three fields in place **left the chain valid under two independent verifiers**, because the canonical payload excluded fields the reader still consumed. He also found a type-confusion case where one verifier accepted a file the other refused to parse: "the two readers accept different files."
 
**The nameable principle: a hash whose scope is narrower than the reader's consumption scope creates a mutable region that verifies.** AXES should state its position before anyone asks.
 
**Write the file with this structure.** (If Martin supplies a drafted text, use it verbatim; otherwise write from this specification.)
 
- **Status line** marking it an open design question inviting challenge, pointing at the issue templates.
- **§1 Why this note exists** - every signed record has a hash scope; some fields cannot be inside it; every exclusion creates an unauthenticated region; in an evidence record almost every field is the evidence.
- **§2 Three things easily confused**, as a table: **excluded at signing** (never inside the hash; not authenticated; a verifier can tell nothing about whether the value is original), **redacted after signing** (inside the hash, committed at emission, withheld from this reader; still authenticated; a tombstone proves presence), **absent** (never captured). A reader who cannot see a field must be able to tell withheld from never-captured, because they support opposite conclusions.
- **§3 What the CrossMsg-Signing prior art actually proves.** Be precise, because `docs/09` currently overstates it (Task 8). Two separate ideas: the **Signature Exclusion Principle**, narrow and universal (the signature is computed over content excluding itself), and the **canonical KVP pattern**, an **inclusion** mechanism - a declared mapping table extracting business content into a flat key-value set, so document structure and element order never enter the signing material. The design fork: a declared **inclusion** set leaves a newly added field silently unauthenticated; a declared **exclusion** set puts it inside the hash by default so a genuinely mutable field fails loudly. **For an evidence record a loud failure is recoverable where a silent unauthenticated region is not**, so AXES defaults to inclusion.
- **§4 The current AXES position** - three exclusions: `integrity.signature`, `integrity.envelope_hash` (self-referential) and `recorded_at` (recipient-stamped).
- **§5 Options with trade-offs:** (A) exclude; (B) include and forbid mutation; (C) include a commitment and disclose selectively; (D) **countersignature** - the receiving system countersigns an outer layer covering the emitter's inner envelope plus the fields it added, so a recipient-stamped field is authenticated **by the recipient** rather than excluded. Option D reframes an exclusion as a custody handoff and composes with the existing custody axis.
- **§6 Recommendation**, five rules: default to inclusion; every exclusion declares a reason from a closed set; **sensitivity is never a reason to exclude**; prefer countersignature for recipient-stamped fields; and the hash-scope declaration is itself inside the hash.
- **§7 What a deploying organisation must own.** Every excluded field is a risk accepted on behalf of everyone who later relies on the record. Four questions: which fields are excluded; what an undetected change to each would mean; what compensating controls apply; whether any assurance statement rests on an excluded field. **Make the fourth mechanical:** the hash-scope declaration feeds `reliance_boundary_status` and `known_limitations`, so a report sentence resting on an excluded field carries its caveat automatically.
- **§8 The attack that settles one detail.** If the declaration is outside the hash, an attacker edits it to exclude a field, changes that field, and both the signature and the declaration verify. Therefore the declaration is always inside the scope it declares. Self-descriptive, not self-referential.
- **§9 Feedback wanted**, numbered: is default-inclusion right for an evidence record; is countersignature worth the implementation surface; is the three-value exclusion-reason vocabulary complete; does the withheld-versus-never-captured distinction hold up in a real audit; does automatic caveating make reports unreadable. Close with: **if you can construct a record that verifies while being materially false under these rules, that is the most valuable thing you can send us.**
Add to `docs/06-controlled-vocabularies.md`:
 
```
hash_scope_exclusion_reason (closed): self_referential | recipient_stamped | syntax_mutable
```
 
**Acceptance:** file exists with all nine sections; vocabulary added; `docs/09` links to it.
 
---
 
## 8. Task 8 - Correct the CrossMsg citation in `docs/09`
 
**The defect.** `docs/09-canonicalisation-and-hashing.md` describes declared hash scope as "generalising CrossMsg's `ConversionRules` exclusion set". That file is a JSON Schema generation and element-transformation configuration and **contains no exclusion set for mutable fields**. The project's actual contributions are the Signature Exclusion Principle and the KVP mapping table, which is a declared **inclusion** set. The current sentence overstates prior art in a publicly cited repository.
 
**Change:** rewrite it to describe declared hash scope as generalising **the declared-field-set discipline** demonstrated by the KVP mapping table, note the inclusion-versus-exclusion fork, and link to `docs/09a` §3.
 
**Acceptance:** no sentence attributes an exclusion set to `ConversionRules`; the link exists.
 
---
 
## 9. Task 9 - The Derivation Profile Registry (DPR) series
 
**Why this exists.** Once the envelope stops storing computed values, every computed value in a report moves **outside the evidence boundary** unless the derivation is identified, versioned and reproducible. The signature covers the timestamps, not the arithmetic. Two conforming tools can produce different values from the same envelopes and both be "correct"; a report reissued in three years can differ with no mechanical explanation.
 
This is not a new layer. `docs/01-doctrine-and-non-negotiables.md` §4 already defines a **derived report layer** as "values computed from envelopes, **traceable to them**; a basic open annex is part of the standard". The DPR makes that claim operative. The parallel is exact: the envelope carries `integrity.canonicalisation_version` so bytes-to-digest is reproducible; a report must carry a profile identifier so envelopes-to-value is reproducible.
 
**It also repairs the conformance ladder.** `docs/07` defines SE-C4 as "assurance-report-capable from the open evidence alone", which is untestable as written. Against a named profile it becomes mechanical.
 
**9a. Add to `registers/requirements-register.md`**, Part D, in the existing four-column programme format:
 
```markdown
### D.x Derivation Profile Registry (DPR-*)
Source: observation-versus-derivation design principle, 15 Aug 2026; docs/01 §4 derived layer; docs/07 SE-C4.
 
| ID | Item | Layer | Cross-refs |
|---|---|---|---|
| DPR-001 | Derivation Profile Registry: derived values reproducible from sealed envelopes under an identified, versioned, digest-pinned rule set | standards_package | docs/01 §4; REQ-STD-002, REQ-EXT-001 |
| DPR-002 | Profile document structure: id, version, digest, canonicalisation context, numeric profile, temporal dependencies, normative reference | open_se + package | DPR-001; docs/09 |
| DPR-003 | Per-rule structure: derivation_id, inputs (with cross-envelope join rule), computation, output type/unit, preconditions, failure semantics, two-sided vectors | open_se + package | DPR-002; TRK-019 |
| DPR-004 | Two profile classes: `axes.*` normative and published; proprietary namespaces publish identifier, version and digest but not rules | standards_package | TRK-017 (IPR); docs/01 §4 |
| DPR-005 | Report binding: every derived value carries its derivation_id; every report carries profile id, version and digest | derived + conformance_rule | DPR-001; REQ-EXT-009 |
| DPR-006 | Reports as AXES artefacts: a report envelope references source envelope digests + profile digest + derived values | open_se + derived | DPR-005; REQ-BPO-014 |
| DPR-007 | Numeric determinism in the derived layer: decimal with declared scale and rounding mode; no binary floating point. The envelope layer already achieves this via integer Amount | open_se + conformance_rule | docs/09; golden-trace-v2 Amount migration |
| DPR-008 | Temporal dependency pinning: profiles declare calendar and IANA tzdata versions | open_se | Module 01; IDS-005 |
| DPR-009 | Failure semantics: a derivation returns a typed outcome, never a bare number, when a precondition fails | conformance_rule | capture_status, evidence_gap_recorded |
| DPR-010 | Profile immutability and supersession: behavioural change is a new version declaring what changed and which prior outputs it invalidates | standards_package | TRK-006 |
| DPR-011 | SE-C4 becomes testable: claimed against a named profile, verified by independent re-derivation | conformance_rule | docs/07 SE-C4; DPR-001 |
| DPR-012 | `axes.*` seed set: capture lag, pipeline lag, anchoring lag, sequence integrity, authority-validity-at-action | open_se | Module 01 three-point time model |
| DPR-013 | No gatekeeper: any party may mint a profile in its own namespace; only `axes.*` is normative | standards_package | docs/01 §5 |
| DPR-014 | Boundary rule: a derivation computes a value from observations; it does not decide what the value means | conformance_rule | docs/01 §5 |
| DPR-015 | Golden Trace v2 carries a worked profile instance and re-derivation procedure | programme_action | EB-004, CRE-009, D-008 |
```
 
**9b. The failure vocabulary for DPR-009**, in `docs/06-controlled-vocabularies.md`. Each value exists because it supports a **different** conclusion for a reader:
 
```
derivation_outcome (closed):
  ok
  underivable_missing_input            - a required input was never captured; a genuine evidence gap
  undisclosed                          - committed at emission but not disclosed to this reader. NOT a gap.
                                         If redaction reads as missing evidence, an auditor concludes the
                                         opposite of the truth.
  not_independently_reproducible_keyed - depends on a secret; a verifier without it can check consistency
                                         but not recompute. A designed privacy property working correctly.
  indeterminate_clock_skew             - clock provenance unknown on one side, or the margin falls inside
                                         the combined uncertainty
  underivable_identifier_scope         - the join crosses relying parties on a pairwise identifier;
                                         unsound by design, not unavailable by accident
  underivable_unverified_identifier    - attribution attempted on an identifier below the threshold
  derived_with_gap                     - the span contains a recorded evidence gap
  superseded                           - the source envelope has been superseded by an amendment
  underivable_conflicting_inputs       - inputs carry corroboration_state: conflicting_evidence; a derivation
                                         MUST NOT silently pick a side
  precision_insufficient               - input precision cannot support the requested output precision
  outside_capture_boundary             - the path was outside the capture boundary
```
 
**9c. `axes.authority_valid_at_action`** (part of DPR-012). Document explicitly: it compares an emitter's action time against an external issuer's validity window - **two clocks** - so it MUST return `valid_at_action | invalid_at_action | indeterminate_clock_skew`, never a boolean. In a chargeback dispute the boundary case is where the money is.
 
**9d. Decision-register entries:**
 
```
| Derivation Profile Registry as the mechanism for the derived layer's traceability claim | accept-core | observation-versus-derivation principle, 15 Aug 2026 |
| Two profile classes: axes.* published; proprietary profiles publish identity but not rules | accept-core | preserves TRK-017 IPR posture while making reports reproducible |
| Derived values are not stored unless operative (computed and acted upon by the executing system) | accept-core | observation-versus-derivation principle |
| SE-C4 conformance claims must name a derivation profile | accept-conditional on DPR-002/003 | docs/07 |
```
 
**Acceptance:** fifteen rows in the existing format; twelve-value failure vocabulary with the reason each is distinct; `axes.authority_valid_at_action` with its three-state return; four decision entries.
 
---
 
## 10. Task 10 - Ratify the casing decision
 
**Why this exists.** `docs/06-controlled-vocabularies.md` §2.10 records that naming conventions are "confirmed as editorial decisions for the Field Catalogue - ratify there", and §3 lists five open naming decisions. **Casing is not among them**, because it was never identified as a question. `lower_snake` is an inherited default with no recorded rationale.
 
The evidence supports it. ISO 20022 maintains three representations and **lowerCamelCase appears in none**: the business model uses full spaced title-case names; XML tags use abbreviated vowel-stripped forms (`MsgId`, `CreDtTm`); the ISO 20022 JSON Schema generation draft retains those; and the ISO 20022 API/JSON best-practices whitepaper §7.1 states element names **may use snake_case, all lowercase with underscores**, with `ssi_category` and `currency_code` as examples.
 
**10a.** Add to `registers/decision-register.md`:
 
```
| Field keys are lower_snake; enum values are lower_snake | accept-core | ISO 20022 API/JSON best-practices whitepaper §7.1 recommends unabbreviated snake_case for JSON representations of ISO 20022 semantics; lowerCamelCase appears in no ISO 20022 representation. AXES is internally consistent at 274 keys with zero camelCase and 29 enum values with zero drift. |
| Concept-level interoperability via declared representation pairs, never derived transforms | accept-core | camel-to-snake transforms are ambiguous at digit boundaries and acronyms. ISO 20022 stores abbreviations in the repository at design time rather than deriving them. |
```
 
**10b.** In `docs/06-controlled-vocabularies.md` §3, add casing as a **closed** item with that rationale, so the omission is visibly repaired.
 
**10c.** Document the cross-layer rule in `docs/12-standards-alignment.md`: a field's **key** takes the convention of its document (x402 wire layer is camelCase, evidence layer is snake_case); a field's **concept** is the interoperable unit; a registry declares both spellings and never derives them. State why it matters beyond tidiness: **under JCS two spellings sort to different positions, producing different canonical bytes, different digests, and two content identities.** Note the one designed exception: a relying-party-scoped identifier (Task 1) legitimately produces different digests at different relying parties.
 
**Acceptance:** two decision entries; casing closed in §3; the cross-layer rule with both the JCS consequence and the pairwise exception.
 
---
 
## 11. Task 11 - Custody, correlation and settlement-role corrections
 
**11a. "A schema cannot mint an identity it did not issue."** An external contributor (Dani Danwin, TrustLayers) argued that decision identity needs two coordinates pinned in two venues: the **digest context** belongs in a registry, immutable and owner-authored; the **capturer's identity** belongs at the runtime that emits the record, issuer-established at the commit boundary. Two records byte-identical under one digest context can still differ in whether the capturer was issuer-established or self-asserted.
 
In the custody documentation, state normatively: **`emitter_independence_level` and `capture_relationship` record an identity established elsewhere at the commit boundary. They MUST NOT be self-declared by the emitting schema, and a consumer MUST NOT read them as an assertion the envelope itself can support.** Credit the contributor by handle.
 
**Document a third coordinate**, arising from Task 1 and not yet stated externally: two records byte-identical under one digest context, with the same issuer-established capturer, **can still be about different subjects** if the identifiers are relying-party-scoped. Digest context, capturer identity and identifier scope are three independent coordinates of decision identity.
 
**11b. Correlation finding and triage disposition as envelope kinds.** External work (Ioannis Loutsis, Agentmetry) established that portable evidence must carry the asynchronous cross-event **finding** no single decision produced, and its later human **triage disposition**, on the same append-only chain. Worked example: three individually-permitted tool calls (list a directory, read a credentials file to a temporary path, POST to a collector) produce one critical cross-event credential-exfiltration finding no per-call gate can see.
 
The accompanying discipline (Dani Danwin): each layer has an owner. Enforcement belongs to the policy engine; **correlation belongs to SOC and threat-detection, not the custodian**; custody-of-the-fact belongs to the witness. Collapsing the correlator's job into the witness is how a custodian becomes something it has no authority to be.
 
Add both as `event_kind` values, documented as **witnessed, never authored**: the custody axis records who produced the finding, when, and how far confirmed. **The custodian attests that a finding was emitted, by whom and when. It never asserts the correlation itself.**
 
**11c. `settlement_role` direction-neutral redefinition.** `docs/15-AXES_Payee_Settlement_Role_Design_Note.md` §2 defines `origin` as "the party that earns the value". On the payer side the distinction is who **funds** it, so the same token would carry an inverted meaning by context - a code-set reuse trap. Redefine as the party's relationship to the value flow:
 
```
origin        - the principal: the party whose value it is, whether earned or spent
facilitator   - a relay settling on another party's behalf
proxy_gateway - a pass-through intermediary that fronts other services and routes value onward
```
 
Amend §3: the checkability rule is underdetermined once a party may hold several identifiers. **State which identifier the check runs against** (the `primary`) and what a mismatch on an `alternative` means (a signal, not a disqualification). If the current wording has been quoted externally, add a line explaining the correction rather than editing silently.
 
**Acceptance:** the not-self-declared rule stated normatively and credited; third coordinate documented; two envelope kinds with the witnessed-not-authored discipline; `settlement_role` redefined; §3 names the identifier.
 
---
 
## 12. Task 12 - GATED: corpus regeneration and supersession
 
**DO NOT START. See guardrail 1.** When Martin confirms the supersession announcement is going out, this task covers: removing `anchoring_latency_ms` and adding `anchor_requested_at`; reconciling the `anchored_at` / `emitted_at` / `recorded_at` ordering; renaming `declared_heartbeat_interval_s`; regenerating both corpora byte-identically via the generators; updating `vectors/expected.json` pinned canonical bytes; republishing every digest, both chain heads and both bundle digests; and updating the disclosure note from Task 4b.
 
**It must also:** verify the regenerated bundle re-verifies end to end; confirm a clean second regen (`git diff --stat` empty); and **publish the new targets in the same place as the old ones**, so a reader sees a transition rather than discovers drift. Prepare a short supersession note naming the old and new chain heads and bundle digests, the reason, and an explicit invitation to re-run - addressed to `MarkovianProtocol`, `wowlegend` and `giskard09`, all of whom have re-run voluntarily before.
 
---
 
## 13. Task 13 - The "why this field exists" documentation layer
 
**Why this exists.** A reader examining the schema for the first time should understand **why** an element exists, not only what it holds. Several AXES fields exist because a named person in a public forum described a concrete failure, and the schema is far more persuasive when it carries that provenance.
 
**Adopt a four-part note** for every field in the catalogue, starting with Module 01 and applied to every field this work order touches:
 
```
**What it records.** One sentence, factual.
**Why it exists.** The concrete failure it prevents, with a worked example where one exists.
**What it does NOT do.** The lane boundary, so a reader does not over-read the field.
**Origin.** Where the requirement came from, credited by name or handle where public.
```
 
**Worked exemplar** - match this register: specific, plain, no marketing.
 
```markdown
### `corroboration_state`
 
**What it records.** How far a claim in this envelope has been confirmed by a party
other than the one that made it, on a graded scale from uncorroborated to
externally anchored.
 
**Why it exists.** A sealed record can be cryptographically perfect and factually
false. An operator running a fleet of agents reported issuing 41 requests to an
external service, receiving HTTP 200 on every one, and gaining zero of the
outcomes those requests were supposed to produce. Under a three-artifact model
that produces 41 well-formed, signable, replayable decisions, controls and
outcomes attesting to 41 events that did not happen. The failure is not in the
cryptography; it is that the post-execution outcome was the response to the
agent's own request, which is self-attestation with a canonicalisation step in
front of it. `corroboration_state` is where a record states, honestly, how much
better than self-attestation it actually is.
 
**What it does NOT do.** It does not establish that the external state is what the
record claims. A corroboration handle makes independent checking possible; it
does not make the claim true. Determining truth requires a defined verifier,
observation method, timing condition and acceptance rule, and those are outside
this standard.
 
**Origin.** Raised as the correspondence-versus-integrity problem in
microsoft/agent-governance-toolkit discussion #276 by parweb, with the
attested-versus-corroborated distinction and the requirement that an outcome
handle must not be the write response.
```
 
**Apply to at least:** `corroboration_state`, `capture_relationship`, `emitter_independence_level`, `assertion_basis`, `identifier_scope`, `verification_status`, `entry_basis`, `signer_presence`, `settlement_role`, `anchor_requested_at`, `capture_status`, `evidence_gap_recorded`, and the two new envelope kinds from Task 11b.
 
**Rules:** credit real people and public forums accurately, using the handle or name as it appears publicly; **never credit anyone for anything they did not say**; never name a private source (write the requirement without attribution); keep worked examples concrete and short, a number and an outcome beats a paragraph of theory; and **"What it does NOT do" is not optional** - it is the lane boundary and it is what stops a reader over-reading the schema.
 
**Acceptance:** the pattern documented in `docs/05-field-catalogue/README.md` as house style; exemplar present; listed fields carry the note; every credit is to a public source.
 
---
 
## 14. Task 14 - Settle and publish the `canonicalisation_version` registry value
 
**Why this exists, and it is overdue.** Colin H Winter asked the same question twice in AXES issue #6, on 7 and 8 August, and it is still unanswered: the thread pinned `canonicalisation_version` as `"RFC8785"` but the corpus ships `"RFC8785-JCS"`. He regenerated canoncheck to the corpus form on his own initiative and asked which is registry. **Confirmed: the corpus and `vectors/expected.json` at `776cc0b` both ship `RFC8785-JCS`.**
 
This is not a cosmetic question. It is exactly the canon-registry problem an external standards participant (Steven Mih, Ahana / LF Presto) is arguing in AGT #276: **a canon identifier must dereference to an immutable statement of algorithm revision, hash and output encoding**, because two implementations that both say "JCS + SHA-256" still diverge on UTF-16 member-sort versus normalisation, and on bare hex versus prefixed digest. An identifier that is only a name is not a registry entry.
 
**Changes:**
 
- Declare `RFC8785-JCS` the normative value, in `docs/09` and the field catalogue.
- **Make it dereference.** Document what the identifier resolves to: RFC 8785 (JCS) at its published revision; UTF-8 output; object members sorted by UTF-16 code unit; no Unicode normalisation applied; and the digest declared separately (`hash_algorithm`, currently SHA-256) with its output encoding stated (bare lowercase hex). A second implementer must be able to reproduce the bytes from this statement alone, without reading the code.
- Add a decision-register entry recording the value and that the earlier `RFC8785` form is retired.
- Note in `docs/09` that the identifier is versioned: a change in any of those properties is a **new identifier**, never a redefinition of this one.
**Acceptance:** `RFC8785-JCS` normative and documented as a dereferenceable statement covering revision, output encoding, sort rule, normalisation posture and digest encoding; decision entry present; the immutability rule stated.
 
---
 
## 15. Task 15 - Ship an executable reference verifier
 
**Why this exists.** Two external parties independently found there is not one. `giskard09`, 7 Aug: *"didn't find an executable custody-ref validator on your side (tools/ has the generator, no verifier for negative cases) so today it's one-sided in practice."* `wowlegend`, 11 Aug: there is no `custody_verdict` anywhere in the repo at `776cc0b`, and `vectors/README.md` marks an in-repo reference verifier as Planned (P4).
 
The consequence is structural: **negative vectors cannot be checked in-repo, and every cross-check stays one-sided.** An external party can confirm the corpus reproduces, but cannot confirm that AXES's own rejection criteria reject what they claim to. It also blocks Tasks 5, 6 and 9 from being testable rather than merely documented.
 
**Build it**, following the house pattern used elsewhere in the estate: stdlib plus one crypto library, no network, no hosted calls, runnable offline against the committed corpus.
 
Minimum capability:
 
1. Recompute canonical bytes for an envelope and compare against the pinned `canonical_utf8` where present.
2. Recompute the digest and compare against `envelope_hash`.
3. Verify chain linkage and sequence closure across a bundle.
4. **Evaluate `vectors/expected.json` expectations**, including the negative cases: a vector marked `"expect":"reject"` must reject **with the stated reason code**, not merely fail. Absence of an `expect` key is an implied pass, per the existing `vectors/README.md` convention.
5. Exercise the custody twins - `custody_deployer_captured_reject` must reject with `custody_independence_reject`; `custody_accept_independent_external` must pass.
6. Report a typed outcome per check, never a bare boolean.
**Acceptance:** the verifier runs offline against both committed corpora and the full vector set; every pinned expectation is evaluated including reason codes; the custody twins behave as pinned; `vectors/README.md` updated to reflect that the verifier is shipped rather than Planned.
 
---
 
## 16. Task 16 - Audit every check for the "cannot say yes" failure
 
**Why this exists.** In AXES issue #6 on 11 Aug, `wowlegend` withdrew one of his own controls after discovering it could not pass anything: *"Under your identity syntax the criterion cannot return `valid` for any input, so it rejected without deciding. It could not have distinguished a passing case from a failing one."* Independently, Ryan Cason found his canonicalisation guard passed 148 tests while being substitutable with a broken comparator, and called it "a guard that looked like one".
 
**Same failure class: a check that reports a verdict it did not reach.** A criterion with an empty pass-set is worse than no criterion, because it produces confident output that carries no information. This is a live risk in AXES's own suite and nobody has audited for it.
 
**Do this:**
 
- For **every** predicate in the vector suite and in the new reference verifier (Task 15), demonstrate that there exists an input that **passes** and an input that **fails**. Both must exist as committed vectors.
- Where a predicate currently has only failing vectors, either construct the passing case or record in `vectors/README.md` that the predicate is unexercised in the positive direction and therefore proves nothing yet.
- Add this as a standing rule in the vectors README: **a check ships with at least one passing and one failing vector, or it ships marked as unexercised.**
- Add a register row: `| TLC-xxx | Every conformance predicate must have a demonstrated non-empty pass-set and fail-set | conformance_rule | AXES #6, 11 Aug |`
**Acceptance:** every predicate has both a passing and a failing vector, or is explicitly marked unexercised; the standing rule is in the vectors README; register row added.
 
---
 
## 17. Task 17 - Identity syntax portability
 
**Why this exists, with direct evidence.** In AXES issue #6, `wowlegend` ran his independence criterion against the two custody twins. AXES identifiers as written (`agent:caldera/ap-pilot`, `org:caldera-robotics`) were **unparseable** to his verifier, which rejected **both** twins including the one AXES accepts - a false negative. Rewriting the same identities as `0x`-addresses made his criterion match 2/2. His conclusion: *"the independence predicate agrees with yours; the normaliser is what does not, and an independence criterion bound to one identity syntax is not portable."*
 
That is empirical support for the `identifier_type` field in Task 2, and better evidence than any argument from first principles.
 
**Changes:**
 
- Document that **every identifier declares its type or namespace**, so an external verifier knows the parse rule rather than guessing. Reuse the `identifier_type` field from Task 2b.
- Where AXES uses its own prefixed forms (`agent:`, `org:`, `person:pseu/`, `tool:`, `runtime:`), **document the syntax explicitly in the field catalogue** - what the prefix means, what follows it, and what a consumer may and may not infer from it. Today a second implementer has to reverse-engineer it from examples.
- State the portability rule: **a conformance predicate MUST NOT be bound to one identity syntax.** A predicate that cannot parse an identifier returns `verification_unavailable` or the appropriate typed outcome, never a rejection, because rejecting an unparseable identifier manufactures a false negative.
- Credit the finding.
**Acceptance:** identifier syntax documented per prefix; the parse-rule requirement stated; the do-not-reject-on-unparseable rule normative; credit present.
 
---
 
## 18. Task 18 - Make stub status machine-readable
 
**Why this exists.** In AXES issue #6, `wowlegend` observed that stub status is embedded in a free-text basis string: `counterparty_signed (webhook mTLS, STUB)`. His point: a demonstrated counterparty signature and a stub are *"separable only by parsing a parenthetical"*, and although `report_D_forensic` discloses it in prose, **"the disclosure is not reachable by a verifier."**
 
That undercuts the honest-stubbing doctrine, which is one of the things AXES has that the field mostly does not. A disclosure only a human can read is not a control.
 
**Changes:**
 
- Add a structured field alongside the basis string recording whether the basis is demonstrated or stubbed, from a closed vocabulary (for example `basis_status`: `demonstrated | stubbed | simulated`). Do not embed status in free text.
- Apply the same rule to `anchoring_method`, which currently carries `write_once_store (SIMULATED)` in the same shape. The D-015 reading rule already says a SIMULATED anchor must not be read as a closed existence bound; make that reachable by a verifier rather than only by a reader.
- **Corpus-affecting, so the field definition lands here and the values land in Task 12.**
- Related, already booked: `wowlegend` also measured that across the fin bundle **0 of 43 acknowledgment rungs name a confirming party** - the ladder names the scheme, hash-binds the artifact, and identifies no counterparty, *"which is why the independence question could not be put to these records at all."* GAP-EXEC-002 already books this as HIGH with `counterparty_evidence_strength` as the remedy. **Add his measurement to that row as external corroboration** rather than opening a new item.
**Acceptance:** `basis_status`-style structured field defined and documented; the same treatment specified for `anchoring_method`; GAP-EXEC-002 annotated with the external measurement; no corpus values changed in this task.
 
---
 
## 19. Definition of done
 
- [ ] Tasks 1 to 11 and 13 to 18 complete; **Task 12 untouched** and marked GATED in the changelog
- [ ] `CHANGELOG.md` has one dated entry per task describing what changed and why
- [ ] All new vocabularies are **closed** sets in `docs/06-controlled-vocabularies.md`
- [ ] Every new or changed field key is `lower_snake`; every new enum value is `lower_snake`
- [ ] **No em dashes anywhere** in any file touched (grep the diff)
- [ ] British spelling; "Magentix AI" never bare "Magentix"
- [ ] No schema file published; no conformance claim added or strengthened
- [ ] No fabricated digests, signatures, timestamps or addresses
- [ ] **The corpus bytes are unchanged.** Verify the published digests still match: fin chain head `71c10986…` / bundle `b45f7c47…`; ind `93733e6a…` / `b926af903…`. A clean regen must still produce `git diff --stat` empty
- [ ] The new non-ASCII vectors (Task 6) do not alter any existing pinned value
- [ ] Every external credit points to a public source; no private source named
- [ ] One commit per task, task number in the message, not squashed
## 20. Notes for the human reviewer (Martin)
 
- **Task 14 is the fastest win here and it is overdue.** Colin asked twice, a week ago, and answering it in the thread costs one comment. The repo half is small; the courtesy half matters more.
- **Task 15 (reference verifier) is the largest single piece of work** and it unblocks Tasks 5, 6 and 9 from being testable rather than documented. Two external parties have now named its absence in public.
- **Task 12 needs your go-ahead and a supersession announcement**, not just permission. Three parties published results against digests this work order will change. All three have re-run voluntarily before, so the cost is courtesy, but only if the boundary is announced rather than discovered.
- **Task 13 carries the reputational risk.** Crediting external contributors by name builds the relationships; a mis-attribution in a public repo is worse than no attribution. Review those notes before the push.
- **Task 7 (`docs/09a`) publishes an open question under the project's name** and invites people to break it. That is deliberate and it is the register this ecosystem responds to, but confirm you want it out before the push.
- **Separately, and not a Cursor task:** Colin's 13 Aug comment offering canoncheck notarisation into a witnessed, Bitcoin-anchored transparency log with an offline inclusion proof is unanswered, and it is a credible **second lane for EB-004** alongside Walter Hawkins's Coston2 notary. Worth a reply on its own merits, and it reduces the concentration risk of depending on a single community anchoring operator.
 
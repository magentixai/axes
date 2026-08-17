# Field origin notes (why this field exists)

House style for catalogue fields, starting with Module 01 and every field Work Order 16 touches. Pattern documented in [README.md](README.md).

```
**What it records.** One sentence, factual.
**Why it exists.** The concrete failure it prevents, with a worked example where one exists.
**What it does NOT do.** The lane boundary, so a reader does not over-read the field.
**Origin.** Where the requirement came from, credited by name or handle where public.
```

Rules: credit real people and public forums accurately; never credit anyone for anything they did not say; never name a private source; keep examples short; **"What it does NOT do" is not optional**.

---

### `corroboration_state`

**What it records.** How far a claim in this envelope has been confirmed by a party other than the one that made it, on a graded scale from uncorroborated to externally anchored.

**Why it exists.** A sealed record can be cryptographically perfect and factually false. An operator running a fleet of agents reported issuing 41 requests to an external service, receiving HTTP 200 on every one, and gaining zero of the outcomes those requests were supposed to produce. Under a three-artifact model that produces 41 well-formed, signable, replayable decisions, controls and outcomes attesting to 41 events that did not happen. The failure is not in the cryptography; it is that the post-execution outcome was the response to the agent's own request, which is self-attestation with a canonicalisation step in front of it. `corroboration_state` is where a record states, honestly, how much better than self-attestation it actually is.

**What it does NOT do.** It does not establish that the external state is what the record claims. A corroboration handle makes independent checking possible; it does not make the claim true. Determining truth requires a defined verifier, observation method, timing condition and acceptance rule, and those are outside this standard.

**Origin.** Raised as the correspondence-versus-integrity problem in microsoft/agent-governance-toolkit discussion #276 by parweb, with the attested-versus-corroborated distinction and the requirement that an outcome handle must not be the write response.

---

### `capture_relationship`

**What it records.** The relationship between the party that captured the evidence and the party that executed the action (self, same domain, deployer domain, independent third party), as established at the commit boundary.

**Why it exists.** Two records can be byte-identical under one digest context and still differ in whether the capturer was issuer-established or self-asserted. A schema that lets the emitting record mint that independence claim is attesting to a fact it did not issue.

**What it does NOT do.** It MUST NOT be self-declared by the emitting schema. A consumer MUST NOT read it as an assertion the envelope itself can support. It records an identity established elsewhere.

**Origin.** Custody axis proposed by neldan00077 (TrustLayers) in AGT #276 / axes#3 / axes#10; reference implementation custody-ref-v1 by giskard09. The not-self-declared rule: Dani Danwin (TrustLayers).

---

### `emitter_independence_level`

**What it records.** How independent the evidence emitter is from the executing agent, as established at the commit boundary.

**Why it exists.** Distinguishing the agent being evidenced from the collector of the evidence is a first-order internal-assurance requirement (REQ-IA-001). Without it, every envelope is self-talk.

**What it does NOT do.** Same as `capture_relationship`: it records an identity established elsewhere. It MUST NOT be self-declared by the emitting schema.

**Origin.** IA 9.2 vocabulary seed; independence and completeness disqualifications contributed by Tersign (Kevin Zhang), axes#2; not-self-declared coordinate: Dani Danwin (TrustLayers).

---

### `assertion_basis`

**What it records.** The epistemic status of a claim: observed, measured, asserted, inferred, derived, or interpreted, at envelope, block, or field scope. The more specific declaration governs.

**Why it exists.** Declaring `observed` once at envelope scope while storing a derived latency (or an unverified identifier) makes a false epistemic declaration about the envelope's own contents with no structural way to tell which field is which.

**What it does NOT do.** It does not make a derived value true, and it does not convert an assertion into an observation. It labels how the value was obtained.

**Origin.** External Assurance three-axis provenance split (docs/06 §2.9); field-scope applicability from WO16 Task 3 after the published anchor envelope's inconsistency.

---

### `identifier_scope`

**What it records.** The linkability of an identifier: global, relying-party pairwise, issuer-internal, or ephemeral.

**Why it exists.** Without it a consumer cannot tell whether two envelopes carrying different subject identifiers describe two subjects or one subject seen from two relying parties. That ambiguity silently corrupts any join. Pairwise identifiers are long established (SAML persistent NameID, OIDC pairwise `sub`, eIDAS sector-specific identifiers, Apple private relay).

**What it does NOT do.** AXES records the identifier, its scope, and a pointer to who can resolve it. It never records the resolution. Linkage lives with the issuer.

**Origin.** x402 Identity WG use case, issue #10, Nicole Dunn / Baselayer.

---

### `verification_status`

**What it records.** Whether a particular identifier in an identifier set has been verified, failed verification, could not be verified, or remains unverified.

**Why it exists.** A party may claim an identifier it does not control. If that claim is recorded as established, downstream attribution, joins and even revenue figures follow the false identifier inside a cryptographically perfect envelope.

**What it does NOT do.** It does not prove control. Verified means a named verifier applied a named method at a named time, not that the identifier is true in the world. It contains the problem; it does not prevent namespace squatting.

**Origin.** x402 Identity WG, Alfred Tom / OMA3 issues #3 and #4; empirical parse-rule support from wowlegend in axes#6.

---

### `entry_basis`

**What it records.** How this identifier entered the record: counterparty-asserted, observed on a live 402 response, credential-backed, or third-party attested.

**Why it exists.** The same string can arrive as an advertisement, as a live observation, or as a signed credential. Treating them as equivalent is how an asserted address becomes "the" payee.

**What it does NOT do.** It is not a verification. `counterparty_asserted` plus `verification_status: verified` is a coherent pair; `observed_live_402` without verification is still only an observation.

**Origin.** Same Identity WG thread as `verification_status` (Alfred Tom / OMA3).

---

### `signer_presence`

**What it records.** Whether authorship is unsigned, stripped (named author, no signature), unverifiable, or invalid.

**Why it exists.** Deleting the `signature` field while leaving the named author in place made a naive verifier return valid, even under a require-signatures flag, because the signature cannot sit inside its own hash input. One "absent" state was covering two different things.

**What it does NOT do.** A top-level fail is a fail-closed aggregate, not a claim that every lower property failed. `stripped` MUST fail regardless of any strictness flag; the attacker chooses whether the verifier runs strict.

**Origin.** Ryan Cason (orionsys); Chou Deyu (Guardian) endorsed keeping the states distinct.

---

### `settlement_role`

**What it records.** A payee's relationship to the value flow: origin (the principal whose value it is, earned or spent), facilitator, or proxy gateway.

**Why it exists.** On-chain `tx.from` under relaying is the facilitator, not the payer. A record that captures a wallet without the economic role cannot distinguish earned revenue from relayed value, so aggregators guess and published volume figures do not reconcile.

**What it does NOT do.** It is a declared fact, not a badge of honesty. Whether to trust the declaration is an evaluator concern. Reputation does not fold into the role. Checkability runs against the `primary` identifier; a mismatch on an `alternative` is a signal, not a disqualification.

**Origin.** Attribution gap named by Mancy Thurston (Paddock) in aggregator requirements; direction-neutral redefinition in WO16 Task 11c after the "earns the value" wording inverted on the payer side.

---

### `anchor_requested_at`

**What it records.** When the emitter requested the external anchor (ISO 8601 UTC).

**Why it exists.** Storing a derived anchoring latency both baked a unit into a key and produced a number that reconciled with no pair of timestamps on the published anchor envelope. Naming the derivation (`anchored_at − anchor_requested_at`) matches the existing three-point time model.

**What it does NOT do.** It is not the lag. The lag is derived. It does not prove the anchor store is real (`basis_status` / D-015 reading rule).

**Origin.** Module 01 three-point time model; D-017; published-vector defect recorded in WO16 Task 4.

---

### `capture_status`

**What it records.** Whether this event was captured, missing (recoverable or not), or lay outside the declared capture boundary.

**Why it exists.** Silence and uninstrumented paths must be distinguishable. The interbank pacs.008 leg in the Golden Trace is `outside_capture_boundary`: honest disclosure, not a hidden gap (GT-006).

**What it does NOT do.** It does not fill the missing evidence. `outside_capture_boundary` is not an excuse to omit a commit that was inside the boundary.

**Origin.** External Assurance `capture_status` (EA 10.3); practice confirmation GT-006.

---

### `evidence_gap_recorded`

**What it records.** An event_kind (and the envelope that carries it) stating that a required evidence element is missing, with the gap declared rather than implied by silence.

**Why it exists.** Evidence gaps disclosed, never hidden, is doctrine. A derivation that spans a recorded gap returns `derived_with_gap` rather than a bare number.

**What it does NOT do.** Recording the gap does not repair it and does not authorise a reader to treat adjacent envelopes as complete.

**Origin.** Standards Group event_kind merge (docs/06 §2.10); doctrine evidence-gap rule.

---

### `correlation_finding` (event_kind)

**What it records.** A witnessed cross-event finding no single decision produced.

**Why it exists.** Three individually permitted tool calls can compose into a credential-exfiltration finding no per-call gate can see. Portable evidence must carry that finding on the same append-only chain.

**What it does NOT do.** The custodian attests that a finding was emitted, by whom and when. It never asserts the correlation itself.

**Origin.** Ioannis Loutsis (Agentmetry); witnessed-not-authored discipline, Dani Danwin (TrustLayers).

---

### `triage_disposition` (event_kind)

**What it records.** A later human disposition of a correlation finding, on the same chain.

**Why it exists.** The finding and its triage are different facts at different times. Editing the finding envelope would violate append-only.

**What it does NOT do.** It does not convert the custodian into a SOC. Disposition is witnessed; the correlation remains owned by the correlator.

**Origin.** Same as `correlation_finding`.

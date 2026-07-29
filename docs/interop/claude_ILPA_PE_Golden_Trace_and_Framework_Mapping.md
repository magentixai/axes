# ILPA / Private-Equity Golden Trace  -  Scenario Spec & Framework-Mapping Issue Outline

**Purpose:** Capture the ILPA/PE thread so the direction and the build-vs-issue decision are not lost, and stand up the two concrete next artifacts: the PE Golden Trace scenario spec (the third worked vertical), and the ILPA↔AXES Framework-mapping issue outline (ready to post verbatim).

**Status:** working capture + design spec. The scenario is not yet built; the Framework-mapping issue is not yet opened. Both are gated on the build, per the decision in §1.

**Provenance:** ILPA/PE discussion thread, July 2026. ILPA specifics in §2 are grounded in that thread's web research (sources listed there) and should be re-verified against ILPA's published v2.0 suite before the mapping is finalised, because the suite is mid-rollout across 2026–27.

**Naming in force:** the standard is **AXES** (Autonomous eXecution Evidence Standard, locked 20 July 2026); the envelope artifact remains the **Standards Envelope (SE)**; **ARBITR** is the proprietary implementation/interpretation layer; **Magentix.ai** hosts the repo (`magentixai/axes`) and the AXES reports section on the website. British spelling throughout. §4 (the issue outline) is written em-dash-free so it can be pasted straight into GitHub as an AXES issue.

**Sits alongside:** the financial Golden Trace (accounts-payable, ISO 20022  -  run `APRUN-2026-06-09-A`, delegation `AD-7844`) and the manufacturing example (QIF / ISA-95). This is the **third vertical**, proving cross-industry generality and opening the PE/LP market in one move.

---

## 1. Decision captured (the build-vs-issue call)

The thread resolved a real ambiguity: *is a PE/ILPA run a change to the standard, or an instance of it?* The answer, and the reason it matters, are load-bearing enough to record.

**A PE/ILPA run is an instance of AXES, not a change to it.** It decomposes into the identical five-element skeleton every AXES scenario uses  -  delegated authority, pre-commit controls, commit boundary, reconciliation, hash chain  -  and simply references ILPA artifacts where the AP example references ISO 20022 and the factory example references QIF and ISA-95. So the worked example itself does **not** belong "in the standard" as an issue. Raising "should AXES support PE?" as a standard issue would be answering a question the skeleton already answers.

**What does legitimately belong against the standard is the ILPA mapping**  -  and the correct intake category is **Framework mapping issue** ("gap or error mapping AXES onto a runtime, framework, or protocol"). Not *Evidence gap*  -  that template is for a scenario the schema cannot evidence, and this one it can. The mapping is where the ILPA XML data definitions ↔ AXES field correspondence gets recorded, assessment-routed through the CONTRIBUTING 11-question process, and captured in the decision register, rather than asserted on a marketing page.

**Ordering (build-first):**

1. **Build the PE Golden Trace first**, as the worked corpus. Building is what tells us whether it is a clean instance (no standard change) or whether it stresses something real  -  most likely the **event-to-period rollup** (many calls and distributions over a quarter aggregating into an ILPA Capital Account Statement), which is exactly the existing **Topology** territory. That is not knowable until it is built.
2. **Open the Framework-mapping issue (ILPA ↔ AXES)** backed by the draft mapping the build produces  -  plus a **Topology modelling issue** or a **Field proposal** only if the build genuinely surfaces one. Each issue then arrives with running structure behind it, not as a preference.
3. **Publish the third example** on the Magentix AXES reports section and in `examples/` once built and verified, alongside financial and manufacturing.

**Two reasons build-first is right, not merely tidy:**

- **It is our own doctrine.** "Running code before words" is the same discipline used in x402 and the point Rul1an was hammering in the Microsoft thread. An ILPA standard-issue opened before there is a corpus is a preference; opened after, it is evidence.
- **Market timing and control of the reveal.** A finished, re-verifiable artifact beats a half-built aspiration when shown to LPs and GPs, and opening the Framework-mapping issue *does* telegraph the PE move. Telegraphing is on-brand (openness is the strategy), but the *when* is ours to choose. Building first keeps that option open.

**Net:** host the third Golden Trace as an example (it is an instance); let the one genuinely standard-touching part  -  the ILPA mapping  -  go in as a Framework-mapping issue with the corpus behind it.

---

## 2. ILPA grounding (as captured July 2026  -  re-verify before finalising the mapping)

The fact that changes the difficulty in our favour: **ILPA does not only publish spreadsheet templates  -  it publishes an XML-compliant version of the Reporting Template with formal data definitions, plus a Fund-of-Funds XML variant.** Interop is therefore a *mapping onto an existing structured vocabulary*, not a schema we have to invent. This is the same shape as mapping to ISO 20022.

Key points to hold:

- **Difficulty:** moderate, and nearly all of it is **domain mapping**, not anything structural. The skeleton already fits.
- **The v2.0 suite is a moving target (2026–27 rollout):** Reporting Template / Capital Account Statement effective for 2026 periods; Capital Call & Distribution (CC&D) v2.0 effective Q1 2027; Performance Template in 2027. **Map to the XML definitions and version the mapping** rather than chasing spreadsheet revisions.
- **ILPA is a voluntary industry standard**, driven by LP demand for comparability  -  *not* a regulatory mandate. The SEC Private Fund Adviser Rules that would have mandated standardised reporting were vacated by the Fifth Circuit in mid-2024, so current momentum is market-driven. This *helps* the case: voluntary adoption runs on trust signals, which is precisely what an evidence layer supplies.
- **The real regulatory clock sits alongside ILPA, not inside it:** operational-resilience and record-keeping regimes  -  **DORA**, **AIFMD II** (EU), and the **EU AI Act Article 26** deployer-log-custody argument. These are where "regulation requires this" is actually true; ILPA is comparability, not compliance.

**Layer separation (the usual framing).** ILPA standardises *what the numbers are and how they are presented*; AXES evidences *that an autonomous process produced those numbers under proper authority, in scope, and that an LP or auditor can verify it without taking the GP's word*. Complementary, not competing:

> **AXES is to ILPA reporting what TLS is to HTTP.** It does not replace an ILPA template; it makes an ILPA-shaped artifact emitted by an automated process trustworthy.

This is the same move made in x402 ("the blockchain proves a transfer occurred; it does not prove it was authorised, in-scope, or properly delegated").

**Honest near-term framing (do not oversell autonomy).** Genuinely autonomous capital calls and distributions are early. Today it is fee engines, notice generation, and reconciliation bots that are automating. So the pitch is not "autonomous PE fund ops"  -  it is *"as these pieces automate, their ILPA outputs need execution evidence a GP, LP and auditor can trust."* That honest-limits framing is stronger, not weaker, and it is the scoped-assurance discipline in action.

---

## 3. PE Golden Trace  -  scenario spec

A worked instance: a PE fund treasury/ops agent, acting under delegated authority, runs a capital call and a distribution, and a quarter-end rollup renders an ILPA CC&D notice and Capital Account Statement  -  with the four AXES audience reports drawn from the single hash-chained record.

All identifiers below are **provisional placeholders** for the build. Run/delegation IDs follow the corpus style (`APRUN-2026-06-09-A`, `AD-7844`).

### 3.1 The fund and parties (illustrative)

- **Fund:** *Meridian Capital Partners IV, L.P.*  -  a mid-market buyout fund. (Fictional; a self-contained synthetic fund, like the AP example's synthetic company.)
- **GP:** *Meridian Capital GP IV, LLC*, acting under the Limited Partnership Agreement (LPA).
- **Fund administrator:** *Aptera Fund Services* (third-party admin)  -  relevant to corroboration and custody grading, because some evidence is admin-captured rather than GP-captured.
- **LPs:** a small set of institutional LPs (e.g. a public pension, a university endowment, a fund-of-funds) with differing commitments  -  enough to exercise per-LP allocation, comparability, and the FoF XML variant on at least one LP.
- **Executing agent:** a treasury/fund-ops agent (the "Meridian ops agent") emitting SE envelopes via an AXES connector.

### 3.2 The delegated authority

- **Delegation receipt:** `AD-8xxx` (provisional; parallel to `AD-7844`). Granting principal: the GP's CFO / Fund Controller. Grantee: the Meridian ops agent.
- **Authority scope (bounded by the LPA):** issue capital call notices under the LPA's call mechanics; process distributions and apply the distribution waterfall; accrue management fees and carried interest. Hard bounds: **per-LP commitment caps**, **uncalled-capital / recycling limits**, **LPA call-notice period and value-date rules**.
- **SE representation:** `authority_scope` (scalar, for indexing) + `authority_context` (rich) carrying the LPA reference, the delegation scope, and `delegation_receipt_id` = `AD-8xxx`. The granting principal is captured (`delegator_id`, per GAP-IA-008).

### 3.3 The runs

- **Run 1  -  Capital call.** A drawdown across the LPs for a specific portfolio investment plus fees, issued as **ILPA CC&D notices** (one per LP). Exercises: commitment-cap and recycling checks, beneficiary/bank-detail verification, maker-checker, call-notice-period compliance.
- **Run 2  -  Distribution.** Return of capital plus realised gain from an exit, with the **distribution waterfall** applied, issued as **ILPA CC&D distribution notices**. Exercises: waterfall inputs, offsets/recycling, per-LP allocation, value-date.
- **Run 3  -  Quarter-end rollup.** Aggregation of the calls, distributions, fee/carry accruals and NAV movements into a per-LP **ILPA Capital Account Statement** (capital-account roll-forward). This is the rollup run that most likely stresses the standard (see §3.6).

**Provisional run IDs:** `PECDRUN-2026-Q3-A` (call), `PECDRUN-2026-Q3-B` (distribution), `PECAPRUN-2026-Q3-ROLLUP` (capital-account statement), tied together by trace/continuation lineage.

> **Boundary of responsibility (state this plainly in the example).** AXES does **not** compute the waterfall, the fee/carry calculation, or NAV. It evidences that whatever engine computed them ran **under authority, in scope, with reconciliation, and with an unbroken chain**. AXES is evidence, not the fund-accounting engine. This is the ILPA-vs-AXES layer line applied at the run level.

### 3.4 ILPA artifacts at the commit boundary

- **ILPA CC&D notice (v2.0)**  -  sits at the commit boundary of Run 1 and Run 2. Structurally the same role ISO 20022 `pacs.008` plays in the AP example: the artifact issued / the cash moved.
- **ILPA Capital Account Statement**  -  the period-oriented artifact produced by Run 3.
- Bank statement (`camt.053`-equivalent) and the commitment register are the **reconciliation sources**, not commit-boundary artifacts.

### 3.5 Five-element decomposition (mapped to SE)

| # | Skeleton element | In this scenario | SE representation (illustrative) |
|---|---|---|---|
| 1 | **Delegated authority** | GP CFO → ops agent under the LPA; bounded by commitment caps, recycling limits, call mechanics | `authority_scope` + `authority_context` (LPA ref, scope); `delegation_receipt_id = AD-8xxx`; `delegator_id` |
| 2 | **Pre-commit controls** | Commitment-cap check; uncalled-capital / recycling-limit check; beneficiary & bank-detail verification; maker-checker; call-notice-period / value-date | `external_commit.attempted` with control evidence: cap/limit checks; `identity_verification_ref` / `consent_authority_match` (bank details); `dual_control_required_indicator`, `maker_ref` / `checker_ref`; `deadline_ref` + value/settlement date |
| 3 | **Commit boundary** | CC&D notice issued / cash moved; LP inbound-wire leg declared outside the capture boundary by design | `external_commit.completed`; `corroboration_state` graded per fact; `capture_boundary` declaration (LP wire leg `outside_capture_boundary`, parallel to the interbank `pacs.008` leg in the AP example) |
| 4 | **Reconciliation** | Called vs committed against the commitment register; cash against the bank statement; authority utilisation | `source_system_reconciliation` event (GT-001); `authority_utilisation_ratio` (called capital vs remaining commitment  -  the leading-indicator move from GT-005) |
| 5 | **Hash chain** | Append-only envelope chain across all three runs; corrections as new envelopes; external anchor | `envelope_hash` chain; `supersedes_envelope_id` + `amendment_reason` for a corrected notice; `external_anchor_ref` (SIMULATED in v1; real `distributed_ledger` anchor in v2 per EB-004 / axes#3) |

### 3.6 Event-to-period rollup (the Topology-stressing part)

AXES is **event-oriented** (per-action envelopes); ILPA reporting is **period-oriented** (quarterly statements, capital-account statements). Run 3 requires a **period-scoped rendering over a set of runs**: many CC&D events across a quarter aggregating into one Capital Account Statement per LP.

This is a **lineage/rollup design** and touches exactly the existing **Topology** issue type (the repo already models continuation/trace topology, e.g. `cross_scope` / `continuation_ref`). It is the single most likely place the build surfaces a genuine standard question. **Do not pre-decide it**  -  build Run 3, see whether the existing topology primitives express "these N envelopes roll up into this one period statement" cleanly, and open a **Topology modelling issue** *only if* they do not.

### 3.7 Report views (one execution, many professional truths)

The standard's canonical four-audience reports (board / audit / regulator / forensic  -  Reports A–D in the AP corpus) reframed for PE stakeholders, plus the ILPA artifact itself as the LP-facing presentation rendering. All drawn from the single record; none requiring separate evidence collection.

| AXES audience report | PE stakeholder | What it answers here |
|---|---|---|
| **A  -  Board** | GP Investment Committee / fund board | Did the fund call and distribute within authority, on time, without breach? Authority utilisation; exceptions; board-action items |
| **B  -  Audit** | Fund auditor + LP operational due diligence | Capital-account roll-forward, fee/carry calculation basis, reconciliation to bank and commitment register, control operation (maker-checker)  -  every statement resolving to named fields |
| **C  -  Regulator** | SEC / AIFMD II / DORA / EU AI Act Art 26 | Deployer log-custody of the automated process, operational resilience, record-keeping  -  the Art 26 custody position made explicit (see the AXES custody-axis note) |
| **D  -  Forensic** | Fraud investigator / forensic | Provenance of the CC&D notice and identity-binding of bank details; custody axis (`capture_relationship`); spoofing resistance  -  the EFD thesis in a new domain (see §5) |
| **(presentation)  -  LP view** | Limited Partners | The **ILPA-shaped artifact itself** (CC&D notice + Capital Account Statement) rendered from the single record. ILPA's own comparability vocabulary; AXES simply makes it trustworthy |

The LP view is deliberately **not** a fifth report type. It is the ILPA artifact as a presentation-layer rendering  -  which is exactly what keeps this a clean *instance* of the standard.

### 3.8 Scoped-assurance / honest-limits notes (build these into the bundle)

- **v1 stubs, declared:** signatures are `SIG-STUB`; the external anchor is `SIMULATED`. State the reading rule in the bundle, as the AP corpus does. A SIMULATED anchor is not a closed independent bound.
- **Autonomy is nascent:** frame as "as fee engines, notice generation and reconciliation bots automate, their ILPA outputs need trustworthy execution evidence"  -  not "autonomous fund ops today".
- **ILPA is voluntary:** AXES asserts execution-under-authority, **never** guaranteed ILPA conformance or regulatory compliance.
- **Moving target:** map to the XML definitions; version the mapping against the v2.0 suite.
- **AXES ≠ the accounting engine:** it does not compute the waterfall, fees, carry, or NAV (§3.3).

---

## 4. Framework-mapping issue outline  -  ready to post verbatim

*The block below is written em-dash-free and in British spelling so it can be pasted directly into GitHub as an AXES issue once the PE Golden Trace corpus exists to back it. It is an **outline**: the mapping-annex rows are the shape to complete from the build, not the final field set.*

---

**Title:** Framework mapping: ILPA Reporting Standards (XML definitions) <-> AXES / SE evidence fields

**Type:** Framework mapping issue

**Status:** Draft. Do not merge before the PE Golden Trace corpus (`PECDRUN-2026-Q3-*`) is built and verified. The corpus is the backing evidence for every row here.

**Summary**

ILPA publishes an XML-compliant Reporting Template with formal data definitions, plus a Fund-of-Funds XML variant. This issue records the mapping between those ILPA data definitions and AXES / SE evidence fields, so that an ILPA-shaped artifact (a Capital Call and Distribution notice, a Capital Account Statement) emitted by an automated PE treasury process can be evidenced as having been produced under proper authority, in scope, and reconcilable, without an LP or auditor taking the GP's word.

AXES does not replace ILPA and does not compute fund-accounting values. ILPA standardises what the numbers are and how they are presented. AXES evidences that an autonomous process produced them under authority. The relationship is the same as ISO 20022 in the accounts-payable example: AXES references the domain artifact at the commit boundary, it does not redefine it.

**In scope**

- Mapping of ILPA CC&D notice data elements and Capital Account Statement data elements to AXES / SE fields, derived forms, ARBITR proprietary outputs, or presentation-layer labels.
- Declaring, per ILPA element, which AXES layer owns it (open SE, derived, ARBITR proprietary, or presentation).
- Identifying any controlled-vocabulary additions ILPA mapping requires.
- Flagging the event-to-period rollup as a candidate Topology modelling issue if the corpus build surfaces it.

**Out of scope**

- Any claim of ILPA conformance or certification. AXES evidences execution, it does not certify ILPA compliance.
- Fund-accounting computation (waterfall, fees, carry, NAV). AXES evidences that the computing process ran under authority, not the arithmetic itself.
- Freezing to a spreadsheet template revision. Map to the XML definitions and version against the v2.0 suite.

**Mapping annex (complete from the build; rows below are the shape, not the final set)**

| ILPA XML data element (illustrative) | Owning AXES layer | AXES field / derived form / label | Notes |
|---|---|---|---|
| Fund identifier | open SE | `org_id` / `authority_context` fund ref | Stable fund reference on every envelope |
| LP identifier | open SE | `target_resource_id` (opaque) / presentation label | Opaque or hashed; comparability label at presentation |
| Commitment reference and cap | open SE + derived | `authority_context` scope; `authority_utilisation_ratio` | Cap is an authority bound, utilisation is derived |
| Call amount | open SE | commit-boundary artifact value on `external_commit.completed` | The notice value at the commit boundary |
| Call due date / notice period | open SE | `deadline_ref` + deadline type; value/settlement date | Exercises call-mechanics compliance |
| Call purpose | open SE + presentation | `operation` + `semantics` label | Portable key open, client label at presentation |
| Beneficiary bank details | open SE + derived | `identity_verification_ref`, `consent_authority_match`; `capture_relationship` | The fraud-provenance surface (see forensic view) |
| Contributions (period) | open SE aggregated | rollup over `external_commit.completed` (call) envelopes | Period rollup, Topology territory |
| Distributions (period) | open SE aggregated | rollup over distribution commit envelopes | Waterfall output referenced, not computed |
| Management fee / carry accrual | open SE ref + derived | fee/carry accrual event ref; ARBITR interpretation | AXES references the accrual, does not compute it |
| Opening / closing capital account balance | derived + presentation | capital-account roll-forward view | Period-oriented render over the run set |
| Realised / unrealised gain, NAV | out of scope for computation; referenced | evidence pointer to the source-of-record value | AXES evidences provenance, not the valuation |

**Assessment against the CONTRIBUTING 11-question route**

1. Does it support execution accountability? Yes. It binds ILPA outputs to authority, scope, and reconciliation.
2. Does it support board, audit, regulator, or forensic reporting? All four, plus the LP presentation view.
3. Is it vendor-neutral? Yes. It maps to a public ILPA data standard, not to any product.
4. Is it runtime-neutral? Yes. Nothing here depends on a specific agent framework.
5. Does it create unnecessary implementation burden? No. It is a mapping annex against existing fields, not new required core fields, subject to the build.
6. Open schema or ARBITR proprietary? Split is declared per row in the annex. Evidence fields open, interpretation and client labels proprietary or presentation.
7. Does it duplicate an existing field? To be confirmed row by row against the field catalogue during completion.
8. Does it require a controlled-vocabulary update? Possibly, for PE-specific operation or purpose keys. Flag any in the annex.
9. Does it affect conformance? No new conformance level. May add conformance vectors for PE commit-boundary and rollup cases.
10. Does it introduce privacy or security risk? Handle LP identifiers as opaque or hashed. Bank details via reference and verification status, never raw in the envelope.
11. Does it support the report-backwards design rule? Yes. Every mapped element traces to a statement in one of the audience reports or the LP artifact.

**Dependencies**

- Backed by the PE Golden Trace corpus (`PECDRUN-2026-Q3-*`). Do not proceed without it.
- Potential **Topology modelling issue** for the event-to-period rollup (many CC&D events aggregating into one Capital Account Statement per LP), opened only if the build shows the existing topology primitives do not express it cleanly.
- Potential **Field proposal** or **Controlled vocabulary proposal** only if the build surfaces a genuine gap.

**Acceptance criteria**

- Every ILPA CC&D and Capital Account Statement data element in the target XML definitions has a mapping row with an owning layer.
- Each open-SE row resolves to a field that exists in the catalogue, or is raised as an explicit Field proposal.
- The mapping is versioned against a stated ILPA v2.0 suite version.
- A reviewer can trace each mapped element back to a statement in one of the audience reports or the LP artifact.

**Versioning note**

Map to the ILPA XML data definitions and version this mapping against the v2.0 suite (Reporting Template and Capital Account Statement effective for 2026 periods, CC&D v2.0 effective Q1 2027, Performance Template 2027). Do not track spreadsheet revisions.

---

## 5. Why this vertical is compelling for AXES specifically

- **It hits the LP–GP trust gap ILPA exists to narrow.** Voluntary adoption runs on trust signals; an evidence layer supplies exactly that.
- **It plays the multi-audience rendering strength.** LP, GP, fund admin, auditor and regulator all need different cuts of the same capital activity  -  ILPA's own thesis mirrors "one execution, many professional truths".
- **It lands the fraud-provenance thesis directly.** Fraudulent capital-call notices and spoofed bank details are a live, growing loss vector in private markets. Provenance-led identity binding on the notice  -  `capture_relationship` / `corroboration_state` plus bank-detail verification  -  is the **Enhanced Fraud Data (EFD)** argument in a new domain. Cross-reference the AXES custody-axis design note: this is where the custody axis earns its keep in PE.
- **It proves cross-industry generality.** Financial (ISO 20022) + manufacturing (QIF / ISA-95) + PE (ILPA) is a strong breadth signal for the standard.

---

## 6. Next actions (ordered)

1. **Build Run 1 (capital call)** as `PECDRUN-2026-Q3-A`: synthetic fund, delegation `AD-8xxx`, per-LP CC&D notices, five-element decomposition, hash chain, honest v1 stubs.
2. **Build Run 2 (distribution)** as `PECDRUN-2026-Q3-B`: waterfall output referenced (not computed), per-LP allocation, value-date.
3. **Build Run 3 (rollup)** as `PECAPRUN-2026-Q3-ROLLUP`: per-LP Capital Account Statement over the run set. **Watch the topology.** Record whether existing primitives express the rollup cleanly.
4. **Generate the four audience reports + the LP artifact rendering**, every sentence resolving to named fields, with scoped-assurance notes from §3.8.
5. **Draft the mapping annex** from the build; complete the §4 issue outline.
6. **Open the Framework-mapping issue** (§4), plus a Topology modelling issue or Field proposal only if the build surfaced one.
7. **Publish** the third example to `examples/` and the Magentix AXES reports section, alongside financial and manufacturing. Choose the timing deliberately, since opening the issue telegraphs the PE move.

---

## 7. Open questions / risks to hold

- **Event-to-period rollup (highest).** Does existing topology express "N envelopes roll up into one period statement", or does it need a modelling extension? Resolved only by building Run 3.
- **Moving target.** The v2.0 suite is mid-rollout. Confirm current effective dates and the exact XML definition version at mapping time; version the mapping accordingly.
- **Autonomy nascency.** Keep the pitch honest (§2). The near-term buyers are the automating pieces (fee engines, notice generation, reconciliation bots), not fully autonomous fund ops.
- **Layer-split placement.** A few rows (fee/carry accrual, capital-account balances) sit on the open/derived/proprietary boundary. Decide each per the 11-question route, not by default.
- **Regulatory framing accuracy.** ILPA is voluntary. The regulatory weight is DORA, AIFMD II, and EU AI Act Art 26  -  cite those, not ILPA, when the argument is "regulation requires this".

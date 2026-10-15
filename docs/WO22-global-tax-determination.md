# WO22 - Global tax determination: inputs, components and recomputable results

**Repo:** `magentixai/axes`
**Branch to work from:** `main` (corpus of record is gt-v2.1, tag `corpus/2026-10-12-gt-v2.1`; this work order does not touch it)
**Raised by:** Martin Sansone · **Date:** 15 Oct 2026
**Status:** ready to implement. Nothing in this work order is normative until its decision-register entries are made.
**Driver:** Tax WG review (Oct 2026) of the trust-lanes tax example: US sales tax is sourced to the buyer's location, so a seller cannot quote before the buyer has declared it. Checking that point against AXES showed the whole tax surface is shaped around EU VAT business-to-business reverse charge. This work order makes the tax record jurisdiction-neutral, so any indirect-tax system is a profile, not a fork.

---

## 0. Read this before touching anything

**Scope anchor.** AXES is broad-breadth: tax determination is a property of an M2M transaction of any kind, not of payments only. The x402 tax lane is one binding of what this work order defines, and the first one exercised.

Current state, verified 15 Oct 2026 at `ba2710f`:

- The envelope `tax` block (`examples/x402-b2b-vat/*/envelopes.jsonl`, emitted by `tools/x402/generate_b2b_vat_example.py`) carries one `tax_profile_ref`, one `tax_treatment_type`, `determination_status` and `principal_attribution_status`. **No jurisdiction, no components, no inputs.**
- The `supplier` block carries a single `supplier_vat_id`.
- `schema/x402-wire/tax-1.json` has the server quote `{determinationStatus, taxResultRef}` in the `402` and the buyer present its declaration **after** the quote.
- `profiles/x402_eu_vat_b2b_tax_authority_v1.json` checks reverse charge and supplier VAT id only.
- **None of these tax fields appear in `docs/05-field-catalogue/` or `docs/06-controlled-vocabularies.md`.** They exist only in the example generator, the example and one profile.
- `docs/x402-trust-lanes-solution.md` describes the tax lane with the quote first.

Reference specification: x402-foundation/wg-tax **PR #5, revision 6** (`67a09b1`, 26 Sep 2026), *Buyer-side tax declaration*: https://github.com/x402-foundation/wg-tax/pull/5 . It is already declaration-first (its §6.7), already has `liableParty` and `mechanism` axes (§5.2), and is structured as a common contract plus a first profile, `eu-vat`. Its gaps for global use are listed in §4 below.

**Task 0, mandatory, before writing any code:** read in full `tools/x402/generate_b2b_vat_example.py`, `schema/x402-wire/tax-1.json`, `profiles/x402_eu_vat_b2b_tax_authority_v1.json`, `docs/x402-trust-lanes-solution.md`, `docs/06-controlled-vocabularies.md`, `docs/20-naming-rules.md`, and PR #5 rev 6. Write a short inventory (`docs/WO22-task0-inventory.md`) of every tax and supplier field that exists today, where it is emitted, where it is checked, and which tool reads it. **Where this work order and the repo disagree, the repo is right and the work order is stale: say so rather than following it.**

---

## 1. Hard constraints - violating any of these is a failed work order

- **Do not regenerate or edit the gt-v2.1 or gt-v2.0 corpora.** New module, new examples, new vectors, new tag. If any change would alter a published digest, stop and escalate to Martin.
- **AXES never determines tax.** It records a determination, the facts it rests on, and the engine and rule version that produced it. No rates, thresholds, sourcing rules or tax computation anywhere in this repo.
- **No jurisdiction's law asserted as fact.** Examples and vectors are synthetic and labelled so. Profile packs cite their source (a published spec, a WG decision) or carry an `unsettled_question_notes` entry.
- **Absence is never zero.** An undetermined result carries no components. A `null` rate is not `0`. (Carried from PR #5 §4.3 and §6.3.)
- **Personal data stays out of shared artefacts.** Buyer location and tax identifiers are recorded as salted commitments wherever the record can leave the party that holds it.
- **`tax-1` and the existing B2B VAT example keep verifying.** Additive changes only; `supplier_vat_id` becomes a deprecated alias, not a removal.
- **Names follow `docs/20-naming-rules.md`** (lower_snake in records, x402 spelling on the wire, no unit-in-key).
- **No new runtime dependencies** in verifier or evaluator code. Python standard library only.
- **British English. No em dashes** in any file that could become public-facing.

---

## 2. The design in four moves

### 2.1 Declare, resolve, quote, accept

The seller states what it needs to know before it states a price.

1. The buyer's agent may send its declaration with the first request (PR #5 §2.3 header, seller-only, never through a facilitator). Best case: one `402`, already tax-inclusive.
2. If it did not, the `402` tax lane carries `inputsRequired`: the fact types and minimum granularity each offered profile needs (for example `buyer.location@iso3166-2+postal`, `buyer.exemption`, `buyer.tax_id`), plus `floor`. The quote is `UNDETERMINED`.
3. The buyer repeats the unpaid request with the declaration; the seller re-quotes; the buyer pays. The paid retry re-sends the declaration so the server rebuilds identical requirements.
4. The quote carries `basisRef` (digest of exactly the inputs used) and `pricingBasis` (`tax_inclusive` | `tax_exclusive`). **The signed amount equals the quoted total.**

x402 v2 (`e95b066`) allows this unchanged: the server derives `accepts[].amount` itself and nothing forbids a second `402`. The gap is client support, not protocol. Do not use an `upto` flow for tax: it fixes the tax after the buyer signs.

### 2.2 A result with components, not a treatment

One determination holds **N components**, so stacked jurisdictions (state plus local, federal plus provincial) and several tax systems in one exchange are native.

Per component: `jurisdiction_ref`, `tax_type`, `treatment_type`, `liable_party_role`, `mechanism`, optional `rate` (`schema/ratio.schema.json`), `taxable_base` and `tax_amount` (`schema/amount.schema.json`), `legal_basis_ref`.

Reverse charge is not a special case: it is `liable_party_role: buyer` with `mechanism: reverse_charge`. The same axis carries self-assessed use tax, withholding and marketplace collection.

### 2.3 Inputs are facts with provenance

Each input: `fact_type`, `value` or `value_commitment`, `source_type`, `verification_status` (the four-state result: `verified` | `contradicted` | `indeterminate` | `not_evaluated`), `evidence_refs`.

The record answers the auditor's first question, "on what facts?", and keeps "the buyer declared X" separate from "a registry confirmed X". An agent's network address is `evidence_derived` and may be recorded as `contradicted` against a declared location: it identifies infrastructure, not the principal.

### 2.4 Engine-neutral and recomputable

`resolver`: `resolver_id`, `ruleset_ref`, `ruleset_version`, `rates_as_of`, `tax_point_at`. A relying party re-runs the same engine at the same rule version on the same inputs and compares. Identifiers are namespaced by their publisher; no central registry is assumed.

Seller facts follow the same pattern: `supplier.tax_registrations[]`. Nexus is simply "a registration exists in that jurisdiction".

---

## 3. Tasks

Sequence: **T0 → T3 → T1/T2 → T4 → T5 core → T6 → T5 packs → T7/T8 → T9.**

### T1. `tax_determination` record block

New field-catalogue module (next free module number; check `docs/04-module-map.md`). Replaces the flat `tax` block for new emitters.

```json
"tax_determination": {
  "profile_refs": ["x402-tax:eu-vat@rev6"],
  "determination_status": "determined",
  "pricing_basis": "tax_exclusive",
  "components": [
    {
      "jurisdiction_ref": {"iso_3166": "DE"},
      "tax_type": "vat",
      "treatment_type": "taxable",
      "liable_party_role": "buyer",
      "mechanism": "reverse_charge",
      "rate": null,
      "legal_basis_ref": "eu:vat-directive:art-196"
    }
  ],
  "inputs": [
    {
      "fact_type": "buyer_establishment",
      "value_commitment": "sha256:…",
      "source_type": "declared_buyer",
      "verification_status": "verified",
      "evidence_refs": ["…"]
    }
  ],
  "resolver": {
    "resolver_id": "…",
    "ruleset_ref": "…",
    "ruleset_version": "…",
    "rates_as_of": "…",
    "tax_point_at": "…"
  },
  "basis_ref": "sha256:…",
  "result_ref": "sha256:…"
}
```

`determination_status`: `determined` | `partial` | `undetermined`. `undetermined` MUST carry no `components`. `partial` is new relative to PR #5 and must be justified in the decision register or dropped.

`jurisdiction_ref`: `{iso_3166: <alpha-2 or 3166-2>, local_code?: {system: <named code system>, value}}`. The code system is always named; this work order picks none.

**Acceptance:** the existing B2B VAT example re-emitted under T1 maps to exactly one component (`DE`, `vat`, `taxable`, `buyer`, `reverse_charge`), and the old `tax` block is still emitted alongside it for the deprecation window.

### T2. Supplier registrations

`supplier.tax_registrations[]`: `{jurisdiction_ref, registration_scheme, registration_id | registration_id_commitment, verification_status}`. `supplier_vat_id` stays as a deprecated alias with a decision-register entry naming its removal condition.

### T3. Controlled vocabularies (`docs/06`)

Add, each marked closed or open with an extension rule:

| Vocabulary | Initial values |
|---|---|
| `tax_type` | `vat` · `gst` · `sales` · `use` · `consumption` · `excise` · `withholding` · `other` |
| `treatment_type` | `taxable` · `exempt` · `zero_rated` · `not_in_scope` · `not_due` |
| `liable_party_role` | `seller` · `buyer` · `marketplace` · `withholding_agent` · `none` |
| `mechanism` | `seller_collected` · `reverse_charge` · `self_assessed` · `withheld` · `marketplace_collected` · `none` |
| `fact_type` | `buyer_establishment` · `buyer_use_location` · `buyer_delivery_location` · `buyer_taxable_status` · `buyer_tax_id` · `buyer_exemption` · `seller_establishment` · `seller_registration` · `supply_classification` · `tax_point` |
| `source_type` | `declared_buyer` · `declared_seller` · `registry_verified` · `evidence_derived` · `defaulted` |
| `registration_scheme` | `vat` · `gst` · `sales_tax_permit` · `other` (open) |

`verification_status` reuses the existing four-state vocabulary. Add a mapping table from PR #5 `qualificationBasis` values to these.

### T4. Wire schema `schema/x402-wire/tax-2.json`

Adds `inputsRequired` (array of `{profile, factType, granularity}`), `floor`, and quote `{determinationStatus, basisRef, pricingBasis, taxResultRef}`. Allows the declaration-first and two-round flows of §2.1. `tax-1.json` remains valid and unchanged.

**Acceptance:** schema validates the existing `payment_required.json` / `payment_payload.json` pair (as tax-1) and the new US example (as tax-2).

### T5. Requirement profiles

- **Core** `axes:x402_tax_determination_core@1`, jurisdiction-neutral:
  - components present if and only if `determination_status` is `determined` (or `partial`, if kept);
  - every input has a `source_type` and a `verification_status`;
  - `basis_ref` recomputes from the recorded inputs;
  - signed amount equals the quoted total.
- **Packs**, each extending core and citing its source:
  - `eu_vat_b2b` - re-base the existing `x402_eu_vat_b2b_tax_authority@1`.
  - `eu_vat_b2c` - two non-contradictory location inputs.
  - `us_sales_use` - sub-national `jurisdiction_ref` present; exemption input present when `treatment_type` is `exempt`; seller registration in the jurisdiction when `mechanism` is `seller_collected`; `self_assessed` with `liable_party_role: buyer` when it is not. **Mark every rule `unsettled_question_notes` until the Tax WG confirms it.**
  - `withholding` - placeholder with the open question in §5.

### T6. Examples and vectors

All synthetic, labelled synthetic, generated by tool, never hand-edited.

| Vector | Expect |
|---|---|
| EU B2B reverse charge (existing example re-emitted) | pass core + `eu_vat_b2b` |
| US business buyer with exemption | pass core + `us_sales_use` |
| US seller without registration in buyer's state, buyer self-assesses | pass core + `us_sales_use` |
| Stacked federal + provincial components | pass core |
| Negative: `undetermined` with components | fail core |
| Negative: network address contradicts declared location, result still `determined` on it | fail core |
| Negative: signed amount differs from quoted total | fail core |

Every predicate added ships with at least one passing and one failing fixture, or is declared `unexercised` with a reason (TLC-008).

### T7. Correlation hash

No change. `basisRef` sits inside the tax lane info, which `axes:x402_correlation@1` already commits to. Add one test proving a changed declaration changes the correlation hash.

### T8. Doctrine (`docs/01`)

One line: *AXES records tax determinations and the facts and rule version they rest on; it never determines tax.*

### T9. Docs that must change with this

- `docs/x402-trust-lanes-solution.md`: tax lane flow becomes declare, resolve, quote, accept; add one non-EU example.
- `examples/x402-b2b-vat/README.md`: note the T1 re-emission.
- `registers/decision-register.md`: one entry each for T1 block shape, `partial` (keep or drop), `supplier_vat_id` deprecation, T3 vocabularies.
- `CHANGELOG.md`.

---

## 4. Alignment with wg-tax PR #5 (offer upstream, do not fork)

These are offered to PR #5 as answers to its own open questions, credited to its structure. AXES follows whatever the Tax WG adopts.

| # | Gap in rev 6 | PR #5 ref | Proposal |
|---|---|---|---|
| 1 | Location is country-only and establishment-only | §2.1 | ISO 3166-2, optional local code with a named system, separate use or delivery location |
| 2 | One result | §5.2, Q9, Q11 | A list of components |
| 3 | EU vocabulary | §5.2 | `taxType`; global values for `mechanism` and `liableParty`; EU values stay in `eu-vat` |
| 4 | Business relief is a VAT number only | §2.1 | Tax identifier scheme; exemption or resale certificate reference |
| 5 | No machine-readable statement of what the seller needs | §4.4 | `inputsRequired` in the `402` |
| 6 | Tax-exclusive pricing not bound | §4.4, §6.6 | `pricingBasis`; signed amount equals quoted total |
| 7 | Results not reproducible | Q3, Q4 | Resolver, ruleset and version, rates-as-of; publisher-namespaced identifiers |
| 8 | Profiles not identifiable or negotiable | Q1, Q11 | Profile id and version on quote and receipt; unsupported profile yields `UNDETERMINED` |
| 9 | Location evidence EU-only | Q5 | Typed evidence inputs with source and status; per-profile sufficiency rule |
| 10 | Check results not aligned with the Identity WG | §4.2 | Map to the four-state result |

Already right in PR #5, keep as is: no computation or rates; undetermined emits no axes; null is not zero; the three timestamps; settlement asset and frozen exchange rate; principal attribution; declaration-first flow.

---

## 5. Open questions - for the Tax WG, not to be answered in code

1. What must a seller hold to defend a US sourcing decision, and at what granularity (state plus postal code, or finer)?
2. Which local jurisdiction code system should a US profile name?
3. Can an x402 facilitator ever be a marketplace facilitator for tax purposes?
4. Is withholding, as a payment leg to an authority, in scope for agent payments?
5. Do registration thresholds belong in the seller's registrations or in the resolver?

---

## 6. Exit criteria

- [ ] `docs/WO22-task0-inventory.md` committed.
- [ ] T3 vocabularies in `docs/06`; T1 and T2 in the field catalogue; decision-register entries made.
- [ ] `tax-2.json` committed; `tax-1.json` unchanged and still passing.
- [ ] Core profile and `us_sales_use` pack committed, the pack marked unsettled.
- [ ] All T6 vectors generated by tool, each predicate with a pass and a fail (or declared unexercised).
- [ ] Existing B2B VAT example still verifies; gt-v2.1 and gt-v2.0 digests unchanged in CI.
- [ ] Trust-lanes doc and example README updated; CHANGELOG entry.

## Credits

- wg-tax PR #5 and its author, for the common-contract-plus-profiles structure and the declaration-first flow this work order builds on.
- Tax WG review (Oct 2026), for the sales-tax sourcing point that exposed the gap.

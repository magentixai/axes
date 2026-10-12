# AXES Design Note - Payee settlement role (settle-time record)
 
**Status:** design note / proposed schema addition to the settle-time record. Not yet in the corpus.
**Date:** 2026-08-11.
**Origin:** the attribution gap in Mancy Thurston's (Paddock) aggregator requirements (assessment: `claude/Mancy_Aggregator_Proposal_AXES_Assessment.md`). The gap she names at the discovery/measurement layer is the same one the AXES settle-time record exists to close at the evidence layer; without the role, the evidence record inherits the same ambiguity.
**Conventions:** British spelling. NO EM DASHES in any text destined for the repo. "Magentix AI", never bare "Magentix".
 
---
 
## 1. The problem
 
An agent pays a resource five cents. A facilitator submits the transfer on the seller's behalf, so on-chain the sender is the relay, not the buyer, and the receiving wallet maps to no authoritative name. One payment is now observable in two places (the payTo wallet and the facilitator relay transaction) and nothing on-chain says whose revenue it is. Aggregators guess, differently, roughly a quarter-million times a day, which is a large part of why published x402 volume figures do not reconcile across sources.
 
Two failure modes fall out of this, and both reach the AXES settle-time record:
 
- **Identity cannot come from the chain.** Under relaying (EIP-3009 and similar), `tx.from` is the facilitator, not the payer. An evidence record that reads payer or payee identity from raw chain data is wrong precisely in the common case.
- **"Who was paid" is not enough; "in what role" is required.** A settle-time record that captures a payee wallet without the payee's economic role cannot distinguish earned revenue from relayed or passed-through value, so it inherits the aggregator's double-counting problem inside the evidence layer.
## 2. The addition: `settlement_role` on payee attribution
 
Add a declared `settlement_role` to each payee in the settle-time record. Enum, aligned to Mancy's discovery-descriptor role so a discovery-time declaration and a settlement-time record share one vocabulary:
 
- `origin` - the principal: the party whose value it is, whether earned or spent. On the payee side that is typically the resource provider whose payTo receives the payment as its own revenue; on the payer side it is the party whose value is spent. Earned volume, when that is the question, is the set of payments whose *payee* role is `origin`.
- `facilitator` - a relay settling on another party's behalf (including an x402 facilitator relaying or settling on a seller's behalf). The observed wallet is a relay hop, not the principal.
- `proxy_gateway` - a pass-through intermediary that fronts other services and routes value onward.
`facilitator` and `proxy_gateway` are pass-through and must not be counted as earned. This is the double-counting fix, moved from the aggregator's guess into the record's declaration.
 
## 3. Rules (what keeps it honest)
 
- **Declared and checkable, not a badge.** Like `capture_relationship` (custody) and `corroboration_state`, the role is a load-bearing declaration. A payee claiming `origin` is checkable against the host's own live 402 response (does it advertise this payTo) and against observed on-chain behaviour (does the value stay, or flow onward). **The check runs against the `primary` identifier** in the identifier set (Module 01 §1.24). A mismatch on an `alternative` identifier is a signal, not a disqualification. A role a payee's behaviour cannot support is a fraud signal to surface.
- **Correction to earlier wording.** Section 2 previously defined `origin` as "the party that earns the value". That token inverted on the payer side (who *funds* the value). The direction-neutral redefinition above replaces it; this line exists so an external quotation of the old sentence is not silently rewritten.
- **Identity is carried by the attestation identity, never derived from `tx.from`.** The authorisation record's attestation identity is the source of truth for who authorised; the settle-time record's payee attribution plus `settlement_role` is the source of truth for who was paid and in what capacity. State this in doctrine with the relayer case as the worked example: an implementation that reads payer or payee from the chain sender is non-conformant.
- **Category discipline holds.** `settlement_role` is a declared fact in the record. Whether to trust the declaration is the Assurance report / Evaluator layer, measured independently on top (Mancy's own scope note: reputation and outcomes stay out of the self-declared file). Do not fold reputation into the role.
- **Corroboration composes.** A payee's `origin` claim may itself carry a `corroboration_state` (how independently the "this party earns it" claim is corroborated), so the two axes stack rather than collide.
## 4. Interop with the discovery descriptor
 
Mancy's descriptor declares, at discovery time, the host's `settlement_addresses` per chain and its `role`. The AXES settle-time record records, at settlement time, the payee attribution and (with this addition) the payee `settlement_role`. Same enum at both ends means the two interlock: a descriptor's declared payTo and role can be cross-checked against the settle-time record that actually discharged the payment. This is the concrete form of "x402 standardises how agents pay; AXES standardises how you prove who was paid, in what role, and that it was authorised."
 
## 5. Schema sketch (illustrative, not final)
 
```json
"settlement": {
  "payees": [
    {
      "payee_ref": "<attestation identity / key reference - NOT tx.from>",
      "address": { "chain": "eip155:8453", "value": "0x..." },
      "settlement_role": "origin",            // origin | facilitator | proxy_gateway
      "amount": { "value": "50000", "decimals": 6, "asset": "caip19:..." },
      "corroboration_state": "source_system_corroborated"   // optional, composes
    }
  ]
}
```
 
## 6. Open questions
 
- Where exactly the role attaches when a single settlement has multiple hops (origin plus facilitator in one record) - a list of payees each with its own role, or an explicit hop order. Lean: a list, with role per payee, and no silent merging of hops (Walter's harness rule: shared payout does not equal same operator).
- Whether `settlement_role` needs a fourth value for split-settlement / revenue-share cases, or whether those are modelled as multiple `origin` payees.
- Registry placement: add `settlement_role` to the field catalogue and the numeric/vocabulary registries; note the enum is shared with the x402 discovery descriptor so the two stay aligned if either changes.
## 7. Next steps
 
- Land this as an issue/decision-register entry in the AXES repo (magentixai/axes) once shaped.
- Feed the "identity from attestation, not tx.from" doctrine line into the record-shape argument for tsc#4.
- Coordinate the shared enum with Mancy so the discovery descriptor and the settle-time record do not drift.
 
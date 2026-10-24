# Binding profile catalogue (seed)

> **Status: proposed (D-051).** Rules and status definitions: [docs/21](../docs/21-binding-profile-catalogue.md). How to write and publish your own profile: [docs/22, profile authoring guide](../docs/22-profile-authoring-guide.md). An entry is immutable at its identifier; a changed procedure is a new version. Add an entry by pull request, with the elements docs/21 section 2 lists.

## Entries

| Identifier | Protocol bound | Binds | Status | Implementation and vectors | Owner |
|---|---|---|---|---|---|
| `axes:x402_correlation@1` | x402 v2, `exact` scheme with EIP-3009 on EVM networks; other schemes refused, not mapped | A correlation core both parties hold at authorisation (from the served PaymentRequired and the signed PaymentPayload) to one `correlation_hash`; settlement and the receipt are excluded and checked separately | `candidate` | `tools/x402/x402_correlation.py`; two-sided vectors in `tools/x402/vectors/` (20); cross-checked against the external `x402-payment-fingerprint/0` vectors (`tools/x402/crosscheck_payment_fingerprint.py`) | AXES steward |
| `axes:x402_payment_anchor@1` | x402 v2, with the offer-receipt extension (x402-foundation/x402#3827, pinned when written) | An evidence record to the x402 payment it concerns, checkable offline against recorded settlement data; references `axes:x402_correlation@1` rather than re-deriving payment fields | `reserved` | In preparation | AXES steward |
| `axes:ap2_mandate_ref@1` | Google Agent Payments Protocol (AP2), version pinned when written | An evidence record to an AP2 Checkout or Payment Mandate, an SD-JWT, by digest of the mandate as received | `reserved` | Not started | AXES steward, until the AP2 maintainers publish their own |
| `axes:mastercard_vi_ref@1` | Mastercard Verifiable Intent (agent-intent/verifiable-intent), version pinned when written | An evidence record to a layered SD-JWT Verifiable Intent credential, by digest as received | `reserved` | Not started | AXES steward, until Mastercard publishes its own |
| `axes:aep_chain_ref@1` | A-Comm Evidence Protocol, v1.0.3-rc.2 or its final | An AXES record to an AEP artifact or chain head, by digest as received; neither standard's records are rewritten | `reserved` | Not started | AXES steward, until A-Comm publishes its own |

## Field disposition (filled in per profile when it reaches `experimental`)

| Identifier | `never_redactable` | `disclosable_by_role` | `out_of_record` |
|---|---|---|---|
| `axes:x402_correlation@1` | `binding_hash` (the `correlation_hash`), network | To be set under D-045: payer, payment legs and amounts, resource, disclosed to the payment verifier role | To be set; the recipe's two salts never go on chain (docs/x402-trust-lanes-solution.md) |

The `axes:x402_correlation@1` row is a proposal for review.

## Not in this catalogue

- **Anchor profiles.** These are listed in [docs/anchoring-profiles.md](../docs/anchoring-profiles.md), for example `axes:anchor_registry_bytes32@1`.
- **Requirement profiles.** These live in [`profiles/`](../profiles/).

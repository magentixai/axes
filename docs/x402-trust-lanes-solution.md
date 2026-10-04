# x402 trust lanes: a solution proposal

> **Status: proposal for the x402 working-group chairs.** Nothing here changes settlement, requires a lane, or depends on one implementation. Worked example: [`examples/x402-b2b-vat/`](../examples/x402-b2b-vat/).

## The problem in three lines

- A business that pays with x402 cannot book the spend without supplier identity and a tax result, and today neither travels with the payment (wg-identity #22, wg-tax PR #5).
- A party who relies on the payment later needs evidence it can check. Each thread is inventing its own receipt and its own join key for that (x402#2887, #3170, tsc#4).
- The authority to spend (#3220), the decision to spend (#3086) and the outcome are separate facts, bound by separate parties. Nothing ties them to the payment without making one party's claim another's.

## The pattern

**Three optional lanes, one common contract.** Each lane is an x402 extension owned by its working group: `identity`, `tax`, `evidence`, and `authority` if its owner wants it.
- The server's `info` carries `offered` (profile identifiers), `required`, optionally `floor` and `profileRegistry`, and the lane's own facts.
- The client echoes it unchanged and appends `chosen` and `presentation`.
- Opting out is `chosen: "declined"`.
- Choices are per lane: three identity options and four tax options are seven offers, not twelve combinations. Rules that span lanes live once, in the relying party's requirement profile.

**Tiers, adopted progressively:**

| Tier | What changes |
|---|---|
| 0 Pay | Plain x402 |
| 1 Declare | Lanes offered and chosen; local checks only |
| 2 Bind | Both parties compute the same correlation hash; each keeps its own record |
| 3 Assure | Independent anchors per party; evaluation against requirement profiles |

## The join key

`axes:x402_correlation@1`: SHA-256 over the RFC 8785 bytes of a core both parties hold identically at authorization:
- network, asset contract, total and payment legs, payer, resource, nonce and expiry;
- an optional payment identifier and offer hash;
- two salts that never go on-chain;
- per lane, the choice and a hash of the echoed information.

**It commits to:**
- **The tax result, the supplier identity and the principal attribution**, through the lane hashes. An auditor finds one answer, not two.
- **A #3220 mandate, without a new field.** Under #3220 the nonce already is the mandate binding, so a verifier recomputes the binding rather than trusting a claim.

**It excludes:**
- **The receipt.** The receipt carries the hash, so including it would be circular.
- **The settlement.** It happens later and can fail; it is checked separately, by decode-and-compare.
- **Anything one-sided.**

**Two carriers:**
- **Option 1, works today:** the client appends `correlationDigest` to its evidence lane echo; the server recomputes it.
- **Option 2, proposed:** receipt `version: 2` adds the optional `correlationDigest`, signed by the server. Version 1 is unaffected.

## Where each piece lands

| Piece | Natural owner | Ask |
|---|---|---|
| `identity` lane, disclosure profiles | Identity WG | Adopt the lane and common contract; own the disclosure profiles (#34) |
| `tax` lane, `eu-vat` profile | Tax WG | Carry PR #5 as the lane's first profile |
| `authority` lane | #3220 author | Use the common contract for the section 19 binding, if wanted |
| `evidence` lane, correlation recipe | Evidence-record group (tsc#4) | Take the recipe and its two-sided vectors as a Phase 1 corpus item |
| Receipt `version: 2` member | offer-and-receipt maintainers via the TSC | Agree the route: issue or PR |
| One nonce derivation | #3220 and #3226 authors | Agree one tagged derivation over optional named members, so bindings compose instead of competing for the single EIP-3009 nonce |
| Records, anchoring, evaluation | AXES | Reference material, not an x402 dependency |

## What this does not do

- No change to settlement, facilitators or the base protocol.
- No required lane; every lane can be declined unless a server's legal floor requires it.
- No single implementation: ARBITR built the reference example, and anyone can reproduce it from the published inputs.
- AXES records the bindings; it never makes them, and never re-asserts one party's authority as another's.

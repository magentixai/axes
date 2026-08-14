# AXES / AEP / x402 coherence tracker

**Purpose.** Prevent drift between Magentix AI's three adjacent surfaces while they are built in parallel:

1. **AXES** evidence envelopes and settle-time records (`magentixai/axes`)
2. **AEP** (Agent Evidence Profile) wording - especially AEP #28 on signatures over canonical bytes
3. **x402 discovery signed manifest** (`magentixai/x402-signed-manifest-ref` and Domain Discovery reserved hook)

**Conventions:** British spelling. No em dashes. "Magentix AI".

**Status:** living tracker. Update the row when either side changes. Do not let Slack or a single PR be the only record of alignment.

---

## Alignment rows

| # | Topic | Shared rule | AXES / AEP | x402 discovery | Status |
|---|---|---|---|---|---|
| 1 | **Settlement role enum** | Closed set: `origin` \| `facilitator` \| `proxy_gateway`. Pass-through roles (`facilitator`, `proxy_gateway`) are not earned volume. | Settle-time payee `settlement_role` (design note `docs/15-AXES_Payee_Settlement_Role_Design_Note.md`). Same vocabulary as discovery. | Manifest `host.role` and checkable declaration in MECHANISM.md / reference kit. | **Aligned** - keep one enum; any new value must land on both sides in the same change window. |
| 2 | **Signing-input convention** | Sign the **RFC 8785 canonical bytes** directly (pure Ed25519 / declared `alg`). SHA-256 is a **content digest** for chaining / anchoring only - not the Ed25519 signing input under `alg: Ed25519`. | AEP #28: signature over the canonical bytes. Golden Trace today uses `SIG-STUB`; real SE signing MUST follow this (axes issue [#11](https://github.com/magentixai/axes/issues/11)). | Mechanism **1.1.x**, `.sig` `sig_input: "canonical-bytes"`, `content_digest` published separately. | **Aligned in intent**; AXES real signatures still pending (stubs). |
| 3 | **Identity provenance** | Payer / payee **identity is never derived from `tx.from`** (relayer / EIP-3009). Authorisation identity comes from the attestation / evidence identity; payee attribution is declared with role. | Doctrine + settle-time record: attestation identity; `payee_ref` not chain sender. | Discovery `payTo` / `settlementAddresses` are **declared** under the domain key - authenticity of declaration, not chain-derived identity. | **Aligned** - discovery proves declaration authorship; AXES proves authorisation and settlement attribution. Do not collapse the two. |
| 4 | **Detached `.sig` schema id** | In-band `v` on the signature artefact so second implementers know the shape without reading prose. | When SE envelopes gain real signatures, declare an equivalent in-band profile / schema id. | `.sig` requires `v: "x402sig1"` (mechanism 1.1.1). Bump to `x402sig2` on incompatible construction. | **x402 done**; AXES profile id TBD with SE signing. |
| 5 | **Three-way crypto vs reachability** | `authentic` \| `signature-invalid` \| `unsigned` are crypto/parse outcomes. TCP timeout / WAF ban is **did not answer** and may be vantage-dependent. | Assurance / sweep reports must not map unreachable to unsigned. | MECHANISM.md reachability note; Imunify domain whitelist for discovery host (ops runbook). | **Documented** on x402 side. |
| 6 | **Canonicalisation** | RFC 8785 JCS over the signed / hashed object; digest algorithm declared and agile. | Golden Trace v2 / P1-1; `canonicalisation_version: RFC8785-JCS`. | `canon: "RFC8785-JCS"` in `.sig`. | **Aligned**. |

---

## Change gate

Before merging a change that touches role vocabulary, signing construction, identity fields, or `.sig` / envelope schema:

1. Check this table - which row moves?
2. Update the other surface in the same programme slice (or open a blocking issue with an owner).
3. Bump the in-band schema id (`x402sigN` / future AXES profile id) if the construction is incompatible.
4. Note the decision in the AXES decision register when normative.

---

## Pointers

| Artefact | Path / URL |
|---|---|
| x402 reference kit | https://github.com/magentixai/x402-signed-manifest-ref |
| x402 MECHANISM | kit `MECHANISM.md` |
| Payee settlement role design | `docs/15-AXES_Payee_Settlement_Role_Design_Note.md` |
| Discovery reference (local) | `docs/x402/Discovery_Signed_Manifest_Reference.md` |
| SE signing alignment issue | https://github.com/magentixai/axes/issues/11 |
| Signing-input work order | `docs/x402/Cursor_WorkOrder_SigningInput_Delta.md` |

---

## Revision

| Date | Note |
|---|---|
| 2026-08-14 | Tracker created. Rows 1-6 seeded from Slack interop (Walter / Melchiorre), signing-input delta, payee-role design note, and `.sig` `v: x402sig1` landing. |

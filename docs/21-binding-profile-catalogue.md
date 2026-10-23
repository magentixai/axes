# Binding profile catalogue

> **Status: proposed (D-051), open for challenge.** Nothing here is normative until D-051 is decided. The catalogue itself is [`registers/binding-profile-catalogue.md`](../registers/binding-profile-catalogue.md).

## 1. Why a catalogue

Payment and authorisation protocols for agents are still competing: x402, Google AP2, Mastercard Verifiable Intent, Visa Trusted Agent Protocol, ACP, and evidence standards such as AEP that wrap them. Adopters cannot wait for a winner, and AXES should not pick one.

A binding profile is a named, versioned, immutable procedure for tying an AXES evidence record to one protocol's artefacts: a payment, a mandate, a settlement, another standard's chain. AXES plays the part of a container format, and each protocol is carried through its own registered profile. When a protocol fades, its profile is deprecated and the records made under it keep verifying, because the profile identifier still names a fixed, published procedure.

This is the pattern AXES already uses for anchors (`anchor_profile_ref`, docs/anchoring-profiles.md), requirement profiles (docs/07, D-033) and canonicalisation identifiers (`RFC8785-JCS`, docs/09).

## 2. What a binding profile declares

| Element | Rule |
|---|---|
| Identifier | `<namespace>:<lower_snake_name>@<version>` (docs/20 N13). Immutable; a changed procedure is a new version. The profile's digest is the SHA-256 of its RFC 8785 bytes and is pinned by records that use it. |
| Protocol bound | The protocol and its exact version or commit, for example x402 v2, AP2 at a pinned commit, AEP v1.0.3-rc.2. |
| Artefacts | Which protocol artefacts are referenced, and how they are hashed. Artefacts are always hashed **as received** and never re-canonicalised, so the protocol's own bytes stay authoritative. Identifiers and key names minted by the protocol are carried verbatim. |
| Field disposition | Every binding field is exactly one of: `never_redactable` (a verifier of the binding always needs it, for example network, settlement reference, the binding digest); `disclosable_by_role` (committed, and disclosed only to named roles, for example amount and payee to the payment verifier, under D-045); `out_of_record` (referenced by digest only). |
| Verification | A runnable procedure, its mapping to the four verification states (docs/06), and two-sided vectors with one pinned outcome per edge. |
| Status | One of `reserved`, `experimental`, `candidate`, `stable`, `deprecated`, `superseded` (section 4). |
| Owner and licence | The change controller and the licence of the profile text and vectors. |

## 3. Rules that keep the catalogue from fragmenting AXES

1. **Profiles add or tighten, never relax.** A profile may require more fields or narrow a vocabulary. It may not relax a core rule, and it may not make a core never-redactable field redactable (D-049). This mirrors the "strictest wins, floors cannot be relaxed" composition rule for requirement profiles (D-034).
2. **Several bindings per record.** One record may bind, for example, an x402 settlement, an AP2 mandate and a Mastercard Verifiable Intent credential at once, each under its own profile. An adopter can therefore hedge across protocols inside a single record instead of betting on one.
3. **Unknown means not evaluated.** A verifier that does not implement a profile reports `not_evaluated` / `instrument_failure` / `profile_unsupported` (docs/06 §2.13). This is never a pass and never a finding against the record.
4. **Deprecation never breaks records.** A deprecated or superseded profile is still evaluated under its own procedure. Translation to a successor is explicit and named, never silent (D-021).
5. **Domain separation.** Any value a profile hashes or signs on the AXES side carries the AXES domain tag (D-050). This never extends to re-hashing the protocol's own bytes.

## 4. Status lifecycle and admission

| Status | Meaning | Bar |
|---|---|---|
| `reserved` | The identifier is held; no procedure is published | A one-line scope statement |
| `experimental` | Procedure published; may change under a new version | Pinned text and at least one vector |
| `candidate` | Procedure complete and implemented | Two-sided vectors and one implementation passing them |
| `stable` | Fit for reliance | Two independent implementations passing the same vectors, a stated claim ceiling, and a named change controller |
| `deprecated` | Still evaluated; not for new records | Reason and successor, if any |
| `superseded` | Replaced by a named successor | Explicit translation published |

The same admission bar applies to every profile, including those minted by the AXES steward.

## 5. Namespaces

- `axes:` is reserved for profiles reviewed by the AXES steward. These include AXES's own reference profiles for binding to other organisations' protocols.
- Anyone may publish profiles under their own namespace, as for requirement profiles (D-033). A protocol owner, for example a card network or an AP2 maintainer, may publish and own the binding profile for its protocol. An `axes:` reference profile can then be superseded by the owner's.
- A later revision of the AXES individual Internet-Draft may request an IANA registry for binding profiles. The -00 lists the registries AXES maintains in its repository.

## 6. How a record names its bindings (proposed key names, subject to docs/20 review)

```json
"bindings": [
  {
    "binding_profile_ref": "axes:x402_correlation@1",
    "binding_profile_hash": "<SHA-256 of the profile's RFC 8785 bytes>",
    "binding_profile_hash_algorithm": "SHA-256",
    "binding_hash": "<the digest the profile defines, for example correlation_hash>",
    "binding_hash_algorithm": "SHA-256"
  }
]
```

Fields a profile marks `disclosable_by_role` appear in the record as commitments under D-045, never in clear.

## 7. Seed catalogue

See [`registers/binding-profile-catalogue.md`](../registers/binding-profile-catalogue.md). It holds one candidate profile that exists today (`axes:x402_correlation@1`) and reserved identifiers for the profiles in preparation.

# Hash scope and exclusions

> **Status: open design question, inviting challenge.** This note states a named principle and a current AXES position so reviewers can break it before the schema freeze (P1-1). Comments via the [issue templates](../CONTRIBUTING.md). If you can construct a record that verifies while being materially false under these rules, that is the most valuable thing you can send us.

Related: [docs/09-canonicalisation-and-hashing.md](09-canonicalisation-and-hashing.md). Vocabulary: `hash_scope_exclusion_reason` in [docs/06](06-controlled-vocabularies.md).

## 1. Why this note exists

Every signed record has a hash scope: the bytes the digest actually covers. Some fields cannot sit inside that scope (a signature cannot bind itself). Every exclusion creates an unauthenticated region. In an evidence record almost every field *is* the evidence, so an unauthenticated region is not a transport convenience; it is a place a reader still consumes while a verifier says the record is intact.

An independent reviewer (Rul1an) reproduced a concrete failure in a comparable system: a real audit file confirmed under that system's own integrity check, then three fields edited in place left the chain valid under two independent verifiers, because the canonical payload excluded fields the reader still consumed. He also found a type-confusion case where one verifier accepted a file the other refused to parse: the two readers accept different files.

**Nameable principle:** a hash whose scope is narrower than the reader's consumption scope creates a mutable region that verifies.

## 2. Three things easily confused

| State | Inside the hash? | Authenticated? | What a verifier can say |
|---|---|---|---|
| **Excluded at signing** | Never | No | Nothing about whether the present value is original |
| **Redacted after signing** | Yes (committed at emission); withheld from this reader | Yes | A tombstone proves presence; the withheld bytes still bind |
| **Absent** | Never captured | n/a | The field was not recorded |

A reader who cannot see a field must be able to tell withheld from never-captured, because they support opposite conclusions (concealment versus a genuine gap).

## 3. What the CrossMsg-Signing prior art actually proves

Two separate ideas, often conflated. [docs/09](09-canonicalisation-and-hashing.md) previously overstated the second.

1. **Signature Exclusion Principle** - narrow and universal: the signature is computed over content excluding itself.
2. **Canonical KVP pattern** - an **inclusion** mechanism: a declared mapping table extracts business content into a flat key-value set, so document structure and element order never enter the signing material. `ConversionRules` in that project is a JSON Schema generation and element-transformation configuration. It does **not** contain an exclusion set for mutable fields.

**Design fork.** A declared **inclusion** set leaves a newly added field silently unauthenticated. A declared **exclusion** set puts a new field inside the hash by default, so a genuinely mutable field fails loudly. **For an evidence record a loud failure is recoverable where a silent unauthenticated region is not**, so AXES defaults to inclusion (everything in the hash unless an exclusion is declared with a reason).

## 4. The current AXES position

Three exclusions today:

| Field | Reason (`hash_scope_exclusion_reason`) |
|---|---|
| `integrity.signature` | `self_referential` |
| `integrity.envelope_hash` | `self_referential` |
| `recorded_at` | `recipient_stamped` |

Everything else in the canonical envelope is inside the hash, including signing-key identity.

## 5. Options with trade-offs

| Option | Meaning | Cost |
|---|---|---|
| (A) Exclude | Field never in the hash | Unauthenticated region the reader may still consume |
| (B) Include and forbid mutation | Field in the hash; later change breaks the chain | Recipient-stamped fields cannot be filled after emission |
| (C) Include a commitment and disclose selectively | Value committed; this export may withhold it | Needs tombstones / selective disclosure (P1-1 remaining decision) |
| (D) Countersignature | Receiving system signs an outer layer covering the emitter's inner envelope plus the fields it added | Recipient-stamped fields are authenticated **by the recipient** rather than excluded. Reframes an exclusion as a custody handoff and composes with the existing custody axis |

## 6. Recommendation (five rules)

1. Default to inclusion.
2. Every exclusion declares a reason from the closed set `hash_scope_exclusion_reason`.
3. **Sensitivity is never a reason to exclude.** Sensitive values are committed and selectively disclosed (redaction-after-signing), not left unauthenticated.
4. Prefer countersignature (option D) for recipient-stamped fields rather than a permanent exclusion.
5. The hash-scope declaration is itself inside the hash.

## 7. What a deploying organisation must own

Every excluded field is a risk accepted on behalf of everyone who later relies on the record. Four questions:

1. Which fields are excluded?
2. What would an undetected change to each mean?
3. What compensating controls apply?
4. Does any assurance statement rest on an excluded field?

Make the fourth mechanical: the hash-scope declaration feeds `reliance_boundary_status` and `known_limitations`, so a report sentence resting on an excluded field carries its caveat automatically.

## 8. The attack that settles one detail

If the declaration is outside the hash, an attacker edits it to exclude a field, changes that field, and both the signature and the declaration verify. Therefore the declaration is always inside the scope it declares. Self-descriptive, not self-referential (the declaration is not hashing itself as a circular digest; it is covered by the digest it describes).

## 9. Feedback wanted

1. Is default-inclusion right for an evidence record?
2. Is countersignature worth the implementation surface?
3. Is the three-value exclusion-reason vocabulary complete?
4. Does the withheld-versus-never-captured distinction hold up in a real audit?
5. Does automatic caveating make reports unreadable?

If you can construct a record that verifies while being materially false under these rules, that is the most valuable thing you can send us.

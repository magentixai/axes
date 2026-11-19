# Extension & Namespace Model

> **Status: minimum normative text (D-059), published for challenge.** This section fixes what an emitter may put in `extensions` and what a reader does with content it does not understand. It deliberately stops there. Registration of namespaces, versioning of an extension's own content and the promotion path into the core are described, but light.

The key words MUST, MUST NOT, SHOULD and MAY are used as in RFC 2119 and RFC 8174.

## 1. Why extensions exist, and what they may not do

Implementations need to carry data the core catalogue does not define: a product's own interpretation, a sector's extra identifiers, an experiment. Without a rule, that data ends up as invented top-level keys, and a reader cannot tell a new core field from a private one. The extension model gives private data one place to live, keeps it inside the evidence, and tells every reader what to do when it meets something it does not know.

Three things extensions MUST NOT do:

1. **Override the core.** An extension never changes the meaning of a canonical field. A member inside an extension that shares a name with a canonical key is extension content, nothing more; readers MUST take canonical semantics from the canonical key only.
2. **Hold trust conclusions about the record.** Scores, confidence, assurance assertions and report hints are computed by readers, never stored in the evidence (D-025, D-031). An extension that carries them is still evidence of what the emitter said, but a reader MUST NOT treat it as a result.
3. **Escape the hash.** Extensions are inside the hash scope like every other member except those listed in docs/09a. Nothing is stripped, reordered or normalised before hashing.

## 2. Where extensions live

Every envelope MAY carry one top-level member, `extensions`, whose value is a JSON object. Each member of `extensions` is one **namespace**:

```json
"extensions": {
  "com.example.claims": {
    "extension_ref": "https://example.com/axes-extensions/claims/1",
    "extension_version": "1",
    "must_understand_indicator": false,
    "claim_reference_id": "CLM-2026-0419"
  }
}
```

- **Namespace names** are a reversed DNS name the owner controls, lower case, at least two labels separated by dots (`com.example`, `ai.magentix.arbitr`). The `axes` namespace and any name beginning `axes.` are reserved for this specification. A namespace is never a bare product name, so no vendor can occupy a generic word.
- **Namespace objects** carry three reserved members, then any content the extension defines:
  - `extension_ref` (string, SHOULD): where a reader finds the extension's definition.
  - `extension_version` (string, SHOULD): the version of that definition, compared as an exact string.
  - `must_understand_indicator` (boolean, OPTIONAL): `true` when a reader that does not implement this extension must not evaluate requirements over the envelope (section 3). Absent means `false`.
- **Names inside a namespace** follow the naming rules in docs/20, so content stays readable and can later be promoted without renaming.
- **No other top-level member** may be added by an emitter. A top-level member that the envelope's `se_version` does not define is not an extension; see section 3.3.

## 3. What a reader does (`unknown_field_policy`)

A reader is any party that verifies, evaluates, stores or forwards envelopes. "Understands" means the reader implements the extension's definition at the stated `extension_version`.

### 3.1 Integrity checks are unaffected

Envelope hashes, chain links, sequence continuity and bundle digests are computed over the bytes as received, extensions included. A reader MUST run them whether or not it understands any extension. An extension can never make a valid record fail integrity checks, and an emitter cannot hide content from them.

### 3.2 Requirement evaluation

When a reader evaluates a requirement (docs/22, WO19) over an envelope:

| The envelope carries | The reader understands it | Result for requirements over that envelope |
|---|---|---|
| No extension, or only extensions it understands | | Evaluated normally |
| An extension it does not understand, `must_understand_indicator` absent or `false` | no | Evaluated normally; the extension is ignored for evaluation |
| An extension it does not understand, `must_understand_indicator: true` | no | `not_evaluated`, reason `instrument_failure`, condition `extension_not_understood`, subject `verifier`. Never `verified`, never `contradicted` |

The last row is deliberately `not_evaluated`, not a finding against the record: the gap is in the reader's capability, not in the evidence. A reader that later implements the extension can evaluate the same bytes.

Requirements that are integrity checks (`chain_integrity`, `sequence_continuity`) follow section 3.1 and are never blocked by an extension.

### 3.3 Unknown top-level members

A top-level member that is neither defined by the envelope's `se_version` nor `extensions`:

- stays in the hash scope and is preserved and forwarded unchanged;
- is evidence that the emitter does not follow this specification at that version. A schema check (A5) reports it; requirement evaluation ignores it.

### 3.4 Preserve and forward

A reader that stores or forwards an envelope MUST keep every member, understood or not, byte for byte. Dropping an extension breaks the envelope hash and is a chain-of-custody failure, not a tidy-up.

## 4. Changing an extension, and promotion into the core

- A changed definition is a new `extension_version`. Records made under the old version keep it; nothing is rewritten.
- An extension that several independent implementers need becomes a candidate for the core through the contribution process (CONTRIBUTING.md). If accepted, the core key appears in a corpus release and in the key-change index (docs/19) as `added`, with the extension path it replaces. Envelopes already emitted keep their extension form.

## 5. Conformance vectors

`vectors/profiles/` carries two-sided cases generated by `tools/generate_profile_vectors.py`:

- `extension_ignorable`: an envelope with an extension that sets no `must_understand_indicator`; the requirement over it is `verified`.
- `extension_not_understood`: the same envelope with `must_understand_indicator: true`; the same requirement is `not_evaluated` / `extension_not_understood`.
- `extension_chain_intact`: a chain whose envelopes carry a must-understand extension; `chain_integrity` is `verified` (section 3.1).

The reference evaluator understands no extensions. An implementation that understands one passes these vectors by treating `com.example.claims` as unknown.

## 6. Open points (challenge welcome)

1. A public registry of namespaces, or reversed DNS alone.
2. Whether `must_understand_indicator` should be scoped to named requirement families instead of the whole envelope.
3. Whether extensions may appear inside blocks (for example `authority.extensions`) as well as at the top level. Today they may not.

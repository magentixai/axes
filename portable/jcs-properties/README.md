# Portable RFC 8785 JCS property vectors

Self-contained package. Lift this directory without the rest of AXES.

```
python3 portable/jcs-properties/verify.py
```

Python standard library only. No pip install. Imports nothing from `tools/`.

## Scope

These vectors pin four RFC 8785 properties that an ASCII-only corpus cannot: UTF-16 member ordering, absence of Unicode normalisation, code-unit rather than locale collation, and digest input encoding. Agreement demonstrates that two canonicalisers produce identical bytes on these inputs. It does not demonstrate that either implements RFC 8785 completely, and it says nothing about any signature, anchoring or evidence-semantics layer above the bytes.

| Property | Fixture | What a wrong implementation does |
|---|---|---|
| UTF-16 member sort (RFC 8785 §3.2.3) | `axes_jcs_surrogate_pair_key.json` | Sorts by Unicode code point (`sorted()`, `json.dumps(sort_keys=True)`); supplementary-plane keys sort after U+E000–U+FFFF instead of before |
| No Unicode normalisation (RFC 8785 §3.1) | `axes_jcs_nfc_nfd_pair.json` | NFC/NFD collapses distinct members and changes the digest |
| Code-unit order, not locale collation | `axes_jcs_collation_ae.json` | German/ICU-style collator puts `ä` before `z`; JCS puts U+00E4 after `z` |
| Digest over UTF-8 canonical bytes | `axes_jcs_digest_encoding.json` | Digests a decoded string or a re-encoded form |

The locale-collation property is pinned because **Ryan Cason / orionsys** found a locale-aware comparator that left 148 tests passing while the bytes diverged. The portable verifier exercises that negative in-process (locale-like member order must diverge from JCS); that divergence is the suite's required `reject` observation.

`MANIFEST.json` pins `canonical_utf8` and `sha256` per vector. `CROSSCHECK.md` records agreement with an independent `rfc8785` PyPI implementation.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | Every vector matches its pin; required pass and reject verdicts observed; every declared reason code exercised |
| 1 | Conformance failure (wrong bytes / failed structural assert) |
| 2 | Suite broken (missing fixture, undeclared or unobserved coverage requirement) |

## Licence

Apache-2.0 (see `LICENSE`). Spec prose elsewhere in AXES remains CC-BY-4.0.

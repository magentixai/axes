# AXES Golden Trace v2 - Linux canoncheck + manifest diff (verification report)

**Branch:** `golden-trace-v2` (magentixai/axes), fresh clone on Linux.
**First pass:** `9721b3f` (found the blocker). **Fix pass:** `a183ded` (re-verified - PASS).
**Toolchain:** Python `jcs` 0.2.1 (RFC 8785) as in the repo; independent Node 22 `canonicalize@2` (Erdtman RFC 8785 reference impl) for the cross-language leg.
**Date:** 2026-08-07.
**Verdict:** RESOLVED. As of `a183ded` the corpus is byte-identical to a clean Linux regeneration, the manifest matches the on-disk bytes, and both corpora verify cross-OS and cross-language. `golden-trace-v2` is now safe to advertise as independently verifiable.

---

## Fix re-verification (a183ded) - all PASS

Re-ran the full Linux check against the fix commit. Every item green:

- **Byte-identical regeneration:** `git diff --stat` after regenerating both corpora and the vectors is **empty**. The Windows-committed corpus equals a clean Linux regeneration, byte for byte. This is the cross-OS reproducibility proof the first pass could not make.
- **Portable bundle values reproduce on Linux, matching the Windows fix-pass values exactly:**
  - Fin bundle `b45f7c47c81e06bc…`, Ind bundle `b926af903de3d508…`.
  - Chain heads unchanged as required: Fin `71c10986320fa148…`, Ind `93733e6a8b6f6be2…`.
- **Manifest self-consistency (the exact check that failed before):** every file hash in `manifest.json` equals the SHA-256 of the on-disk file. Fin 38/38, Ind 40/40, zero mismatches.
- **No CRLF** anywhere in either `out/` tree (0 files).
- **QIF encoding fixed:** `qif_SN0001.xml` carries the Ø as UTF-8 `C3 98`, with no CP1252 `D8` byte.
- **Cross-language canoncheck still holds:** Node `canonicalize` independently recomputes 76/76 envelope hashes and 76/76 chain links for both corpora.
- **Vectors intact:** all 10 pinned vector SHA-256 values reproduced in Node; USDC (`decimals=6`, Base caip19) and custody twins unchanged.

What Cursor changed (per the fix commit): UTF-8 + LF writes via `write_text_utf8_lf` / `write_json_utf8_lf` in both generators and the vector emitter (no platform text mode); `.gitattributes` marks `examples/**/out/**`, `vectors/**`, and the archived v1 corpora `-text`; a manifest self-check (`assert_manifest_matches_files`) runs before exit so a desynced manifest can never ship again.

**Bottom line:** the blocker below is closed. Envelope-chain, canonicalisation, numeric-ruling, custody-vector, AND file-level/manifest claims are all safe to cite on `a183ded`.

---

## What PASSED on the first pass (the substance was always sound)

- **Chain heads reproduce byte-identically on Linux:** Fin `71c10986320fa148…`, Ind `93733e6a8b6f6be2…` - exact matches to the Windows values. The evidence chain is computed over RFC 8785 canonical JSON in memory, so it is immune to filesystem encoding and newline handling.
- **Both corpora verify, twice, in two languages:** Fin and Ind each 76/76 envelope hashes recompute to the stored value, 76/76 `previous_envelope_hash` links verify head-to-tail, and 0 JSON floats in hash scope. Confirmed independently in Python (jcs) and Node (canonicalize).
- **Cross-language byte identity:** Python jcs and Node canonicalize produce byte-identical canonical bytes for all 152 envelopes (76 Fin + 76 Ind).
- **Vectors:** USDC Amount carries `decimals=6` and the Base caip19 asset (`caip19:eip155:8453/erc20:0x8335…2913`); EUR is namespaced `iso4217:EUR` (44 occurrences in the Fin corpus); the large-amount string vector is present; the custody twins behave (`custody_deployer_captured_reject` rejects with `custody_independence_reject`, `custody_accept_independent_external` passes). Zero `<generated>` placeholders remain, and Node independently reproduced all 10 pinned vector SHA-256 values.
- **Float guard fires** on a planted float in hash scope.

## What FAILED on the first pass (9721b3f) - now fixed

**The committed `manifest.json` was hashed over different bytes than the files committed next to it.** Two compounding causes, both proven at the time:

**1. CRLF-vs-LF desync (all text files, both corpora).** The generator wrote corpus files in Python text mode, which emits CRLF on Windows. The manifest hashed those CRLF bytes. But git normalised the files to LF when they were committed. Decisive test: for every Fin file, `sha256(committed_bytes -> CRLF) == the hash stored in the committed manifest`, while `sha256(committed_bytes as-is, LF)` did not. Example, `camt053_20260609.xml`: manifest stored `ff1366c0…`; the committed file (LF) hashed to `9f5f1a25…`; the same file converted to CRLF hashed to `ff1366c0…`.

**2. CP1252-vs-UTF-8 encoding (Ind QIF artifacts only).** The QIF artifacts contain a non-ASCII character (the Ø / diameter symbol). It was written in the Windows default code page as a single byte `0xD8` (CP1252), not as UTF-8 `0xC3 0x98`. The Ind QIF committed blob was CP1252 + LF, the manifest hash matched CP1252 + CRLF, and a Linux regen produced UTF-8 + LF: a three-way mismatch.

**Consequence (at the time).** The repo's own verification recipe (step 6: re-hash each file and compare with `manifest.json`) failed for any third party not on the exact machine configuration that generated the corpus. It passed on Windows-with-autocrlf and failed on Linux, macOS, and Windows with `autocrlf=false`.

## The fix (generator-side, made v2 genuinely portable)

1. **Write every corpus file as UTF-8 + LF explicitly**, never platform-default text mode. DONE (`write_text_utf8_lf` / `write_json_utf8_lf`).
2. **`.gitattributes` marking the pinned corpus byte-preserved** (`examples/**/out/** -text`, `vectors/** -text`, archived v1 `-text`). DONE.
3. **Regenerate the manifest to match on-disk bytes, plus a pre-exit self-check.** DONE (`assert_manifest_matches_files`). Chain heads did not move; bundle hashes settled to the portable values `b45f7c47…` / `b926af903…`.

## Windows vs Linux hashes (final, portable)

| | value | cross-OS |
|---|---|---|
| Fin chain head | `71c10986320fa148…` | identical (never moved) |
| Fin bundle | `b45f7c47c81e06bc…` | Windows == Linux (a183ded) |
| Ind chain head | `93733e6a8b6f6be2…` | identical (never moved) |
| Ind bundle | `b926af903de3d508…` | Windows == Linux (a183ded) |

Superseded intermediate values, for the record: the first-pass committed manifest carried `577f4d17…` (Fin) / `a09a9d1d…` (Ind), which were hashed over CRLF; an interim Linux regen with the old writers produced `634705f1…` / `b4694987…`. Both are obsolete; `b45f7c47…` / `b926af903…` are the portable values to pin.
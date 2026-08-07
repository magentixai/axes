# AXES Golden Trace v2 - Linux canoncheck + manifest diff (verification report)

**Branch:** `golden-trace-v2` @ `9721b3f` (magentixai/axes), fresh clone on Linux.
**Toolchain:** Python `jcs` 0.2.1 (RFC 8785) as in the repo; independent Node 22 `canonicalize@2` (Erdtman RFC 8785 reference impl) for the cross-language leg.
**Date:** 2026-08-07.
**Verdict:** the envelope/evidence layer is solid and reproducible cross-OS. The **manifest layer is not reproducible, and the committed manifest does not match the committed corpus.** Do not advertise `golden-trace-v2` as independently verifiable until the manifest is regenerated with the fix below. Chain-head-level claims are safe to make now.

---

## What PASSED (the substance is sound)

- **Chain heads reproduce byte-identically on Linux:** Fin `71c10986320fa148…`, Ind `93733e6a8b6f6be2…` - exact matches to the Windows values. The evidence chain is computed over RFC 8785 canonical JSON in memory, so it is immune to filesystem encoding and newline handling. This is the property that matters most, and it holds.
- **Both corpora verify, twice, in two languages:** Fin and Ind each 76/76 envelope hashes recompute to the stored value, 76/76 `previous_envelope_hash` links verify head-to-tail, and 0 JSON floats in hash scope. Confirmed independently in Python (jcs) and Node (canonicalize).
- **Cross-language byte identity:** Python jcs and Node canonicalize produce byte-identical canonical bytes for all 152 envelopes (76 Fin + 76 Ind). The digest agility holds: same canonical bytes, SHA-256 over them.
- **Vectors:** USDC Amount carries `decimals=6` and the Base caip19 asset (`caip19:eip155:8453/erc20:0x8335…2913`); EUR is namespaced `iso4217:EUR` (44 occurrences in the Fin corpus); the large-amount string vector is present; the custody twins behave (`custody_deployer_captured_reject` rejects with `custody_independence_reject`, `custody_accept_independent_external` passes). Zero `<generated>` placeholders remain, and Node independently reproduced all 10 pinned vector SHA-256 values.
- **Float guard fires** on a planted float in hash scope.

## What FAILED (blocker)

**The committed `manifest.json` was hashed over different bytes than the files committed next to it.** Two compounding causes, both proven:

**1. CRLF-vs-LF desync (all text files, both corpora).** The generator writes corpus files in Python text mode, which emits CRLF on Windows. The manifest hashes those CRLF bytes. But git normalised the files to LF when they were committed. So the committed files are LF while the manifest records hashes over CRLF. Decisive test: for every Fin file, `sha256(committed_bytes -> CRLF) == the hash stored in the committed manifest`, while `sha256(committed_bytes as-is, LF)` does not. Example, `camt053_20260609.xml`: manifest stores `ff1366c0…`; the committed file (LF) hashes to `9f5f1a25…`; the same file converted to CRLF hashes to `ff1366c0…`. Same result for reports, envelopes.jsonl, samples, and every pain/pacs artifact.

**2. CP1252-vs-UTF-8 encoding (Ind QIF artifacts only).** The QIF artifacts contain a non-ASCII character (the Ø / diameter symbol). It was written in the Windows default code page as a single byte `0xD8` (CP1252), not as UTF-8 `0xC3 0x98`. The in-envelope artifact hash uses `content.encode()` (UTF-8) and is fine, but the file on disk is CP1252, so it never matches. The Ind QIF committed blob is CP1252 + LF, while the manifest hash matches CP1252 + CRLF, and a Linux regen produces UTF-8 + LF: a three-way mismatch.

**Consequence.** The repo's own verification recipe (step 6: re-hash each file in `artifacts/` and compare with `manifest.json`) fails for any third party who is not on the exact machine configuration that generated the corpus. It happens to pass on Windows-with-autocrlf (checkout restores CRLF, matching the CRLF-era hashes), and fails on Linux, on macOS, and on Windows with `autocrlf=false`. A portable, independently-verifiable evidence corpus that only verifies on its author's own git config is the precise failure that discredits a byte-identity exercise. It is contained to the manifest/bundle layer; the envelope chain itself is unaffected.

## The fix (generator-side, makes v2 genuinely portable)

1. **Write every corpus file as UTF-8 + LF explicitly**, never platform-default text mode. Either `open(path, "w", encoding="utf-8", newline="\n")` or build the string and write bytes: `open(path, "wb").write(content.encode("utf-8"))`. This makes on-disk bytes identical on every OS and aligns them with what `content.encode()` and the manifest walk hash. Fixes both causes at the source. Audit every file write in both generators (`examples/golden-trace/generate_golden_trace.py`, `examples/golden-trace-ind/generate_golden_trace.py`) and the report/artifact writers.
2. **Add `.gitattributes` marking the pinned corpus as byte-preserved**, e.g. `examples/**/out/** -text` and `vectors/** -text` (or `binary`). A hash-pinned verification corpus must never be line-ending-normalised by git, whatever a contributor's `autocrlf` is. This is the belt-and-braces guarantee independent of cause 1.
3. **Regenerate the manifest** so its file hashes match the actual on-disk UTF-8/LF bytes, then re-run this Linux check. Chain heads will not move (`71c10986…` / `93733e6a…`); the bundle hashes will change once, to their true portable values, and will then reproduce cross-OS. Add a generator self-check (or CI step) that re-hashes every file against the freshly written manifest before exit, so this can never ship desynced again.

**Fix status (2026-08-07 follow-up):** generators now write UTF-8 + LF explicitly; `.gitattributes` marks pinned corpora `-text`; manifest self-check runs before exit. Re-run this Linux verification on the fix commit; chain heads must stay `71c10986…` / `93733e6a…`; bundle hashes settle to the new portable values from that regen.

**Do not merge or point third parties at `golden-trace-v2` for file-level verification until the fix commit is re-verified on Linux.** Envelope-chain and canonicalisation claims (RFC 8785, cross-language byte identity, the numeric ruling, the custody vectors) are all safe to cite today.

## Windows vs Linux hashes (for the record)

| | Windows (committed manifest) | Linux regen (true portable value, once fixed) |
|---|---|---|
| Fin chain head | `71c10986320fa148…` | `71c10986320fa148…` (identical) |
| Fin bundle | `577f4d17a1af9d3f…` (hashed over CRLF) | `634705f1f24cddbd…` |
| Ind chain head | `93733e6a8b6f6be2…` | `93733e6a8b6f6be2…` (identical) |
| Ind bundle | `a09a9d1d08912147…` (CRLF + CP1252) | `b4694987a6c568c3…` |

The Linux bundle values above are self-consistent on Linux but are not the final answer either - they will change again once the UTF-8/LF fix reshapes the QIF and text bytes. The correct sequence is: apply the fix, regenerate, then the bundle value that emerges is the portable one to pin.
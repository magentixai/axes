# Verify the Golden Trace corpus

A validator should never have to reconstruct this procedure from a thread. This page is the reproduce path.

## Current corpus of record (gt-v2.0)

Until the planned gt-v2.1 release, published third-party figures refer to tag **`corpus/2026-08-08-gt-v2`** (commit `776cc0b`), **not** to default-branch HEAD.

Expected digests:

| Bundle | Chain head | Bundle digest (`bundle_manifest_hash`) |
|---|---|---|
| `examples/golden-trace` | `71c10986320fa148ab89c65c3f92a4ddd12ebfaac2db4f9099fa0443ccb0b564` | `b45f7c47c81e06bceddb5694cd2b0f28cd2afd5082e5c1102b217c713d344352` |
| `examples/golden-trace-ind` | `93733e6a8b6f6be299f656ddfb951f13c9da4756f9d37470649ac3414056fba4` | `b926af903de3d5088a253a486044a7fc1bf8afd046958da0054ea152fc7c3463` |

### Clone at the tag

Clone the tag directly rather than cloning the default branch and switching. This applies the tag's own `.gitattributes`, so pinned bytes reach your disk exactly as committed on every OS.

```bash
git clone --branch corpus/2026-08-08-gt-v2 https://github.com/magentixai/axes.git axes-gt-v2
cd axes-gt-v2
python -m pip install -r requirements-dev.txt
```

`requirements-dev.txt` installs `jcs` (RFC 8785), which the generators and the reference verifier need. On Windows use `python` or `py -3`; `python3` may open the Microsoft Store stub.

### Byte check without regenerating

From a default-branch clone (standard library only):

```bash
python tools/check_corpus_bytes.py --root ../axes-gt-v2
```

This fails if any pinned file contains a CR byte or invalid UTF-8, if manifest keys use backslashes, if any on-disk file differs from its `manifest.json` entry, or if a chain head or bundle digest differs from the table above. A failure here on Windows almost always means line endings were converted on checkout: re-clone at the tag as shown.

### Regenerate both corpora

```bash
python examples/golden-trace/generate_golden_trace.py
python examples/golden-trace-ind/generate_golden_trace.py
git diff --exit-code --stat -- examples/golden-trace/out examples/golden-trace-ind/out vectors
```

The diff must be empty. Then read `chain_head` and `bundle_manifest_hash` from each `out/manifest.json` and compare to the table above, or rerun the byte check. On `golden-trace-v2`, `python tools/axes_verify.py` runs the full reference verifier (pinned vectors, both chains, custody twins, coverage rule).

### Platforms

The same procedure is run on every push by `.github/workflows/cross-platform-verify.yml` on Linux, macOS and Windows (Windows runners check out with `core.autocrlf=true` and a CP1252 default encoding, which is what an external Windows verifier gets). Results are expected to be byte-identical on all three; a difference on any OS is a defect, please report it.

### Check the external anchors

The release statement `anchors/gt-v2.0/release_statement.json` commits to the four digests above; its SHA-256 is `d53f3eb5720d1676088609d4ea6f340121be9a7fc6e97efdf158fa3b96e84216`. From a default-branch clone:

```bash
python -m pip install -r tools/anchoring/requirements.txt
python tools/anchoring/verify_anchor.py anchors/gt-v2.0 --subject anchors/gt-v2.0/release_statement.json
```

Each anchor reports `verified`, `contradicted`, `indeterminate` (for example a pending OpenTimestamps proof) or `not_evaluated` (for example `openssl` missing), with the reason. No network access is used. For the OpenTimestamps anchor, confirm the reported Bitcoin block hash with any Bitcoin node or explorer to establish main-chain membership.

## Superseded or retired tags

| Tag | Meaning |
|---|---|
| `corpus/2026-08-08-gt-v2` | Verified gt-v2.0 (corpus of record until gt-v2.1) |
| `corpus/2026-08-15-pre-merge` | Retired default-branch lineage; never externally verified |

To verify a superseded release, check out that tag and compare against the row in [`RELEASES.md`](RELEASES.md). Do not mix a tag's envelopes with another tag's expected digests.

## How to report a mismatch

Open a [Conformance test proposal](CONTRIBUTING.md) issue (or comment on [axes#6](https://github.com/magentixai/axes/issues/6)) with: the tag or commit you checked out, the digest you computed, the digest you expected, OS and Python version, and whether a second regeneration was dirty. A mismatch against default-branch HEAD while following a published gt-v2.0 figure is expected today; check the tag first.

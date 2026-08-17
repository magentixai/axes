# Verify the Golden Trace corpus

A validator should never have to reconstruct this procedure from a thread. This page is the reproduce path.

## Current corpus of record (gt-v2.0)

Until the planned gt-v2.1 release, published third-party figures refer to tag **`corpus/2026-08-08-gt-v2`** (commit `776cc0b`), **not** to default-branch HEAD.

Expected digests:

| Bundle | Chain head | Bundle digest (`bundle_manifest_hash`) |
|---|---|---|
| `examples/golden-trace` | `71c10986320fa148ab89c65c3f92a4ddd12ebfaac2db4f9099fa0443ccb0b564` | `b45f7c47c81e06bceddb5694cd2b0f28cd2afd5082e5c1102b217c713d344352` |
| `examples/golden-trace-ind` | `93733e6a8b6f6be299f656ddfb951f13c9da4756f9d37470649ac3414056fba4` | `b926af903de3d5088a253a486044a7fc1bf8afd046958da0054ea152fc7c3463` |

### Clone and check out the tag

```bash
git clone https://github.com/magentixai/axes.git
cd axes
git fetch --tags
git checkout corpus/2026-08-08-gt-v2
```

### Regenerate both corpora

```bash
python3 examples/golden-trace/generate_golden_trace.py
python3 examples/golden-trace-ind/generate_golden_trace.py
```

A clean second regeneration must produce an empty `git diff --stat` against the committed `out/` trees.

### Compare digests

Read `chain_head` and `bundle_manifest_hash` from each `out/manifest.json` and compare to the table above. On the tagged tree, `tools/axes_canonical.py` plus `vectors/expected.json` pin envelope-level canonical bytes; run the in-repo reference verifier from that tree (see `vectors/README.md` on `golden-trace-v2` until merge).

## Superseded or retired tags

| Tag | Meaning |
|---|---|
| `corpus/2026-08-08-gt-v2` | Verified gt-v2.0 (corpus of record until gt-v2.1) |
| `corpus/2026-08-15-pre-merge` | Retired default-branch lineage; never externally verified |

To verify a superseded release, check out that tag and compare against the row in [`RELEASES.md`](RELEASES.md). Do not mix a tag's envelopes with another tag's expected digests.

## How to report a mismatch

Open a [Conformance test proposal](CONTRIBUTING.md) issue (or comment on [axes#6](https://github.com/magentixai/axes/issues/6)) with: the tag or commit you checked out, the digest you computed, the digest you expected, OS and Python version, and whether a second regeneration was dirty. A mismatch against default-branch HEAD while following a published gt-v2.0 figure is expected today; check the tag first.

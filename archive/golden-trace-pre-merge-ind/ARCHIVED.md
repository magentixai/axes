# Archived: retired pre-merge lineage (never the corpus of record)

This directory is the Golden Trace lineage that sat on the default branch until gt-v2.1 replaced it there. The generator and `out/` are preserved byte for byte as they were on `main` at `c74de15` (README.md gains only an archive banner); the same lineage is tagged `corpus/2026-08-15-pre-merge` (`b5b6d30`).

- It was **never the corpus of record** and was never externally verified. See the "pre-merge lineage" row in [`RELEASES.md`](../../RELEASES.md).
- It is not reproducible off Windows: the generator wrote with the platform-default encoding and OS path separators. The gt-v2.0 generator fixed both on 7 Aug 2026; the fix was never carried here.
- It carries the retired anchor form (`write_once_store (SIMULATED)` with `externally_anchored`). Do not cite it; do not read its anchors as an existence bound (D-015).

The current corpus is in [`examples/golden-trace/`](../../examples/golden-trace/) and [`examples/golden-trace-ind/`](../../examples/golden-trace-ind/) (gt-v2.1).

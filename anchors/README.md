# External anchors

Detached anchors for AXES release statements and other subjects. An anchor here proves that a subject's digest existed by a stated time, verified by a party other than the AXES maintainers. Nothing under `anchors/` changes any published corpus byte.

| Directory | Subject | Subject digest |
|---|---|---|
| `gt-v2.0/` | `release_statement.json`: RFC 8785 bytes committing to both Golden Trace v2.0 chain heads and bundle digests at tag `corpus/2026-08-08-gt-v2` | `d53f3eb5720d1676088609d4ea6f340121be9a7fc6e97efdf158fa3b96e84216` |

Each directory holds:

- the subject file (its SHA-256 is the anchored digest; recompute it yourself);
- `anchoring.json`: the WO18 A2 block (`anchored_subject_*` plus one entry per anchor in `anchors[]`);
- `proofs/<method>/`: the proof files and their `proof_manifest.json`;
- `last_run.json`: the GitHub Actions run that produced or upgraded the anchors (public log).

## Verify

```bash
python -m pip install -r tools/anchoring/requirements.txt
python tools/anchoring/verify_anchor.py anchors/gt-v2.0 --subject anchors/gt-v2.0/release_statement.json
```

No network access is used. Procedures and what each anchor does and does not establish: [`docs/anchoring-profiles.md`](../docs/anchoring-profiles.md).

## Produce

Anchors are produced by the `anchor` workflow (`.github/workflows/anchor.yml`), dispatched manually; a scheduled run every six hours upgrades pending OpenTimestamps proofs. Each run commits its results under `anchors/` with `last_run.json` pointing at the public run log. `basis_status` is written by the tool from what the anchoring service returned, never by hand.

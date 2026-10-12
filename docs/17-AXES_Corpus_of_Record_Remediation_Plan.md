# AXES corpus-of-record remediation plan
 
**Problem:** the AXES repo has two divergent corpora on two branches. The externally verified one is not the one a third party gets by default. Three parties have published digests that cannot be reproduced from the default branch.
**Goal:** one source of truth, permanently citable, obvious to anyone who lands on the repo, and a governance rule that stops it recurring.
**Written:** 15 Aug 2026.
**Conventions:** British spelling. NO EM DASHES in repo text. "Magentix AI", never bare "Magentix".
 
---
 
## 1. The situation, stated precisely
 
| | fin chain head | fin bundle | ind chain head | ind bundle | `anchoring_latency` form | `vectors/` | verifier |
|---|---|---|---|---|---|---|---|
| **`golden-trace-v2` @ `776cc0b`** | `71c10986…` | `b45f7c47…` | `93733e6a…` | `b926af903…` | `_ms` | yes, 11 pinned | `tools/axes_canonical.py` |
| **`main` @ `b5b6d30`** | `adbde9ed…` | `a900cf39…` | `fde448ee…` | `b3244c5f…` | renamed (D-017) | no | no |
 
**These are two different corpora, not two versions of one.** The divergence predates D-017: the anchor envelope's internal `chain_head_hash` is `41a6eea3…` on main against `bb8c3c34…` on v2, and main carried that before the rename commit.
 
**Who has published against which.** All external verification is against `776cc0b` on the v2 branch: Colin H Winter (`MarkovianProtocol`) twice, 7 and 8 Aug, canoncheck two-sided 152/152 plus file-level 78/78; Kevin Zhang (`wowlegend`, Tersign) 11 Aug, independently reproduced 152/152 with a third stdlib canonicaliser; `giskard09` 7 Aug, clean regen with matching chain heads. **Main's corpus has never been externally verified by anyone.**
 
**The live harm.** A fourth party following those published numbers clones the repo, lands on the default branch, computes `adbde9ed…`, and reasonably concludes the AXES corpus does not reproduce. That is happening now, silently, and it is the failure mode the standard exists to prevent.
 
**What is not wrong.** Guardrail 1 has not been breached. `776cc0b` is intact. D-017 regenerated the unverified corpus, not the verified one. The decision itself is correct and is Martin's own bar Rule 3.
 
---
 
## 2. Phase 0 - today, and it stops the confusion immediately
 
Two actions, under an hour, no merge, no regeneration.
 
**0a. Tag the verified commit.** Branches move; tags do not. Colin, Kevin and Pablo cited a branch state, and the moment that branch merges or rebases their citations rot.
 
```
git tag -a corpus/2026-08-08-gt-v2 776cc0b -m "Golden Trace v2 corpus as independently verified 7-11 Aug 2026"
git push origin corpus/2026-08-08-gt-v2
```
 
Tag main's current corpus too, so the retired lineage stays citable rather than vanishing:
 
```
git tag -a corpus/2026-08-15-pre-merge b5b6d30 -m "Pre-merge default-branch corpus lineage; never externally verified"
```
 
**0b. Put a corpus-of-record note at the top of the README on both branches.** Above the fold, before anything else. Draft text:
 
> ## Corpus of record
>
> The Golden Trace corpus that external parties have independently verified is tagged **`corpus/2026-08-08-gt-v2`** (commit `776cc0b`).
>
> | Bundle | Chain head | Bundle digest |
> |---|---|---|
> | `golden-trace` (fin) | `71c10986…` | `b45f7c47…` |
> | `golden-trace-ind` | `93733e6a…` | `b926af903…` |
>
> **The default branch currently carries a different, earlier corpus lineage that has not been externally verified.** If you are reproducing published figures, or following a verification result cited in a public thread, check out the tag above. A reconciliation is in progress and is tracked in [`RELEASES.md`](RELEASES.md).
 
That single paragraph converts a silent trap into a stated, dated limitation. It is the honest-stubbing doctrine applied to the repo rather than to a bundle.
 
---
 
## 3. Phase 1 - the reconciliation, as one operation not two
 
**Principle: one regeneration, one supersession, one announcement.** Every corpus change costs three external parties a re-run. Do not spend that twice in a week.
 
**1a. Merge, taking the verified corpus wholesale.** Merge `golden-trace-v2` into the default branch, resolving every conflict under `examples/*/out/`, `vectors/` and `tools/` **in favour of v2**. Keep main's documentation, registers, `PROVENANCE.md`, `NOTICE` and `CONTRIBUTING`. The v2 corpus wins because it is the better artefact (RFC 8785 normative in place of the `GT-JCS-0` stand-in, integer `Amount` with a build assertion barring floats in hash scope, the LF/`.gitattributes` portability fix, custody twins, 11 pinned vectors) and because it is the one the outside world has verified.
 
**1b. Apply the corpus-affecting changes in the same operation.** D-017's rename, plus Task 4 of the alignment work order: remove the stored derived latency field, add `anchor_requested_at`, name the lag as a derivation in the catalogue, reconcile the `anchored_at` / `emitted_at` / `recorded_at` ordering, and rename `declared_heartbeat_interval_s`. All of it, once.
 
**1c. Regenerate, verify, tag.** Confirm a clean second regen (`git diff --stat` empty), re-hash every file against the fresh manifest, then tag the result as the new release.
 
**1d. Retire the branch.** After the merge, delete `golden-trace-v2` from the remote. The tag preserves it permanently. **There should be exactly one branch anyone is ever asked to look at.**
 
---
 
## 4. Phase 2 - the permanent apparatus
 
Four artefacts, so this cannot recur quietly.
 
**2a. `RELEASES.md` - the corpus release register.** One row per release, newest first. Every published digest resolves forever.
 
```markdown
| Release | Tag / commit | fin chain head | fin bundle | ind chain head | ind bundle | Status | What changed and why | Independently verified by |
|---|---|---|---|---|---|---|---|---|
| gt-v2.1 | `corpus/…` | … | … | … | … | current | Removed the stored anchoring-latency field in favour of `anchor_requested_at` plus a named derivation (D-017, bar Rule 3); reconciled anchor timestamp ordering; renamed `declared_heartbeat_interval_s` | pending |
| gt-v2.0 | `corpus/2026-08-08-gt-v2` (`776cc0b`) | `71c10986…` | `b45f7c47…` | `93733e6a…` | `b926af903…` | superseded, verified | RFC 8785 normative; integer `Amount`; portability fix; custody twins | MarkovianProtocol (7, 8 Aug), wowlegend/Tersign (11 Aug), giskard09 (7 Aug) |
| pre-merge lineage | `corpus/2026-08-15-pre-merge` | `adbde9ed…` | `a900cf39…` | `fde448ee…` | `b3244c5f…` | retired | earlier default-branch lineage | none |
```
 
**Superseded is not the same as wrong.** A superseded release was authoritative on its date, and a citation to it must still resolve. That is the same rule already applied to a dated anchor.
 
**2b. `VERIFY.md` - one page for anyone checking the work.** The exact clone-and-regenerate commands, the expected chain heads and bundle digests for the current release, how to verify at a superseded tag, and how to report a mismatch. Today that procedure exists only inside a comment in issue #6. A validator should never have to reconstruct it from a thread.
 
**2c. `manifest.json` carries its own release identifier.** A bundle on disk should name which release it belongs to, so a file separated from its repo is still self-describing. This is the standard's own doctrine applied to its own artefacts.
 
**2d. The governance rule, in `CONTRIBUTING.md` and the decision register:**
 
> **The corpus changes only in announced releases.** No corpus regeneration lands on the default branch outside a tagged release with a `RELEASES.md` row, published digests, and notice to anyone who has published a verification result against the previous release. A field rename or schema correction may be *decided* at any time; it *lands in the corpus* at the next release.
 
That is the rule D-017 crossed without noticing, and writing it down is the fix.
 
---
 
## 5. Phase 3 - the announcement
 
One comment on AXES issue #6, addressed to `MarkovianProtocol`, `wowlegend` and `giskard09`, covering: that the verified corpus is now tagged and permanently citable; that the default branch carried a different lineage and now does not; the old and new digests side by side; what changed and why; and an explicit invitation to re-run, with the note that this is one supersession rather than a series.
 
**Lead with the branch problem, not the field rename.** The rename is minor and defensible. The fact that the default branch did not reproduce their published numbers is the thing that cost them something, and naming it first is what makes the rest credible. All three have re-run voluntarily before, and all three have publicly corrected their own errors in that thread. It is the right room for a straight account.
 
---
 
## 6. Why this is worth doing properly
 
AXES argues that a record should make it possible to know which bytes were authoritative, when, and on whose say-so. The repo currently cannot answer that about itself.
 
Fixing it with tags, a release register and a stated no-silent-regeneration rule does not merely tidy the repository. It makes the repo a worked example of the discipline the standard is selling, and it gives a straight answer to the sharpest question anyone at the TSC could ask: *how do I know the corpus I verified is the corpus you are citing?*
 
---
 
## 7. Order of execution
 
1. **Phase 0 today** - tags plus the README note. Stops third-party confusion immediately and costs nothing.
2. **Phase 2a and 2b next** - `RELEASES.md` and `VERIFY.md` can be written before the merge and make the merge easier to explain.
3. **Phase 1 as one planned operation** - merge, corpus changes, regenerate, tag, delete the branch.
4. **Phase 3 immediately after** - announce, with both digest sets in the message.
5. **Phase 2c and 2d** - the manifest release identifier and the governance rule, folded into the same release.
**Do not start Phase 1 before Phase 0.** If the merge happens first and someone follows a published citation to a branch that no longer exists in that state, the tag that would have saved them does not exist yet.
# WO17 — Portable JCS property vectors + machine-enforced coverage rule

**Repo:** `magentixai/axes`
**Branch to work from:** `golden-trace-v2` (this is the corpus of record; `main` carries an earlier, externally unverified lineage)
**Raised by:** Martin Sansone · **Date:** 25 Aug 2026
**Driver:** Commitment made to Pablo Etcheverry (giskard09) on 17 Aug for the LFDT `recomputable-evidence` lab rubric. Two contributions were accepted by him and are outstanding as *liftable artefacts*.

---

## 0. Read this before touching anything

**Most of the substance already exists on `golden-trace-v2`. This work order is about making it enforced and liftable, not about building it.**

Current state, verified 25 Aug 2026:

- `vectors/README` already states the coverage rule: *"Standing rule (WO16 Task 16): a check ships with at least one passing and one failing committed vector, or it ships marked as unexercised. TLC-008."*
- A predicate coverage table already exists in that README, in prose.
- Four `axes_jcs_*` property vectors already pin UTF-16 member-sort, NFC/NFD non-normalisation, surrogate handling and digest encoding. Credit for the underlying finding: **Ryan Cason / orionsys** — a locale-aware comparator left 148 tests passing while the bytes diverged. That credit must survive every change in this work order.
- `tools/test_locale_comparator_guard.py` already exists as the negative check.
- `tools/axes_verify.py` already evaluates `expected.json` including typed `reject_code` verdicts.

**So the gaps are three, and they are all about enforcement and portability:**

1. The coverage rule is **documented in a README table, not enforced by code**. A predicate can be added tomorrow with no fixtures and nothing fails.
2. The vectors are **coupled to the AXES corpora** and live on a non-default branch. Pablo cannot lift them into a neutral rubric without importing AXES.
3. The pinned values are **self-generated**. Nothing in the repo demonstrates agreement with an independent RFC 8785 implementation, which is the exact "self-graded" weakness the lab's rubric exists to catch.

**Task 0, mandatory, before writing any code:** check out `golden-trace-v2`, read `vectors/README`, `vectors/expected.json`, `tools/axes_verify.py`, `tools/generate_jcs_property_vectors.py`, `tools/axes_canonical.py` and `tools/test_locale_comparator_guard.py` in full. Produce a short written inventory of which predicates and which of the four JCS properties are already pinned, and which are not. **Do not assume anything in §2 is missing until that inventory says so.** Where this work order and the repo disagree, the repo is right and the work order is stale — say so rather than following it.

---

## 1. Hard constraints — violating any of these is a failed work order

- **Never hand-edit `canonical_utf8` or `sha256` in `vectors/expected.json`.** Every pinned byte is emitted by `tools/axes_canonical.py`. If a value needs to change, change the generator and regenerate.
- **Do not run `tools/generate_conformance_vectors.py`.** It rewrites the original 11 pins and constitutes a silent corpus edit. Only `tools/generate_jcs_property_vectors.py` may be run — it adds property vectors without rewriting existing pins.
- **Do not regenerate either Golden Trace corpus.** The published chain heads and bundle digests (`corpus/2026-08-08-gt-v2`, commit `776cc0b`) have been externally verified. A regeneration invalidates cited figures in public threads.
- **If any change would alter a published digest, stop and escalate to Martin.** Colin Winter (MarkovianProtocol / canoncheck) must be told before any corpus regeneration — he runs canoncheck against the tag.
- **Do not ship a broken-chain negative fixture.** `vectors/README` already records why: it would mutate the corpus of record. That predicate stays `unexercised` with its reason, and that is the correct outcome, not a gap to close.
- **No new runtime dependencies** in anything intended to be portable. Python standard library only.
- **Preserve all existing credit lines**, in particular Ryan Cason / orionsys on the JCS property vectors.
- **British English** in all prose. **No em dashes** in any file that could become public-facing.

---

## 2. Deliverable A — make the coverage rule executable

**The rule (TLC-008, from WO16 Task 16), restated normatively:**

> Every normative predicate the verifier can evaluate MUST have at least one committed fixture that passes it and at least one committed fixture that fails it. A predicate that cannot have one MUST be declared `unexercised` with a written reason. A predicate that is neither covered nor declared is a conformance failure of the suite itself.

**Why it matters, for the commit message and the register entry:** a predicate that has never returned both verdicts is not a tested predicate. Three independent arrivals at this in one week — Ryan Cason planted a fault and watched 148 tests pass; an implementer withdrew a control after finding it could not return valid for any input; TMerlini's verifier carried a 32-byte constraint that had never fired in a year and returned False for a valid cell. A False from a verifier you have never seen return True is not evidence.

### A1. Add a predicate manifest

Create `vectors/predicates.json`. One entry per normative predicate the verifier evaluates. Suggested shape, adapt to what `axes_verify.py` actually exposes:

```json
{
  "schema": "axes.predicate-coverage/1",
  "predicates": [
    {
      "id": "canonical_bytes_digest",
      "description": "Canonical bytes and SHA-256 digest reproduce from the canonicaliser",
      "pass_fixtures": ["<every vector carrying a pinned canonical_utf8>"],
      "fail_fixtures": ["axes_jcs_collation_ae.json"],
      "fail_mechanism": "locale-like comparator substituted via tools/test_locale_comparator_guard.py"
    },
    {
      "id": "chain_link_sequence",
      "description": "Envelope hash chain link and sequence integrity",
      "pass_fixtures": ["examples/golden-trace/out/envelopes.jsonl", "examples/golden-trace-ind/out/envelopes.jsonl"],
      "fail_fixtures": [],
      "unexercised": true,
      "unexercised_reason": "A committed broken-chain negative would mutate the corpus of record. Deliberately not shipped."
    }
  ]
}
```

Populate it from the existing README table, which already carries the correct content for: canonical bytes/digest, duplicate-key canonicalisation reject, custody independence, unparseable identity, the JCS property set, and chain link/sequence.

**Note the unparseable-identity row carefully.** The README records that `axes_identity_unparseable_hex.json` must return `verification_unavailable`, **not** a reject, and that a verifier rejecting it would be the false negative. That is a typed-outcome predicate, not a binary one. The manifest must express that: for predicates with more than two outcomes, require one committed fixture per declared outcome, not merely one pass and one fail.

### A2. Enforce it in the verifier

Extend `tools/axes_verify.py` so a run fails, with a distinct non-zero exit code, if any of these hold:

- a predicate in `predicates.json` has no pass fixture and is not marked `unexercised`
- a predicate has no fail fixture (or no fixture for a declared non-pass outcome) and is not marked `unexercised`
- a predicate is marked `unexercised` without an `unexercised_reason`
- a fixture named in `predicates.json` does not exist on disk
- **a declared outcome was not actually observed during the run** — this is the load-bearing one. Follow the pattern in `giskard09/action-ref-conformance/manifest-v2/verify.py`: exit 0 only if every declared verdict was observed at least once and every declared reject code was exercised. Counting fixtures is not the same as observing verdicts.

Use distinct exit codes so CI can tell the two apart: **exit 1** = a real conformance failure (a vector behaved wrongly); **exit 2** = the suite itself is broken (a predicate is unaccounted for, a fixture is missing, a declared outcome was never observed).

### A3. Add a self-test that proves the enforcement works

`tools/test_coverage_rule_guard.py`. It must demonstrate that the new check can fail, not merely that it passes — otherwise the enforcement is itself an unexercised predicate, which would be a lovely irony to ship. Suggested: build a temporary in-memory or tmpdir manifest with a predicate missing its fail fixture, assert the verifier exits 2. Do not mutate the committed `predicates.json` to do this.

### A4. Register entries

- `registers/requirements-register.md` — record **TLC-008** as now machine-enforced, citing `predicates.json` and the verifier check. If TLC-008 already has an entry from WO16, amend it rather than duplicating.
- `registers/decision-register.md` — one entry for the decision that predicate coverage is enforced at run time rather than by review, with the three-independent-arrivals rationale and the credit line.

---

## 3. Deliverable B — a portable, liftable JCS property package

**This is the half Pablo actually needs.** The lab rubric cannot depend on AXES, so the vectors must stand alone.

### B1. Create `portable/jcs-properties/`

Self-contained, at the repository root, deliberately **not** under `vectors/` so it is obviously separable. Match the packaging convention the neighbouring suites already use (`giskard09/action-ref-conformance/manifest-v2`, `jsuich/x402-action-receipt/vectors`), because matching it is what makes it liftable without translation:

```
portable/jcs-properties/
  README.md          scope, the four properties, what it does and does not prove, credit
  MANIFEST.json      profile + per-vector expected verdict and reason taxonomy
  vectors/
    *.json           one file per vector, bytes on disk are the fixture
  verify.py          reference verifier, Python stdlib only, zero dependencies
  LICENSE            Apache-2.0
```

`verify.py` must:
- take no arguments and default to its own directory, so `python3 portable/jcs-properties/verify.py` just works
- import nothing outside the standard library, and **not** import from `tools/`
- exit 0 only if every vector matches its declared verdict, both pass and reject verdicts were observed at least once, and every declared reason code was exercised
- exit 1 on a real conformance failure, exit 2 if the suite is internally broken

### B2. The four properties, and what each one catches

Carry across the existing `axes_jcs_*` vectors rather than authoring new ones where they already cover the property. Add only what the Task 0 inventory shows is missing.

| Property | The bug it catches | Fixture requirement |
|---|---|---|
| **UTF-16 member sort** | RFC 8785 §3.2.3 sorts object members by UTF-16 code unit, not code point. A supplementary character (U+10000 and above) encodes as a surrogate pair starting 0xD800, which sorts **before** any character in U+E000–U+FFFF. Python's `sorted()` and `json.dumps(sort_keys=True)` sort by code point and get this **wrong**. This is the bug giskard09 found in his own production canonicaliser. | At least one object whose members include both a supplementary-plane key and a key in U+E000–U+FFFF, where code-point and code-unit ordering **differ**. If the existing vector does not produce differing orders, it does not pin the property. |
| **No normalisation** | RFC 8785 §3.1 performs no Unicode normalisation. `"ä"` as U+00E4 and `"a"` + U+0308 are two distinct members that must **both survive** canonicalisation. A canonicaliser that normalises collapses them and silently changes the digest. | One object carrying both forms as separate members. Assert member count is preserved and both appear in the canonical output. |
| **Code-unit ordering, not locale collation** | A German or ICU collator sorts `ä` adjacent to `a`, therefore before `z`. Code-unit ordering puts U+00E4 (0x00E4) after `z` (0x007A). Indistinguishable from a correct comparator on any ASCII corpus. | `axes_jcs_collation_ae.json` already covers this. Carry it, and carry the locale-comparator guard as the executable negative. |
| **Digest input encoding** | The digest must be over the canonical **UTF-8 bytes**, not over a decoded string or a re-encoded form. | Whichever existing vector pins this. |

**On the surrogate case specifically:** verify by construction that the two orderings actually differ for the chosen keys. A vector that uses supplementary characters but where code-point and code-unit order happen to agree pins nothing. Assert the divergence in a comment in the generator and in `MANIFEST.json`.

### B3. Cross-verify against an independent implementation

**Non-negotiable, and the reason the package is worth anything to a neutrality lab.** Self-generated expected values graded by their own generator are precisely the failure mode the rubric targets.

- Reproduce every pinned value in `portable/jcs-properties/` using at least one independent RFC 8785 implementation that shares no code with `tools/axes_canonical.py`. Candidates: the `rfc8785` PyPI package; the `canonicalize` npm package; the reference test data in `cyberphone/json-canonicalization`.
- Where an independent implementation is available, add `portable/jcs-properties/CROSSCHECK.md` recording: implementation name, version, commit or release pinned, date run, per-vector result, and any divergence.
- **If an independent implementation disagrees, stop and escalate to Martin.** Do not adjust the AXES pins to match, and do not adjust the expected values to make the run green. A divergence is a finding, and it is worth more than a clean pass.
- If no independent implementation can be obtained in the sandbox, say so explicitly in `CROSSCHECK.md` and mark the cross-check **`not_performed`**, with the reason. Do not imply verification that did not occur. That is the honest-absence rule applied to our own suite.

### B4. Scope statement in the README

State plainly what the package does and does not prove. Draft:

> These vectors pin four RFC 8785 properties that an ASCII-only corpus cannot: UTF-16 member ordering, absence of Unicode normalisation, code-unit rather than locale collation, and digest input encoding. Agreement demonstrates that two canonicalisers produce identical bytes on these inputs. It does not demonstrate that either implements RFC 8785 completely, and it says nothing about any signature, anchoring or evidence-semantics layer above the bytes.

Credit line, preserved: the locale-collation property is pinned because **Ryan Cason / orionsys** found a locale-aware comparator that left 148 tests passing while the bytes diverged.

---

## 4. Deliverable C — resolve the branch problem

Pablo, or any steward, currently has to know to check out a non-default branch to find any of this. That is a real barrier to lifting it.

**Do not attempt the `golden-trace-v2` → `main` merge as part of this work order.** It is gated separately (Action Register B2: apply D-017 and Task 4 corpus changes, regenerate, tag, delete the branch, announce) and it touches the corpus of record.

Instead, do the cheap thing:

- Add a short pointer to `tools/README` and `vectors/README` **on `main`** stating that the coverage rule, the JCS property vectors and the portable package live on `golden-trace-v2` until the announced merge, with direct links.
- Add the same pointer to the repository root `README.md` under the existing corpus-of-record note, so anyone arriving cold finds it.
- **`portable/jcs-properties/` should be reachable from `main`** if that can be done without touching corpus files. If it can be added to `main` cleanly as a new, self-contained directory with no dependency on the corpus lineage, do that and say so. If not, leave it on `golden-trace-v2` and make the pointer unambiguous. Flag which you did.

---

## 5. Acceptance criteria

The work order is complete when all of the following are demonstrably true:

- [ ] Task 0 inventory written, listing what already existed before any change
- [ ] `vectors/predicates.json` exists and accounts for **every** normative predicate `axes_verify.py` evaluates
- [ ] Every predicate has pass and fail fixtures, or an `unexercised` flag with a written reason
- [ ] Multi-outcome predicates (e.g. unparseable identity → `verification_unavailable`) declare a fixture per outcome, not merely pass/fail
- [ ] `python tools/axes_verify.py` exits 0 on the current tree
- [ ] `python tools/axes_verify.py` exits **2**, not 1, when a predicate is unaccounted for — proven by `tools/test_coverage_rule_guard.py`
- [ ] The verifier fails if a declared outcome was never observed during the run, not merely if a fixture is absent
- [ ] `python3 portable/jcs-properties/verify.py` runs from a clean checkout with **no** pip install and exits 0
- [ ] `portable/jcs-properties/` imports nothing from `tools/` and nothing outside the standard library
- [ ] The surrogate vector demonstrably has differing code-point and code-unit orderings, asserted not assumed
- [ ] The NFC/NFD vector preserves both members through canonicalisation
- [ ] `CROSSCHECK.md` exists and either records an independent implementation's per-vector results, or states `not_performed` with a reason
- [ ] No published digest changed. `corpus/2026-08-08-gt-v2` chain heads and bundle digests unchanged: `71c10986…`, `b45f7c47…`, `93733e6a…`, `b926af90…`
- [ ] `generate_conformance_vectors.py` was not run
- [ ] Ryan Cason / orionsys credit preserved wherever the JCS property vectors are described
- [ ] Register entries landed in both `registers/requirements-register.md` and `registers/decision-register.md`
- [ ] Pointers added on `main`
- [ ] All prose British English, no em dashes

---

## 6. Deliver back to Martin

A short written summary containing:

1. **What already existed** before this work order (the Task 0 inventory). Martin believes he owes Pablo two things; if they were already largely built, he needs to know that before he replies.
2. **What changed**, file by file.
3. **The cross-check result**, including any divergence, stated plainly.
4. **One paste-ready paragraph for Pablo** describing what the portable package is, where it is, what it pins, what it does not prove, and the credit line — so Martin can send it without rewriting.
5. **Anything you could not do**, and why. An honest partial result is the point of the whole exercise; a disguised one is the failure it exists to catch.

---

*Cross-refs: axes#5 (P1-1 canonicalisation spike) · axes#6 (conformance vectors, canoncheck byte-identity harness) · axes#10 (custody axis) · WO16 Task 16 / TLC-008 · LF-Decentralized-Trust/lab-proposals#2 · `giskard09/composed-attestation-3leg-worked-example` PR#2 (the independence rubric this feeds).*

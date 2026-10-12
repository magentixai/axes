# AXES corpus releases

Every published Golden Trace digest resolves here. **Superseded is not the same as wrong:** a superseded release was authoritative on its date, and a citation to it must still resolve. That is the same rule already applied to a dated anchor.

Reproduce a release with [`VERIFY.md`](VERIFY.md).

| Release | Tag / commit | fin chain head | fin bundle | ind chain head | ind bundle | Status | What changed and why | Independently verified by |
|---|---|---|---|---|---|---|---|---|
| gt-v2.1 | `corpus/2026-10-12-gt-v2.1` (commit recorded on tagging) | `cbd1a73e910bd51f01cf5dd097c9a68869b733550d96db891d0f288bd4db59f1` | `e922486b74689592ddc54c74725c9c5a55d8d793f12cade2e58929ab4801164e` | `5ca428eac8ed5dde5b7720218712bdd2ede484a6892ac7894db2e1772a519dd6` | `dd01b56c718c6a61f06725318ab99738799128d9cb527d5e468e9be5b78ebb31` | current | Every group in [docs/19](docs/19-key-change-index.md): (1) **anchoring block** restructured to Module 14 (`anchored_subject_*`, `anchors[]`); **retires `write_once_store (SIMULATED)`**: method `write_once_store` plus `basis_status: simulated`; **`externally_anchored` no longer asserted over a simulated anchor** (D-015, D-020, D-021); export final anchor uses the same block; (2) stored `anchoring_latency_ms` removed for `anchor_requested_at` and a named derivation; anchor timestamp ordering fixed (D-017, catalogue 1.26); (3) `basis_status` beside every authenticity claim: `envelope_signature_basis_status`, acknowledgment rungs (catalogue 1.27); (4) D-024 naming renames, `*.sha256` to `hash` plus `hash_algorithm`, `declared_heartbeat_interval` as ISO 8601 (`PT60S`); (5) conformance harness key names (`expected.json`, `predicates.json`), `axes_gt_0037` renamed `axes_gt_0036`; (6) release statement anchored with RFC 3161 and OpenTimestamps (below). Verifier: every anchoring block reads `indeterminate` / `basis_not_demonstrated`, none `contradicted`, proved by a two-sided vector | pending: re-verification invited in the release notice to MarkovianProtocol, wowlegend/Tersign and giskard09 |
| gt-v2.0 | `corpus/2026-08-08-gt-v2` (`776cc0b`) | `71c10986320fa148ab89c65c3f92a4ddd12ebfaac2db4f9099fa0443ccb0b564` | `b45f7c47c81e06bceddb5694cd2b0f28cd2afd5082e5c1102b217c713d344352` | `93733e6a8b6f6be299f656ddfb951f13c9da4756f9d37470649ac3414056fba4` | `b926af903de3d5088a253a486044a7fc1bf8afd046958da0054ea152fc7c3463` | superseded, verified | RFC 8785 normative (`RFC8785-JCS`); integer Amount; LF/`.gitattributes` portability fix; custody twins; 11 pinned vectors | MarkovianProtocol (7, 8 Aug 2026), wowlegend/Tersign (11 Aug 2026), giskard09 (7 Aug 2026) |
| pre-merge lineage | `corpus/2026-08-15-pre-merge` (`b5b6d30`) | `adbde9ed20ef4580c77fff54fc2ee15e3cdc45c72245860982cb01e5bec3caec` | `a900cf39fc00394c2da6317eb7c25d022cadf23e227c501dacf3d22c5d6c6233` | `fde448ee3cff3f29b65ac112740a61bb3ab5cb4e8db578ea0cbe57040bf96f43` | `b3244c5f731a0daa33fbf69ebd8b2975a3cf5d604d7ecb06a0fa8e844fb431fd` | retired | Earlier default-branch lineage, including D-017 rename of `anchoring_latency_ms` to `anchoring_latency` applied to this unverified tree. Never the corpus of record. Not reproducible off Windows: generated with the platform-default encoding (CP1252 `Ø` in Ind QIF artifacts) and OS path separators in Fin manifest keys, so Linux and macOS regeneration gives different bundle digests. The gt-v2.0 generator fixed both on 7 Aug 2026 and the fix was not carried to this lineage. | none |

**Corpus of record: gt-v2.1.** Cite gt-v2.1 for new work. Citations to gt-v2.0 still resolve: its tag verifies against the digests above in CI on every push (`tools/releases/gt-v2.0.json`), and its anchors are unchanged. Do not mix a release's envelopes with another release's digests.

## External anchors

Each release statement is anchored outside AXES so a third party can confirm the published digests existed by a stated time without trusting the maintainers. Verify with [`VERIFY.md`](VERIFY.md#check-the-external-anchors); procedures in [`docs/anchoring-profiles.md`](docs/anchoring-profiles.md).

| Release | Release statement digest | Anchor | Method | Status |
|---|---|---|---|---|
| gt-v2.0 | `d53f3eb5720d1676088609d4ea6f340121be9a7fc6e97efdf158fa3b96e84216` | FreeTSA, serial `0x08DE791D`, 2026-10-04T13:53:53Z | RFC 3161 time-stamp authority | verified offline |
| gt-v2.0 | same | Bitcoin `block:969860:000000000000000000021172cf9dff46a5b9c878d233d44a26cc1151614f20d1`, 2026-10-04T14:28:53Z | OpenTimestamps | verified offline (header proof of work; main-chain membership checkable against any Bitcoin node) |
| gt-v2.1 | recorded when the release statement is anchored (`anchors/gt-v2.1/`) | FreeTSA | RFC 3161 time-stamp authority | pending |
| gt-v2.1 | same | Bitcoin, via OpenTimestamps calendars | OpenTimestamps | pending (upgraded by the scheduled `anchor` workflow once in a block) |

Further independent lanes (a witnessed transparency log, an on-chain registry) are added as their operators run them.

## Governance

The corpus changes only in announced releases. No regeneration lands on the default branch outside a tagged release with a row in this file, published digests, and notice to anyone who has published a verification result against the previous release. A field rename or schema correction may be decided at any time; it lands in the corpus at the next release.

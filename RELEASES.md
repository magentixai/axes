# AXES corpus releases

Every published Golden Trace digest resolves here. **Superseded is not the same as wrong:** a superseded release was authoritative on its date, and a citation to it must still resolve. That is the same rule already applied to a dated anchor.

Reproduce a release with [`VERIFY.md`](VERIFY.md).

| Release | Tag / commit | fin chain head | fin bundle | ind chain head | ind bundle | Status | What changed and why | Independently verified by |
|---|---|---|---|---|---|---|---|---|
| gt-v2.1 | not yet tagged | - | - | - | - | planned | One announced regeneration after merge of the verified corpus onto the default branch: remove the stored anchoring-latency field in favour of `anchor_requested_at` plus a named derivation (D-017, bar Rule 3, WO16 Task 4/12); reconcile anchor timestamp ordering; rename `declared_heartbeat_interval_s`. Corpus lands only in this tagged release. | pending |
| gt-v2.0 | `corpus/2026-08-08-gt-v2` (`776cc0b`) | `71c10986320fa148ab89c65c3f92a4ddd12ebfaac2db4f9099fa0443ccb0b564` | `b45f7c47c81e06bceddb5694cd2b0f28cd2afd5082e5c1102b217c713d344352` | `93733e6a8b6f6be299f656ddfb951f13c9da4756f9d37470649ac3414056fba4` | `b926af903de3d5088a253a486044a7fc1bf8afd046958da0054ea152fc7c3463` | current, verified | RFC 8785 normative (`RFC8785-JCS`); integer Amount; LF/`.gitattributes` portability fix; custody twins; 11 pinned vectors | MarkovianProtocol (7, 8 Aug 2026), wowlegend/Tersign (11 Aug 2026), giskard09 (7 Aug 2026) |
| pre-merge lineage | `corpus/2026-08-15-pre-merge` (`b5b6d30`) | `adbde9ed20ef4580c77fff54fc2ee15e3cdc45c72245860982cb01e5bec3caec` | `a900cf39fc00394c2da6317eb7c25d022cadf23e227c501dacf3d22c5d6c6233` | `fde448ee3cff3f29b65ac112740a61bb3ab5cb4e8db578ea0cbe57040bf96f43` | `b3244c5f731a0daa33fbf69ebd8b2975a3cf5d604d7ecb06a0fa8e844fb431fd` | retired | Earlier default-branch lineage, including D-017 rename of `anchoring_latency_ms` to `anchoring_latency` applied to this unverified tree. Never the corpus of record. | none |

**Until gt-v2.1 ships:** treat **gt-v2.0** as the corpus of record for any third-party citation. Do not expect those digests from default-branch HEAD.

## Governance

The corpus changes only in announced releases. No regeneration lands on the default branch outside a tagged release with a row in this file, published digests, and notice to anyone who has published a verification result against the previous release. A field rename or schema correction may be decided at any time; it lands in the corpus at the next release.

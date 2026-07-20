# Security Policy

AXES is an evidence standard; weaknesses in its integrity model, canonicalisation, redaction or access rules are security issues even when no code is involved.

**Reporting.** For vulnerabilities in the specification's cryptographic/integrity design or in reference tooling, please use GitHub's private vulnerability reporting on this repository (Security → Report a vulnerability), or contact the steward via magentix.ai. Please do not open public issues for exploitable weaknesses before coordination.

**In scope:** hash-chain or canonicalisation weaknesses; redaction/tombstone bypasses; envelope spoofing or replay constructions; ways to make gamed or misleading evidence appear conformant; access-model leaks (including restriction metadata leaking restricted facts); reference-tooling vulnerabilities.

**Also welcome (as public issues):** structural misuse concerns - surveillance risk, under-emission incentives, metric gaming - via the *Security / privacy concern* issue template. The [threat model](docs/11-threat-model.md) is the living home for these.

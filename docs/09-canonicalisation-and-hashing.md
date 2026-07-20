# Canonicalisation, Hashing & Amendment

> **Status: in development — Roadmap P1/P3.** This stub states intended scope so reviewers can challenge the plan before the text lands. Comments welcome via the issue templates.

THE open core-design question (P1-1) - gates the schema freeze. Scope: canonical byte form (JCS/RFC 8785 baseline candidate), envelope hash scope (Golden Trace finding: signing-key identity inside, hash and signature outside), chain rules, field-level redaction-tolerant hashing (salted per-field vs Merkle), redaction tombstones, unknown-field treatment, the append-only amendment model, and byte-level test vectors seeded from the Golden Trace.

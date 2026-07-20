# Tools

| Tool | Status |
|---|---|
| `validator/` | Planned (Roadmap P4) - open reference validator; conformance is defined by spec + validator + test vectors, never by any vendor's ingestion |
| `test-vectors/` | Seeding (Roadmap P3) - byte-level canonicalisation/hashing vectors derived from the Golden Trace. The Golden Trace's own build surfaced why these matter: two silent hash-scope mistakes were caught only by its verifier |

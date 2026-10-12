# Vendored copies

`profiles/` and `key-aliases.json` are byte-for-byte copies of the canonical `profiles/` and `schema/key-aliases.json` in this tree. The evaluator reads them here so published evaluation records keep their recorded paths. CI fails if the copies differ. Edit the canonical files, then copy.

# External vectors: x402-payment-fingerprint/0

`vectors.json` is copied unchanged from [babyblueviper1/preaction-governance-conformance](https://github.com/babyblueviper1/preaction-governance-conformance/tree/964e2c141cbac506e73c7d72563ca921b08f4e73/examples/x402-payment-fingerprint), commit `964e2c1` (2026-10-06), licence CC0-1.0, offered on x402-foundation/tsc#4.

SHA-256 of the file as copied: `da788992a1f995329877173700f869d8e6675685f01463cd81732f5e2d033d02`.

The file keeps its author's key names. It is test input, not AXES output, so docs/20 does not apply to it.

`tools/x402/crosscheck_payment_fingerprint.py` runs these vectors through `axes:x402_correlation@1` and checks that both recipes agree on the payment:

- copies that share one fingerprint give one correlation hash;
- payments with different fingerprints give different correlation hashes;
- inputs the fingerprint refuses as malformed, the correlation recipe refuses too.

Both recipes leave out the signature and lowercase addresses. The difference: the fingerprint covers the payment only, while the correlation core also commits to the resource, expiry, both salts and every lane choice. Recipe @1 reads x402 version 2 messages only, so it refuses version 1 copies rather than mapping network aliases. The cross-check therefore runs twice: once on the copies as held (version 1 copies are refused, never split) and once after mapping version 1 aliases to CAIP-2 with the fingerprint's own table.

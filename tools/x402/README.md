# x402 tools (WO20)

| File | Purpose |
|---|---|
| `x402_correlation.py` | `axes:x402_correlation@1`: the correlation core and `correlation_hash` from a PaymentRequired and PaymentPayload; receipt and party checks; #3220 mandate-binding recomputation. Standard library plus `jcs` |
| `test_x402_correlation.py` | Two-sided self-test over `vectors/` |
| `generate_correlation_vectors.py` | Regenerates `vectors/` from the worked example (deterministic; CI checks it regenerates identically) |
| `generate_b2b_vat_example.py` | Development tool for `examples/x402-b2b-vat/` (needs `eth-account`; test keys only) |

Inputs under any `x402-wire/` directory are x402 messages in x402's own spelling; everything AXES emits follows docs/20.

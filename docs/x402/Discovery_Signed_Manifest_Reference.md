# Discovery signed manifest - reference design and build note

**Purpose.** A reference `/.well-known/x402` manifest signed with a detached-signature hook, so an independent consumer (e.g. a daily discovery sweep) can verify the descriptor's own `payTo` / `role` / `settlementAddresses` were authored by the domain operator, not merely served. It is the concrete instance of the descriptor-authenticity requirement (Walter's R5) proposed for the next #2979 revision.

**Aligned with:** magentixai/x402-signed-manifest-ref mechanism **1.1.1** (`v: "x402sig1"`; pure Ed25519 over canonical bytes; SHA-256 as content digest only). See also [`AXES_AEP_x402_Coherence_Tracker.md`](AXES_AEP_x402_Coherence_Tracker.md).

## The three-layer model

1. **Pointer** - the `_x402.<domain>` TXT record pointing at the manifest. Authenticated by DNSSEC (Walter's draft).
2. **Payload** - the `/.well-known/x402` manifest itself, where `payTo`, `acceptedNetworks`, and the host's declared wallets and role live. Backstopped by TLS alone today. This is the layer the reference signs.
3. **Key** - the verifying key, published out of band in DNS (DKIM precedent), ideally DNSSEC-signed, so a client can check the payload signature without trusting the server that served it.

DNSSEC authenticates the key record; the key verifies the payload. That is the loop TLS cannot close on its own.

## 1. The manifest (the payload being signed)

```json
{
  "x402Version": 2,
  "resources": [ ... ],
  "payTo": { "eip155:8453": "0x..." },
  "acceptedNetworks": ["eip155:8453"],
  "host": {
    "role": "origin",                     // origin | facilitator | proxy_gateway
    "settlementAddresses": { "eip155:8453": ["0x..."] }
  },
  "version": { "descriptorVersion": 1, "issuedAt": "<ISO-8601 UTC>" }
}
```

`role` and `settlementAddresses` are self-declared but checkable: the address against the host's own live 402 response, the role against observed on-chain behaviour. The signature makes the declaration non-repudiable and tamper-evident.

## 2. Canonicalisation and signing input

- Canonical form: RFC 8785 (JCS) over the manifest object.
- **Signing input:** pure Ed25519 (RFC 8032) over the canonical bytes (the message), not a SHA-256 prehash.
- **Content digest:** SHA-256 of the canonical bytes, published in the `.sig` for content-addressing / anchoring only - not the signing input.
- Robust to whitespace, key order and CDN re-serialisation, because the signature is over the canonical bytes, not the served bytes.

## 3. The detached signature (sibling file `/.well-known/x402.sig`)

```json
{
  "v": "x402sig1",
  "canon": "RFC8785-JCS",
  "sig_input": "canonical-bytes",
  "alg": "Ed25519",
  "kid": "s1._x402key.<domain>",
  "sig": "<base64url Ed25519 signature over the RFC 8785 canonical manifest bytes>",
  "content_digest": { "alg": "SHA-256", "value": "<hex sha256 of the canonical bytes>" },
  "signedAt": "<ISO-8601 UTC>"
}
```

`v` is the in-band schema id (parallel to DNS `v=x402key1`). Second implementers read `v` from the artefact.

Detached = the signature is not inside the hashed payload; it is this separate artefact, so existing #2979 consumers ignore it and signature-aware consumers fetch it.

## 4. Key discovery in DNS (DKIM precedent)

```
s1._x402key.<domain>.  IN TXT  "v=x402key1; alg=Ed25519; k=<base64url public key>"
```

DNSSEC-signed by the zone is the intended anchor for the key record. The `kid` in the `.sig` names which key record to fetch.

## 5. Verification procedure

1. Resolve `_x402.<domain>` TXT -> manifest URL.
2. Fetch the manifest and `.sig`.
3. Resolve the key record named by `kid` -> public key.
4. Canonicalise the manifest (RFC 8785); verify `sig` over the canonical bytes with pure Ed25519; recompute SHA-256 and check `content_digest.value`.
5. Report `authentic` | `signature-invalid` (tampered/substituted) | `unsigned` (no `.sig`). This separates "answers differently" from "did not answer".

## Notes

- Role enum is `origin | facilitator | proxy_gateway`, shared with the aggregator descriptor and the evidence record.
- Distinct from the attestations extension (#2999/#3000): this signs the descriptor's own payload; attestations answer whether to trust the participant.
- Agile mechanisms: `canon`, `sig_input`, `alg`, and `content_digest.alg` are declared in the `.sig`. If a future payload needs a prehash, declare a prehash `alg` explicitly - do not reintroduce silent SHA-256-then-Ed25519 under `alg: Ed25519`.
- AXES SE envelope signatures MUST use the same convention (sign canonical bytes; SHA-256 as content digest / chain hash only) when real signing replaces `SIG-STUB`.

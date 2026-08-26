# Independent RFC 8785 cross-check

**Status:** performed  
**Date run:** 2026-08-26  
**Independent implementation:** [`rfc8785`](https://pypi.org/project/rfc8785/) PyPI package  
**Version:** `0.1.4`  
**API used:** `rfc8785.dumps(obj)` → UTF-8 bytes; SHA-256 of those bytes compared to `MANIFEST.json`  
**Shared code with AXES?** No. This package does not import `tools/axes_canonical.py`, `jcs`, or the portable `verify.py` canonicaliser. Pins in `MANIFEST.json` were emitted by the portable stdlib canonicaliser and cross-checked here; they also match the AXES `tools/axes_canonical` bytes for the same fixtures (byte-identical on this date).

## Per-vector results

| Vector | MANIFEST sha256 (prefix) | rfc8785 0.1.4 | Result |
|---|---|---|---|
| `axes_jcs_surrogate_pair_key.json` | `39242da865244d1c…` | `39242da865244d1c…` | agree |
| `axes_jcs_nfc_nfd_pair.json` | `dbdaaf1d6a18db91…` | `dbdaaf1d6a18db91…` | agree |
| `axes_jcs_collation_ae.json` | `03ffae0c9b25e21e…` | `03ffae0c9b25e21e…` | agree |
| `axes_jcs_digest_encoding.json` | `0b38b7240eb6c4b3…` | `0b38b7240eb6c4b3…` | agree |

**Divergence:** none. Full digests:

- surrogate: `39242da865244d1cacb2fc7996b14dc34d49b53654dcf4e93de542141431978b`
- nfc_nfd: `dbdaaf1d6a18db91af67d2a5bdd65e54088cfb1966856d31bdef6255c2df284b`
- collation: `03ffae0c9b25e21ed4f2354729d94372475deae20fded748ad3e5d1a25d68535`
- digest_encoding: `0b38b7240eb6c4b3b1a812935615daac2e5143a7028755112f6ea4a306b9e4a9`

## Reproduce

```bash
pip install rfc8785==0.1.4
python -c "import json, hashlib, rfc8785, pathlib
root = pathlib.Path('portable/jcs-properties')
man = json.loads((root/'MANIFEST.json').read_text(encoding='utf-8'))
for v in man['vectors']:
    obj = json.loads((root/'vectors'/v['id']).read_text(encoding='utf-8'))
    out = rfc8785.dumps(obj)
    if isinstance(out, str):
        out = out.encode('utf-8')
    got = hashlib.sha256(out).hexdigest()
    print(v['id'], 'agree' if got == v['sha256'] else f'DIVERGE {got}')"
```

The portable suite itself needs no pip install: `python portable/jcs-properties/verify.py`.

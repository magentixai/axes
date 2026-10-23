"""EVM primitives for the distributed_ledger anchor profile (docs/anchoring-profiles.md).

Standard library only: keccak-256 (hashlib has SHA-3, which pads differently), RLP, block header
hashing, the logs bloom, receipt encoding and Merkle-Patricia trie proofs. Enough to show offline
that a receipt sits under a block whose hash recomputes from its header; nothing here talks to a
node.
"""

# ---------------------------------------------------------------- keccak-256

_RC = [
    0x0000000000000001, 0x0000000000008082, 0x800000000000808A, 0x8000000080008000,
    0x000000000000808B, 0x0000000080000001, 0x8000000080008081, 0x8000000000008009,
    0x000000000000008A, 0x0000000000000088, 0x0000000080008009, 0x000000008000000A,
    0x000000008000808B, 0x800000000000008B, 0x8000000000008089, 0x8000000000008003,
    0x8000000000008002, 0x8000000000000080, 0x000000000000800A, 0x800000008000000A,
    0x8000000080008081, 0x8000000000008080, 0x0000000080000001, 0x8000000080008008,
]
_ROT = [[0, 36, 3, 41, 18], [1, 44, 10, 45, 2], [62, 6, 43, 15, 61], [28, 55, 25, 21, 56], [27, 20, 39, 8, 14]]
_M64 = (1 << 64) - 1


def _rol(v, n):
    return ((v << n) | (v >> (64 - n))) & _M64 if n else v


def _keccak_f(a):
    for rc in _RC:
        c = [a[x][0] ^ a[x][1] ^ a[x][2] ^ a[x][3] ^ a[x][4] for x in range(5)]
        d = [c[(x - 1) % 5] ^ _rol(c[(x + 1) % 5], 1) for x in range(5)]
        for x in range(5):
            for y in range(5):
                a[x][y] ^= d[x]
        b = [[0] * 5 for _ in range(5)]
        for x in range(5):
            for y in range(5):
                b[y][(2 * x + 3 * y) % 5] = _rol(a[x][y], _ROT[x][y])
        for x in range(5):
            for y in range(5):
                a[x][y] = b[x][y] ^ ((~b[(x + 1) % 5][y]) & b[(x + 2) % 5][y])
        a[0][0] ^= rc


def keccak256(data):
    rate = 136
    msg = bytearray(data) + b"\x01"
    msg += b"\x00" * ((-len(msg)) % rate)
    msg[-1] |= 0x80
    a = [[0] * 5 for _ in range(5)]
    for off in range(0, len(msg), rate):
        block = msg[off:off + rate]
        for i in range(rate // 8):
            a[i % 5][i // 5] ^= int.from_bytes(block[8 * i:8 * i + 8], "little")
        _keccak_f(a)
    return b"".join(a[i % 5][i // 5].to_bytes(8, "little") for i in range(4))


# ---------------------------------------------------------------- RLP

def _hexbytes(v):
    v = v[2:] if v.startswith("0x") else v
    return bytes.fromhex(v if len(v) % 2 == 0 else "0" + v)


def _int_bytes(v):
    n = int(v, 16) if isinstance(v, str) else int(v)
    return n.to_bytes((n.bit_length() + 7) // 8, "big") if n else b""


def _len_prefix(n, short, long_):
    if n < 56:
        return bytes([short + n])
    ln = n.to_bytes((n.bit_length() + 7) // 8, "big")
    return bytes([long_ + len(ln)]) + ln


def rlp_encode(item):
    if isinstance(item, (bytes, bytearray)):
        b = bytes(item)
        if len(b) == 1 and b[0] < 0x80:
            return b
        return _len_prefix(len(b), 0x80, 0xB7) + b
    payload = b"".join(rlp_encode(x) for x in item)
    return _len_prefix(len(payload), 0xC0, 0xF7) + payload


def rlp_decode(data):
    item, end = _rlp_item(data, 0)
    if end != len(data):
        raise ValueError("trailing bytes after RLP item")
    return item


def _rlp_item(d, i):
    p = d[i]
    if p < 0x80:
        return d[i:i + 1], i + 1
    if p < 0xB8:
        n = p - 0x80
        return d[i + 1:i + 1 + n], i + 1 + n
    if p < 0xC0:
        ll = p - 0xB7
        n = int.from_bytes(d[i + 1:i + 1 + ll], "big")
        return d[i + 1 + ll:i + 1 + ll + n], i + 1 + ll + n
    if p < 0xF8:
        n, start = p - 0xC0, i + 1
    else:
        ll = p - 0xF7
        n, start = int.from_bytes(d[i + 1:i + 1 + ll], "big"), i + 1 + ll
    out, j = [], start
    while j < start + n:
        x, j = _rlp_item(d, j)
        out.append(x)
    return out, start + n


# ---------------------------------------------------------------- block header

# Field order of the header hash preimage, oldest fields first. A field is included once the
# chain's header carries it (London adds baseFeePerGas, Shanghai withdrawalsRoot, Cancun the blob
# and beacon fields, Prague requestsHash).
_HEADER_FIELDS = [
    ("parentHash", "b"), ("sha3Uncles", "b"), ("miner", "b"), ("stateRoot", "b"),
    ("transactionsRoot", "b"), ("receiptsRoot", "b"), ("logsBloom", "b"), ("difficulty", "i"),
    ("number", "i"), ("gasLimit", "i"), ("gasUsed", "i"), ("timestamp", "i"), ("extraData", "b"),
    ("mixHash", "b"), ("nonce", "b"), ("baseFeePerGas", "i"), ("withdrawalsRoot", "b"),
    ("blobGasUsed", "i"), ("excessBlobGas", "i"), ("parentBeaconBlockRoot", "b"), ("requestsHash", "b"),
]


def header_hash(header):
    """keccak256(RLP(header fields)), from a JSON-RPC block object."""
    fields = []
    for name, kind in _HEADER_FIELDS:
        if name not in header or header[name] is None:
            break
        v = header[name]
        fields.append(_hexbytes(v) if kind == "b" else _int_bytes(v))
    return "0x" + keccak256(rlp_encode(fields)).hex()


def bloom_contains(bloom_hex, item):
    """Ethereum logs bloom membership (three 11-bit indices from keccak256(item)). A bloom can give a
    false positive, never a false negative, so this is a consistency check, not a proof."""
    bloom = int(bloom_hex, 16)
    h = keccak256(item)
    for i in (0, 2, 4):
        bit = ((h[i] << 8) | h[i + 1]) & 2047
        if not (bloom >> bit) & 1:
            return False
    return True


# ---------------------------------------------------------------- receipts and the receipts trie

def receipt_encoding(r):
    """Consensus encoding of one receipt (EIP-2718 typed envelope; OP Stack deposit fields)."""
    logs = [[_hexbytes(l["address"]), [_hexbytes(t) for t in l["topics"]], _hexbytes(l["data"])] for l in r["logs"]]
    status = _int_bytes(r["status"])
    body = [status, _int_bytes(r["cumulativeGasUsed"]), _hexbytes(r["logsBloom"]), logs]
    rtype = int(r.get("type", "0x0"), 16)
    if rtype == 0x7E:
        if r.get("depositNonce") is not None:
            body.append(_int_bytes(r["depositNonce"]))
        if r.get("depositReceiptVersion") is not None:
            body.append(_int_bytes(r["depositReceiptVersion"]))
    enc = rlp_encode(body)
    return enc if rtype == 0 else bytes([rtype]) + enc


def _nibbles(b):
    out = []
    for x in b:
        out += [x >> 4, x & 15]
    return out


def _hp(nibs, leaf):
    flag = 2 if leaf else 0
    if len(nibs) % 2:
        return bytes([(flag + 1) << 4 | nibs[0]]) + bytes(nibs[i] << 4 | nibs[i + 1] for i in range(1, len(nibs), 2))
    return bytes([flag << 4]) + bytes(nibs[i] << 4 | nibs[i + 1] for i in range(0, len(nibs), 2))


def _hp_decode(b):
    flag = b[0] >> 4
    nibs = ([b[0] & 15] if flag & 1 else []) + _nibbles(b[1:])
    return nibs, bool(flag & 2)


def _node(items, depth, store):
    """Build a trie node over (nibble key, value) items sharing a prefix of length depth.
    Returns the node's reference: its RLP if shorter than 32 bytes, else its keccak256."""
    if len(items) == 1:
        k, v = items[0]
        enc = rlp_encode([_hp(k[depth:], True), v])
    else:
        common = depth
        while all(len(k) > common for k, _ in items) and len({k[common] for k, _ in items}) == 1:
            common += 1
        if common > depth:
            child = _node(items, common, store)
            enc = rlp_encode([_hp(items[0][0][depth:common], False), child])
        else:
            branch, value = [b""] * 16, b""
            for n in range(16):
                sub = [(k, v) for k, v in items if len(k) > depth and k[depth] == n]
                if sub:
                    branch[n] = _node(sub, depth + 1, store)
            for k, v in items:
                if len(k) == depth:
                    value = v
            enc = rlp_encode(branch + [value])
    if len(enc) < 32:
        return rlp_decode(enc)
    h = keccak256(enc)
    store[h] = enc
    return h


def receipts_trie(receipts):
    """Return (root hex, store of node hash -> node bytes) for a block's receipts, keyed by RLP(index)."""
    items = sorted((_nibbles(rlp_encode(_int_bytes(i))), receipt_encoding(r)) for i, r in enumerate(receipts))
    store = {}
    ref = _node(items, 0, store)
    if not isinstance(ref, bytes) or len(ref) != 32:
        enc = rlp_encode(ref)
        ref = keccak256(enc)
        store[ref] = enc
    return "0x" + ref.hex(), store


def trie_proof(store, root_hex, index):
    """The nodes on the path from the root to the receipt at `index`, as hex strings."""
    key = _nibbles(rlp_encode(_int_bytes(index)))
    node, proof = store[_hexbytes(root_hex)], []
    while True:
        proof.append("0x" + node.hex())
        item = rlp_decode(node)
        while True:
            if len(item) == 17:
                if not key:
                    return proof
                nxt, key = item[key[0]], key[1:]
            else:
                path, leaf = _hp_decode(item[0])
                if leaf:
                    return proof
                key, nxt = key[len(path):], item[1]
            if isinstance(nxt, list):
                item = nxt
                continue
            break
        node = store[nxt]


def verify_trie_proof(root_hex, index, proof_hex):
    """Walk an inclusion proof. Returns the value bytes at RLP(index) or None if the proof does not hold."""
    key = _nibbles(rlp_encode(_int_bytes(index)))
    want = _hexbytes(root_hex)
    for node_hex in proof_hex:
        node = _hexbytes(node_hex)
        if keccak256(node) != want:
            return None
        item = rlp_decode(node)
        while True:
            if len(item) == 17:
                if not key:
                    return item[16] or None
                nxt, key = item[key[0]], key[1:]
            else:
                path, leaf = _hp_decode(item[0])
                if key[:len(path)] != path:
                    return None
                key = key[len(path):]
                if leaf:
                    return item[1] if not key else None
                nxt = item[1]
            if isinstance(nxt, list):
                item = nxt
                continue
            if nxt == b"":
                return None
            want = nxt
            break
    return None

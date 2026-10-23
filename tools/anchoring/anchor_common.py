"""Shared helpers for AXES anchor producers and the anchor verifier (WO18 A2, A5).

Standard library only. Method-specific code lives in produce.py and verify_anchor.py.
"""
import datetime
import hashlib
import json
import os

ANCHORING_FILE = "anchoring.json"
PROOF_MANIFEST = "proof_manifest.json"

# Registry identifiers for the procedures defined in docs/anchoring-profiles.md.
# An identifier is immutable: a changed procedure gets a new identifier.
PROFILE_OTS = "axes:opentimestamps_sha256_digest@1"
PROFILE_RFC3161 = "axes:rfc3161_sha256_imprint@1"

PROFILE_ANCHOR_REGISTRY = "axes:anchor_registry_bytes32@1"

# CAIP-2 identifier of Bitcoin mainnet (genesis block hash prefix).
BITCOIN_MAINNET = "bip122:000000000019d6689c085ae165831e93"

# AnchorRegistry (giskard09, argentum-core), deployed with CREATE2 at one address on several EVM
# chains: anchor(bytes32 ref) emits Anchored(bytes32 indexed ref, address indexed anchoredBy,
# uint256 timestamp). Selector and topic are keccak-256 of the signatures below.
ANCHOR_REGISTRY_CONTRACT = "0x49feca52bc634a9ab773226d16619dec547794aa"
ANCHOR_REGISTRY_SELECTOR = "eecdf927"   # anchor(bytes32)
ANCHOR_REGISTRY_TOPIC = "0xfe2289542f7a0110ac112c3a4d712afdcaaf2900a1326f4e6f340b563a0e8734"  # Anchored(bytes32,address,uint256)


def sha256_hex(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    with open(path, "rb") as f:
        return sha256_hex(f.read())


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def iso_from_unix(seconds):
    return datetime.datetime.fromtimestamp(seconds, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


def canonical_bytes(obj):
    """RFC 8785 bytes. Uses the jcs package when present; the inputs written here
    contain only ASCII strings, integers, booleans and null, for which sorted-key
    compact JSON is byte-identical to RFC 8785."""
    try:
        import jcs  # noqa: WPS433
        return jcs.canonicalize(obj)
    except ImportError:
        return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def write_json(path, obj):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_proof_manifest(proof_dir, files, description):
    """Hash every proof file; the manifest's own SHA-256 becomes anchor_proof_hash."""
    entries = {}
    for name in sorted(files):
        entries[name] = sha256_file(os.path.join(proof_dir, name))
    manifest = {"manifest_note": description, "file_hash_algorithm": "SHA-256", "file_hashes": entries}
    path = os.path.join(proof_dir, PROOF_MANIFEST)
    write_json(path, manifest)
    return sha256_file(path)


def load_block(anchor_dir):
    path = os.path.join(anchor_dir, ANCHORING_FILE)
    if os.path.exists(path):
        return read_json(path)
    return None


def new_block(subject_type, subject_hash):
    return {
        "anchored_subject_type": subject_type,
        "anchored_subject_hash": subject_hash,
        "anchored_subject_hash_algorithm": "SHA-256",
        "anchors": [],
    }


def upsert_anchor(block, entry):
    block["anchors"] = [a for a in block["anchors"] if a.get("anchor_id") != entry["anchor_id"]]
    block["anchors"].append(entry)
    block["anchors"].sort(key=lambda a: a["anchor_id"])
    return block

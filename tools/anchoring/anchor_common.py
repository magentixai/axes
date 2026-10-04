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

# CAIP-2 identifier of Bitcoin mainnet (genesis block hash prefix).
BITCOIN_MAINNET = "bip122:000000000019d6689c085ae165831e93"


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

#!/usr/bin/env python3
"""Produce real anchors for an AXES subject (WO18 A5.1, A5.2).

  python tools/anchoring/produce.py stamp   --subject FILE --out DIR [--methods opentimestamps,timestamp_authority]
  python tools/anchoring/produce.py upgrade --out DIR

`stamp` submits the subject's SHA-256 to each method and records what the mechanism returned.
`upgrade` completes OpenTimestamps proofs once a Bitcoin attestation exists.

basis_status is written by this tool from the run and never by hand: an entry exists only if the
mechanism returned a proof. A pending OpenTimestamps proof has anchor_requested_at and no
anchored_at; "pending" is derived, never stored (WO18 A2.4).

Needs network access and, for OpenTimestamps, the `opentimestamps` package
(tools/anchoring/requirements.txt); for RFC 3161, the `openssl` binary.
"""
import argparse
import io
import os
import re
import subprocess
import sys
import tempfile
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import anchor_common as ac  # noqa: E402

OTS_CALENDARS = [
    "https://a.pool.opentimestamps.org",
    "https://b.pool.opentimestamps.org",
    "https://a.pool.eternitywall.com",
]
TSA_URL = "https://freetsa.org/tsr"
TSA_CA_URL = "https://freetsa.org/files/cacert.pem"
TSA_CERT_URL = "https://freetsa.org/files/tsa.crt"
TSA_OPERATOR = "https://freetsa.org"
BLOCK_APIS = ["https://blockstream.info/api", "https://mempool.space/api"]
UA = {"User-Agent": "axes-anchor-producer/1 (+https://github.com/magentixai/axes)"}


def http(url, data=None, headers=None, timeout=60):
    req = urllib.request.Request(url, data=data, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


# ---------------------------------------------------------------- OpenTimestamps

def _ots():
    from opentimestamps.core.op import OpSHA256
    from opentimestamps.core.serialize import StreamDeserializationContext, StreamSerializationContext
    from opentimestamps.core.timestamp import DetachedTimestampFile, Timestamp
    from opentimestamps.core.notary import BitcoinBlockHeaderAttestation, PendingAttestation
    return OpSHA256, StreamDeserializationContext, StreamSerializationContext, DetachedTimestampFile, Timestamp, BitcoinBlockHeaderAttestation, PendingAttestation


def ots_stamp(digest, proof_dir):
    OpSHA256, SDC, SSC, DTF, Timestamp, _, _ = _ots()
    ts = Timestamp(digest)
    ok = []
    for cal in OTS_CALENDARS:
        try:
            body = http(cal + "/digest", data=digest, headers={"Accept": "application/vnd.opentimestamps.v1"})
            ts.merge(Timestamp.deserialize(SDC(io.BytesIO(body)), digest))
            ok.append(cal)
        except Exception as exc:  # a calendar being down is not fatal while one succeeds
            print("calendar %s: %s" % (cal, exc), file=sys.stderr)
    if not ok:
        raise SystemExit("no OpenTimestamps calendar accepted the digest; no entry written")
    os.makedirs(proof_dir, exist_ok=True)
    buf = io.BytesIO()
    DTF(OpSHA256(), ts).serialize(SSC(buf))
    with open(os.path.join(proof_dir, "subject.ots"), "wb") as f:
        f.write(buf.getvalue())
    return ok


def _walk(ts):
    yield ts
    for sub in ts.ops.values():
        yield from _walk(sub)


def ots_upgrade(proof_dir):
    """Ask each pending calendar for the completed path; store Bitcoin block headers."""
    OpSHA256, SDC, SSC, DTF, Timestamp, BTC, Pending = _ots()
    path = os.path.join(proof_dir, "subject.ots")
    with open(path, "rb") as f:
        dtf = DTF.deserialize(SDC(io.BytesIO(f.read())))
    changed = False
    for node in list(_walk(dtf.timestamp)):
        for att in list(node.attestations):
            if isinstance(att, Pending):
                try:
                    body = http(att.uri + "/timestamp/" + node.msg.hex(), headers={"Accept": "application/vnd.opentimestamps.v1"})
                except Exception as exc:
                    print("upgrade %s: %s" % (att.uri, exc), file=sys.stderr)
                    continue
                node.merge(Timestamp.deserialize(SDC(io.BytesIO(body)), node.msg))
                changed = True
    if changed:
        buf = io.BytesIO()
        dtf.serialize(SSC(buf))
        with open(path, "wb") as f:
            f.write(buf.getvalue())
    heights = sorted({att.height for _, att in dtf.timestamp.all_attestations() if isinstance(att, BTC)})
    headers = []
    for h in heights:
        name = "bitcoin-header-%d.hex" % h
        hp = os.path.join(proof_dir, name)
        if not os.path.exists(hp):
            for api in BLOCK_APIS:
                try:
                    bhash = http("%s/block-height/%d" % (api, h)).decode().strip()
                    hdr = http("%s/block/%s/header" % (api, bhash)).decode().strip()
                    with open(hp, "w", encoding="ascii", newline="\n") as f:
                        f.write(hdr + "\n")
                    break
                except Exception as exc:
                    print("header %d via %s: %s" % (h, api, exc), file=sys.stderr)
        if os.path.exists(hp):
            headers.append((h, name))
    return headers


def header_time_and_hash(hex_header):
    import hashlib
    raw = bytes.fromhex(hex_header.strip())
    t = int.from_bytes(raw[68:72], "little")
    bhash = hashlib.sha256(hashlib.sha256(raw).digest()).digest()[::-1].hex()
    return t, bhash


# ---------------------------------------------------------------- RFC 3161

def openssl(*args, data=None):
    return subprocess.run(["openssl", *args], input=data, capture_output=True, check=True).stdout


def tsa_stamp(digest_hex, proof_dir):
    os.makedirs(proof_dir, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tsq = os.path.join(tmp, "req.tsq")
        openssl("ts", "-query", "-digest", digest_hex, "-sha256", "-cert", "-out", tsq)
        with open(tsq, "rb") as f:
            req = f.read()
    tsr = http(TSA_URL, data=req, headers={"Content-Type": "application/timestamp-query"})
    with open(os.path.join(proof_dir, "token.tsr"), "wb") as f:
        f.write(tsr)
    for url, name in ((TSA_CA_URL, "tsa-ca.pem"), (TSA_CERT_URL, "tsa.crt")):
        with open(os.path.join(proof_dir, name), "wb") as f:
            f.write(http(url))
    text = openssl("ts", "-reply", "-in", os.path.join(proof_dir, "token.tsr"), "-text").decode()
    gen = re.search(r"Time stamp: (.+)", text).group(1).strip()
    serial = re.search(r"Serial number: (\S+)", text).group(1).strip()
    return gen, serial


def openssl_time_to_iso(s):
    import datetime
    s = re.sub(r"\.\d+", "", s).replace(" GMT", "")
    d = datetime.datetime.strptime(s, "%b %d %H:%M:%S %Y")
    return d.strftime("%Y-%m-%dT%H:%M:%S.000Z")


# ---------------------------------------------------------------- commands

def cmd_stamp(args):
    with open(args.subject, "rb") as f:
        data = f.read()
    import hashlib
    digest = hashlib.sha256(data).digest()
    digest_hex = digest.hex()
    block = ac.load_block(args.out) or ac.new_block(args.subject_type, digest_hex)
    if block["anchored_subject_hash"] != digest_hex:
        raise SystemExit("subject hash differs from the existing anchoring.json; refusing to mix subjects")
    methods = args.methods.split(",")
    if "opentimestamps" in methods:
        pdir = os.path.join(args.out, "proofs", "opentimestamps")
        requested = ac.utc_now()
        cals = ots_stamp(digest, pdir)
        proof_hash = ac.write_proof_manifest(pdir, ["subject.ots"], "OpenTimestamps proof; pending until upgraded. Calendars: " + ", ".join(cals))
        ac.upsert_anchor(block, {
            "anchor_id": "anch:ots",
            "anchoring_method": "opentimestamps",
            "anchor_profile_id": ac.PROFILE_OTS,
            "basis_status": "demonstrated",
            "anchor_commitment_hash": digest_hex,
            "anchor_commitment_hash_algorithm": "SHA-256",
            "anchor_requested_at": requested,
            "anchor_service_ref": ac.BITCOIN_MAINNET,
            "anchor_operator_ref": None,
            "anchor_proof_ref": "proofs/opentimestamps/" + ac.PROOF_MANIFEST,
            "anchor_proof_hash": proof_hash,
            "anchor_verification_procedure_ref": "docs/anchoring-profiles.md#axes-opentimestamps-sha256-digest-1",
        })
    if "timestamp_authority" in methods:
        pdir = os.path.join(args.out, "proofs", "timestamp_authority")
        requested = ac.utc_now()
        gen, serial = tsa_stamp(digest_hex, pdir)
        proof_hash = ac.write_proof_manifest(pdir, ["token.tsr", "tsa-ca.pem", "tsa.crt"], "RFC 3161 token from " + TSA_URL + " with the TSA certificate chain")
        ac.upsert_anchor(block, {
            "anchor_id": "anch:tsa-freetsa",
            "anchoring_method": "timestamp_authority",
            "anchor_profile_id": ac.PROFILE_RFC3161,
            "basis_status": "demonstrated",
            "anchor_commitment_hash": digest_hex,
            "anchor_commitment_hash_algorithm": "SHA-256",
            "anchor_requested_at": requested,
            "anchored_at": openssl_time_to_iso(gen),
            "anchor_service_ref": TSA_URL,
            "anchor_record_ref": "serial:" + serial,
            "anchor_operator_ref": TSA_OPERATOR,
            "anchor_proof_ref": "proofs/timestamp_authority/" + ac.PROOF_MANIFEST,
            "anchor_proof_hash": proof_hash,
            "anchor_verification_procedure_ref": "docs/anchoring-profiles.md#axes-rfc3161-sha256-imprint-1",
        })
    ac.write_json(os.path.join(args.out, ac.ANCHORING_FILE), block)
    print("wrote", os.path.join(args.out, ac.ANCHORING_FILE))


def cmd_upgrade(args):
    block = ac.load_block(args.out)
    if not block:
        raise SystemExit("no anchoring.json in " + args.out)
    entry = next((a for a in block["anchors"] if a["anchoring_method"] == "opentimestamps"), None)
    if not entry:
        print("no OpenTimestamps entry")
        return
    pdir = os.path.join(args.out, "proofs", "opentimestamps")
    headers = ots_upgrade(pdir)
    if not headers:
        print("still pending")
        return
    height, name = headers[0]
    with open(os.path.join(pdir, name)) as f:
        t, bhash = header_time_and_hash(f.read())
    files = ["subject.ots"] + [n for _, n in headers]
    entry["anchor_proof_hash"] = ac.write_proof_manifest(pdir, files, "OpenTimestamps proof with archived Bitcoin block headers")
    entry["anchored_at"] = ac.iso_from_unix(t)
    entry["anchor_record_ref"] = "block:%d:%s" % (height, bhash)
    ac.upsert_anchor(block, entry)
    ac.write_json(os.path.join(args.out, ac.ANCHORING_FILE), block)
    print("upgraded: Bitcoin block", height, bhash)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("stamp")
    s.add_argument("--subject", required=True)
    s.add_argument("--subject-type", default="release_statement",
                   choices=["chain_head", "envelope", "bundle_manifest", "release_statement"])
    s.add_argument("--out", required=True)
    s.add_argument("--methods", default="opentimestamps,timestamp_authority")
    s.set_defaults(fn=cmd_stamp)
    u = sub.add_parser("upgrade")
    u.add_argument("--out", required=True)
    u.set_defaults(fn=cmd_upgrade)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()

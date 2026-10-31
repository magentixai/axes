"""Bundle verification: every file digest, the manifest digest and the stream, offline and inside one root."""
from __future__ import annotations

import hashlib
import os
import stat
from typing import List, Optional, Union

from .canonical import DEFAULT_POLICY, HashPolicy, canonicalize
from .errors import ParseError, ResourceLimitError, UnsafePathError, UnsupportedCapabilityError
from .integrity import verify_stream
from .jsonio import DEFAULT_LIMITS, Limits, load_subject, parse_json, read_bytes
from .results import Finding, State, VerificationReport

SUPPORTED_FORMATS = ("golden_trace_bundle_v2_1",)
MANIFEST = "manifest.json"
STREAM = "envelopes.jsonl"


def safe_join(root: str, relative: str) -> str:
    """Resolve a manifest path inside root. Absolute paths, drive or UNC prefixes, backslashes, '..' and
    links that lead outside root are refused."""
    if not isinstance(relative, str) or not relative or "\\" in relative or "\x00" in relative:
        raise UnsafePathError("path is empty or contains a backslash or NUL")
    if relative.startswith("/") or (len(relative) > 1 and relative[1] == ":") or relative.startswith("//"):
        raise UnsafePathError("absolute path")
    parts = relative.split("/")
    if any(p in ("", ".", "..") for p in parts):
        raise UnsafePathError("path has an empty, '.' or '..' segment")
    root_real = os.path.realpath(root)
    target = os.path.realpath(os.path.join(root_real, *parts))
    try:
        inside = os.path.commonpath([root_real, target]) == root_real
    except ValueError:  # different drives on Windows
        inside = False
    if not inside:
        raise UnsafePathError("path resolves outside the bundle")
    return target


def _read_regular(path: str, limits: Limits) -> bytes:
    """One read of a regular file; anything else (a directory, a device, a FIFO) is refused."""
    if not stat.S_ISREG(os.stat(path).st_mode):
        raise UnsafePathError("not a regular file")
    return read_bytes(path, limits)


def verify_bundle(root: Union[str, os.PathLike], *, policy: HashPolicy = DEFAULT_POLICY,
                  expected_manifest_hash: Optional[str] = None, expected_chain_head: Optional[str] = None,
                  bundle_format: str = "golden_trace_bundle_v2_1", limits: Limits = DEFAULT_LIMITS) -> VerificationReport:
    """Verify an unpacked bundle directory: every file listed in manifest.json against its digest, the
    manifest digest, and the envelope stream with its chain head. Nothing outside root is read, nothing
    is written, and no network is used."""
    if bundle_format not in SUPPORTED_FORMATS:
        raise UnsupportedCapabilityError("bundle format %r is not supported" % (bundle_format,))
    root = os.fspath(root)
    if not os.path.isdir(root):
        raise FileNotFoundError("not a directory: %s" % root)
    findings: List[Finding] = []
    try:
        # The manifest is held to the same containment rule as the files it lists (review finding S6).
        manifest = parse_json(_read_regular(safe_join(root, MANIFEST), limits), limits)
    except UnsafePathError as exc:
        findings.append(Finding("manifest", State.CONTRADICTED, "artifact", "bundle_path_unsafe", "divergence",
                                MANIFEST, str(exc) + "; not read"))
        return VerificationReport("bundle", tuple(findings), release=policy.release)
    except FileNotFoundError:
        findings.append(Finding("manifest", State.INDETERMINATE, "operator", "bundle_file_absent", "absence",
                                MANIFEST, "the bundle has no manifest"))
        return VerificationReport("bundle", tuple(findings), release=policy.release)
    except ParseError as exc:
        findings.append(Finding("manifest", State.CONTRADICTED, "artifact", "value_outside_domain", "divergence",
                                MANIFEST, str(exc)))
        return VerificationReport("bundle", tuple(findings), release=policy.release)
    files = manifest.get("files") if isinstance(manifest, dict) else None
    if not isinstance(files, dict) or not files:
        findings.append(Finding("manifest", State.INDETERMINATE, "artifact", "field_absent_undeclared", "absence",
                                MANIFEST, "the manifest lists no files"))
        return VerificationReport("bundle", tuple(findings), release=policy.release)
    if len(files) > limits.max_files:
        raise ResourceLimitError("manifest lists more than %d files" % limits.max_files)

    good = 0
    snapshots = {}  # bytes as hashed, so the stream checked is the stream committed (review finding S4)
    for rel, digest in files.items():
        try:
            path = safe_join(root, rel)
        except UnsafePathError as exc:
            findings.append(Finding("file", State.CONTRADICTED, "artifact", "bundle_path_unsafe", "divergence",
                                    rel, str(exc) + "; not read"))
            continue
        try:
            st = os.stat(path)
        except FileNotFoundError:
            findings.append(Finding("file", State.INDETERMINATE, "operator", "bundle_file_absent", "absence",
                                    rel, "listed file is not in the bundle"))
            continue
        if not stat.S_ISREG(st.st_mode):
            findings.append(Finding("file", State.CONTRADICTED, "artifact", "bundle_path_unsafe", "divergence",
                                    rel, "listed path is not a regular file"))
            continue
        data = read_bytes(path, limits)
        snapshots[rel] = data
        actual = hashlib.sha256(data).hexdigest()
        if actual != digest:
            findings.append(Finding("file", State.CONTRADICTED, "artifact", "bundle_file_hash_mismatch", "divergence",
                                    rel, "file bytes differ from the manifest digest"))
        else:
            good += 1
    if good == len(files):
        findings.insert(0, Finding("file", State.VERIFIED, note="%d file digests recomputed" % good))

    recomputed = hashlib.sha256(canonicalize(files)).hexdigest()
    stored = manifest.get("bundle_manifest_hash")
    for label, pinned in (("stored bundle_manifest_hash", stored), ("pinned value", expected_manifest_hash)):
        if pinned is None:
            continue
        if pinned == recomputed:
            findings.append(Finding("manifest_hash", State.VERIFIED, note="manifest digest equals the " + label))
        else:
            findings.append(Finding("manifest_hash", State.CONTRADICTED, "artifact", "bundle_manifest_hash_mismatch",
                                    "divergence", MANIFEST, "recomputed manifest digest differs from the " + label))

    stream = None
    if STREAM in snapshots:
        try:
            stream = verify_stream(load_subject(snapshots[STREAM], jsonl=True, limits=limits), policy=policy,
                                   expected_chain_head=expected_chain_head or manifest.get("chain_head"))
            findings.extend(stream.findings)
        except ParseError as exc:
            findings.append(Finding("stream", State.CONTRADICTED, "artifact", "value_outside_domain", "divergence",
                                    STREAM, str(exc)))
    elif STREAM in files:
        pass  # unsafe, absent or not a regular file: reported above as a file finding
    else:
        findings.append(Finding("stream", State.INDETERMINATE, "artifact", "bundle_file_absent", "absence",
                                STREAM, "the manifest lists no envelope stream"))
    return VerificationReport("bundle", tuple(findings), envelope_count=stream.envelope_count if stream else 0,
                              file_count=len(files), chain_head=stream.chain_head if stream else None,
                              sequence_range=stream.sequence_range if stream else None,
                              bundle_manifest_hash=recomputed, release=policy.release,
                              limitations=stream.limitations if stream else VerificationReport.__dataclass_fields__["limitations"].default)

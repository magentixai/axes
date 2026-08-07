#!/usr/bin/env python3
"""
AXES canonical bytes (RFC 8785 JCS) and SHA-256 digest helpers.

Hash scope: envelope with integrity.envelope_hash and integrity.signature removed.
All canonical bytes and digests for conformance vectors MUST be emitted through
this module - never hand-authored.
"""

from __future__ import annotations

import hashlib
import json
import os
from decimal import Decimal
from typing import Any

try:
    import jcs
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "The 'jcs' package is required for RFC 8785 canonicalisation. "
        "Install with: pip install jcs"
    ) from exc

CANONICALISATION_VERSION = "RFC8785-JCS"
HASH_ALGORITHM = "SHA-256"

# Namespaced asset references: fiat = iso4217:<CODE>; crypto = caip19:<CAIP-19 id>
EUR_ASSET = "iso4217:EUR"
# USDC on Base mainnet (eip155:8453) - exercises decimals=6 / higher-precision path
USDC_ASSET = "caip19:eip155:8453/erc20:0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"


def canonical_bytes(obj: Any) -> bytes:
    """RFC 8785 (JCS) canonical UTF-8 bytes."""
    return jcs.canonicalize(obj)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_preimage(envelope: dict) -> bytes:
    """Canonical bytes for envelope hashing (hash fields excluded)."""
    env = json.loads(json.dumps(envelope))
    integ = env.get("integrity", {})
    integ.pop("envelope_hash", None)
    integ.pop("signature", None)
    return canonical_bytes(env)


def envelope_digest(envelope: dict) -> str:
    return sha256_hex(hash_preimage(envelope))


def assert_no_floats_in_hash_scope(envelope: dict, path: str = "") -> None:
    """Fail generation if any JSON float appears in the hash-scoped record."""
    env = json.loads(json.dumps(envelope))
    integ = env.get("integrity", {})
    integ.pop("envelope_hash", None)
    integ.pop("signature", None)
    _walk_no_floats(env, path or "envelope")


def _walk_no_floats(obj: Any, path: str) -> None:
    if isinstance(obj, float):
        raise AssertionError(f"JSON float in hash scope at {path}: {obj!r}")
    if isinstance(obj, dict):
        for k, v in obj.items():
            _walk_no_floats(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _walk_no_floats(v, f"{path}[{i}]")


def amount_from_decimal(
    value: Decimal | str | int,
    *,
    decimals: int = 2,
    asset: str | None = None,
) -> dict:
    """
    Build an Amount object from a decimal quantity.
    Fails if the source decimal carries more precision than decimals permits.
    asset is a namespaced string (iso4217:EUR or caip19:...).
    """
    d = Decimal(str(value))
    factor = Decimal(10) ** decimals
    atomic = d * factor
    if atomic != atomic.to_integral_value():
        raise ValueError(
            f"amount {value!r} is not exact at {decimals} decimal places "
            f"(atomic={atomic})"
        )
    return {
        "value": str(int(atomic)),
        "decimals": decimals,
        "asset": asset if asset is not None else EUR_ASSET,
    }


def ratio_display(numerator: int, denominator: int) -> float:
    """Report-layer utilisation (outside hash scope)."""
    if denominator == 0:
        raise ZeroDivisionError("ratio denominator is zero")
    return numerator / denominator


def decimal_str(value: Decimal | str | float | int, places: int | None = None) -> str:
    """Exact decimal string for dimensionless / dimensional config values (not Amount)."""
    d = Decimal(str(value))
    if places is not None:
        q = Decimal(10) ** -places
        d = d.quantize(q)
        return format(d, f".{places}f")
    return format(d, "f")


def write_text_utf8_lf(path: str, content: str) -> None:
    """Write text as UTF-8 with LF endings on every platform (never CRLF or CP1252)."""
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def write_json_utf8_lf(path: str, obj: Any, *, indent: int | None = 2) -> None:
    """Write JSON as UTF-8 + LF; trailing newline for stable diffs."""
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=indent, ensure_ascii=False)
        f.write("\n")


def assert_manifest_matches_files(out_dir: str, files: dict[str, str]) -> None:
    """Fail if any pinned file hash disagrees with the bytes on disk."""
    for rel, expected in files.items():
        path = os.path.join(out_dir, *rel.split("/"))
        actual = sha256_hex(open(path, "rb").read())
        if actual != expected:
            raise AssertionError(
                f"manifest desync at {rel}: manifest={expected} disk={actual}"
            )

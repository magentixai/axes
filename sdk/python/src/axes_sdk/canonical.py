"""Canonical bytes and envelope digests under a declared release."""
from __future__ import annotations

import copy
import hashlib
from dataclasses import dataclass
from typing import Any, Tuple

from ._ref import canonical as _ref
from .errors import DomainError, UnsupportedCapabilityError

CANONICALIZATION = "RFC8785-JCS"
HASH_FUNCTIONS = {"SHA-256": hashlib.sha256}
SAFE_INTEGER = _ref.SAFE_INTEGER

# Members removed before hashing, per release. gt-v2.0 named the signature integrity.signature; from
# gt-v2.1 it is integrity.envelope_signature. A member is excluded only under the release that defines it.
SELF_REFERENTIAL = {
    "gt-v2.0": ("envelope_hash", "signature"),
    "gt-v2.1": ("envelope_hash", "envelope_signature"),
}
DEFAULT_RELEASE = "gt-v2.1"


@dataclass(frozen=True)
class HashPolicy:
    """What a caller accepts: the release whose hash scope applies, and the algorithms it will compute."""
    release: str = DEFAULT_RELEASE
    supported_hash_algorithms: Tuple[str, ...] = ("SHA-256",)

    def __post_init__(self):
        if self.release not in SELF_REFERENTIAL:
            raise UnsupportedCapabilityError("release %r is not supported; known: %s"
                                             % (self.release, ", ".join(sorted(SELF_REFERENTIAL))))
        unknown = [a for a in self.supported_hash_algorithms if a not in HASH_FUNCTIONS]
        if unknown:
            raise UnsupportedCapabilityError("hash algorithm(s) not implemented: %s" % ", ".join(unknown))


DEFAULT_POLICY = HashPolicy()


def check_domain(value: Any) -> None:
    """Raise DomainError if value holds a fractional or non-finite number, or an integer outside
    +/-(2^53 - 1)."""
    try:
        _ref.check_hash_domain(value)
    except _ref.DomainError as exc:
        raise DomainError(str(exc)) from None


def canonicalize(value: Any) -> bytes:
    """RFC 8785 bytes of a value in the AXES domain. Unlike a general JCS library, this refuses numbers
    that RFC 8785 would round."""
    check_domain(value)
    return _ref.canonical_bytes(value)


def envelope_preimage(envelope: dict, policy: HashPolicy = DEFAULT_POLICY) -> bytes:
    """The exact bytes that are hashed: the envelope without its self-referential members, canonicalised.
    The caller's object is not modified."""
    if not isinstance(envelope, dict):
        raise TypeError("an envelope is a JSON object")
    scoped = copy.deepcopy(envelope)
    integrity = scoped.get("integrity")
    if isinstance(integrity, dict):
        for name in SELF_REFERENTIAL[policy.release]:
            integrity.pop(name, None)
    return canonicalize(scoped)


def declared_algorithm(envelope: dict, policy: HashPolicy = DEFAULT_POLICY) -> str:
    """The envelope's declared digest algorithm, after checking that it and the canonicalisation
    identifier are supported. Raises UnsupportedCapabilityError otherwise."""
    integrity = envelope.get("integrity") if isinstance(envelope.get("integrity"), dict) else {}
    algorithm = integrity.get("hash_algorithm")
    if algorithm not in policy.supported_hash_algorithms:
        raise UnsupportedCapabilityError("hash_algorithm %r is not supported" % (algorithm,))
    # gt-v2.0 predates canonicalization_version and is RFC 8785 throughout; from gt-v2.1 it is required.
    canon = integrity.get("canonicalization_version", CANONICALIZATION if policy.release == "gt-v2.0" else None)
    if canon != CANONICALIZATION:
        raise UnsupportedCapabilityError("canonicalization_version %r is not supported" % (canon,))
    return algorithm


def hash_envelope(envelope: dict, policy: HashPolicy = DEFAULT_POLICY) -> str:
    """The envelope hash as bare lowercase hexadecimal, under the envelope's declared algorithm."""
    algorithm = declared_algorithm(envelope, policy)
    return HASH_FUNCTIONS[algorithm](envelope_preimage(envelope, policy)).hexdigest()


def genesis_value(algorithm: str = "SHA-256") -> str:
    """previous_envelope_hash of the first envelope: zeros as long as a hexadecimal digest of the algorithm."""
    return "0" * (HASH_FUNCTIONS[algorithm]().digest_size * 2)

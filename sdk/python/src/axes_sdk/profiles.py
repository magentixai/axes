"""Requirement profile sets: loading, pinning and the profiles bundled with the SDK."""
from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from typing import Dict, Iterable, Mapping, Optional, Tuple, Union

from ._ref import evaluate as _ev
from .canonical import canonicalize
from .errors import ParseError, ProfileResolutionError
from .jsonio import DEFAULT_LIMITS, Limits, parse_json, read_bytes

try:
    from importlib.resources import files as _files
except ImportError:  # Python 3.8
    _files = None


def profile_digest(profile: dict) -> str:
    """SHA-256 of a profile's RFC 8785 bytes, as recorded in requirement_profile_hash."""
    return hashlib.sha256(canonicalize(profile)).hexdigest()


@dataclass(frozen=True)
class ProfileSet:
    """Profiles by id@version, plus the key aliases used to read subjects of earlier releases."""
    profiles: Mapping[str, dict]
    alias_entries: Tuple[dict, ...] = field(default=())

    @classmethod
    def from_documents(cls, documents: Iterable[dict], alias_entries: Iterable[dict] = ()) -> "ProfileSet":
        out: Dict[str, dict] = {}
        for p in documents:
            try:
                keys = ("%s@%s" % (p["requirement_profile_id"].split("@")[0], p["requirement_profile_version"]),
                        p["requirement_profile_id"])
            except (KeyError, TypeError, AttributeError):
                raise ProfileResolutionError("a document is not a requirement profile") from None
            for key in keys:
                if key in out and profile_digest(out[key]) != profile_digest(p):
                    raise ProfileResolutionError("%s is defined twice with different content" % key)
                out[key] = p
        return cls(out, tuple(alias_entries))

    def digest(self, ref: str) -> str:
        return profile_digest(self.profiles[ref])

    def closure(self, ref: str) -> Tuple[Tuple[str, ...], Tuple[str, ...], Tuple[str, ...]]:
        """(profiles in resolution order, missing references, references that close a cycle)."""
        order, missing, cycles = _ev.closure(ref, self.profiles)
        return tuple(order), tuple(sorted(set(missing))), tuple(sorted(set(cycles)))

    def check_pins(self, ref: str, pins: Mapping[str, str]) -> None:
        """Raise ProfileResolutionError unless every profile in ref's closure has the pinned digest.
        A profile in the closure without a pin is refused too: pin the whole closure."""
        order, missing, _ = self.closure(ref)
        if missing:
            raise ProfileResolutionError("not available: " + ", ".join(missing))
        for r in order:
            if r not in pins:
                raise ProfileResolutionError("no pin for %s, which %s depends on" % (r, ref))
            if pins[r] != self.digest(r):
                raise ProfileResolutionError("%s does not match its pin" % r)


def _read_dir(directory: str, limits: Limits):
    docs = []
    for name in sorted(os.listdir(directory)):
        if name.endswith(".json"):
            value = parse_json(read_bytes(os.path.join(directory, name), limits), limits)
            if isinstance(value, dict) and "requirement_profile_id" in value:
                docs.append(value)
    return docs


def load_profile_set(directory: Union[str, os.PathLike], aliases: Optional[Union[str, os.PathLike]] = None, *,
                     limits: Limits = DEFAULT_LIMITS) -> ProfileSet:
    """Load every profile in a directory (strictly parsed) and, optionally, a key-aliases file."""
    entries = ()
    if aliases is not None:
        value = parse_json(read_bytes(aliases, limits), limits)
        if not isinstance(value, dict) or not isinstance(value.get("entries"), list):
            raise ParseError("the aliases file has no entries list")
        entries = tuple(value["entries"])
    return ProfileSet.from_documents(_read_dir(os.fspath(directory), limits), entries)


def bundled_profiles() -> ProfileSet:
    """The reference profiles and key aliases shipped with this SDK version (copied from the AXES
    repository at build time; see data/MANIFEST.json for their digests)."""
    if _files is None:
        raise RuntimeError("bundled profiles need Python 3.9 or later")
    data = _files("axes_sdk") / "data"
    docs = []
    for item in sorted(data.joinpath("profiles").iterdir(), key=lambda p: p.name):
        if item.name.endswith(".json"):
            value = parse_json(item.read_bytes())
            if isinstance(value, dict) and "requirement_profile_id" in value:
                docs.append(value)
    aliases = parse_json(data.joinpath("key-aliases.json").read_bytes())
    return ProfileSet.from_documents(docs, aliases["entries"])

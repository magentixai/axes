"""Strict ingestion. Every untrusted JSON entry point goes through parse_json."""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from typing import Any, Tuple, Union

from .errors import DuplicateKeyError, ParseError, ResourceLimitError


@dataclass(frozen=True)
class Limits:
    """Upper bounds on what the SDK will read. The defaults admit the published corpora with a wide margin."""
    max_bytes: int = 256 * 1024 * 1024
    max_depth: int = 64
    max_records: int = 1_000_000
    max_files: int = 10_000


DEFAULT_LIMITS = Limits()


def _pairs(items):
    out = {}
    for key, value in items:
        if key in out:
            raise DuplicateKeyError("duplicate member name in a JSON object")
        out[key] = value
    return out


def _constant(name):
    raise ParseError("non-finite number %s" % name)


def _check(value: Any, depth: int, limits: Limits) -> None:
    stack = [(value, depth)]
    while stack:
        item, d = stack.pop()
        if d > limits.max_depth:
            raise ResourceLimitError("nesting deeper than %d" % limits.max_depth)
        if isinstance(item, str):
            try:
                item.encode("utf-8")
            except UnicodeEncodeError:
                raise ParseError("string contains a lone surrogate") from None
        elif isinstance(item, dict):
            for k, v in item.items():
                stack.append((k, d + 1))
                stack.append((v, d + 1))
        elif isinstance(item, list):
            stack.extend((v, d + 1) for v in item)


def parse_json(data: Union[bytes, str], limits: Limits = DEFAULT_LIMITS) -> Any:
    """Parse one JSON text strictly: UTF-8, no duplicate members, no NaN or Infinity, no lone surrogates,
    bounded size and depth. Numbers keep their JSON type; the hash-scope domain is checked separately."""
    if isinstance(data, bytes):
        if len(data) > limits.max_bytes:
            raise ResourceLimitError("input larger than %d bytes" % limits.max_bytes)
        try:
            data = data.decode("utf-8")
        except UnicodeDecodeError:
            raise ParseError("input is not valid UTF-8") from None
    elif len(data) > limits.max_bytes:
        raise ResourceLimitError("input larger than %d bytes" % limits.max_bytes)
    if data.startswith("﻿"):
        raise ParseError("input starts with a byte order mark")
    try:
        value = json.loads(data, object_pairs_hook=_pairs, parse_constant=_constant)
    except (DuplicateKeyError, ParseError):
        raise
    except ValueError as exc:
        raise ParseError("not valid JSON: %s" % exc.__class__.__name__) from None
    _check(value, 0, limits)
    return value


@dataclass(frozen=True)
class Subject:
    """An envelope stream as read: the parsed envelopes, the exact bytes, and their SHA-256."""
    envelopes: Tuple[dict, ...]
    raw: bytes
    sha256: str
    source: str = "<memory>"

    def __len__(self) -> int:
        return len(self.envelopes)


def read_bytes(path: Union[str, os.PathLike], limits: Limits = DEFAULT_LIMITS) -> bytes:
    size = os.path.getsize(path)
    if size > limits.max_bytes:
        raise ResourceLimitError("%s is larger than %d bytes" % (os.fspath(path), limits.max_bytes))
    with open(path, "rb") as f:
        return f.read(limits.max_bytes + 1)


def load_subject(source: Union[str, os.PathLike, bytes], *, jsonl: bool = None,
                 limits: Limits = DEFAULT_LIMITS) -> Subject:
    """Read an envelope stream from a path or from bytes. JSON Lines (one envelope per line) is assumed
    for a path ending in .jsonl or for bytes whose first non-blank character is not '['; a JSON array or a
    single JSON object is also accepted."""
    if isinstance(source, (bytes, bytearray)):
        raw, name = bytes(source), "<memory>"
    else:
        raw, name = read_bytes(source, limits), os.fspath(source)
    if jsonl is None:
        if name.endswith(".jsonl"):
            jsonl = True
        elif raw.lstrip()[:1] == b"[":
            jsonl = False
        else:
            try:  # one JSON object, possibly spread over several lines
                jsonl = not isinstance(parse_json(raw, limits), dict)
            except ParseError:
                jsonl = True
    if jsonl:
        envelopes = []
        for number, line in enumerate(raw.split(b"\n"), 1):
            if not line.strip():
                continue
            if len(envelopes) >= limits.max_records:
                raise ResourceLimitError("more than %d records" % limits.max_records)
            try:
                envelopes.append(parse_json(line, limits))
            except ParseError as exc:
                raise ParseError("line %d: %s" % (number, exc)) from None
    else:
        value = parse_json(raw, limits)
        envelopes = value if isinstance(value, list) else [value]
    if not all(isinstance(e, dict) for e in envelopes):
        raise ParseError("every record must be a JSON object")
    return Subject(tuple(envelopes), raw, hashlib.sha256(raw).hexdigest(), name)

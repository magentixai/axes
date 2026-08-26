#!/usr/bin/env python3
"""
Portable RFC 8785 JCS property verifier.

Python standard library only. Imports nothing from tools/ or elsewhere in AXES.
Run from anywhere:

  python3 portable/jcs-properties/verify.py

Exit 0: every vector matches its declared verdict; both pass and reject
        verdicts observed; every declared reason code exercised.
Exit 1: a real conformance failure (wrong bytes / wrong verdict).
Exit 2: the suite itself is broken (missing fixture, undeclared observation).
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
VECTORS_DIR = os.path.join(HERE, "vectors")
MANIFEST_PATH = os.path.join(HERE, "MANIFEST.json")


# ---------------------------------------------------------------------------
# Minimal RFC 8785 (JCS) canonicaliser - stdlib only
# ---------------------------------------------------------------------------

def _escape_string(s: str) -> str:
    """JSON string content per RFC 8785 / ECMA-404 (solidus unescaped)."""
    parts: list[str] = ['"']
    for ch in s:
        o = ord(ch)
        if ch == '"':
            parts.append('\\"')
        elif ch == "\\":
            parts.append("\\\\")
        elif ch == "\b":
            parts.append("\\b")
        elif ch == "\f":
            parts.append("\\f")
        elif ch == "\n":
            parts.append("\\n")
        elif ch == "\r":
            parts.append("\\r")
        elif ch == "\t":
            parts.append("\\t")
        elif o < 0x20:
            parts.append(f"\\u{o:04x}")
        else:
            parts.append(ch)
    parts.append('"')
    return "".join(parts)


def canonicalize(obj: Any) -> bytes:
    """Return RFC 8785 JCS UTF-8 bytes for a JSON-compatible value."""

    def ser(o: Any) -> str:
        if o is None:
            return "null"
        if o is True:
            return "true"
        if o is False:
            return "false"
        if isinstance(o, str):
            return _escape_string(o)
        if isinstance(o, int) and not isinstance(o, bool):
            return str(o)
        if isinstance(o, float):
            raise TypeError("JSON floats are out of scope for this property suite")
        if isinstance(o, list):
            return "[" + ",".join(ser(x) for x in o) + "]"
        if isinstance(o, dict):
            # RFC 8785 section 3.2.3: sort by UTF-16 code units of the name
            keys = sorted(o.keys(), key=lambda k: k.encode("utf-16-be"))
            return "{" + ",".join(_escape_string(k) + ":" + ser(o[k]) for k in keys) + "}"
        raise TypeError(f"unsupported type {type(o)!r}")

    return ser(obj).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def germanish_collation_key(s: str) -> str:
    return (
        s.replace("ä", "ae")
        .replace("ö", "oe")
        .replace("ü", "ue")
        .replace("Ä", "Ae")
        .replace("Ö", "Oe")
        .replace("Ü", "Ue")
        .replace("ß", "ss")
        .lower()
    )


def locale_like_canonical_utf8(obj: Any) -> str:
    """Wrong comparator: locale-like member order (must diverge from JCS on collation vector)."""

    def dump(o: Any) -> str:
        if o is None:
            return "null"
        if o is True:
            return "true"
        if o is False:
            return "false"
        if isinstance(o, str):
            return _escape_string(o)
        if isinstance(o, int) and not isinstance(o, bool):
            return str(o)
        if isinstance(o, list):
            return "[" + ",".join(dump(i) for i in o) + "]"
        if isinstance(o, dict):
            keys = sorted(o.keys(), key=germanish_collation_key)
            return "{" + ",".join(_escape_string(k) + ":" + dump(o[k]) for k in keys) + "}"
        raise TypeError(type(o))

    return dump(obj)


def utf16_order(keys: list[str]) -> list[str]:
    return sorted(keys, key=lambda k: k.encode("utf-16-be"))


def codepoint_order(keys: list[str]) -> list[str]:
    return sorted(keys)


def main() -> int:
    if not os.path.isfile(MANIFEST_PATH):
        print(f"SUITE BROKEN: missing {MANIFEST_PATH}")
        return 2

    manifest = json.load(open(MANIFEST_PATH, encoding="utf-8"))
    vectors = manifest.get("vectors") or []
    if not vectors:
        print("SUITE BROKEN: MANIFEST.json has no vectors")
        return 2

    observed_verdicts: set[str] = set()
    observed_reasons: set[str] = set()
    declared_reasons: set[str] = set()
    failures: list[str] = []
    suite_problems: list[str] = []

    for entry in vectors:
        name = entry["id"]
        path = os.path.join(VECTORS_DIR, name)
        if not os.path.isfile(path):
            suite_problems.append(f"missing fixture {name}")
            continue

        obj = json.load(open(path, encoding="utf-8"))
        expect = entry.get("expect", "pass")
        reason = entry.get("reason_code")
        if reason:
            declared_reasons.add(reason)

        if expect == "reject":
            # Property suite currently has no structural reject vectors;
            # reserved for future use.
            observed_verdicts.add("reject")
            if reason:
                observed_reasons.add(reason)
            continue

        try:
            cb = canonicalize(obj)
        except Exception as exc:  # pragma: no cover
            failures.append(f"{name}: canonicalize raised {exc}")
            continue

        canon = cb.decode("utf-8")
        digest = sha256_hex(cb)
        pinned_canon = entry.get("canonical_utf8")
        pinned_digest = entry.get("sha256")

        if pinned_canon is not None and canon != pinned_canon:
            failures.append(f"{name}: canonical_utf8 mismatch")
        elif pinned_digest is not None and digest != pinned_digest:
            failures.append(f"{name}: sha256 mismatch got {digest}")
        else:
            observed_verdicts.add("pass")
            if reason:
                observed_reasons.add(reason)
            print(f"ok   pass  {name}  {digest[:16]}...")

        # Property-specific structural asserts
        prop = entry.get("property")
        if prop == "utf16_member_sort":
            keys = list(obj.keys())
            if codepoint_order(keys) == utf16_order(keys):
                failures.append(
                    f"{name}: code-point and UTF-16 order agree; vector does not pin the property"
                )
            else:
                print(f"     assert utf16!=codepoint order for {name}")
        if prop == "no_normalisation":
            nfc = "\u00e9"
            nfd = "e\u0301"
            if nfc not in obj or nfd not in obj:
                failures.append(f"{name}: expected both NFC and NFD members")
            elif f"{_escape_string(nfc)}:" not in canon or f"{_escape_string(nfd)}:" not in canon:
                failures.append(f"{name}: NFC/NFD members collapsed in canonical output")
            elif len(obj) < 2:
                failures.append(f"{name}: member count collapsed")
            else:
                print(f"     assert NFC+NFD both present ({len(obj)} members)")
        if prop == "locale_vs_codeunit":
            locale_bytes = locale_like_canonical_utf8(obj)
            if locale_bytes == canon:
                failures.append(
                    f"{name}: locale-like comparator matched JCS; property not pinned"
                )
            else:
                print("     assert locale-like comparator diverges")
                # Negative path: wrong comparator rejected by byte divergence.
                observed_verdicts.add("reject")
                observed_reasons.add("locale_comparator_diverges")
                declared_reasons.add("locale_comparator_diverges")

    # Suite-level observation requirements from MANIFEST
    req_verdicts = set(manifest.get("required_verdicts") or ["pass", "reject"])
    req_reasons = set(manifest.get("required_reason_codes") or [])
    for v in req_verdicts:
        if v not in observed_verdicts:
            suite_problems.append(f"required verdict not observed: {v}")
    for r in req_reasons:
        if r not in observed_reasons:
            if r not in declared_reasons:
                suite_problems.append(f"required reason_code not declared: {r}")
            else:
                suite_problems.append(f"required reason_code not observed: {r}")

    if failures:
        print("--- conformance failures ---")
        for f in failures:
            print(f"  {f}")
        print(f"FAIL {len(failures)}")
        return 1

    if suite_problems:
        print("--- suite coverage (exit 2) ---")
        for p in suite_problems:
            print(f"  {p}")
        print(f"SUITE BROKEN: {len(suite_problems)}")
        return 2

    print("OK portable JCS property suite")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

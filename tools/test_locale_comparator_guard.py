#!/usr/bin/env python3
"""
Deliberate negative check (WO16 Task 6): a locale-like member comparator
must NOT reproduce the pinned JCS bytes for axes_jcs_collation_ae.json.

Credit: an external implementer (Ryan Cason / orionsys) found a canonicaliser
that passed 148 tests while remaining substitutable with a broken comparator,
because every vector was ASCII-keyed. A property that is only named is not pinned.
"""

from __future__ import annotations

import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.axes_canonical import hash_preimage
from tools.axes_verify import germanish_collation_key, locale_like_canonical_utf8

VECTOR = os.path.join(ROOT, "vectors", "axes_jcs_collation_ae.json")
EXPECTED = os.path.join(ROOT, "vectors", "expected.json")


def main() -> int:
    obj = json.load(open(VECTOR, encoding="utf-8"))
    pinned = json.load(open(EXPECTED, encoding="utf-8"))["axes_jcs_collation_ae.json"]["canonical_utf8"]
    jcs = hash_preimage(obj).decode("utf-8")
    locale_like = locale_like_canonical_utf8(obj)
    keys_utf16 = sorted(obj.keys())  # Python 3 str sort is Unicode code point, not UTF-16
    keys_locale = sorted(obj.keys(), key=germanish_collation_key)
    if jcs != pinned:
        print("FAIL: JCS output drifted from pin")
        return 1
    if locale_like == pinned:
        print("FAIL: locale-like comparator matched the pin; the collation property is not pinned")
        return 1
    print("OK: locale-like comparator diverges from pinned RFC 8785 bytes")
    print(f"  utf16/code-point key order: {keys_utf16}")
    print(f"  locale-like key order:      {keys_locale}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

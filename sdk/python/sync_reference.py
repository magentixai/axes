#!/usr/bin/env python3
"""Copies the reference implementation and the published profiles into the SDK package.

The SDK does not reimplement the AXES rules. It packages the repository's reference modules,
rewritten only so that they import from inside the package, and adds a typed, in-memory API on top.
Run from the repository root:

  python sdk/python/sync_reference.py          # write the copies
  python sdk/python/sync_reference.py --check  # exit 1 if any copy differs (CI)
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PKG = os.path.join(REPO, "sdk", "python", "src", "axes_sdk")
HEADER = ("# GENERATED from %s by sdk/python/sync_reference.py. Do not edit here:\n"
          "# change the reference module and run the sync script.\n")

PATH_BLOCK = ('ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))\n'
              "if ROOT not in sys.path:\n"
              "    sys.path.insert(0, ROOT)\n")
MODULES = [
    ("tools/axes_canonical.py", "_ref/canonical.py", []),
    ("tools/axes_anchoring_guard.py", "_ref/anchoring_guard.py", []),
    ("tools/axes_evaluate.py", "_ref/evaluate.py", [
        # A library never edits sys.path (validation finding: coupling to remove).
        (PATH_BLOCK, 'ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))\n'),
        ("from tools.axes_canonical import (", "from .canonical import ("),
        ("from tools import axes_anchoring_guard as anchoring_guard", "from . import anchoring_guard"),
    ]),
]


def rendered():
    """Every generated file as {package-relative path: bytes}."""
    out = {}
    for src, dst, rewrites in MODULES:
        text = open(os.path.join(REPO, src), encoding="utf-8").read()
        for old, new in rewrites:
            if text.count(old) != 1:
                raise SystemExit("sync: %r not found exactly once in %s" % (old[:50], src))
            text = text.replace(old, new)
        out[dst] = (HEADER % src + text).encode("utf-8")
    out["_ref/__init__.py"] = (HEADER % "tools/" + '"""Reference modules, copied verbatim apart from imports."""\n').encode()
    manifest = {}
    for name in sorted(os.listdir(os.path.join(REPO, "profiles"))):
        if name.endswith(".json"):
            data = open(os.path.join(REPO, "profiles", name), "rb").read()
            out["data/profiles/" + name] = data
            manifest["profiles/" + name] = hashlib.sha256(data).hexdigest()
    data = open(os.path.join(REPO, "schema", "key-aliases.json"), "rb").read()
    out["data/key-aliases.json"] = data
    manifest["key-aliases.json"] = hashlib.sha256(data).hexdigest()
    out["data/MANIFEST.json"] = (json.dumps({"source": "profiles/ and schema/key-aliases.json of the AXES repository",
                                             "sha256": manifest}, indent=2, sort_keys=True) + "\n").encode()
    return out


def main(argv):
    check = "--check" in argv
    stale = []
    for rel, data in rendered().items():
        path = os.path.join(PKG, *rel.split("/"))
        current = open(path, "rb").read() if os.path.isfile(path) else None
        if current != data:
            stale.append(rel)
            if not check:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "wb") as f:
                    f.write(data)
    if check:
        print("FAIL SDK copies differ from the reference: " + ", ".join(stale) if stale else "OK SDK copies match the reference")
        return 1 if stale else 0
    print("wrote %d file(s)" % len(stale))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

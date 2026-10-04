#!/usr/bin/env python3
"""AXES key naming lint (docs/20-naming-rules.md).

Checks every key, enum-like value and AXES-minted identifier in the given JSON or JSONL
files against the naming rules N1 to N13. Standard library only.

  python tools/check_key_naming.py FILE_OR_DIR [...] [--baseline FILE] [--write-baseline FILE]

A baseline lists known violations in a frozen corpus of record (D-018), each mapped to its
key change index entry. Known violations are reported but do not fail; anything new fails.
Exit 0 when nothing new is found.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

SNAKE = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)*$")

# N3: the last token of a scalar key is its class word; it fixes the value type.
CLASS_WORDS = {
    # identity and citation
    "id": "identifier of a party, system, component, or of this object itself",
    "ref": "citation of a document, artefact or record a reader fetches",
    "key": "cryptographic or idempotency key identifier",
    # integrity
    "hash": "bare lowercase hex digest",
    "algorithm": "registry identifier of an algorithm",
    "signature": "encoded signature",
    # time
    "at": "RFC 3339 UTC instant, millisecond precision, Z",
    "on": "calendar date YYYY-MM-DD",
    "from": "RFC 3339 UTC instant, start of validity (effective_from only)",
    "until": "RFC 3339 UTC instant, end of validity (effective_until only)",
    "duration": "ISO 8601 duration", "interval": "ISO 8601 duration", "lag": "ISO 8601 duration",
    "latency": "ISO 8601 duration", "timeout": "ISO 8601 duration",
    # quantity
    "count": "non-negative integer", "number": "ordinal or business number string",
    "index": "integer position", "ratio": "decimal string in [0, 1]",
    "value": "measured value (sibling _unit)", "unit": "UCUM unit code", "decimals": "integer scale",
    # other scalars
    "version": "version string", "path": "JSON Pointer (RFC 6901)", "expression": "predicate expression",
    "name": "human-readable name", "note": "free text, never parsed", "indicator": "boolean",
    "text": "exact string payload whose bytes matter (for example canonical JSON)",
    # closed enumerations
    "type": "enum: what kind of thing an object is", "kind": "enum: event classification",
    "class": "enum: category on a declared scale", "status": "enum: outcome or progress of a step",
    "state": "enum: position on a declared ladder or verdict", "code": "enum: reason or condition code",
    "mode": "enum", "phase": "enum", "basis": "enum: epistemic or legal basis", "method": "enum: mechanism",
    "role": "enum: party role", "scope": "enum: reach of an identifier or grant", "source": "enum: origin of a value",
    "scheme": "enum or registry id of an encoding scheme", "level": "enum: graded level",
    "posture": "enum: configured stance", "origin": "enum: producer class", "layer": "enum: capture layer",
    "result": "enum: control or check result",
}
DURATION = {"duration", "interval", "lag", "latency", "timeout"}
# Registered datatypes whose members are fixed (N3 exception).
DATATYPE_MEMBERS = {"value", "asset", "decimals", "unit", "scheme", "ref", "hash", "hash_algorithm"}
# Registered external pass-through blocks: members keep the external system's names (N12).
EXTERNAL_BLOCKS = {"sampling_parameters"}

# Canonicalization fixtures whose keys are the test data itself (exempt, N12).
CANONICALIZATION_FIXTURES = ("axes_jcs_",)

UNIT_TOKENS = {"ms", "s", "sec", "secs", "seconds", "min", "mins", "minutes", "hours", "hrs", "days",
               "mm", "cm", "kg", "g", "bytes", "kb", "mb", "gb", "pct", "percent", "bps", "usd", "eur"}
# N2: American spelling, unabbreviated words. British stems that differ from American spelling.
BRITISH_STEMS = ("isation", "behaviour", "colour", "centre", "licence", "defence", "programme", "catalogue",
                 "utilis", "organis", "harmonis", "canonicalis", "recognis", "authoris", "analyse", "minimis",
                 "maximis", "optimis", "prioritis", "normalis", "serialis", "initialis", "summaris",
                 "standardis", "finalis", "categoris", "travell", "cancell", "labell", "modell", "artefact",
                 "acknowledgement", "judgement")
# N2: abbreviations are not used; approved acronyms and domain terms are listed in docs/20 section 3.
ABBREVIATIONS = {"ack", "org", "cfg", "conf", "msg", "txn", "tx", "req", "resp", "num", "qty", "amt", "cnt",
                 "ts", "dt", "desc", "info", "mgmt", "auth", "attr", "addr", "acct", "svc", "env", "param",
                 "params", "prev", "max", "min", "pct", "seq", "src", "dst", "lat", "dur", "alg"}
ALGORITHM_TOKENS = {"sha256", "sha384", "sha512", "sha1", "md5", "keccak256", "blake2b", "blake3"}
RFC3339 = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,9})?Z$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
HEX = re.compile(r"^[0-9a-f]{40,128}$")
ISO_DURATION = re.compile(r"^P(?!$)(\d+Y)?(\d+M)?(\d+W)?(\d+D)?(T(?=\d)(\d+H)?(\d+M)?(\d+(\.\d+)?S)?)?$")
AXES_ID = re.compile(r"^axes:[a-z][a-z0-9]*(_[a-z0-9]+)*@[0-9A-Za-z.]+$")


def british(word):
    return any(stem in word for stem in BRITISH_STEMS)


def check_key(path, key, value, parent, out):
    def v(rule, msg):
        out.append({"path": path, "key": key, "rule": rule, "detail": msg})

    if parent in EXTERNAL_BLOCKS:
        return
    if not SNAKE.match(key):
        v("N1", "not lower_snake")
        return
    tokens = key.split("_")
    if any(british(t) for t in tokens):
        v("N2", "British spelling in key")
    if any(t in ABBREVIATIONS for t in tokens):
        v("N2", "abbreviation in key")
    if tokens[-1] in UNIT_TOKENS:
        v("N4", "unit in key")
    if any(t in ALGORITHM_TOKENS for t in tokens):
        v("N8", "algorithm name in key; use <x>_hash plus <x>_hash_algorithm")
    if tokens[-1] == "flag" or tokens[0] in ("is", "has"):
        v("N5", "boolean must end _indicator")
    if tokens[-1] in ("timestamp", "time", "date", "datetime"):
        v("N9", "time key must end _at (instant) or _on (date)")
    last = tokens[-1]
    if isinstance(value, bool):
        if last != "indicator":
            v("N5", "boolean must end _indicator")
        return
    if isinstance(value, dict):
        if last in CLASS_WORDS and last not in ("amount",):
            v("N7", "object key ends in a scalar class word")
        return
    if isinstance(value, list):
        if not (last.endswith("s") or last == "items"):
            v("N6", "array key must be plural")
        return
    # scalar
    if last not in CLASS_WORDS and key not in DATATYPE_MEMBERS:
        v("N3", "no class word")
        return
    if len(tokens) == 1 and key not in DATATYPE_MEMBERS:
        v("N3", "bare class word; keys are fully qualified outside registered datatypes")
    if isinstance(value, str):
        if last == "at" and not RFC3339.match(value):
            v("N9", "_at value is not an RFC 3339 UTC instant")
        if last == "on" and not DATE.match(value):
            v("N9", "_on value is not a date")
        if last == "hash" and not HEX.match(value):
            v("N8", "_hash value is not bare lowercase hex")
        if last in DURATION and not ISO_DURATION.match(value):
            v("N4", "duration value is not ISO 8601")
        if value.startswith("axes:") and not AXES_ID.match(value):
            v("N13", "AXES identifier must be axes:<lower_snake>@<version>")
        enumish = last in ("type", "kind", "class", "status", "state", "code", "mode", "phase", "basis",
                           "method", "role", "scope", "source", "level", "posture", "origin", "layer", "result")
        if enumish and SNAKE.match(value) and british(value):
            v("N2", "British spelling in enum value")
    if isinstance(value, int) and last == "count" and value < 0:
        v("N3", "_count must be non-negative")


def data_key(key):
    """Keys that are data, not field names: file names, paths, corpus names in a map (N12)."""
    return any(c in key for c in "./-:@") or not key.isascii()


def walk(obj, path, parent, out):
    if isinstance(obj, dict):
        for k, val in obj.items():
            p = path + "/" + k
            if not data_key(k):
                check_key(p, k, val, parent, out)
            walk(val, p, k, out)
    elif isinstance(obj, list):
        for i, x in enumerate(obj):
            walk(x, path + "/" + str(i), parent, out)


def schema_properties(obj, out, path=""):
    """Treat a JSON Schema's property names as keys (types taken from the schema)."""
    if isinstance(obj, dict):
        for k, sub in (obj.get("properties") or {}).items():
            t = sub.get("type") if isinstance(sub, dict) else None
            if isinstance(t, list):
                t = next((x for x in t if x != "null"), None)
            sample = {"boolean": True, "object": {}, "array": []}.get(t)
            check_key(path + "/" + k, k, sample, None, out)
        for k, sub in obj.items():
            schema_properties(sub, out, path + "/" + k)
    elif isinstance(obj, list):
        for x in obj:
            schema_properties(x, out, path)


def files_in(targets):
    for t in targets:
        if os.path.isdir(t):
            for root, _, names in os.walk(t):
                for n in sorted(names):
                    if n.endswith((".json", ".jsonl")):
                        yield os.path.join(root, n)
        else:
            yield t


def lint(targets):
    found = []
    for f in files_in(targets):
        rel = f.replace(os.sep, "/")
        if os.path.basename(f).startswith(CANONICALIZATION_FIXTURES):
            continue
        out = []
        with open(f, encoding="utf-8") as fh:
            if f.endswith(".jsonl"):
                for n, line in enumerate(fh, 1):
                    if line.strip():
                        walk(json.loads(line), "#%d" % n, None, out)
            else:
                doc = json.load(fh)
                if isinstance(doc, dict) and "$schema" in doc:
                    schema_properties(doc, out)
                else:
                    walk(doc, "", None, out)
        for o in out:
            o["file"] = rel
        found.extend(out)
    return found


def signature(o):
    return (o["file"], o["key"], o["rule"])


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("targets", nargs="+")
    ap.add_argument("--baseline")
    ap.add_argument("--write-baseline")
    a = ap.parse_args(argv)
    found = lint(a.targets)
    distinct = {}
    for o in found:
        distinct.setdefault(signature(o), o)
    if a.write_baseline:
        rows = [{"file": k[0], "key": k[1], "rule": k[2], "detail": v["detail"], "change_index_ref": ""}
                for k, v in sorted(distinct.items())]
        with open(a.write_baseline, "w", encoding="utf-8", newline="\n") as fh:
            json.dump({"note": "Known naming violations in a frozen corpus of record (D-018). Each is fixed in the "
                               "release named by its change index entry.", "violations": rows}, fh, indent=2)
            fh.write("\n")
        print("wrote %d baseline entries" % len(rows))
        return 0
    known = set()
    if a.baseline:
        with open(a.baseline, encoding="utf-8") as fh:
            known = {(r["file"], r["key"], r["rule"]) for r in json.load(fh)["violations"]}
    new = {k: v for k, v in distinct.items() if k not in known}
    for k, o in sorted(distinct.items()):
        print("%s %-4s %-40s %s  [%s]" % ("known" if k in known else "NEW  ", o["rule"], o["key"], o["detail"], o["file"]))
    print("%d distinct (%d known, %d new)" % (len(distinct), len(distinct) - len(new), len(new)))
    return 1 if new else 0


if __name__ == "__main__":
    sys.exit(main())

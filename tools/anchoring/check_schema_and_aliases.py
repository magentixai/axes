#!/usr/bin/env python3
"""Schema and change-index consistency check for the anchoring block (WO18 A2/A3).

1. Every anchors/*/anchoring.json and every examples/anchoring/*.json validates against
   schema/anchoring.schema.json; every examples/anchoring/invalid/*.json is rejected.
2. docs/19-key-change-index.md and schema/key-aliases.json agree one for one: every alias
   path leaf and decision appears in the index, and every index row in a release section is
   covered by at least one alias of the same change type.

Exit 0 when all checks pass. Needs `jsonschema` (tools/anchoring/requirements.txt).
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FAILS = []


def p(*parts):
    return os.path.join(ROOT, *parts)


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def blocks_in(doc):
    if "records" in doc:
        return [r["anchoring"] for r in doc["records"]]
    return [doc]


def check_schema():
    try:
        import jsonschema
    except ImportError:
        print("FAIL jsonschema not installed (pip install -r tools/anchoring/requirements.txt)")
        FAILS.append("jsonschema")
        return
    validator = jsonschema.Draft202012Validator(load(p("schema", "anchoring.schema.json")))
    valid = sorted(glob.glob(p("anchors", "*", "anchoring.json")) + glob.glob(p("examples", "anchoring", "*.json")))
    for path in valid:
        for block in blocks_in(load(path)):
            errs = list(validator.iter_errors(block))
            rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
            print("%s valid   %s%s" % ("ok  " if not errs else "FAIL", rel, "" if not errs else ": " + errs[0].message))
            if errs:
                FAILS.append(rel)
    pv = jsonschema.Draft202012Validator(load(p("schema", "requirement-profile.schema.json")))
    for path in sorted(glob.glob(p("profiles", "*.json"))):
        errs = list(pv.iter_errors(load(path)))
        rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
        print("%s profile %s%s" % ("ok  " if not errs else "FAIL", rel, "" if not errs else ": " + errs[0].message))
        if errs:
            FAILS.append(rel)
    for lane in ("identity", "tax", "evidence"):
        lv = jsonschema.Draft202012Validator(load(p("schema", "x402-wire", lane + "-1.json")))
        for msg in sorted(glob.glob(p("examples", "x402-b2b-vat", "x402-wire", "payment_*.json"))):
            info = ((load(msg).get("extensions") or {}).get(lane) or {}).get("info")
            errs = list(lv.iter_errors(info)) if info is not None else []
            rel = os.path.relpath(msg, ROOT).replace(os.sep, "/")
            print("%s %s lane %s" % ("ok  " if not errs else "FAIL", lane, rel))
            if errs:
                FAILS.append(rel + ":" + lane)
    for path in sorted(glob.glob(p("examples", "anchoring", "invalid", "*.json"))):
        errs = list(validator.iter_errors(load(path)))
        rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
        print("%s reject  %s" % ("ok  " if errs else "FAIL", rel))
        if not errs:
            FAILS.append(rel)


def leaf(path):
    return path.split(".")[-1].replace("[]", "") if path else None


def index_rows(md):
    """Rows of change tables (those with a 'Change type' column) per release section."""
    rows, section, header = [], None, None
    for line in md.splitlines():
        m = re.match(r"^## (\S+) to (\S+)", line)
        if m:
            section = (m.group(1), m.group(2).rstrip(":,;"))
            continue
        if not line.startswith("|") or section is None:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-+:?", c) for c in cells):
            continue
        if "Change type" in cells:
            header = cells
            continue
        if header and len(cells) == len(header):
            rows.append((section, dict(zip(header, cells)), line))
        elif header is None or len(cells) != len(header):
            header = None if "Change type" not in cells else header
    return rows


def decision_text(decision):
    """D-021 stays D-021; WO18-A2 is written 'WO18 A2'; WO16-T18 is written 'WO16 Task 18'."""
    m = re.fullmatch(r"(WO\d+)-T(\d+)", decision)
    if m:
        return "%s Task %s" % m.groups()
    m = re.fullmatch(r"(WO\d+)-(A\d+)", decision)
    return "%s %s" % m.groups() if m else decision


def check_aliases():
    md = open(p("docs", "19-key-change-index.md"), encoding="utf-8").read()
    aliases = load(p("schema", "key-aliases.json"))["entries"]
    rows = index_rows(md)
    ticked = set(re.findall(r"`([^`]+)`", md))
    ticked_text = " ".join(ticked)
    for a in aliases:
        name = "%s -> %s" % (a["from_path"], a["to_path"])
        for leafname in filter(None, (leaf(a["from_path"]), leaf(a["to_path"]))):
            if leafname not in ticked_text:
                print("FAIL alias %s: `%s` not in docs/19" % (name, leafname))
                FAILS.append(name)
        if decision_text(a["decision_ref"]) not in md:
            print("FAIL alias %s: decision %s not in docs/19" % (name, a["decision_ref"]))
            FAILS.append(name)
    for (rf, rt), row, line in rows:
        ctype = row.get("Change type", "").strip("`")
        same = [a for a in aliases if a["from_release_ref"] == rf and a["to_release_ref"] == rt and a["change_type"] == ctype]
        hit = [a for a in same if any(l and ("`%s" % l in line or "%s`" % l in line or l in line)
                                      for l in (leaf(a["from_path"]), leaf(a["to_path"])))]
        if not hit:
            print("FAIL docs/19 row without alias (%s to %s, %s): %s" % (rf, rt, ctype, line[:90]))
            FAILS.append(line[:40])
    print("ok   key-aliases.json (%d entries) and docs/19 (%d rows) checked" % (len(aliases), len(rows)))


def main():
    check_schema()
    check_aliases()
    print("FAILED: %d" % len(FAILS) if FAILS else "OK schema and alias consistency")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())

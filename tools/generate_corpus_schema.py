#!/usr/bin/env python3
"""Generate schema/envelope-corpus-gt-v2.1.schema.json from the published gt-v2.1 corpora.

The schema describes the envelope as it stands in the corpus of record, so implementers (for
example ARBITR) can validate against it today. It is NOT the normative SE v0.1 envelope schema,
which stays blocked on redaction-tolerant hashing and catalogue completion (schema/README.md).

Rules applied (deterministic; rerun after any corpus change):
- top level: every member seen in either corpus is listed; members present in every envelope are
  required; no other top-level member except `extensions` (docs/08 3.3, D-059);
- nested objects list the members seen, with their types, and stay open (modules 02 to 13 are not
  catalogued yet);
- numbers are integers within +/-(2^53 - 1) only (docs/09 value domain); `_at` strings are RFC 3339
  UTC with milliseconds; `_hash` strings are 64 lowercase hex characters (docs/20 N8, N9);
- `se_version` is the literal "0.1-draft" (D-054) and `execution_phase` the four lifecycle values
  (D-055).

  python tools/generate_corpus_schema.py           # write
  python tools/generate_corpus_schema.py --check   # exit 1 if the file would change, or a corpus fails it
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CORPORA = ["examples/golden-trace/out/envelopes.jsonl", "examples/golden-trace-ind/out/envelopes.jsonl"]
OUT = os.path.join(ROOT, "schema", "envelope-corpus-gt-v2.1.schema.json")
SAFE = 2 ** 53 - 1
AT = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$"
HEX64 = r"^[0-9a-f]{64}$"
EXTERNAL_BLOCKS = {"sampling_parameters"}  # as tools/check_key_naming.py (docs/20 N12)


def kind(v):
    if isinstance(v, bool):
        return "boolean"
    if isinstance(v, int):
        return "integer"
    if isinstance(v, float):
        raise SystemExit("float in corpus: outside the AXES value domain")
    if isinstance(v, str):
        return "string"
    if v is None:
        return "null"
    if isinstance(v, list):
        return "array"
    return "object"


class Node:
    """Observed shape of one JSON location across all envelopes."""

    def __init__(self):
        self.kinds = set()
        self.members = {}   # name -> Node, for objects
        self.items = None   # Node, for arrays

    def add(self, v):
        k = kind(v)
        self.kinds.add(k)
        if k == "object":
            for name, sub in v.items():
                self.members.setdefault(name, Node()).add(sub)
        elif k == "array":
            self.items = self.items or Node()
            for e in v:
                self.items.add(e)

    def schema(self, name=""):
        if name in EXTERNAL_BLOCKS:
            return {"type": "object", "additionalProperties": True,
                    "description": "External pass-through block: members keep the external system's names (docs/20 N12)."}
        types = sorted(self.kinds)
        s = {"type": types[0] if len(types) == 1 else types}
        if "integer" in self.kinds:
            s["minimum"], s["maximum"] = -SAFE, SAFE
        if self.kinds == {"string"}:
            if name.endswith("_at"):
                s["pattern"] = AT
            elif name.endswith("_hash"):
                s["pattern"] = HEX64
        if "object" in self.kinds:
            s["properties"] = {n: self.members[n].schema(n) for n in sorted(self.members)}
            s["additionalProperties"] = True
        if "array" in self.kinds and self.items is not None:
            s["items"] = self.items.schema(name)
        return s


def load():
    envs = []
    for rel in CORPORA:
        with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
            envs.extend(json.loads(line) for line in f if line.strip())
    return envs


def build(envs):
    top = Node()
    for e in envs:
        top.add(e)
    required = sorted(set.intersection(*(set(e) for e in envs)))
    props = {n: top.members[n].schema(n) for n in sorted(top.members)}
    props["se_version"] = {"const": "0.1-draft", "description": "Literal string, compared exactly (D-054)."}
    props["execution_phase"] = {"enum": ["advisory", "approval", "execution", "commit"],
                                "description": "Lifecycle stage (D-055)."}
    props["extensions"] = {
        "type": "object",
        "description": "Namespaced extensions (docs/08, D-059).",
        "propertyNames": {"pattern": r"^[a-z0-9-]+(\.[a-z0-9-]+)+$", "not": {"pattern": r"^axes(\.|$)"}},
        "additionalProperties": {
            "type": "object",
            "properties": {"extension_ref": {"type": "string"}, "extension_version": {"type": "string"},
                           "must_understand_indicator": {"type": "boolean"}},
        },
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://github.com/magentixai/axes/schema/envelope-corpus-gt-v2.1.schema.json",
        "title": "AXES envelope as published in the gt-v2.1 corpus (not normative)",
        "description": ("Generated by tools/generate_corpus_schema.py from both gt-v2.1 corpora (%d envelopes). "
                        "Describes the corpus of record so implementers can validate against it. It is not the "
                        "normative SE v0.1 envelope schema, which remains blocked on redaction-tolerant hashing "
                        "and catalogue completion (schema/README.md)." % len(envs)),
        "type": "object",
        "required": required,
        "additionalProperties": False,
        "properties": props,
    }


def render(schema):
    return json.dumps(schema, indent=2, ensure_ascii=False, sort_keys=False) + "\n"


def main(argv):
    envs = load()
    text = render(build(envs))
    try:
        import jsonschema
    except ImportError:
        print("FAIL jsonschema not installed (pip install -r tools/anchoring/requirements.txt)")
        return 1
    schema = json.loads(text)
    jsonschema.Draft202012Validator.check_schema(schema)
    validator = jsonschema.Draft202012Validator(schema)
    bad = [(i, err.message) for i, e in enumerate(envs, 1) for err in validator.iter_errors(e)]
    if bad:
        print("FAIL corpus envelopes do not validate:", bad[:5])
        return 1
    if "--check" in argv:
        with open(OUT, encoding="utf-8") as f:
            if f.read() != text:
                print("FAIL %s is stale: run tools/generate_corpus_schema.py" % os.path.relpath(OUT, ROOT))
                return 1
        print("OK corpus schema current; %d envelopes validate" % len(envs))
        return 0
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print("wrote %s; %d envelopes validate" % (os.path.relpath(OUT, ROOT), len(envs)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

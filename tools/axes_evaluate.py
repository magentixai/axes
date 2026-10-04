#!/usr/bin/env python3
"""
AXES evaluator (WO19): applies a requirement profile to a subject and emits an evaluation record.

  python tools/axes_evaluate.py --profile ID@VERSION --subject PATH [--subject-release gt-v2.0]
                                [--profiles-dir vendor/main/profiles] [--aliases vendor/main/key-aliases.json]
                                [--sequence-range FIRST:LAST] [--evaluated-at INSTANT] [--out FILE]

Deterministic: no model, no network, no clock read in the evaluation path (the evaluation time is
an input). Two evaluators given the same subject, profile and pinned evidence produce the same
result_core_hash (D13). Results use the four-state vocabulary under AXES key names (docs/20).

A subject from an earlier release is read through the key change index (schema/key-aliases.json):
profile field paths are written in current names, and the translation is recorded, never silent
(D-021).

Stdlib plus the existing `jcs` dependency.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from tools.axes_canonical import canonical_bytes, envelope_digest, sha256_hex  # noqa: E402
from tools import axes_anchoring_guard as anchoring_guard  # noqa: E402

EVALUATOR_ID = "axes:reference_evaluator@1"
EVALUATOR_VERSION = "1"
VENDOR = os.path.join(ROOT, "vendor", "main")

LADDERS = {
    "axes:corroboration_state_ladder@1": ["uncorroborated", "internally_corroborated", "source_system_corroborated",
                                         "third_party_confirmed", "externally_anchored"],
    "axes:verification_status_ladder@1": ["unverified", "verification_unavailable", "verified"],
}
NEVER_SATISFIES = {"conflicting_evidence", "verification_failed"}
SEVERITY = {"verified": 0, "not_evaluated": 1, "indeterminate": 2, "contradicted": 3}
OBLIGATION_ORDER = {"optional": 0, "conditional": 1, "required": 2, "prohibited": 3}
MISSING = object()


# ---------- results ----------

def result(ref, state, reason=None, condition=None, subject="artifact", note="", refs=None):
    r = {"requirement_ref": ref, "verification_state": state, "verification_subject_type": subject,
         "observed_note": note, "evidence_refs": sorted(refs or [])[:5]}
    if reason:
        r["verification_reason_code"] = reason
    if condition:
        r["verification_condition_code"] = condition
    return r


def worst(results):
    return max(results, key=lambda r: SEVERITY[r["verification_state"]])


# ---------- paths and key translation ----------

def pointer_get(obj, pointer):
    cur = obj
    for part in [p.replace("~1", "/").replace("~0", "~") for p in pointer.split("/")[1:]]:
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        elif isinstance(cur, list) and part.isdigit() and int(part) < len(cur):
            cur = cur[int(part)]
        else:
            return MISSING
    return cur


class Translator:
    """Maps a current-name pointer to the subject release's pointer via key-aliases.json."""

    def __init__(self, aliases_path, release):
        self.release = release
        self.map = {}
        self.used = []
        if release and aliases_path and os.path.isfile(aliases_path):
            for e in json.load(open(aliases_path, encoding="utf-8"))["entries"]:
                if e["from_release_ref"] == release and e["from_path"] and e["change_type"] == "renamed" \
                        and "[]" not in e["to_path"] and "*" not in e["to_path"]:
                    self.map[e["to_path"]] = e["from_path"]

    def pointer(self, pointer):
        dotted = pointer.strip("/").replace("/", ".")
        if dotted in self.map:
            old = "/" + self.map[dotted].replace(".", "/")
            self.used.append("%s -> %s" % (pointer, old))
            return old
        # bare leaf aliases (from_path without a block prefix), e.g. org_id
        leaf = dotted.rsplit(".", 1)[-1]
        for to, frm in self.map.items():
            if to == leaf and "." not in frm:
                old = pointer.rsplit("/", 1)[0] + "/" + frm
                self.used.append("%s -> %s" % (pointer, old))
                return old
        return pointer


# ---------- condition expressions ----------

TOKEN = re.compile(r'\s*(?:(?P<str>"(?:[^"\\]|\\.)*")|(?P<ptr>/[A-Za-z0-9_~/.-]*)|(?P<name>[a-z_]+)|(?P<sym>[(),\[\]]))')


class PredicateError(ValueError):
    pass


def parse_expression(text):
    tokens, pos = [], 0
    while pos < len(text):
        m = TOKEN.match(text, pos)
        if not m or m.end() == pos:
            if text[pos:].strip() == "":
                break
            raise PredicateError("unexpected input at %d" % pos)
        kind = m.lastgroup
        tokens.append((kind, m.group(kind)))
        pos = m.end()
    i = 0

    def take(kind=None, value=None):
        nonlocal i
        if i >= len(tokens):
            raise PredicateError("unexpected end")
        k, v = tokens[i]
        if (kind and k != kind) or (value and v != value):
            raise PredicateError("expected %s %s, got %s" % (kind, value, v))
        i += 1
        return v

    def node():
        name = take("name")
        take("sym", "(")
        if name in ("all", "any"):
            args = [node()]
            while tokens[i][1] == ",":
                take("sym", ",")
                args.append(node())
            take("sym", ")")
            return (name, args)
        if name == "not":
            a = node()
            take("sym", ")")
            return ("not", a)
        if name in ("present", "absent"):
            p = take("ptr")
            take("sym", ")")
            return (name, p)
        if name == "equals":
            p = take("ptr")
            take("sym", ",")
            v = json.loads(take("str"))
            take("sym", ")")
            return ("equals", p, v)
        if name == "in":
            p = take("ptr")
            take("sym", ",")
            take("sym", "[")
            vals = [json.loads(take("str"))]
            while tokens[i][1] == ",":
                take("sym", ",")
                vals.append(json.loads(take("str")))
            take("sym", "]")
            take("sym", ")")
            return ("in", p, vals)
        raise PredicateError("unknown function " + name)

    tree = node()
    if i != len(tokens):
        raise PredicateError("trailing input")
    return tree


def holds(tree, env, tr):
    op = tree[0]
    if op == "all":
        return all(holds(t, env, tr) for t in tree[1])
    if op == "any":
        return any(holds(t, env, tr) for t in tree[1])
    if op == "not":
        return not holds(tree[1], env, tr)
    value = pointer_get(env, tr.pointer(tree[1]))
    if op == "present":
        return value is not MISSING
    if op == "absent":
        return value is MISSING
    if op == "equals":
        return value == tree[2]
    if op == "in":
        return value in tree[2]
    raise PredicateError(op)


# ---------- durations ----------

DUR = re.compile(r"^P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?$")


def duration_seconds(text):
    m = DUR.match(text or "")
    if not m:
        raise ValueError("unsupported duration " + str(text))
    d, h, mi, s = (int(x) if x else 0 for x in m.groups())
    return ((d * 24 + h) * 60 + mi) * 60 + s


def instant(text):
    return datetime.strptime(text, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)


# ---------- checks ----------

def declared_absence(env, field_path):
    for a in env.get("field_absences") or []:
        if a.get("field_path") == field_path:
            return a.get("absence_reason_code")
    return None


def basis_of(env, field_path, tr):
    parent, leaf = field_path.rsplit("/", 1)
    value = pointer_get(env, tr.pointer(field_path))
    if isinstance(value, dict) and "basis_status" in value:
        return value["basis_status"]
    sibling = pointer_get(env, tr.pointer(parent + "/" + leaf + "_basis_status"))
    return None if sibling is MISSING else sibling


def check_field(req, env, tr):
    """One envelope; returns a result or None when the requirement does not apply."""
    ref, path = req["requirement_id"], req["field_path"]
    eid = env.get("envelope_id", "?")
    value = pointer_get(env, tr.pointer(path))
    ob = req["obligation_type"]
    if value is MISSING:
        if ob == "prohibited" or ob == "optional":
            return result(ref, "verified", note="absent", refs=[eid])
        declared = declared_absence(env, path)
        if declared == "not_applicable":
            return result(ref, "contradicted", "divergence", "field_declared_not_applicable", "artifact",
                          "declared not_applicable but required", [eid])
        if declared == "not_captured":
            return result(ref, "indeterminate", "absence", "field_absent_declared", "operator", "declared not_captured", [eid])
        if declared == "withheld":
            return result(ref, "not_evaluated", None, "field_withheld", "operator", "withheld by the producer", [eid])
        if declared == "redacted":
            return result(ref, "not_evaluated", None, "field_redacted", "access", "redacted for this reader", [eid])
        return result(ref, "indeterminate", "absence", "field_absent_undeclared", "artifact", "%s absent" % path, [eid])
    if ob == "prohibited":
        return result(ref, "contradicted", "divergence", "prohibited_field_present", "artifact", "%s present" % path, [eid])
    if "accepted_values" in req and value not in req["accepted_values"]:
        return result(ref, "contradicted", "divergence", "value_not_accepted", "artifact",
                      "%s = %s" % (path, value), [eid])
    if "minimum_value" in req:
        ladder = LADDERS.get(req.get("value_ladder_ref"))
        if ladder is None:
            return result(ref, "not_evaluated", "instrument_failure", "value_ladder_unsupported", "verifier",
                          str(req.get("value_ladder_ref")), [eid])
        if value in NEVER_SATISFIES:
            return result(ref, "indeterminate", "divergence", "conflicting_evidence", "artifact", "%s = %s" % (path, value), [eid])
        if value not in ladder or ladder.index(value) < ladder.index(req["minimum_value"]):
            return result(ref, "indeterminate", "absence", "value_below_minimum", "artifact",
                          "%s = %s, minimum %s" % (path, value, req["minimum_value"]), [eid])
    if "required_basis_status" in req:
        basis = basis_of(env, path, tr)
        if basis != req["required_basis_status"]:
            return result(ref, "indeterminate", "absence", "basis_not_demonstrated", "operator",
                          "%s basis_status %s" % (path, basis or "absent"), [eid])
    return result(ref, "verified", note="present", refs=[eid])


def check_anchoring(req, env, release):
    ref = req["requirement_id"]
    eid = env.get("envelope_id", "?")
    if "anchoring" not in env:
        declared = declared_absence(env, "/anchoring")
        if declared:
            return result(ref, "indeterminate", "absence", "field_absent_declared", "operator", declared, [eid])
        return result(ref, "indeterminate", "absence", "anchor_insufficient", "artifact", "no anchoring block", [eid])
    rs = anchoring_guard.evaluate(env, release or "gt-v2.1")
    block = env["anchoring"]
    if "anchors" not in block:
        g = anchoring_guard.decisive(rs)
        return result(ref, "indeterminate", "absence", "anchor_insufficient", "artifact",
                      "legacy block: %s" % g["verification_condition_code"], [eid])
    a_req = req.get("anchoring") or {}
    methods = set(a_req.get("accepted_anchoring_methods") or [])
    need = a_req.get("minimum_independent_anchor_count", 1)
    max_lag = a_req.get("maximum_anchoring_lag")
    good, lag_exceeded = 0, False
    for a in block["anchors"]:
        if methods and a.get("anchoring_method") not in methods:
            continue
        if a.get("basis_status") != req.get("required_basis_status", "demonstrated"):
            continue
        if any(r["anchor_id"] == a.get("anchor_id") and r["verification_state"] == "contradicted" for r in rs):
            continue
        if max_lag and a.get("anchored_at") and a.get("anchor_requested_at"):
            lag = (instant(a["anchored_at"]) - instant(a["anchor_requested_at"])).total_seconds()
            if lag > duration_seconds(max_lag):
                lag_exceeded = True
                continue
        good += 1
    if any(r["verification_state"] == "contradicted" for r in rs):
        c = anchoring_guard.decisive(rs)
        return result(ref, "contradicted", "divergence", c["verification_condition_code"], "artifact", "anchor contradicted", [eid])
    if good >= need:
        return result(ref, "verified", note="%d qualifying anchors" % good, refs=[eid])
    if lag_exceeded:
        return result(ref, "indeterminate", "absence", "anchor_lag_exceeded", "artifact", "lag above %s" % max_lag, [eid])
    return result(ref, "indeterminate", "absence", "anchor_insufficient", "artifact",
                  "%d qualifying anchors, %d required" % (good, need), [eid])


def check_settlement(req, env, tr):
    """Decode-and-compare (x402#3220 section 13 rule a): committed versus settled."""
    ref = req["requirement_id"]
    eid = env.get("envelope_id", "?")
    block = pointer_get(env, tr.pointer(req["field_path"]))
    if block is MISSING or not isinstance(block, dict):
        return result(ref, "indeterminate", "absence", "settlement_not_observed", "artifact", "no settlement block", [eid])
    settled = block.get("settled_artifact")
    committed = block.get("committed_terms")
    if not settled:
        return result(ref, "indeterminate", "absence", "settlement_not_observed", "artifact", "no decoded settled artifact", [eid])
    if not committed:
        return result(ref, "indeterminate", "absence", "field_absent_undeclared", "artifact", "no committed terms", [eid])
    for key in ("asset_id", "total_amount", "payment_legs"):
        if settled.get(key) != committed.get(key):
            return result(ref, "contradicted", "divergence", "settlement_commitment_mismatch", "artifact",
                          "%s differs between committed terms and the settled artifact" % key, [eid])
    return result(ref, "verified", note="committed terms equal the decoded settled artifact", refs=[eid])


def check_chain(req, envs):
    ref = req["requirement_id"]
    prev = "0" * 64
    for env in envs:
        integ = env.get("integrity") or {}
        if integ.get("previous_envelope_hash") != prev:
            return result(ref, "contradicted", "divergence", "chain_break", "artifact",
                          "link broken at sequence %s" % env.get("sequence_number"), [env.get("envelope_id", "?")])
        if integ.get("envelope_hash") != envelope_digest(env):
            return result(ref, "contradicted", "divergence", "envelope_hash_mismatch", "artifact",
                          "hash differs at sequence %s" % env.get("sequence_number"), [env.get("envelope_id", "?")])
        prev = integ["envelope_hash"]
    return result(ref, "verified", note="%d envelopes linked" % len(envs))


def check_sequence(req, envs):
    ref = req["requirement_id"]
    seqs = [e.get("sequence_number") for e in envs]
    if not seqs or seqs != list(range(seqs[0], seqs[0] + len(seqs))):
        return result(ref, "indeterminate", "absence", "sequence_gap", "artifact", "sequence not contiguous")
    return result(ref, "verified", note="sequence %d..%d contiguous" % (seqs[0], seqs[-1]))


def evaluate_requirement(req, envs, tr, release):
    ct = req["check_type"]
    if ct == "chain_integrity":
        return check_chain(req, envs)
    if ct == "sequence_continuity":
        return check_sequence(req, envs)
    tree = None
    if req["obligation_type"] == "conditional":
        try:
            tree = parse_expression(req["condition_expression"])
        except PredicateError as exc:
            return result(req["requirement_id"], "not_evaluated", "instrument_failure", "predicate_unparseable",
                          "verifier", str(exc))
    per = []
    for env in envs:
        if tree is not None and not holds(tree, env, tr):
            continue
        if ct == "field_presence":
            per.append(check_field(req, env, tr))
        elif ct == "anchoring":
            per.append(check_anchoring(req, env, release))
        elif ct == "settlement_commitment":
            per.append(check_settlement(req, env, tr))
        else:
            return result(req["requirement_id"], "not_evaluated", "instrument_failure", "check_type_unsupported", "verifier", ct)
    if not per:
        if req["obligation_type"] == "conditional":
            return result(req["requirement_id"], "verified", note="condition false for every envelope in scope")
        return result(req["requirement_id"], "indeterminate", "absence", "field_absent_undeclared", "artifact", "no envelope in scope")
    w = dict(worst(per))
    bad = [r for r in per if r["verification_state"] == w["verification_state"] and r.get("verification_condition_code") == w.get("verification_condition_code")]
    w["evidence_refs"] = sorted({x for r in bad for x in r["evidence_refs"]})[:5]
    w["observed_note"] = "%d of %d envelopes in scope: %s" % (len(bad), len(per), w["observed_note"])
    return w


# ---------- mapping from existing AXES vocabularies (WO19 section 4.5) ----------

EXISTING_VALUE_MAP = {
    ("derivation_outcome", "underivable_missing_input"): ("indeterminate", "absence", "field_absent_undeclared", "artifact"),
    ("derivation_outcome", "undisclosed"): ("not_evaluated", None, "access_restricted", "access"),
    ("derivation_outcome", "underivable_conflicting_inputs"): ("indeterminate", "divergence", "conflicting_evidence", "artifact"),
    ("derivation_outcome", "underivable_unverified_identifier"): ("indeterminate", "absence", "identifier_unverified", "artifact"),
    ("derivation_outcome", "outside_capture_boundary"): ("admissibility_excluded", None, None, None),
    ("verification_status", "verification_unavailable"): ("not_evaluated", None, "verification_unavailable", "network"),
    ("anchoring_guard", "anchor_simulated_claims_external"): ("contradicted", "divergence", "anchor_simulated_claims_external", "artifact"),
    ("anchoring_guard", "anchor_independence_unproven"): ("indeterminate", "absence", "anchor_independence_unproven", "artifact"),
    ("anchoring_guard", "anchor_method_unverifiable"): ("not_evaluated", "instrument_failure", "anchor_method_unverifiable", "verifier"),
}


def map_existing_value(vocabulary, value):
    """Return (state, reason, condition, subject); admissibility exclusions are not one of the four states."""
    return EXISTING_VALUE_MAP.get((vocabulary, value))


# ---------- profiles ----------

def load_profiles(directory):
    out = {}
    for name in sorted(os.listdir(directory)):
        if name.endswith(".json"):
            raw = open(os.path.join(directory, name), encoding="utf-8").read()
            p = json.loads(raw)
            out["%s@%s" % (p["requirement_profile_id"].split("@")[0], p["requirement_profile_version"])] = p
            out[p["requirement_profile_id"]] = p
    return out


def resolve(profile_ref, profiles, seen=()):
    """Returns (requirements in order, list of conflicts) after strictest-wins composition (D10)."""
    p = profiles.get(profile_ref)
    if p is None:
        return None, []
    merged, conflicts = {}, []
    for parent in p.get("extended_profile_refs") or []:
        if parent in seen:
            conflicts.append(("cycle", parent))
            continue
        reqs, c = resolve(parent, profiles, seen + (profile_ref,))
        conflicts += c
        for r in reqs or []:
            merged[r["requirement_id"]] = r
    for r in p["requirements"]:
        old = merged.get(r["requirement_id"])
        if old is None:
            merged[r["requirement_id"]] = r
            continue
        if OBLIGATION_ORDER[r["obligation_type"]] >= OBLIGATION_ORDER[old["obligation_type"]]:
            merged[r["requirement_id"]] = r
        elif old.get("floor_indicator"):
            conflicts.append((r["requirement_id"], "relaxes a floor"))
        if {old["obligation_type"], r["obligation_type"]} == {"required", "prohibited"}:
            conflicts.append((r["requirement_id"], "required versus prohibited"))
    return list(merged.values()), conflicts


# ---------- evaluation ----------

def read_subject(path):
    if path.endswith(".jsonl"):
        return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]
    obj = json.load(open(path, encoding="utf-8"))
    return obj if isinstance(obj, list) else [obj]


def evaluate(profile_ref, subject_path, profiles_dir, aliases_path, release=None, sequence_range=None,
             evaluated_at="1970-01-01T00:00:00.000Z", subject_type=None):
    profiles = load_profiles(profiles_dir)
    profile = profiles.get(profile_ref)
    envs = read_subject(subject_path)
    if sequence_range:
        lo, hi = sequence_range
        envs = [e for e in envs if lo <= e.get("sequence_number", -1) <= hi]
    tr = Translator(aliases_path, release)
    subject_hashes = [sha256_hex(open(subject_path, "rb").read())]
    if profile is None:
        results = [result("profile", "not_evaluated", "instrument_failure", "profile_unsupported", "verifier", profile_ref)]
        profile_hash, version = "0" * 64, "unknown"
    else:
        profile_hash = sha256_hex(canonical_bytes(profile))
        version = profile["requirement_profile_version"]
        reqs, conflicts = resolve(profile_ref, profiles)
        conflicted = {c[0] for c in conflicts}
        results = []
        for req in reqs:
            if req["requirement_id"] in conflicted:
                results.append(result(req["requirement_id"], "indeterminate", "divergence", "profile_conflict", "verifier",
                                      "; ".join(c[1] for c in conflicts if c[0] == req["requirement_id"])))
                continue
            try:
                results.append(evaluate_requirement(req, envs, tr, release))
            except Exception as exc:  # an evaluator fault is never a finding about the subject
                results.append(result(req["requirement_id"], "not_evaluated", "instrument_failure",
                                      "evaluator_fault", "verifier", type(exc).__name__))
    required = [r for r in results]
    states = {r["verification_state"] for r in required}
    overall = "contradicted" if "contradicted" in states else (
        "indeterminate" if states & {"indeterminate", "not_evaluated"} else "verified")
    conditional_refs = sorted(r["requirement_ref"] for r in results
                              if r["verification_state"] != "verified" or r.get("verification_condition_code"))
    record = {
        "evaluation_id": "eval:%s:%s" % (profile_ref, subject_hashes[0][:16]),
        "requirement_profile_ref": profile_ref,
        "requirement_profile_version": version,
        "requirement_profile_hash": profile_hash,
        "hash_algorithm": "SHA-256",
        "subject_type": subject_type or (profile["subject_types"][0] if profile else "bundle"),
        "subject_hashes": subject_hashes,
        "evaluator_id": EVALUATOR_ID,
        "evaluator_version": EVALUATOR_VERSION,
        "evaluated_at": evaluated_at,
        "pinned_evidence_items": [],
        "results": results,
        "overall_verification_state": overall,
        "guarantee_type": "conditional" if conditional_refs else "unconditional",
        "conditional_requirement_refs": conditional_refs,
    }
    if release:
        record["subject_release_ref"] = release
        record["key_translation_ref"] = "schema/key-aliases.json (%d paths translated)" % len(set(tr.used))
    core = {k: v for k, v in record.items() if k not in ("evaluation_id", "evaluator_id", "evaluator_version", "evaluated_at")}
    record["result_core_hash"] = sha256_hex(canonical_bytes(core))
    return record


def main(argv=None):
    ap = argparse.ArgumentParser(description="AXES evaluator (WO19)")
    ap.add_argument("--profile", required=True)
    ap.add_argument("--subject", required=True)
    ap.add_argument("--subject-release")
    ap.add_argument("--subject-type")
    ap.add_argument("--profiles-dir", default=os.path.join(VENDOR, "profiles"))
    ap.add_argument("--aliases", default=os.path.join(VENDOR, "key-aliases.json"))
    ap.add_argument("--sequence-range")
    ap.add_argument("--evaluated-at", default="1970-01-01T00:00:00.000Z")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    rng = tuple(int(x) for x in a.sequence_range.split(":")) if a.sequence_range else None
    rec = evaluate(a.profile, a.subject, a.profiles_dir, a.aliases, a.subject_release, rng, a.evaluated_at, a.subject_type)
    text = json.dumps(rec, indent=2, ensure_ascii=False) + "\n"
    if a.out:
        open(a.out, "w", encoding="utf-8", newline="\n").write(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Checks the -00 appendices against the repository. Run from the repository root.

A (worked example): the canonical bytes in ietf/appendix/envelope-0009.jcs.txt, joined, equal the
RFC 8785 bytes of envelope 9 of the gt-v2.1 financial trace with the two self-referential members
removed; their SHA-256 equals the stored envelope hash, the stored previous hash and the next
envelope's previous hash.

B (CDDL): ietf/appendix/axes.cddl accepts every integrity block in both gt-v2.1 bundles, every
anchoring block (in-trace and release), the anchor verifier's results on the release anchors and
every evaluation record. Each rule also rejects a copy with one value broken. Needs the Ruby
`cddl` gem on PATH.

C (vocabularies): every condition code the reference tools emit or the vectors expect is listed in
the draft's condition-code table.

--write regenerates the appendix A files from the corpus. Exit 0 when every check passes.
"""
import copy
import glob
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.getcwd()
APPX = os.path.join(ROOT, "ietf", "appendix")
DRAFT = os.path.join(ROOT, "ietf", "draft-sansone-axes-evidence-envelope.md")
BUNDLES = ["examples/golden-trace/out/envelopes.jsonl", "examples/golden-trace-ind/out/envelopes.jsonl"]
WIDTH = 64
FAILS = []


def check(ok, label):
    print("%s %s" % ("ok  " if ok else "FAIL", label))
    if not ok:
        FAILS.append(label)


def jcs(obj):
    # Sufficient for these inputs: integers, strings, booleans and null only (checked below).
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def envelopes(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def presentation(env, limit=69):
    """Pretty JSON for the draft; string values too long for one line are broken inside the string."""
    out = []
    for line in json.dumps(env, indent=2, ensure_ascii=True).splitlines():
        m = re.match(r'^(\s*"[^"]+": ")([^"]*)(",?)$', line)
        if len(line) <= limit or not m:
            out.append(line)
            continue
        head, value, tail = m.groups()
        if len(head) > 40:  # key on its own line, value below it
            out.append(head[:-1].rstrip())
            head = " " * (len(head) - len(head.lstrip()) + 2) + '"'
        pad = " " * len(head)

        def cut(text, room):
            # Digests split in half; other values after a separator where possible.
            if re.fullmatch(r"[0-9a-f]{64}", value) and room >= 32:
                return 32
            stops = [i + 1 for i, ch in enumerate(text[:room]) if ch in "/:-"]
            return stops[-1] if stops else room

        n = cut(value, limit - len(head))
        out.append(head + value[:n])
        rest = value[n:]
        while rest:
            if len(pad) + len(rest) + len(tail) <= limit:
                out.append(pad + rest + tail)
                rest = ""
            else:
                n = cut(rest, limit - len(pad))
                out.append(pad + rest[:n])
                rest = rest[n:]
    return "\n".join(out)


def worked_example(write):
    rows = envelopes(BUNDLES[0])
    prev, env, nxt = rows[7], rows[8], rows[9]
    scoped = copy.deepcopy(env)
    del scoped["integrity"]["envelope_hash"], scoped["integrity"]["envelope_signature"]
    raw = jcs(scoped)
    digest = hashlib.sha256(raw).hexdigest()
    path = os.path.join(APPX, "envelope-0009.jcs.txt")
    shown_path = os.path.join(APPX, "envelope-0009.json")
    if write:
        with open(path, "w", encoding="ascii", newline="\n") as f:
            f.write("\n".join(raw[i:i + WIDTH].decode("ascii") for i in range(0, len(raw), WIDTH)) + "\n")
        with open(shown_path, "w", encoding="ascii", newline="\n") as f:
            f.write(presentation(env) + "\n")
    with open(shown_path, encoding="ascii") as f:
        figure = f.read()
    check(max(len(line) for line in figure.splitlines()) <= 69 and
          re.sub(r"\s", "", figure) == re.sub(r"\s", "", json.dumps(env, separators=(",", ":"))),
          "A: the presented envelope is envelope 9, line breaks aside, within 69 columns")
    with open(path, encoding="ascii") as f:
        shown = "".join(line.rstrip("\n") for line in f).encode("ascii")
    check(all(b < 128 for b in raw) and b" " not in raw, "A: canonical bytes are ASCII with no spaces, so wrapping is unambiguous")
    check(shown == raw, "A: appendix bytes equal the canonical bytes of envelope 9 (%d bytes)" % len(raw))
    check(hashlib.sha256(shown).hexdigest() == env["integrity"]["envelope_hash"] == digest,
          "A: SHA-256 of the appendix bytes is the stored envelope hash " + digest)
    check(env["integrity"]["previous_envelope_hash"] == prev["integrity"]["envelope_hash"],
          "A: previous_envelope_hash is envelope 8's hash")
    check(nxt["integrity"]["previous_envelope_hash"] == digest, "A: envelope 10 links to envelope 9")
    with open(DRAFT, encoding="utf-8") as f:
        text = f.read()
    for value in (digest, prev["integrity"]["envelope_hash"], str(len(raw))):
        check(value in text.replace("\n", "").replace(" ", ""), "A: draft states " + value[:16])


def cddl_validate(rule, instances, label):
    tmp = tempfile.mkdtemp()
    try:
        spec = os.path.join(tmp, "s.cddl")
        with open(os.path.join(APPX, "axes.cddl"), encoding="utf-8") as f:
            body = f.read()
        with open(spec, "w", encoding="utf-8") as f:
            f.write("root = [* %s]\n\n%s" % (rule, body))
        inst = os.path.join(tmp, "i.json")
        with open(inst, "w", encoding="utf-8") as f:
            json.dump(instances, f)
        cmd = shutil.which("cddl")
        if cmd is None:
            check(False, "B: cddl gem not on PATH")
            return False
        r = subprocess.run([cmd, spec, "validate", inst], capture_output=True, text=True)
        return r.returncode == 0 and "CDDL validation failure" not in (r.stdout + r.stderr)
    finally:
        shutil.rmtree(tmp)


def cddl_two_sided(rule, instances, breaker, label):
    check(cddl_validate(rule, instances, label), "B: %s accepts %d %s" % (rule, len(instances), label))
    bad = copy.deepcopy(instances[0])
    breaker(bad)
    check(not cddl_validate(rule, [bad], label), "B: %s rejects a broken copy" % rule)


def cddl_checks():
    integ, blocks = [], []
    for b in BUNDLES:
        for e in envelopes(b):
            integ.append(e["integrity"])
            if "anchoring" in e:
                blocks.append(e["anchoring"])
    for f in sorted(glob.glob("anchors/*/anchoring.json")):
        with open(f, encoding="utf-8") as fh:
            blocks.append(json.load(fh))
    sys.path.insert(0, os.path.join(ROOT, "tools", "anchoring"))
    import verify_anchor as va  # noqa: E402
    results = []
    for d in sorted(glob.glob("anchors/*/")):
        results += va.verify_block(d)
    evals = []
    for f in sorted(glob.glob("evaluations/*/*.json")):
        with open(f, encoding="utf-8") as fh:
            evals.append(json.load(fh))
    cddl_two_sided("integrity", integ, lambda i: i.update(previous_envelope_hash="ABC"), "integrity blocks")
    cddl_two_sided("anchoring-block", blocks, lambda b: b.update(anchored_subject_type="log_entry"),
                   "anchoring blocks")
    cddl_two_sided("anchor-result", results, lambda r: r.update(verification_state="passed"),
                   "anchor verifier results")
    cddl_two_sided("evaluation-record", evals, lambda e: e.update(guarantee_type="guaranteed"),
                   "evaluation records")
    return results, evals


def vocab_checks(results, evals):
    with open(DRAFT, encoding="utf-8") as f:
        text = f.read()
    m = re.search(r"\{#vocab-conditions\}(.*?)\n# ", text, re.S)
    listed = set(re.findall(r"^\| `([a-z_]+)`", m.group(1), re.M)) if m else set()
    check(len(listed) > 30, "C: condition-code table found in the draft (%d codes)" % len(listed))
    used = set()
    for r in results:
        used.add(r.get("verification_condition_code"))
    for e in evals:
        for r in e["results"]:
            used.add(r.get("verification_condition_code"))
    pat = re.compile(r'"verification_condition_code":\s*"([a-z_]+)"')
    for f in glob.glob("vectors/**/expected.json", recursive=True) + glob.glob("vectors/**/predicates.json", recursive=True):
        with open(f, encoding="utf-8") as fh:
            used.update(pat.findall(fh.read()))
    src = ""
    for f in ["tools/anchoring/verify_anchor.py", "tools/axes_evaluate.py", "tools/axes_verify.py",
              "tools/axes_anchoring_guard.py"]:
        with open(f, encoding="utf-8") as fh:
            src += fh.read()
    emitted = set(re.findall(r'"((?:anchor|field|value|chain|sequence|profile|basis|correlation|settlement|nonce|'
                             r'binding|identifier|external|access|prohibited|cap|conflicting|envelope|predicate|'
                             r'check|evaluator|requirement|legacy)_[a-z_]+)"', src))
    emitted &= {c for c in emitted if re.search(r'(result|_r)\([^)]*"%s"' % c, src) or c in used}
    # Field names passed alongside a code are not codes.
    for pair in re.findall(r'"([a-z_]+)"\s*[:\]]|get\("([a-z_]+)"', src):
        emitted -= set(pair)
    used |= emitted
    used.discard(None)
    missing = sorted(used - listed)
    check(not missing, "C: every condition code in tools and vectors is in the table" +
          (": missing " + ", ".join(missing) if missing else " (%d used)" % len(used)))


def main():
    write = "--write" in sys.argv
    worked_example(write)
    results, evals = cddl_checks()
    vocab_checks(results, evals)
    print("FAILED: %d" % len(FAILS) if FAILS else "OK appendices A, B and C")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())

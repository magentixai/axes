#!/usr/bin/env python3
"""Cross-platform byte check for a Golden Trace corpus tree.

Standard library only. Runs identically on Linux, macOS and Windows.

Checks, for each corpus named in the expectations file:
  1. every pinned file under <corpus>/out/ (and vectors/, if present) is
     valid UTF-8 and contains no CR byte (catches platform text mode,
     CP1252 writes and git line-ending conversion on checkout);
  2. manifest.json keys use forward slashes and are sorted;
  3. every file's on-disk SHA-256 equals its manifest entry (no regeneration
     needed, so this checks the bytes exactly as git put them on disk);
  4. chain_head and bundle_manifest_hash equal the published release values.

Usage:
  python tools/check_corpus_bytes.py [--root DIR] [--expect FILE]

Exit codes: 0 all checks pass; 1 a check failed; 2 the checker could not run.
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def sha256_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def byte_problems(path):
    with open(path, "rb") as f:
        data = f.read()
    problems = []
    if b"\r" in data:
        problems.append("contains CR (line endings converted on checkout or written in text mode)")
    try:
        data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        problems.append("not valid UTF-8 at byte %d (platform-default encoding write?)" % exc.start)
    return problems


def pinned_files(root, rel_dirs):
    for rel_dir in rel_dirs:
        base = os.path.join(root, *rel_dir.split("/"))
        if not os.path.isdir(base):
            continue
        for dirpath, _, fnames in os.walk(base):
            for fn in sorted(fnames):
                full = os.path.join(dirpath, fn)
                yield os.path.relpath(full, root).replace("\\", "/"), full


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=os.path.dirname(HERE), help="repository tree to check (default: this repo)")
    ap.add_argument("--expect", default=os.path.join(HERE, "corpus_of_record.json"),
                    help="JSON file of expected release digests")
    args = ap.parse_args()

    try:
        with open(args.expect, encoding="utf-8") as f:
            expect = json.load(f)
    except (OSError, ValueError) as exc:
        print("ERROR cannot read expectations %s: %s" % (args.expect, exc))
        return 2

    root = os.path.abspath(args.root)
    failures = 0

    def fail(msg):
        nonlocal failures
        failures += 1
        print("FAIL " + msg)

    rel_dirs = ["vectors"] + ["examples/%s/out" % c for c in expect["corpora"]]
    n_files = 0
    for rel, full in pinned_files(root, rel_dirs):
        n_files += 1
        for p in byte_problems(full):
            fail("%s: %s" % (rel, p))

    for corpus, want in sorted(expect["corpora"].items()):
        out = os.path.join(root, "examples", corpus, "out")
        mpath = os.path.join(out, "manifest.json")
        try:
            with open(mpath, encoding="utf-8") as f:
                manifest = json.load(f)
        except (OSError, ValueError) as exc:
            fail("%s: cannot read manifest.json: %s" % (corpus, exc))
            continue
        keys = list(manifest.get("files", {}).keys())
        if any("\\" in k for k in keys):
            fail("%s: manifest keys contain backslashes (generated with OS path separators)" % corpus)
        if keys != sorted(keys):
            fail("%s: manifest keys not sorted" % corpus)
        mismatched = 0
        for rel, digest in manifest.get("files", {}).items():
            path = os.path.join(out, *rel.replace("\\", "/").split("/"))
            if not os.path.isfile(path):
                fail("%s: manifest lists missing file %s" % (corpus, rel))
            elif sha256_file(path) != digest:
                mismatched += 1
                fail("%s: on-disk bytes differ from manifest for %s" % (corpus, rel))
        for field in ("chain_head", "bundle_manifest_hash"):
            if manifest.get(field) != want[field]:
                fail("%s: %s is %s, published %s is %s"
                     % (corpus, field, manifest.get(field), expect["release"], want[field]))
        if not mismatched:
            print("ok   %s: %d manifest entries match on-disk bytes; chain %s... bundle %s..."
                  % (corpus, len(keys), want["chain_head"][:12], want["bundle_manifest_hash"][:12]))

    print("%d pinned files scanned for CR / invalid UTF-8" % n_files)
    print("%s %s byte check (%s, Python %s)"
          % ("OK" if not failures else "FAILED", expect["release"], sys.platform, sys.version.split()[0]))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())

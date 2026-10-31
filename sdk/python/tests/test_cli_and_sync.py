import copy
import json
import subprocess
import sys

import pytest

from axes_sdk import load_subject
from axes_sdk.cli import main

from conftest import needs_repo, repo

pytestmark = needs_repo


def test_verify_stream_exit_codes(fin_path, tmp_path, capsys):
    assert main(["verify-stream", fin_path]) == 0
    envs = [copy.deepcopy(e) for e in load_subject(fin_path).envelopes]
    envs[3]["event_kind"] = "changed"
    bad = tmp_path / "bad.jsonl"
    bad.write_text("\n".join(json.dumps(e) for e in envs) + "\n", encoding="utf-8")
    assert main(["verify-stream", str(bad), "--json"]) == 1
    out = capsys.readouterr().out
    assert json.loads(out[out.index("{"):])["overall_state"] == "contradicted"
    (tmp_path / "dup.jsonl").write_text('{"a":1,"a":2}\n', encoding="utf-8")
    assert main(["verify-stream", str(tmp_path / "dup.jsonl")]) == 3
    assert main(["verify-stream", str(tmp_path / "missing.jsonl")]) == 3
    assert main(["no-such-command"]) == 3


def test_verify_bundle_and_evaluate(fin_path, tmp_path):
    assert main(["verify-bundle", repo("examples", "golden-trace", "out")]) == 0
    assert main(["evaluate", fin_path, "--profile", "axes:gt_fin_internal_audit@1"]) == 0
    out = tmp_path / "rec.json"
    assert main(["evaluate", fin_path, "--profile", "axes:gt_fin_regulator@1", "--out", str(out)]) == 2
    assert json.loads(out.read_text(encoding="utf-8"))["overall_verification_state"] == "indeterminate"


def test_hash(tmp_path, fin_path, capsys):
    env = load_subject(fin_path).envelopes[8]
    p = tmp_path / "e.json"
    p.write_text(json.dumps(env), encoding="utf-8")
    assert main(["hash", str(p)]) == 0
    assert capsys.readouterr().out.strip() == env["integrity"]["envelope_hash"]


def test_sdk_copies_match_the_reference():
    r = subprocess.run([sys.executable, repo("sdk", "python", "sync_reference.py"), "--check"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr

import json
import os

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.environ.get("AXES_REPO") or os.path.abspath(os.path.join(HERE, "..", "..", ".."))
HAVE_REPO = os.path.isfile(os.path.join(REPO, "tools", "releases", "gt-v2.1.json"))

needs_repo = pytest.mark.skipif(not HAVE_REPO, reason="AXES repository not found; set AXES_REPO")


def repo(*parts):
    return os.path.join(REPO, *parts)


@pytest.fixture(scope="session")
def release():
    with open(repo("tools", "releases", "gt-v2.1.json"), encoding="utf-8") as f:
        return json.load(f)["corpora"]


@pytest.fixture(scope="session")
def fin_path():
    return repo("examples", "golden-trace", "out", "envelopes.jsonl")


@pytest.fixture(scope="session")
def ind_path():
    return repo("examples", "golden-trace-ind", "out", "envelopes.jsonl")

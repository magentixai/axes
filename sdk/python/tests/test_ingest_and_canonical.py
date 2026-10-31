import copy

import pytest

from axes_sdk import (DomainError, DuplicateKeyError, HashPolicy, Limits, ParseError, ResourceLimitError,
                      UnsupportedCapabilityError, canonicalize, envelope_preimage, genesis_value, hash_envelope,
                      load_subject, parse_json)

from conftest import needs_repo


@pytest.mark.parametrize("text", [
    b'{"kind":"good","kind":"bad"}',
    b'{"a":{"b":1,"b":2}}',
    b'[{"x":1},{"y":1,"y":1}]',
])
def test_duplicate_members_refused_at_any_depth(text):
    with pytest.raises(DuplicateKeyError):
        parse_json(text)


@pytest.mark.parametrize("text", [b'{"n":NaN}', b'{"n":Infinity}', b'{"n":-Infinity}', b'\xff{}',
                                  b'{"s":"\\ud800"}', b'\xef\xbb\xbf{}', b'{"a":'])
def test_non_strict_json_refused(text):
    with pytest.raises(ParseError):
        parse_json(text)


def test_limits():
    with pytest.raises(ResourceLimitError):
        parse_json(b"[" * 70 + b"]" * 70)
    with pytest.raises(ResourceLimitError):
        parse_json(b'"' + b"a" * 100 + b'"', Limits(max_bytes=50))


def test_jsonl_and_array_subjects():
    s = load_subject(b'{"a":1}\n\n{"a":2}\n')
    assert len(s) == 2 and len(s.sha256) == 64
    assert len(load_subject(b'[{"a":1},{"a":2}]')) == 2
    with pytest.raises(ParseError, match="line 2"):
        load_subject(b'{"a":1}\n{"a":1,"a":2}\n')


@pytest.mark.parametrize("value", [1.5, 2 ** 53, -(2 ** 53), float("inf"), {"x": [0.1]}])
def test_domain_refuses_numbers_rfc8785_would_round(value):
    with pytest.raises(DomainError):
        canonicalize(value)


def test_canonical_bytes_known_values():
    assert canonicalize({"b": 1, "a": [True, None, "x"]}) == b'{"a":[true,null,"x"],"b":1}'
    # UTF-16 code units: "z" 0x007A, then the euro sign 0x20AC, then the emoji's high surrogate 0xD83D.
    assert canonicalize({"€": 1, "\U0001F600": 2, "z": 3}) == '{"z":3,"€":1,"\U0001F600":2}'.encode()
    assert canonicalize(2 ** 53 - 1) == b"9007199254740991"


def test_preimage_does_not_modify_the_envelope():
    env = {"a": 1, "integrity": {"hash_algorithm": "SHA-256", "envelope_hash": "x", "envelope_signature": "y"}}
    before = copy.deepcopy(env)
    assert envelope_preimage(env) == b'{"a":1,"integrity":{"hash_algorithm":"SHA-256"}}'
    assert env == before


def test_release_scopes_differ():
    env = {"integrity": {"envelope_hash": "x", "signature": "s", "envelope_signature": "t"}}
    assert envelope_preimage(env, HashPolicy("gt-v2.1")) == b'{"integrity":{"signature":"s"}}'
    assert envelope_preimage(env, HashPolicy("gt-v2.0")) == b'{"integrity":{"envelope_signature":"t"}}'
    with pytest.raises(UnsupportedCapabilityError):
        HashPolicy("gt-v9")


def test_unsupported_algorithm_is_never_hashed_with_sha256():
    with pytest.raises(UnsupportedCapabilityError):
        hash_envelope({"integrity": {"hash_algorithm": "SHA3-256"}})
    with pytest.raises(UnsupportedCapabilityError):
        hash_envelope({"integrity": {"hash_algorithm": "SHA-256", "canonicalization_version": "not-jcs"}})
    assert genesis_value() == "0" * 64


@needs_repo
def test_digests_equal_the_stored_hashes_and_the_worked_example(fin_path, ind_path):
    from conftest import repo
    for path in (fin_path, ind_path):
        for env in load_subject(path).envelopes:
            assert hash_envelope(env) == env["integrity"]["envelope_hash"]
    with open(repo("ietf", "appendix", "envelope-0009.jcs.txt"), encoding="ascii") as f:
        shown = "".join(line.rstrip("\n") for line in f).encode("ascii")
    assert envelope_preimage(load_subject(fin_path).envelopes[8]) == shown

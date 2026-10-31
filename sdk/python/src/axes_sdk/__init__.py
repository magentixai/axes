"""AXES SDK: offline verification and deterministic evaluation of AXES evidence.

    from axes_sdk import load_subject, verify_stream, bundled_profiles, evaluate, EvaluationContext

    subject = load_subject("examples/golden-trace/out/envelopes.jsonl")
    report = verify_stream(subject)
    print(report.overall_state, report.chain_head)

    result = evaluate(subject, "axes:gt_fin_internal_audit@1", bundled_profiles())
    print(result.overall_verification_state, result.result_core_hash)

The SDK implements draft-sansone-axes-evidence-envelope-00 through the AXES reference modules, which it
packages unchanged apart from imports (axes_sdk._ref). It checks integrity, links, sequence, bundle files
and requirement profiles. It does not verify envelope signatures (not yet specified), external anchors,
or completeness of capture, and it never uses the network.
"""
from ._version import __version__
from .bundle import verify_bundle
from .canonical import (HashPolicy, canonicalize, check_domain, envelope_preimage, genesis_value,
                        hash_envelope)
from .errors import (AxesError, DomainError, DuplicateKeyError, ParseError, ProfileResolutionError,
                     ResourceLimitError, UnsafePathError, UnsupportedCapabilityError)
from .evaluation import EvaluationContext, evaluate
from .integrity import verify_stream
from .jsonio import Limits, Subject, load_subject, parse_json
from .profiles import ProfileSet, bundled_profiles, load_profile_set, profile_digest
from .results import EvaluationResult, Finding, State, VerificationReport

__all__ = [
    "__version__", "verify_bundle", "HashPolicy", "canonicalize", "check_domain", "envelope_preimage",
    "genesis_value", "hash_envelope", "AxesError", "DomainError", "DuplicateKeyError", "ParseError",
    "ProfileResolutionError", "ResourceLimitError", "UnsafePathError", "UnsupportedCapabilityError",
    "EvaluationContext", "evaluate", "verify_stream", "Limits", "Subject", "load_subject", "parse_json",
    "ProfileSet", "bundled_profiles", "load_profile_set", "profile_digest", "EvaluationResult", "Finding",
    "State", "VerificationReport",
]

"""Exceptions. Bad evidence becomes a finding; these are raised only for bad calls, unreadable input,
limits and missing capabilities. Messages never include the evidence content itself."""
from __future__ import annotations


class AxesError(Exception):
    """Base class for every SDK exception."""


class ParseError(AxesError, ValueError):
    """The input is not strict JSON (invalid UTF-8, duplicate member, NaN or Infinity, lone surrogate)."""


class DuplicateKeyError(ParseError):
    """An object has two members with the same name. I-JSON forbids it; the SDK never keeps the last one."""


class DomainError(AxesError, ValueError):
    """A value outside the AXES hash-scope domain: a fractional or non-finite number, or an integer
    outside +/-(2^53 - 1)."""


class ResourceLimitError(AxesError):
    """The input exceeds a configured limit (bytes, nesting depth, records, files)."""


class UnsafePathError(AxesError):
    """A path from the evidence would leave the directory the caller approved."""


class UnsupportedCapabilityError(AxesError):
    """A declared digest algorithm, canonicalisation identifier or bundle format the SDK does not implement."""


class ProfileResolutionError(AxesError):
    """A requirement profile set is inconsistent: the same id@version with different content, or a pin
    that does not match."""

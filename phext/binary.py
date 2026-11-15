"""Binary scrolls: the canonical way to store arbitrary bytes inside phext.

Ported 1:1 from libphext-rs 0.6.0 (src/binary.rs).

Phext scrolls are text (valid UTF-8). Arbitrary binary data rides as text
via base64. This module defines the one canonical binary scroll format, so
every phext implementation stores and recognises binary payloads
byte-for-byte identically:

    phext-binary:1:base64
    <base64 body>

Format specification (version 1):
* Line 1 is exactly ``phext-binary:1:base64``, followed by a single line
  break (0x0A).
* The body is RFC 4648 base64: standard alphabet, padding required, no
  line wrapping, no whitespace.
* An empty payload is the header line alone (header + line break + "").
* A scroll whose content begins with the header line is a binary scroll
  by definition. A prefix-matching scroll whose body is not strict
  base64 is a *malformed* binary scroll.

The ingestion rule (canonical behaviour, all ports):
> When non-UTF-8 data is observed in an incoming scroll update, we encode
> it with base64 verbatim.

Byte-oriented entry points (``insert_bytes``, ``replace_bytes``,
``ingest``) never reject and never raise on non-UTF-8 scroll data. Valid
UTF-8 is stored as ordinary text; anything else is stored as a binary
scroll holding the base64 of the exact observed bytes — verbatim, with
no normalisation — so the matching fetch returns the original bytes
exactly. Within a phext byte stream, the nine dimension-break bytes are
always structural; binary payloads that may contain them enter through
the update functions, armoured as base64.
"""

import base64
import binascii
import re

from phext.coordinate import Coordinate
from phext.phext import Phext

BINARY_SCROLL_HEADER = "phext-binary:1:base64"
BINARY_SCROLL_PREFIX = "phext-binary:1:base64\n"

# dimension-break bytes, for the byte-level walker
_SCROLL_BREAK_B = 0x17
_STRUCTURAL_BREAKS = frozenset(
    [0x01, 0x1F, 0x1E, 0x1D, 0x1C, 0x1A, 0x19, 0x18, 0x17]
)
# byte -> dimension index in the (library..scroll) walker, mirroring
# phext.phext._DIMENSION_BREAKS order
_BREAK_DIMENSION_B = {
    0x01: 0, 0x1F: 1, 0x1E: 2, 0x1D: 3, 0x1C: 4, 0x1A: 5, 0x19: 6, 0x18: 7, 0x17: 8,
}
_SCROLL_RUN_B = re.compile(rb"[^\x01\x17-\x1a\x1c-\x1f]+")


def is_binary_scroll(scroll: str) -> bool:
    """True when `scroll` carries the binary scroll header. Decoding
    success is a separate question — see `decode_scroll`."""
    return scroll.startswith(BINARY_SCROLL_PREFIX)


def encode_scroll(payload: bytes) -> str:
    """Encodes raw bytes as a binary scroll (header line + base64 body)."""
    return BINARY_SCROLL_PREFIX + base64.b64encode(payload).decode("ascii")


def decode_scroll(scroll: str):
    """Decodes a binary scroll back to its raw bytes. Returns None when
    the scroll is not a binary scroll, or when its body is not strict
    base64."""
    if not scroll.startswith(BINARY_SCROLL_PREFIX):
        return None
    body = scroll[len(BINARY_SCROLL_PREFIX):]
    try:
        return base64.b64decode(body, validate=True)
    except (binascii.Error, ValueError):
        return None


def insert_binary(buffer: str, location: Coordinate, payload: bytes) -> str:
    """Stores `payload` at `location` as a binary scroll, unconditionally:
    the caller has declared this scroll binary, even if the bytes happen
    to be valid UTF-8."""
    return Phext().insert(buffer, location, encode_scroll(payload))


def replace_binary(buffer: str, location: Coordinate, payload: bytes) -> str:
    """Replaces the scroll at `location` with `payload`, stored as a
    binary scroll (see `insert_binary`)."""
    return Phext().replace(buffer, location, encode_scroll(payload))


def fetch_binary(buffer: str, target: Coordinate) -> bytes:
    """Retrieves the bytes held at `target`. A well-formed binary scroll
    decodes to its payload. Any other scroll — plain text, a malformed
    binary scroll, or no scroll at all — yields the scroll's own UTF-8
    bytes (empty when the coordinate is unoccupied). Total: never raises
    and never loses scroll content."""
    scroll = Phext().fetch(buffer, target)
    decoded = decode_scroll(scroll)
    if decoded is not None:
        return decoded
    return scroll.encode("utf-8")


def _stored_form(payload: bytes) -> str:
    # The stored form of an incoming scroll update, per the ingestion
    # rule: valid UTF-8 stays text; anything else becomes a binary
    # scroll holding the base64 of the exact observed bytes, verbatim.
    try:
        return payload.decode("utf-8")
    except UnicodeDecodeError:
        return encode_scroll(payload)


def insert_bytes(buffer: str, location: Coordinate, payload: bytes) -> str:
    """Byte-oriented insert: stores `payload` at `location` under the
    ingestion rule (UTF-8 as text, non-UTF-8 as a base64-verbatim binary
    scroll)."""
    return Phext().insert(buffer, location, _stored_form(payload))


def replace_bytes(buffer: str, location: Coordinate, payload: bytes) -> str:
    """Byte-oriented replace: stores `payload` at `location` under the
    ingestion rule (UTF-8 as text, non-UTF-8 as a base64-verbatim binary
    scroll)."""
    return Phext().replace(buffer, location, _stored_form(payload))


def _apply_break_b(walker: list, byte: int):
    dimension = _BREAK_DIMENSION_B[byte]
    walker[dimension] += 1
    for lower in range(dimension + 1, 9):
        walker[lower] = 1


def phokenize_bytes(data: bytes):
    """The byte-level twin of the reference `phokenize`: walks a raw byte
    stream and returns each scroll's coordinate and raw bytes, with
    identical segmentation to libphext-rs `binary::phokenize_bytes`.
    Dimension-break bytes are ASCII, so byte offsets are exact; scroll
    bodies are returned uninterpreted, valid UTF-8 or not.

    Segmentation (identical to the reference loop): one entry per maximal
    run of non-break bytes, at the coordinate reached after applying
    every break preceding the run; plus exactly one empty entry when the
    stream holds no run at all (at the default coordinate), or when two
    or more breaks trail the last run (at the coordinate reached after
    the first trailing break)."""
    walker = [1, 1, 1, 1, 1, 1, 1, 1, 1]
    result = []
    position = 0
    runs = list(_SCROLL_RUN_B.finditer(data))
    if not runs:
        return [(Coordinate(1, 1, 1, 1, 1, 1, 1, 1, 1), b"")]
    for run in runs:
        for index in range(position, run.start()):
            _apply_break_b(walker, data[index])
        result.append((Coordinate(*walker), run.group()))
        position = run.end()
    trailing = len(data) - position
    if trailing >= 2:
        _apply_break_b(walker, data[position])
        result.append((Coordinate(*walker), b""))
    return result


def ingest(data: bytes) -> str:
    """Ingests an externally supplied phext byte stream. Every scroll is
    observed as raw bytes: valid UTF-8 scrolls pass through verbatim, and
    any scroll whose bytes are not valid UTF-8 is stored as a binary
    scroll holding the base64 of the exact observed bytes (the ingestion
    rule), so `fetch_binary` at its coordinate returns the original bytes
    exactly. Never rejects, never raises. The result is the canonical
    serialization (the same normal form as implode of explode)."""
    parts = phokenize_bytes(data)
    scrolls = {}
    for coord, raw in parts:
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = encode_scroll(raw)
        scrolls[coord] = text
    ordered = {coord: scrolls[coord] for coord in sorted(scrolls)}
    return Phext().implode(ordered)

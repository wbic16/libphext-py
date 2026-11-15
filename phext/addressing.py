"""Line/column addressing: point, offset, and range addresses (libphext 0.6.1).

Ported 1:1 from libphext-rs 0.6.1 (src/phext.rs, line/column addressing
section; range syntax ratified by Will, 2026-11-15 —
RANGE-SYNTAX-PROPOSAL.md in the ports program workspace).

A point address is ``[$N:]<9D coordinate>@<line>,<column>``: the
multiverse prefix and the coordinate exactly as in
`phext.chain.parse_universe_address`, plus a within-scroll caret
position. Line and column are 1-based; a position names a caret boundary
(column 1 is the boundary before the line's first character; a line of n
characters has valid columns 1..n+1), and columns count Unicode scalar
values — Python `str` indexing already counts code points, so plain
string slicing is scalar-correct (astral characters are single elements;
nothing here encodes to UTF-8 for counting). A point may carry
``+<offsetChars>``: select forward that many characters (scalars) from
the point, counted within the scroll, terminating at the scroll
boundary.

A range address is two point addresses joined by one hyphen:
``<point>-<point>``. The endpoints may span scrolls and universes; an
endpoint without ``@`` names its whole scroll (as start: its first
boundary; as end: its last). Canonical form: endpoints in ascending
(universe, coordinate, line, column) order — direction is discarded —
``$1:`` never written, integers in minimal decimal form. Out-of-range
endpoints fail at resolution, never clamp.

Scroll presence is the phokenize sense used by the 0.6 fixtures: a
coordinate is present exactly when the member's phokenize enumeration
contains it. The enumeration here is `phext.binary.phokenize_bytes` —
the byte-level twin of the reference `phokenize`, whose segmentation
(including the empty-scroll entries) the text phokenize in
`phext.phext` does not surface.
"""

from dataclasses import dataclass
from typing import Optional

from phext.binary import phokenize_bytes
from phext.coordinate import Coordinate

# Rust `usize` on the reference platform is 64-bit; its address parser
# rejects integers that do not fit. Mirror that bound.
_USIZE_MAX = (1 << 64) - 1


@dataclass
class ScrollPosition:
    """A caret boundary inside one scroll: 1-based line and column."""

    line: int
    column: int


@dataclass
class PointAddress:
    """One parsed point address: universe (1-based; 1 when the ``$N:``
    prefix is absent), the 9D coordinate, an optional caret position,
    and an optional forward offset in characters."""

    universe: int
    coordinate: Coordinate
    position: Optional[ScrollPosition] = None
    offset: Optional[int] = None

    def __str__(self) -> str:
        result = ""
        if self.universe > 1:
            result += f"${self.universe}:"
        result += str(self.coordinate)
        if self.position is not None:
            result += f"@{self.position.line},{self.position.column}"
            if self.offset is not None:
                result += f"+{self.offset}"
        return result


@dataclass
class RangeAddress:
    """A parsed range: two point endpoints, normalized to ascending
    order at parse time."""

    start: PointAddress
    end: PointAddress

    def __str__(self) -> str:
        return f"{self.start}-{self.end}"


def _parse_address_uint(text: str):
    if not text or not text.isascii() or not text.isdigit():
        return None
    try:
        value = int(text)
    except ValueError:
        return None
    if value > _USIZE_MAX:
        return None
    return value


def _parse_address_coordinate(text: str):
    arms = text.split("/")
    if len(arms) != 3:
        return None
    values = []
    for arm in arms:
        parts = arm.split(".")
        if len(parts) != 3:
            return None
        for part in parts:
            value = _parse_address_uint(part)
            if value is None or value < 1:
                return None
            values.append(value)
    return Coordinate(*values)


def parse_point_address(address: str):
    """Parses a v0.6.1 point address:
    ``[$N:]<coordinate>[@<line>,<column>[+<offsetChars>]]``.

    Returns a PointAddress, or None on any malformed input: universe 0,
    a coordinate component below 1, a line or column below 1, a sign
    anywhere, or trailing structure. ``$1:`` is accepted on input; the
    canonical `str()` form never emits it."""
    if address.startswith("$"):
        rest = address[1:]
        if ":" not in rest:
            return None
        num, rest = rest.split(":", 1)
        universe = _parse_address_uint(num)
        if universe is None or universe < 1:
            return None
    else:
        universe = 1
        rest = address
    if "@" in rest:
        coord_part, pos_part = rest.split("@", 1)
        if "@" in pos_part:
            return None
    else:
        coord_part, pos_part = rest, None
    coordinate = _parse_address_coordinate(coord_part)
    if coordinate is None:
        return None
    position = None
    offset = None
    if pos_part is not None:
        if "," not in pos_part:
            return None
        line_part, col_part = pos_part.split(",", 1)
        line = _parse_address_uint(line_part)
        if line is None:
            return None
        if "+" in col_part:
            col_text, off_part = col_part.split("+", 1)
            offset = _parse_address_uint(off_part)
            if offset is None:
                return None
        else:
            col_text = col_part
        column = _parse_address_uint(col_text)
        if column is None:
            return None
        if line < 1 or column < 1:
            return None
        position = ScrollPosition(line=line, column=column)
    return PointAddress(
        universe=universe, coordinate=coordinate, position=position, offset=offset
    )


def _endpoint_position_key(point: PointAddress, is_start: bool):
    if point.position is not None:
        return (point.position.line, point.position.column)
    if is_start:
        return (1, 1)
    return (_USIZE_MAX, _USIZE_MAX)


def _endpoint_cmp_key(point: PointAddress, is_start: bool):
    return (
        point.universe,
        point.coordinate.as_tuple(),
        _endpoint_position_key(point, is_start),
    )


def parse_range_address(address: str):
    """Parses a v0.6.1 range address: exactly two point addresses joined
    by one hyphen. The endpoints are normalized to ascending order
    (direction is discarded, per the ratified spec). Range endpoints may
    not carry a ``+offset`` — the offset form never takes a second
    endpoint. Returns a RangeAddress, or None on malformed input."""
    if "-" not in address:
        return None
    first, second = address.split("-", 1)
    if "-" in second:
        return None
    a = parse_point_address(first)
    b = parse_point_address(second)
    if a is None or b is None:
        return None
    if a.offset is not None or b.offset is not None:
        return None
    if _endpoint_cmp_key(a, True) > _endpoint_cmp_key(b, False):
        return RangeAddress(start=b, end=a)
    return RangeAddress(start=a, end=b)


def resolve_scroll_offset(text: str, pos: ScrollPosition):
    """Resolves a caret position inside one scroll to a character
    (scalar) offset. None when the line or column is past the scroll's
    extent — never clamps."""
    if pos.line < 1 or pos.column < 1:
        return None
    line = 1
    column = 1
    offset = 0
    for ch in text:
        if line == pos.line and column == pos.column:
            return offset
        if ch == "\n":
            line += 1
            column = 1
        else:
            column += 1
        offset += 1
    if line == pos.line and column == pos.column:
        return offset
    return None


def enumerate_scrolls(member: str):
    """The member's scrolls in the phokenize sense: a list of
    (Coordinate, scroll text) from the byte-level phokenize enumeration
    the 0.6 fixtures use, decoded back to text."""
    return [
        (coord, raw.decode("utf-8"))
        for coord, raw in phokenize_bytes(member.encode("utf-8"))
    ]


def addressed_scroll_text(member: str, target: Coordinate):
    """The scroll text at a coordinate in one member phext, in the
    phokenize sense of presence: a coordinate is present exactly when
    the phokenize enumeration contains it. None when absent."""
    for coord, text in enumerate_scrolls(member):
        if coord == target:
            return text
    return None

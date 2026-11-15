"""Chains: a stream-level layer of whole phexts (libphext 0.6.0).

Ported 1:1 from libphext-rs 0.6.0 (src/phext.rs, chain layer +
multiverse addressing).

A chain is an ordered series of complete phexts within one stream,
joined by CHAIN_BREAK (0x02) and optionally terminated by CHAIN_CLOSE
(0x03). The chain layer is one rung above the library break: the nine
dimension breaks structure a single phext, while the two chain bytes
structure a stream of phexts. Each member is a whole phext, worked with
the ordinary phext functions; read in succession, a chain's members are
editions in sequence — the chain is how a phext stream encodes time.

`closed` records how the chain ended: True when a CHAIN_CLOSE terminated
it, False when the stream simply ran out (EOF). A chain that ends at EOF
is unclosed — possibly truncated — and is never silently promoted to
closed. A stream with no chain bytes at all is a single unclosed chain
holding one member phext: every pre-0.6 phext reads this way.

Multiverse addressing: inside a chain, each member phext is a universe
indexed from 1. ``$N:<address>`` names a scroll in universe N; a bare
``<address>`` means universe 1.
"""

from dataclasses import dataclass, field

from phext.addressing import (
    PointAddress,
    RangeAddress,
    addressed_scroll_text,
    enumerate_scrolls,
    parse_point_address,
    parse_range_address,
    resolve_scroll_offset,
)
from phext.coordinate import Coordinate
from phext.phext import Phext

CHAIN_BREAK = "\x02"
CHAIN_CLOSE = "\x03"
CHAIN_BREAK_U8 = 0x02
CHAIN_CLOSE_U8 = 0x03


@dataclass
class Chain:
    members: list = field(default_factory=list)
    closed: bool = False

    def serialize(self) -> str:
        """Serializes this chain alone: its members joined by
        CHAIN_BREAK, with a trailing CHAIN_CLOSE when the chain is
        closed. See `serialize_chains` for whole streams."""
        result = CHAIN_BREAK.join(self.members)
        if self.closed:
            result += CHAIN_CLOSE
        return result

    def fetch(self, address: str) -> str:
        """Fetch a scroll by multiverse address: ``$N:coord``, or a bare
        coordinate (universe 1). Out-of-range universes, malformed
        universe prefixes, and missing scrolls all yield an empty
        string, as fetch does for a missing scroll."""
        parsed = parse_universe_address(address)
        if parsed is None:
            return ""
        universe, coord = parsed
        if universe - 1 >= len(self.members):
            return ""
        return Phext().fetch(self.members[universe - 1], coord)

    def resolve_point(self, point):
        """Resolves a point address against this chain: (universe,
        coordinate, character offset within the scroll), or None. A
        point without ``@`` resolves to offset 0 of its scroll. None
        when the universe or scroll is absent or the position is out of
        range — never clamps."""
        if point.universe < 1 or point.universe > len(self.members):
            return None
        text = addressed_scroll_text(
            self.members[point.universe - 1], point.coordinate
        )
        if text is None:
            return None
        if point.position is None:
            offset = 0
        else:
            offset = resolve_scroll_offset(text, point.position)
            if offset is None:
                return None
        return (point.universe, point.coordinate, offset)

    def fetch_point(self, address: str) -> str:
        """Fetches a point address string. A bare point is a caret: it
        fetches the empty string. The offset form fetches the selected
        characters: from the point, forward `offset` characters
        (scalars) within the scroll, terminating at the scroll boundary.
        Any parse or resolution failure fetches the empty string, as
        `Chain.fetch` does."""
        point = parse_point_address(address)
        if point is None:
            return ""
        if point.offset is None:
            return ""
        resolved = self.resolve_point(point)
        if resolved is None:
            return ""
        _, _, offset = resolved
        text = addressed_scroll_text(
            self.members[point.universe - 1], point.coordinate
        )
        if text is None:
            text = ""
        return text[offset : offset + point.offset]

    def resolve_range(self, range_address):
        """Resolves a range against this chain into per-scroll segments:
        a list of (universe, coordinate, segment text) in ascending
        order, or None. Middle scrolls contribute their whole text; the
        endpoint scrolls contribute from/to their endpoint boundaries
        (an endpoint without ``@`` contributes its whole scroll). None
        when either endpoint fails to resolve — an out-of-range endpoint
        is an error, never a clamp."""
        start = range_address.start
        end = range_address.end
        if (
            start.universe < 1
            or end.universe > len(self.members)
            or start.universe > end.universe
        ):
            return None
        # both endpoint scrolls must be present, and both endpoint
        # positions must resolve
        if self.resolve_point(start) is None:
            return None
        if self.resolve_point(end) is None:
            return None
        segments = []
        for universe in range(start.universe, end.universe + 1):
            member = self.members[universe - 1]
            scrolls = sorted(
                enumerate_scrolls(member), key=lambda item: item[0].as_tuple()
            )
            for coord, text in scrolls:
                if universe == start.universe and coord < start.coordinate:
                    continue
                if universe == end.universe and coord > end.coordinate:
                    continue
                lo = 0
                hi = len(text)
                if universe == start.universe and coord == start.coordinate:
                    if start.position is None:
                        lo = 0
                    else:
                        lo = resolve_scroll_offset(text, start.position)
                        if lo is None:
                            return None
                if universe == end.universe and coord == end.coordinate:
                    if end.position is None:
                        hi = len(text)
                    else:
                        hi = resolve_scroll_offset(text, end.position)
                        if hi is None:
                            return None
                if lo > hi:
                    return None
                segments.append((universe, coord, text[lo:hi]))
        return segments

    def fetch_range(self, address: str) -> str:
        """Fetches a range address string: the spanned text with phext
        structure bytes preserved — the covered segments re-assembled at
        their coordinates into a phext (chain) fragment (scroll breaks
        between covered scrolls inside a universe, CHAIN_BREAK between
        universes, never a trailing CHAIN_CLOSE: a fragment is an
        excerpt, not a terminated chain), so the result round-trips as a
        phext fragment. Empty segments contribute nothing. Any parse or
        resolution failure fetches the empty string, as `Chain.fetch`
        does."""
        range_address = parse_range_address(address)
        if range_address is None:
            return ""
        segments = self.resolve_range(range_address)
        if segments is None:
            return ""
        members = []
        engine = Phext()
        for universe in range(range_address.start.universe, range_address.end.universe + 1):
            member = ""
            for seg_universe, coord, text in segments:
                if seg_universe == universe and text != "":
                    member = engine.insert(member, coord, text)
            members.append(member)
        return Chain(members=members, closed=False).serialize()


def parse_chains(stream: str):
    """Splits a stream into its chains. CHAIN_BREAK separates the member
    phexts of a chain; CHAIN_CLOSE terminates a chain, and whatever
    follows it opens the next one — so one stream may hold many chains.
    The stream's final chain is closed only when the stream ends with
    CHAIN_CLOSE.

    Splitting follows split semantics, so empty members and empty
    chains are preserved exactly: parse and serialize are byte-exact
    inverses for every stream."""
    ends_closed = stream.endswith(CHAIN_CLOSE)
    segments = stream.split(CHAIN_CLOSE)
    if ends_closed:
        # split preserves the empty tail after a trailing delimiter;
        # that tail is the end of the stream, not another chain
        segments.pop()
    count = len(segments)
    chains = []
    for i, segment in enumerate(segments):
        closed = ends_closed or (i + 1 < count)
        chains.append(Chain(members=segment.split(CHAIN_BREAK), closed=closed))
    return chains


def serialize_chains(chains) -> str:
    """Serializes a stream of chains back into stream bytes: the inverse
    of `parse_chains`."""
    return "".join(chain.serialize() for chain in chains)


def parse_universe_address(address: str):
    """Parses a multiverse address into (universe, Coordinate), or None
    when the universe prefix is malformed (``$0:``, a missing colon, or
    a non-numeric universe). A bare address is universe 1."""
    if address.startswith("$"):
        rest = address[1:]
        if ":" not in rest:
            return None
        num, coord_part = rest.split(":", 1)
        # mirror Rust's usize parse: ASCII digits only, at least one
        if not num or not num.isascii() or not num.isdigit():
            return None
        universe = int(num)
        if universe < 1:
            return None
    else:
        universe = 1
        coord_part = address
    try:
        coord = Coordinate.from_string(coord_part)
    except Exception:
        return None
    return (universe, coord)

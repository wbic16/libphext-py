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

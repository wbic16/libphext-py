# Ported 1:1 from libphext-rs 0.6.0 src/test_chain.rs
from phext import chain
from phext.chain import Chain
from phext.coordinate import Coordinate
from phext.phext import Phext

P = Phext()
CHAIN_BREAK = chain.CHAIN_BREAK
CHAIN_CLOSE = chain.CHAIN_CLOSE


def coord(address):
    return Coordinate.from_string(address)


def roundtrip(stream):
    chains = chain.parse_chains(stream)
    assert chain.serialize_chains(chains) == stream, f"round trip {stream!r}"


def test_chain_free_input_is_one_unclosed_chain():
    # a phext with no chain bytes: the whole stream is the single member
    # of one unclosed chain, and it serializes back unchanged
    doc = "alpha\x17beta\x01gamma"
    chains = chain.parse_chains(doc)
    assert len(chains) == 1
    assert chains[0].members == [doc]
    assert not chains[0].closed
    assert chain.serialize_chains(chains) == doc

    # single-phext behaviour on the same bytes is untouched: the chain
    # bytes are not dimension breaks, so nothing in the member moves
    assert P.fetch(doc, coord("1.1.1/1.1.1/1.1.2")) == "beta"
    assert P.fetch(doc, coord("2.1.1/1.1.1/1.1.1")) == "gamma"
    roundtrip(doc)


def test_two_phexts_chained_and_closed_round_trip():
    stream = f"edition one{CHAIN_BREAK}edition two{CHAIN_CLOSE}"
    chains = chain.parse_chains(stream)
    assert len(chains) == 1
    assert chains[0].members == ["edition one", "edition two"]
    assert chains[0].closed
    roundtrip(stream)


def test_unclosed_chain_at_eof_reports_truncated():
    chains = chain.parse_chains("one\x02two")
    assert len(chains) == 1
    assert chains[0].members == ["one", "two"]
    assert not chains[0].closed, "a chain ending at EOF must report unclosed"
    roundtrip("one\x02two")


def test_two_chains_in_one_stream_parse_as_two_units():
    stream = "a\x02b\x03c\x02d\x03"
    chains = chain.parse_chains(stream)
    assert len(chains) == 2
    assert chains[0].members == ["a", "b"]
    assert chains[0].closed
    assert chains[1].members == ["c", "d"]
    assert chains[1].closed
    roundtrip(stream)

    # a closed chain followed by an unclosed one stays two distinct chains
    mixed = chain.parse_chains("a\x03b")
    assert len(mixed) == 2
    assert mixed[0].members == ["a"]
    assert mixed[0].closed
    assert mixed[1].members == ["b"]
    assert not mixed[1].closed
    roundtrip("a\x03b")


def test_chained_members_carry_full_phexts():
    # members are complete phexts: coordinates resolve inside each member,
    # and each member restarts at 1.1.1/1.1.1/1.1.1
    first = "root\x17second scroll"
    second = P.insert("", coord("1.1.1/1.1.1/1.1.3"), "third edition")
    stream = f"{first}\x02{second}\x03"
    chains = chain.parse_chains(stream)
    assert len(chains) == 1
    assert len(chains[0].members) == 2
    assert P.fetch(chains[0].members[0], coord("1.1.1/1.1.1/1.1.2")) == "second scroll"
    assert P.fetch(chains[0].members[1], coord("1.1.1/1.1.1/1.1.3")) == "third edition"
    assert P.fetch(chains[0].members[1], coord("1.1.1/1.1.1/1.1.1")) == ""
    roundtrip(stream)


def test_editions_in_succession_read_in_order():
    # the chain is the time axis: members arrive oldest-first and stay ordered
    stream = "v1\x02v2\x02v3\x03"
    chains = chain.parse_chains(stream)
    assert len(chains) == 1
    assert chains[0].members == ["v1", "v2", "v3"]
    assert chains[0].closed
    roundtrip(stream)


def test_empty_and_break_only_streams_round_trip():
    # the empty stream is one unclosed chain holding one empty phext
    chains = chain.parse_chains("")
    assert len(chains) == 1
    assert chains[0].members == [""]
    assert not chains[0].closed
    roundtrip("")

    # a lone close terminates a chain holding one empty phext
    chains = chain.parse_chains("\x03")
    assert len(chains) == 1
    assert chains[0].members == [""]
    assert chains[0].closed
    roundtrip("\x03")

    # leading and trailing breaks preserve their empty members
    assert chain.parse_chains("a\x02")[0].members == ["a", ""]
    assert chain.parse_chains("\x02b")[0].members == ["", "b"]
    assert len(chain.parse_chains("\x02\x02")[0].members) == 3
    roundtrip("a\x02")
    roundtrip("\x02b")
    roundtrip("\x02\x02")
    roundtrip("\x02")

    # back-to-back closes are two chains, the second holding an empty phext
    chains = chain.parse_chains("a\x03\x03")
    assert len(chains) == 2
    assert chains[0].closed and chains[1].closed
    assert chains[1].members == [""]
    roundtrip("a\x03\x03")


def test_serialize_from_constructed_chains():
    c = Chain()
    assert not c.closed
    assert c.serialize() == ""
    c.members.append("v1")
    c.members.append("v2")
    assert c.serialize() == "v1\x02v2"
    c.closed = True
    assert c.serialize() == "v1\x02v2\x03"
    assert chain.serialize_chains([c]) == "v1\x02v2\x03"


def test_chain_layer_does_not_touch_member_structure():
    # splitting happens at the stream level only: a member's own scrolls
    # and breaks are exactly what the single-phext functions see
    chains = chain.parse_chains("x\x17y\x02z\x17w\x03")
    assert chains[0].members == ["x\x17y", "z\x17w"]
    assert len(P.phokenize(chains[0].members[1])) == 2
    roundtrip("x\x17y\x02z\x17w\x03")


def test_multiverse_addressing():
    c = Chain(members=["U1 home", "U2 home"], closed=True)
    assert c.fetch("1.1.1/1.1.1/1.1.1") == "U1 home"
    assert c.fetch("$1:1.1.1/1.1.1/1.1.1") == "U1 home"
    assert c.fetch("$2:1.1.1/1.1.1/1.1.1") == "U2 home"
    assert c.fetch("$3:1.1.1/1.1.1/1.1.1") == ""
    assert chain.parse_universe_address("$0:1.1.1/1.1.1/1.1.1") is None
    parsed = chain.parse_universe_address("$12:2.1.1/1.1.1/1.1.1")
    assert parsed is not None
    n, parsed_coord = parsed
    assert n == 12
    assert parsed_coord == coord("2.1.1/1.1.1/1.1.1")


def test_adjacent_closes_are_two_empty_chains():
    chains = chain.parse_chains("\x03\x03")
    assert len(chains) == 2
    assert all(c.closed for c in chains)
    assert chain.serialize_chains(chains) == "\x03\x03"

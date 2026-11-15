# Ported 1:1 from libphext-rs 0.6.1 src/test_address.rs
from phext import chain
from phext.addressing import (
    ScrollPosition,
    parse_point_address,
    parse_range_address,
)
from phext.chain import Chain
from phext.coordinate import Coordinate
from phext.phext import Phext

P = Phext()


def home():
    return Coordinate.from_string("1.1.1/1.1.1/1.1.1")


def scroll2():
    return Coordinate.from_string("1.1.1/1.1.1/1.1.2")


def member_a():
    member = P.insert("", home(), "alpha bravo\ncharlie delta\necho")
    member = P.insert(member, scroll2(), "second scroll\nline two")
    return member


def member_b():
    return P.insert("", home(), "uni2 home\nsecond line")


def make_chain():
    return Chain(members=[member_a(), member_b()], closed=False)


def test_point_parse_canonical():
    p = parse_point_address("$3:1.1.1/1.1.1/1.1.1@24,5")
    assert p.universe == 3
    assert p.coordinate == home()
    assert p.position == ScrollPosition(line=24, column=5)
    assert p.offset is None
    assert str(p) == "$3:1.1.1/1.1.1/1.1.1@24,5"
    # $1: is accepted on input, never emitted
    p1 = parse_point_address("$1:1.1.1/1.1.1/1.1.1@24,5")
    assert str(p1) == "1.1.1/1.1.1/1.1.1@24,5"
    # leading zeros parse by value; canonical form is minimal decimal
    pz = parse_point_address("1.1.1/1.1.1/1.1.1@024,005")
    assert str(pz) == "1.1.1/1.1.1/1.1.1@24,5"
    # bare coordinate: no position
    bare = parse_point_address("1.1.1/1.1.1/1.1.2")
    assert bare.position is None
    assert str(bare) == "1.1.1/1.1.1/1.1.2"
    # offset form
    po = parse_point_address("1.1.1/1.1.1/1.1.1@24,5+10")
    assert po.offset == 10
    assert str(po) == "1.1.1/1.1.1/1.1.1@24,5+10"


def test_point_parse_rejects():
    for bad in [
        "$0:1.1.1/1.1.1/1.1.1@1,1",  # universe 0
        "1.1.1/1.1.1/1.1.1@0,5",  # line 0
        "1.1.1/1.1.1/1.1.1@24,0",  # column 0
        "1.1.1/1.1.1/0.1.1@1,1",  # coordinate component 0
        "1.1.1/1.1.1@1,1",  # only two arms
        "1.1.1/1.1.1/1.1.1@24",  # no column
        "1.1.1/1.1.1/1.1.1@24,5+",  # empty offset
        "1.1.1/1.1.1/1.1.1@24,+5",  # empty column
        "1.1.1/1.1.1/1.1.1@24,5@1,1",  # second @
        "1.1.1/1.1.1/1.1.1@ 24,5",  # whitespace
        "",  # empty
    ]:
        assert parse_point_address(bad) is None, f"expected rejection: {bad!r}"


def test_point_resolve():
    c = make_chain()
    p = parse_point_address("1.1.1/1.1.1/1.1.1@2,3")
    # line 1 "alpha bravo" = 11 chars + newline = 12; column 3 -> +2
    assert c.resolve_point(p) == (1, home(), 14)
    # last valid boundary of line 1
    end = parse_point_address("1.1.1/1.1.1/1.1.1@1,12")
    assert c.resolve_point(end) == (1, home(), 11)
    # past the line, past the scroll, missing scroll, missing universe
    assert c.resolve_point(parse_point_address("1.1.1/1.1.1/1.1.1@1,13")) is None
    assert c.resolve_point(parse_point_address("1.1.1/1.1.1/1.1.1@4,1")) is None
    assert c.resolve_point(parse_point_address("1.1.1/1.1.1/1.1.9@1,1")) is None
    assert c.resolve_point(parse_point_address("$3:1.1.1/1.1.1/1.1.1@1,1")) is None
    # bare point resolves to offset 0; universe 2 resolves in its own member
    assert c.resolve_point(parse_point_address("1.1.1/1.1.1/1.1.2")) == (1, scroll2(), 0)
    assert c.resolve_point(parse_point_address("$2:1.1.1/1.1.1/1.1.1@2,1")) == (2, home(), 10)


def test_point_fetch_offset():
    c = make_chain()
    assert c.fetch_point("1.1.1/1.1.1/1.1.1@1,1+5") == "alpha"
    assert c.fetch_point("1.1.1/1.1.1/1.1.1@2,1+7") == "charlie"
    # across a line boundary: offset 9 is 'v' of "bravo"
    assert c.fetch_point("1.1.1/1.1.1/1.1.1@1,10+5") == "vo\nch"
    # clipped at the scroll boundary, never into the next scroll
    assert c.fetch_point("1.1.1/1.1.1/1.1.1@3,1+100") == "echo"
    assert c.fetch_point("1.1.1/1.1.1/1.1.1@1,1+0") == ""
    # a bare point is a caret: fetches nothing; failures fetch nothing
    assert c.fetch_point("1.1.1/1.1.1/1.1.1@1,1") == ""
    assert c.fetch_point("1.1.1/1.1.1/1.1.1@9,1+3") == ""
    assert c.fetch_point("$2:1.1.1/1.1.1/1.1.1@1,1+4") == "uni2"


def test_point_fetch_offset_unicode():
    member = P.insert("", home(), "héllo wörld")
    c = Chain(members=[member], closed=False)
    # columns and offsets count scalars: é is one character (two bytes)
    assert c.resolve_point(parse_point_address("1.1.1/1.1.1/1.1.1@1,3")) == (1, home(), 2)
    assert c.fetch_point("1.1.1/1.1.1/1.1.1@1,2+3") == "éll"


def test_range_parse_canonical():
    r = parse_range_address("1.1.1/1.1.1/1.1.1@24,5-1.1.1/1.1.1/1.1.1@24,9")
    assert str(r) == "1.1.1/1.1.1/1.1.1@24,5-1.1.1/1.1.1/1.1.1@24,9"
    # reversed input normalizes: direction is discarded
    rev = parse_range_address("1.1.1/1.1.1/1.1.1@24,9-1.1.1/1.1.1/1.1.1@24,5")
    assert rev == r
    # $1: on input is dropped in canonical form, even beside a $3: endpoint
    cross = parse_range_address("$1:1.1.1/1.1.1/1.1.1@24,5-$3:1.1.1/1.1.1/1.1.1@31,12")
    assert str(cross) == "1.1.1/1.1.1/1.1.1@24,5-$3:1.1.1/1.1.1/1.1.1@31,12"
    # offset forms are not range endpoints
    assert parse_range_address("1.1.1/1.1.1/1.1.1@1,1+3-1.1.1/1.1.1/1.1.1@1,5") is None
    # one hyphen only
    assert parse_range_address("1.1.1/1.1.1/1.1.1-1.1.1/1.1.1/1.1.2-1.1.1/1.1.1/1.1.3") is None


def test_range_fetch_within_scroll():
    c = make_chain()
    # characters 1-5 of line 1 (boundaries 1..6, half-open)
    assert c.fetch_range("1.1.1/1.1.1/1.1.1@1,1-1.1.1/1.1.1/1.1.1@1,6") == "alpha"
    # the whole of line 2, newline included
    assert c.fetch_range("1.1.1/1.1.1/1.1.1@2,1-1.1.1/1.1.1/1.1.1@3,1") == "charlie delta\n"
    # empty range is a caret
    assert c.fetch_range("1.1.1/1.1.1/1.1.1@1,3-1.1.1/1.1.1/1.1.1@1,3") == ""
    # reversed fetches the same extent
    assert c.fetch_range("1.1.1/1.1.1/1.1.1@1,6-1.1.1/1.1.1/1.1.1@1,1") == "alpha"


def test_range_fetch_cross_scroll():
    c = make_chain()
    frag = c.fetch_range("1.1.1/1.1.1/1.1.1@3,2-1.1.1/1.1.1/1.1.2@1,7")
    assert frag == "cho\x17second"
    # the fragment round-trips as a phext: its scrolls fetch back the segments
    parsed = chain.parse_chains(frag)
    assert parsed[0].fetch("1.1.1/1.1.1/1.1.1") == "cho"
    assert parsed[0].fetch("1.1.1/1.1.1/1.1.2") == "second"
    # whole scrolls, no @ on either endpoint: the member itself
    assert c.fetch_range("1.1.1/1.1.1/1.1.1-1.1.1/1.1.1/1.1.2") == member_a()


def test_range_fetch_multiverse():
    c = make_chain()
    frag = c.fetch_range("1.1.1/1.1.1/1.1.1@3,2-$2:1.1.1/1.1.1/1.1.1@1,5")
    # universe 1's scroll 2 lies strictly between the endpoints: a whole segment
    assert frag == "cho\x17second scroll\nline two\x02uni2"
    parsed = chain.parse_chains(frag)
    assert len(parsed) == 1
    assert len(parsed[0].members) == 2
    assert parsed[0].fetch("$2:1.1.1/1.1.1/1.1.1") == "uni2"
    # resolve_range exposes the segments
    range_address = parse_range_address("1.1.1/1.1.1/1.1.1@3,2-$2:1.1.1/1.1.1/1.1.1@1,5")
    segments = c.resolve_range(range_address)
    assert segments == [
        (1, home(), "cho"),
        (1, scroll2(), "second scroll\nline two"),
        (2, home(), "uni2"),
    ]


def test_range_resolution_errors():
    c = make_chain()
    # universe past the end of the chain
    assert c.fetch_range("1.1.1/1.1.1/1.1.1@1,1-$3:1.1.1/1.1.1/1.1.1@1,1") == ""
    assert c.resolve_range(parse_range_address("1.1.1/1.1.1/1.1.1@1,1-$3:1.1.1/1.1.1/1.1.1@1,1")) is None
    # missing endpoint scroll
    assert c.resolve_range(parse_range_address("1.1.1/1.1.1/1.1.1@1,1-1.1.1/1.1.1/1.1.9@1,1")) is None
    # line past the scroll's end: an error, never a clamp
    assert c.resolve_range(parse_range_address("1.1.1/1.1.1/1.1.1@1,1-1.1.1/1.1.1/1.1.1@9,1")) is None
    # column past the line's last boundary
    assert c.resolve_range(parse_range_address("1.1.1/1.1.1/1.1.1@1,1-1.1.1/1.1.1/1.1.1@1,13")) is None

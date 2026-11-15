# Ported 1:1 from libphext-rs 0.6.0 src/test_binary.rs
import random

from phext import binary
from phext.coordinate import Coordinate
from phext.phext import Phext

P = Phext()


def coord(address):
    return Coordinate.from_string(address)


def test_encode_decode_round_trip():
    # empty payload: header line alone
    empty = b""
    scroll = binary.encode_scroll(empty)
    assert scroll == "phext-binary:1:base64\n"
    assert binary.decode_scroll(scroll) == empty

    # every byte value
    all_bytes = bytes(range(256))
    scroll = binary.encode_scroll(all_bytes)
    assert binary.is_binary_scroll(scroll)
    assert binary.decode_scroll(scroll) == all_bytes

    # a plainly non-UTF-8 sequence
    foreign = bytes([0xFF, 0xFE, 0x80, 0x00, 0x61, 0xC3, 0x28])
    scroll = binary.encode_scroll(foreign)
    assert binary.decode_scroll(scroll) == foreign

    # >= 1 MiB payload, deterministic pattern covering all byte values
    big = bytes(i % 256 for i in range(1024 * 1024 + 13))
    scroll = binary.encode_scroll(big)
    assert binary.decode_scroll(scroll) == big


def test_decode_scroll_rejects_non_binary():
    assert binary.decode_scroll("just some text") is None
    assert binary.decode_scroll("") is None
    # header must be a complete line: no line break, no binary scroll
    assert binary.decode_scroll("phext-binary:1:base64") is None
    assert not binary.is_binary_scroll("phext-binary:1:base64")
    # malformed base64 body: recognisably binary, undecodable
    malformed = "phext-binary:1:base64\n!!! not base64 !!!"
    assert binary.is_binary_scroll(malformed)
    assert binary.decode_scroll(malformed) is None


def test_insert_and_fetch_binary():
    target = coord("1.1.1/1.1.1/1.1.2")
    payload = bytes([0x00, 0x01, 0x02, 0xFE, 0xFF, 0x7F, 0x80])

    doc = P.insert("", coord("1.1.1/1.1.1/1.1.1"), "plain text scroll")
    doc = binary.insert_binary(doc, target, payload)

    # the text scroll next door is untouched
    assert P.fetch(doc, coord("1.1.1/1.1.1/1.1.1")) == "plain text scroll"
    # the binary scroll fetches back byte-identical
    assert binary.fetch_binary(doc, target) == payload
    # and its stored form is the canonical binary scroll
    stored = P.fetch(doc, target)
    assert binary.is_binary_scroll(stored)
    assert binary.decode_scroll(stored) == payload


def test_fetch_binary_fallbacks():
    doc = P.insert("", coord("1.1.1/1.1.1/1.1.1"), "hello")
    # a plain text scroll yields its own UTF-8 bytes
    assert binary.fetch_binary(doc, coord("1.1.1/1.1.1/1.1.1")) == b"hello"
    # an unoccupied coordinate yields no bytes (mirrors fetch returning "")
    assert binary.fetch_binary(doc, coord("9.9.9/9.9.9/9.9.9")) == b""
    # a malformed binary scroll yields its own bytes verbatim, not an error
    doc = P.insert("", coord("1.1.1/1.1.1/1.1.1"), "phext-binary:1:base64\n!!!")
    assert binary.fetch_binary(doc, coord("1.1.1/1.1.1/1.1.1")) == \
        "phext-binary:1:base64\n!!!".encode("utf-8")


def test_update_rule_non_utf8_is_base64_verbatim():
    target = coord("1.1.1/1.1.1/1.1.1")
    # payload deliberately includes dimension-break bytes (0x17, 0x1C):
    # armoured as base64, they round-trip as content, not structure
    payload = bytes([0xFF, 0x17, 0x1C, 0x80, 0x00])
    doc = binary.replace_bytes("", target, payload)

    stored = P.fetch(doc, target)
    assert binary.is_binary_scroll(stored), \
        "non-UTF-8 update must be stored as a binary scroll"
    assert binary.fetch_binary(doc, target) == payload

    # same rule through the insert entry point
    doc = binary.insert_bytes("", target, payload)
    assert binary.fetch_binary(doc, target) == payload


def test_update_rule_utf8_stays_text():
    target = coord("1.1.1/1.1.1/1.1.1")
    doc = binary.replace_bytes("", target, "ordinary text ✓".encode("utf-8"))
    assert P.fetch(doc, target) == "ordinary text ✓"
    assert not binary.is_binary_scroll(P.fetch(doc, target))
    assert binary.fetch_binary(doc, target) == "ordinary text ✓".encode("utf-8")


def test_ingest_foreign_byte_stream():
    # a phext byte stream whose second scroll is not valid UTF-8
    stream = b"hello" + b"\x17" + bytes([0xFF, 0xFE, 0x41, 0x80])

    doc = binary.ingest(stream)

    # text scroll passes through verbatim
    assert P.fetch(doc, coord("1.1.1/1.1.1/1.1.1")) == "hello"
    # foreign scroll: stored as a binary scroll, reads back as the original bytes
    foreign_at = coord("1.1.1/1.1.1/1.1.2")
    assert binary.is_binary_scroll(P.fetch(doc, foreign_at))
    assert binary.fetch_binary(doc, foreign_at) == bytes([0xFF, 0xFE, 0x41, 0x80])


def test_ingest_canonical_phext_is_identity():
    doc = P.insert("", coord("1.1.1/1.1.1/1.1.1"), "first")
    doc = P.insert(doc, coord("1.1.1/1.1.1/1.1.2"), "second ✓ scroll")
    doc = P.insert(doc, coord("2.1.1/1.3.1/1.1.1"), "far away")
    assert binary.ingest(doc.encode("utf-8")) == doc


def test_ingest_empty_and_break_only_streams():
    # no error, no content
    doc = binary.ingest(b"")
    assert P.fetch(doc, coord("1.1.1/1.1.1/1.1.1")) == ""
    doc = binary.ingest(bytes([0x17, 0x18]))  # SCROLL_BREAK, SECTION_BREAK
    assert P.fetch(doc, coord("1.1.1/1.1.1/1.1.1")) == ""


def test_phokenize_bytes_matches_phokenize():
    doc = "alpha\x17beta\x18gamma"
    text_parts = P.phokenize(doc)
    byte_parts = binary.phokenize_bytes(doc.encode("utf-8"))
    assert len(text_parts) == len(byte_parts)
    for text_part, byte_part in zip(text_parts, byte_parts):
        assert text_part.coord == byte_part[0]
        assert text_part.text.encode("utf-8") == byte_part[1]


def _phokenize_bytes_literal(data: bytes):
    # A literal, byte-at-a-time transliteration of the reference
    # phokenize_bytes loop (libphext-rs src/binary.rs), used only to
    # cross-check the optimised implementation in phext.binary on
    # small inputs.
    breaks = {0x17, 0x18, 0x19, 0x1A, 0x1C, 0x1D, 0x1E, 0x1F, 0x01}
    apply_map = {
        0x17: "scroll", 0x18: "section", 0x19: "chapter", 0x1A: "book",
        0x1C: "volume", 0x1D: "collection", 0x1E: "series", 0x1F: "shelf",
        0x01: "library",
    }
    result = []
    max_len = len(data)
    walker = Coordinate(1, 1, 1, 1, 1, 1, 1, 1, 1)
    pi = 0
    while True:
        begin = Coordinate(*walker.as_tuple())
        text_start = None
        text_end = max_len
        while pi < max_len:
            byte = data[pi]
            if byte in breaks:
                getattr(walker, apply_map[byte] + "Break")()
                if text_start is not None:
                    text_end = pi
                    pi += 1
                    break
            elif text_start is None:
                text_start = pi
                begin = Coordinate(*walker.as_tuple())
            pi += 1
        scroll = data[text_start:text_end] if text_start is not None else b""
        result.append((begin, scroll))
        if pi >= max_len:
            break
    return result


def test_phokenize_bytes_matches_literal_reference_on_random_streams():
    rng = random.Random(0x6006)
    alphabet = [0x61, 0x62, 0x63, 0x17, 0x18, 0x19, 0x1A, 0x1C, 0x1D,
                0x1E, 0x1F, 0x01, 0x0A, 0xFF, 0x80]
    for _ in range(300):
        data = bytes(rng.choice(alphabet) for _ in range(rng.randrange(0, 40)))
        assert binary.phokenize_bytes(data) == _phokenize_bytes_literal(data), data

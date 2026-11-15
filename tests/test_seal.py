# Ported 1:1 from libphext-rs 0.6.0 src/test_seal.rs
# (the rs "real phext" corpus is its gitignored unit-test.phext; here the
# equivalent is a multi-scroll phext built with the library itself, plus
# a binary-scroll-carrying document exactly as in the rs test.)
import pytest

from phext import seal
from phext.coordinate import Coordinate
from phext.phext import Phext


def _real_phext():
    p = Phext()
    doc = p.insert("", Coordinate.from_string("1.1.1/1.1.1/1.1.1"),
                   "cover text — a real, multi-scroll phext ✓")
    doc = p.insert(doc, Coordinate.from_string("1.1.1/1.1.1/1.1.2"),
                   "second scroll")
    doc = p.insert(doc, Coordinate.from_string("2.3.4/5.6.7/8.9.10"),
                   "far away scroll\nwith a line break")
    return doc


def test_seal_round_trip_real_phext():
    corpus = _real_phext()
    sealed = seal.seal(corpus)
    assert len(sealed) > 0
    # an xz stream starts with the xz magic bytes
    assert sealed[0:6] == b"\xfd7zXZ\x00"
    restored = seal.unseal_string(sealed)
    assert restored == corpus


def test_seal_round_trip_empty_and_small():
    sealed = seal.seal("")
    assert seal.unseal_string(sealed) == ""

    sealed = seal.seal("hello phext")
    assert seal.unseal(sealed) == b"hello phext"


def test_seal_carrying_binary_scrolls():
    # a phext holding base64 binary scrolls (the canonical literal form)
    # seals and unseals with every scroll intact
    doc = "cover text\x17phext-binary:1:base64\nAAEC/f7/fw==\x17after"
    sealed = seal.seal(doc)
    restored = seal.unseal_string(sealed)
    assert restored == doc


def test_seal_is_deterministic():
    doc = "the same phext, sealed twice\x17the same phext, sealed twice"
    first = seal.seal(doc)
    second = seal.seal(doc)
    assert first == second


def test_unseal_rejects_non_xz_data():
    with pytest.raises(Exception):
        seal.unseal(b"this is not an xz stream")
    with pytest.raises(Exception):
        seal.unseal(b"")
    with pytest.raises(Exception):
        seal.unseal_string(b"phext, but unsealed")

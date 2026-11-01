import pytest

from phext.coordinate import Coordinate
from phext.indexed import IndexedPhext
from phext.phext import Phext

# Upstream behaviors covered by this module:
# test_index_offsets_match_iter_scrolls
# test_indexed_fetch_matches_fetch_everywhere
# test_indexed_explode_matches_explode
# test_indexed_generated_document
# test_indexed_empty_and_single_scroll
# test_indexed_unbounded_matches_fetch
# test_indexed_fetch_beyond_999_chapter
# test_index_offsets_built_once
# test_phext_indexed_convenience_constructor

SB = Phext.SCROLL_BREAK
NB = Phext.SECTION_BREAK
CB = Phext.CHAPTER_BREAK
BB = Phext.BOOK_BREAK
VB = Phext.VOLUME_BREAK
LB = Phext.LIBRARY_BREAK


def coord(text):
  return Coordinate.from_string(text)


def assert_equivalent(buffer):
  phext = Phext()
  indexed = IndexedPhext(buffer)
  exploded = phext.explode(buffer)

  # every coordinate present: indexed fetch == linear fetch == explode
  for c, text in exploded.items():
    assert indexed.fetch(c) == phext.fetch(buffer, c)
    assert indexed.fetch(c) == text
    assert c in indexed

  # index offsets point at the same text fetch returns
  for c, (start, length) in phext.index_offsets(buffer).items():
    assert buffer[start:start + length] == phext.fetch(buffer, c)

  # a spread of absent coordinates: both return ""
  for absent in ["9.9.9/9.9.9/9.9.9", "1.1.1/1.1.1/1.1.9",
                 "1.1.1/1.9.1/1.1.1", "5.5.5/5.5.5/5.5.5"]:
    a = coord(absent)
    if a not in exploded:
      assert indexed.fetch(a) == ""
      assert phext.fetch(buffer, a) == ""
      assert a not in indexed

  assert indexed.explode() == exploded
  assert set(indexed.coordinates()) == set(exploded.keys())
  assert set(indexed.keys()) == set(exploded.keys())
  assert len(indexed) == len(phext.phokenize(buffer))
  return indexed


def test_index_offsets_match_iter_scrolls():
  phext = Phext()
  example = "first scroll\x17second scroll\x18second section\x19second chapter\x1Abook 2\x1Cvolume 2\x1Dcollection 2\x1Eseries 2\x1Fshelf 2\x01library 2"
  offsets = phext.index_offsets(example)
  scrolls = phext.phokenize(example)
  assert len(offsets) == len(scrolls)
  position = 0
  for ps in scrolls:
    start, length = offsets[ps.coord]
    assert example[start:start + length] == ps.text
    assert start >= position
    position = start + length


def test_indexed_fetch_matches_fetch_everywhere():
  buffer = "alpha" + SB + "beta" + NB + "gamma" + CB + "delta" + \
           BB + "epsilon" + VB + "zeta" + LB + "eta"
  assert_equivalent(buffer)


def test_indexed_explode_matches_explode():
  buffer = "one" + SB + "two" + SB + "three" + NB + "four"
  indexed = assert_equivalent(buffer)
  assert indexed.explode() == Phext().explode(buffer)


def test_indexed_generated_document():
  # >50 scrolls across volumes, books, chapters, sections and scrolls,
  # built through the library's own implode so coordinates are canonical
  phext = Phext()
  entries = {}
  n = 0
  for volume in (1, 2, 3):
    for book in (1, 2):
      for chapter in (1, 2, 3):
        for section in (1, 2):
          for scroll in (1, 2):
            n += 1
            c = Coordinate(1, 1, 1, 1, volume, book, chapter, section, scroll)
            entries[c] = f"scroll {volume}.{book}.{chapter}.{section}.{scroll} #{n}"
  entries[Coordinate(1, 1, 1, 1, 1, 1, 1, 1, 1)] = "x" * 500  # one long scroll
  buffer = phext.implode(entries)
  assert len(entries) > 50
  assert_equivalent(buffer)


def test_indexed_empty_and_single_scroll():
  assert_equivalent("")
  indexed = IndexedPhext("")
  assert len(indexed) == 0
  assert indexed.coordinates() == []
  assert indexed.fetch(coord("1.1.1/1.1.1/1.1.1")) == ""

  assert_equivalent("just one scroll, no breaks at all")
  single = IndexedPhext("hello")
  assert len(single) == 1
  assert single.fetch(coord("1.1.1/1.1.1/1.1.1")) == "hello"


def test_indexed_unbounded_matches_fetch():
  # 1005 scrolls: since 0.4.0 coordinates are unbounded, so the scrolls
  # past 999 land on DISTINCT coordinates (.../1.1.1000, ...) instead of
  # collapsing onto .../1.1.999 as the old saturation made them. Fetch,
  # indexed fetch and explode must agree everywhere.
  phext = Phext()
  parts = []
  for i in range(1005):
    parts.append(f"s{i}")
  buffer = SB.join(parts)
  indexed = IndexedPhext(buffer)

  at_999 = coord("1.1.1/1.1.1/1.1.999")
  at_1000 = coord("1.1.1/1.1.1/1.1.1000")
  at_1005 = coord("1.1.1/1.1.1/1.1.1005")
  assert phext.fetch(buffer, at_999) == "s998"
  assert indexed.fetch(at_999) == "s998"
  assert phext.fetch(buffer, at_1000) == "s999"
  assert indexed.fetch(at_1000) == "s999"
  assert indexed.fetch(at_1005) == "s1004"

  exploded = phext.explode(buffer)
  for c in exploded:
    assert indexed.fetch(c) == phext.fetch(buffer, c)
  assert indexed.explode() == exploded
  assert indexed.explode()[at_1005] == "s1004"
  # every scroll has its own coordinate now: nothing collapses
  assert len(indexed) == 1005
  assert len(indexed.coordinates()) == 1005


def test_indexed_fetch_beyond_999_chapter():
  # a generated buffer with a scroll at chapter 1500: reachable and
  # fetchable since 0.4.0 removed the cap (this is the CF dataset shape:
  # row r at chapter r+2, most rows beyond 999)
  phext = Phext()
  entries = {
    Coordinate(1, 1, 1, 1, 1, 1, 1, 1, 1): "first",
    Coordinate(1, 1, 1, 1, 1, 1, 1500, 1, 1): "deep chapter",
    Coordinate(1, 1, 1, 1, 1, 1, 16002, 3, 8): "deepest",
  }
  buffer = phext.implode(entries)
  indexed = IndexedPhext(buffer)
  for c, text in entries.items():
    assert phext.fetch(buffer, c) == text
    assert indexed.fetch(c) == text
  assert indexed.explode() == phext.explode(buffer) == entries
  assert len(indexed.coordinates()) == 3


def test_index_offsets_built_once():
  # fetching through an IndexedPhext must not rescan the buffer: patch the
  # scanner to explode if it is called again after construction
  buffer = "a" + SB + "b" + SB + "c"
  indexed = IndexedPhext(buffer)
  phext = Phext()
  calls = []
  original = Phext._iter_offsets

  def counting(self, buf):
    calls.append(1)
    return original(self, buf)

  Phext._iter_offsets = counting
  try:
    for _ in range(10):
      assert indexed.fetch(coord("1.1.1/1.1.1/1.1.2")) == "b"
    assert coord("1.1.1/1.1.1/1.1.3") in indexed
    assert indexed.coordinates()
  finally:
    Phext._iter_offsets = original
  assert calls == []
  assert len(phext.index_offsets(buffer)) == 3


def test_phext_indexed_convenience_constructor():
  phext = Phext()
  buffer = "x" + SB + "y"
  indexed = phext.indexed(buffer)
  assert isinstance(indexed, IndexedPhext)
  assert indexed.fetch(coord("1.1.1/1.1.1/1.1.2")) == "y"
  assert indexed.explode() == phext.explode(buffer)

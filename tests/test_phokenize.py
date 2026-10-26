from phext.coordinate import Coordinate
from phext.positionedScroll import PositionedScroll
from phext.range import Range
from phext.phext import Phext
from legacy_phext import LegacyPhext
from datetime import datetime
from copy import deepcopy
import random
import pytest

# Differential tests: the linear-time implementation must match the original
# (quadratic-constant, per-character deepcopy) implementation exactly.

DELIMITERS = ["\x01", "\x1F", "\x1E", "\x1D", "\x1C", "\x1A", "\x19", "\x18", "\x17"]
TEXT = ["a", "b", "Z", " ", "0", "\n", "\r\n", "\t", "\x1B", "\x02", "\x03", "\x07",
        "é", "日本", "→", "🔱", "🝗", " ", "﻿", "..."]

EDGE_CASES = [
  "",
  "a",
  "\x17",
  "\x01",
  "\x17\x17\x17",
  "\x17a",
  "a\x17",
  "a\x17\x17b",
  "\x01\x1F\x1E\x1D\x1C\x1A\x19\x18\x17",
  "\x01\x1F\x1E\x1D\x1C\x1A\x19\x18\x17tail",
  "head\x01\x1F\x1E\x1D\x1C\x1A\x19\x18\x17",
  "\x17\x18\x19\x1A\x1C\x1D\x1E\x1F\x01x",
  "line one\nline two\x17scroll two\r\n\x18",
  "\x1B is escape, not a delimiter\x17next",
  "日本語\x17🔱 trident\x18é\x01→",
  "hello world\x17\x17\x17scroll 4\x01Library 2",
  "3A\x17B2\x18C1",
  "\n\n\n",
  "\x02\x03\x07",
  # saturation: more than 999 breaks in one dimension
  "a" + "\x17" * 1005 + "b",
  "a" + "\x17" * 998 + "b\x17c\x17d",
  "x" + "\x18" * 998 + "y" + "\x17" * 5 + "z\x18w\x17v",
  "\x01" * 1200 + "far" + "\x1F" * 1000 + "farther",
]

def random_document(rng: random.Random) -> str:
  parts = []
  for _ in range(rng.randint(0, 24)):
    roll = rng.random()
    if roll < 0.35:
      parts.append(rng.choice(DELIMITERS))
    elif roll < 0.45:
      # a run of delimiters, sometimes all the same, sometimes mixed
      if rng.random() < 0.5:
        parts.append(rng.choice(DELIMITERS) * rng.randint(2, 6))
      else:
        parts.append("".join(rng.choice(DELIMITERS) for _ in range(rng.randint(2, 6))))
    else:
      parts.append("".join(rng.choice(TEXT) for _ in range(rng.randint(1, 5))))
  return "".join(parts)

def random_coordinate(rng: random.Random) -> Coordinate:
  return Coordinate(*[rng.choice([1, 1, 1, 2, 3, rng.randint(1, 12)]) for _ in range(9)])

def outcome(fn, *args):
  # the value returned, or the type of exception raised (offset() raises for some inputs)
  try:
    return fn(*args)
  except Exception as e:
    return type(e)

def corpus():
  rng = random.Random(0x17)
  docs = list(EDGE_CASES)
  for _ in range(3000):
    docs.append(random_document(rng))
  return docs

DOCS = corpus()

def as_pairs(stack):
  return [(ps.coord.as_tuple(), ps.text) for ps in stack]

def test_phokenize_matches_legacy():
  new = Phext()
  old = LegacyPhext()
  for doc in DOCS:
    assert as_pairs(new.phokenize(doc)) == as_pairs(old.phokenize(doc)), repr(doc)

def test_phokenize_coordinates_are_distinct_objects():
  phext = Phext()
  stack = phext.phokenize("a\x17b\x17c")
  stack[0].coord.scrollBreak()
  assert stack[1].coord == Coordinate.from_string("1.1.1/1.1.1/1.1.2")
  assert stack[2].coord == Coordinate.from_string("1.1.1/1.1.1/1.1.3")

def test_serialization_matches_legacy():
  new = Phext()
  old = LegacyPhext()
  for doc in DOCS:
    assert new.normalize(doc) == old.normalize(doc), repr(doc)
    assert new.dephokenize(old.phokenize(doc)) == old.dephokenize(old.phokenize(doc)), repr(doc)
    exploded = new.explode(doc)
    assert {k.as_tuple(): v for k, v in exploded.items()} == \
           {k.as_tuple(): v for k, v in old.explode(doc).items()}, repr(doc)
    assert new.implode(exploded) == old.implode(old.explode(doc)), repr(doc)

def test_explode_implode_round_trip():
  phext = Phext()
  checked = 0
  for doc in DOCS:
    coords = [ps.coord.as_tuple() for ps in phext.phokenize(doc)]
    if coords != sorted(set(coords)):
      # a saturated dimension (999) can make coordinates repeat or move backwards;
      # such documents can't round trip through a dict (same as the legacy code)
      continue
    exploded = phext.explode(doc)
    imploded = phext.implode(exploded)
    assert imploded == phext.normalize(doc), repr(doc)
    assert phext.explode(imploded) == exploded, repr(doc)
    checked += 1
  assert checked > 2900

def test_maps_and_index_match_legacy():
  new = Phext()
  old = LegacyPhext()
  for doc in DOCS:
    assert new.textmap(doc) == old.textmap(doc), repr(doc)
    assert new.navmap("/x/", doc) == old.navmap("/x/", doc), repr(doc)
    assert new.index(doc) == old.index(doc), repr(doc)
    assert as_pairs(new.index_phokens(doc)) == as_pairs(old.index_phokens(doc)), repr(doc)
    assert new.expand(doc) == old.expand(doc), repr(doc)
    assert new.contract(doc) == old.contract(doc), repr(doc)
    assert new.create_summary(doc) == old.create_summary(doc), repr(doc)

def test_lookups_match_legacy():
  new = Phext()
  old = LegacyPhext()
  rng = random.Random(0x18)
  for doc in DOCS:
    present = [ps.coord for ps in old.phokenize(doc)]
    if len(present) > 3:
      present = [present[0], rng.choice(present[1:-1]), present[-1]]
    targets = present + [random_coordinate(rng), Coordinate(1,1,1, 1,1,1, 1,1,0)]
    for target in targets:
      assert new.fetch(doc, target) == old.fetch(doc, target), (repr(doc), str(target))
      assert as_pairs(new.next_scroll(doc, target)) == as_pairs(old.next_scroll(doc, target)), (repr(doc), str(target))
      a = new.get_subspace_coordinates(doc, deepcopy(target))
      b = old.get_subspace_coordinates(doc, deepcopy(target))
      assert (a.start, a.end, a.best.as_tuple()) == (b.start, b.end, b.best.as_tuple()), (repr(doc), str(target))
    for target in present[-1:] + targets[-2:-1]:
      assert outcome(new.offset, doc, target) == outcome(old.offset, doc, target), (repr(doc), str(target))

def test_edits_match_legacy():
  new = Phext()
  old = LegacyPhext()
  rng = random.Random(0x19)
  for doc in DOCS[:1500]:
    coord = random_coordinate(rng)
    text = rng.choice(["", "inserted", "日本\n🔱"])
    assert new.insert(doc, coord, text) == old.insert(doc, coord, text), repr(doc)
    assert new.replace(doc, coord, text) == old.replace(doc, coord, text), repr(doc)
    assert new.remove(doc, coord) == old.remove(doc, coord), repr(doc)
    low, high = sorted([random_coordinate(rng), random_coordinate(rng)])
    assert new.range_replace(doc, Range(low, high), text) == old.range_replace(doc, Range(low, high), text), repr(doc)
    other = rng.choice(DOCS)
    assert new.merge(doc, other) == old.merge(doc, other), (repr(doc), repr(other))
    assert new.subtract(doc, other) == old.subtract(doc, other), (repr(doc), repr(other))
    assert new.soundex_v1(doc) == old.soundex_v1(doc), repr(doc)

def test_append_scroll_matches_legacy():
  new = Phext()
  old = LegacyPhext()
  rng = random.Random(0x1A)
  for _ in range(3000):
    start = random_coordinate(rng)
    entry = PositionedScroll(random_coordinate(rng), rng.choice(["", "text", "é"]))
    if rng.random() < 0.1:
      entry.coord.scroll = 0 # below the 1-based floor: the stepwise walk stops past it
    a_location = deepcopy(start)
    b_location = deepcopy(start)
    a = new.append_scroll(entry, a_location)
    b = old.append_scroll(entry, b_location)
    assert a.text == b.text, (str(start), str(entry.coord))
    assert a.coord is a_location
    assert a_location.as_tuple() == b_location.as_tuple(), (str(start), str(entry.coord))

def test_append_scroll_out_of_order():
  # an earlier coordinate appends its text in place without delimiters
  phext = Phext()
  location = Coordinate.from_string("1.1.1/1.1.1/1.1.5")
  result = phext.append_scroll(PositionedScroll(Coordinate.from_string("1.1.1/1.1.1/1.1.2"), "late"), location)
  assert result.text == "late"
  assert location == Coordinate.from_string("1.1.1/1.1.1/1.1.5")

def large_document(scrolls: int) -> str:
  # 500 scrolls per section keeps every coordinate well below the 999 cap
  parts = []
  for i in range(scrolls):
    if i > 0:
      if i % 500 == 0:
        parts.append(Phext.SECTION_BREAK)
      else:
        parts.append(Phext.SCROLL_BREAK)
    parts.append(f"scroll {i} — the quick brown fox 🦊\njumped over the lazy dog")
  return "".join(parts)

def test_explode_performance_50k_scrolls():
  phext = Phext()
  doc = large_document(50000)

  start = datetime.now()
  exploded = phext.explode(doc)
  end = datetime.now()
  elapsed_ms = int((end - start).total_seconds() * 1000)
  print("Explode-50K: " + str(elapsed_ms))

  assert len(exploded) == 50000
  assert exploded[Coordinate.from_string("1.1.1/1.1.1/1.1.1")].startswith("scroll 0 ")
  assert exploded[Coordinate.from_string("1.1.1/1.1.1/1.100.500")].startswith("scroll 49999 ")
  # the per-character implementation took ~12 us per character (~25 s here)
  assert elapsed_ms < 2000

  start = datetime.now()
  imploded = phext.implode(exploded)
  end = datetime.now()
  elapsed_ms = int((end - start).total_seconds() * 1000)
  print("Implode-50K: " + str(elapsed_ms))
  assert imploded == doc
  assert elapsed_ms < 2000

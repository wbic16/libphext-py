# Indexed access to a phext buffer.
#
# Phext.fetch answers one query with one walk over the buffer (with early
# exit), and Phext.offset rebuilds its offset phext on every call. When a
# caller asks many questions of the same buffer, both repeat the scan.
# IndexedPhext pays that scan once: it builds a coordinate ->
# (char_offset, length) index over the buffer (Phext.index_offsets) and
# keeps the buffer, so each fetch is a dict lookup plus a slice.
#
# Semantics are the library's own, by construction: the index is built by
# the same walker Phext._iter_scrolls uses, so coordinates (including the
# 999 saturation) agree with fetch/phokenize on any buffer. Where the two
# could differ is duplicate coordinates (reachable only through
# saturation): fetch returns the FIRST scroll at a coordinate and explode
# keeps the LAST. The index follows fetch, and explode() below re-walks
# the buffer so it stays identical to Phext.explode.
#
# The trade is memory: one dict entry per distinct coordinate, held for
# as long as the object lives. For a single query, Phext.fetch is the
# better tool.
#
# Offsets are character offsets into a str buffer, like the rest of this
# library: IndexedPhext is constructed from a string, not bytes.

from phext.coordinate import Coordinate
from phext.phext import Phext


class IndexedPhext:
  def __init__(self, buffer: str):
    self._phext = Phext()
    self._buffer = buffer
    # one pass: build the first-wins index and the scroll count together
    self._index = {}
    self._count = 0
    for coord, start, length in self._phext._iter_offsets(buffer):
      self._count += 1
      if coord not in self._index:
        self._index[coord] = (start, length)

  def fetch(self, coord: Coordinate) -> str:
    entry = self._index.get(coord)
    if entry is None:
      return ""
    start, length = entry
    return self._buffer[start:start + length]

  def __contains__(self, coord: Coordinate) -> bool:
    return coord in self._index

  def coordinates(self) -> list[Coordinate]:
    return list(self._index.keys())

  def keys(self) -> list[Coordinate]:
    return self.coordinates()

  def index(self) -> dict[Coordinate, tuple[int, int]]:
    # a copy, so callers cannot mutate the live index
    return dict(self._index)

  def explode(self) -> dict[Coordinate, str]:
    # Identical to Phext.explode(buffer): a fresh walk, last scroll wins
    # on duplicate coordinates. Not served from the fetch index, which
    # keeps the first scroll at a coordinate (see module note).
    return self._phext.explode(self._buffer)

  def __len__(self) -> int:
    # scroll count, as phokenize counts: duplicate coordinates (saturation)
    # count once per scroll, so this can exceed len(coordinates())
    return self._count

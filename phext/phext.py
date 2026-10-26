import copy
import re
import xxhash

from dataclasses import dataclass
from typing import Iterator, List

from phext.coordinate import COORDINATE_MAXIMUM, Coordinate
from phext.positionedScroll import PositionedScroll
from phext.range import Range

# The 9 dimension breaks, ordered from library (dimension 0) down to scroll (dimension 8).
# Note: 0x1B (escape) is deliberately not a delimiter.
_DIMENSION_BREAKS = "\x01\x1F\x1E\x1D\x1C\x1A\x19\x18\x17"
_BREAK_DIMENSION = {ch: d for d, ch in enumerate(_DIMENSION_BREAKS)}
# A maximal run of scroll text (anything but a dimension break)
_SCROLL_TEXT = re.compile("[^\x01\x17-\x1A\x1C-\x1F]+")
_NEXT_DIMENSION_BREAK = re.compile("[\x01\x17-\x1A\x1C-\x1F]")
# The first character that `isPhextBreak` accepts (dimension breaks plus line breaks)
_PHEXT_BREAK = re.compile("[\n\x01\x17-\x1A\x1C-\x1F]")
_EXPAND_TABLE = str.maketrans("\n\x17\x18\x19\x1A\x1C\x1D\x1E\x1F", "\x17\x18\x19\x1A\x1C\x1D\x1E\x1F\x01")
_CONTRACT_TABLE = str.maketrans("\x01\x1F\x1E\x1D\x1C\x1A\x19\x18\x17", "\x1F\x1E\x1D\x1C\x1A\x19\x18\x17\n")

def _apply_break(coord: list, dimension: int):
  # same as Coordinate.<dimension>Break(): saturate at 999 and reset the lower dimensions
  if coord[dimension] + 1 < COORDINATE_MAXIMUM:
    coord[dimension] += 1
  for lower in range(dimension + 1, 9):
    coord[lower] = 1

def _set_coordinate(coord: Coordinate, values):
  (coord.library, coord.shelf, coord.series,
   coord.collection, coord.volume, coord.book,
   coord.chapter, coord.section, coord.scroll) = values

@dataclass
class SubspaceBeacon:
  start: int
  end: int
  best: Coordinate

@dataclass
class Phext:
    location: Coordinate

    LIBRARY_BREAK = "\x01"
    STX_BREAK = "\x02"
    ETX_BREAK = "\x03"
    MORE_COWBELL = "\x07"
    SHELF_BREAK = "\x1F"
    SERIES_BREAK = "\x1E"
    COLLECTION_BREAK = "\x1D"
    VOLUME_BREAK = "\x1C"
    BOOK_BREAK = "\x1A"
    CHAPTER_BREAK = "\x19"
    SECTION_BREAK = "\x18"
    SCROLL_BREAK = "\x17"
    LINE_BREAK = "\x0a"
    
    def defaultCoordinate(self) -> Coordinate:
       return Coordinate(1,1,1, 1,1,1, 1,1,1)

    def __init__(self):
      location = self.defaultCoordinate()

    def fetch(self, buffer:str, coord:Coordinate) -> dict[Coordinate, str]:
      for ps in self._iter_scrolls(buffer):
        if ps.coord == coord:
          return ps.text
      return ""
    
    def isPhextBreak(self, byte:str):
      return byte == self.LINE_BREAK or \
            byte == self.SCROLL_BREAK or \
            byte == self.SECTION_BREAK or \
            byte == self.CHAPTER_BREAK or \
            byte == self.BOOK_BREAK or \
            byte == self.VOLUME_BREAK or \
            byte == self.COLLECTION_BREAK or \
            byte == self.SERIES_BREAK or \
            byte == self.SHELF_BREAK or \
            byte == self.LIBRARY_BREAK
    
    def _iter_scrolls(self, buffer:str) -> Iterator[PositionedScroll]:
      # One pass: each maximal run of non-delimiter text is a scroll at the current
      # coordinate; only the delimiters between runs are visited individually.
      walker = list(self.defaultCoordinate().as_tuple())
      position = 0
      for run in _SCROLL_TEXT.finditer(buffer):
        start = run.start()
        for index in range(position, start):
          _apply_break(walker, _BREAK_DIMENSION[buffer[index]])
        yield PositionedScroll(Coordinate(*walker), run.group())
        position = run.end()

    def phokenize(self, buffer:str) -> List[PositionedScroll]:
      return list(self._iter_scrolls(buffer))

    def _advance(self, location: Coordinate, target: Coordinate) -> str:
      # Returns the delimiters that move `location` up to `target`, updating `location` in place.
      # Equivalent to emitting one break at a time while location < target, but computed per dimension.
      here = location.as_tuple()
      there = target.as_tuple()
      if not here < there:
        return ""
      if max(there) >= COORDINATE_MAXIMUM:
        # breaks saturate at 999, so a target dimension of 1000+ is unreachable and the
        # original stepwise walk can spin forever; defer to it rather than change behavior here
        return self._advance_stepwise(location, target)
      dimension = 0
      while here[dimension] == there[dimension]:
        dimension += 1
      parts = [_DIMENSION_BREAKS[dimension] * (there[dimension] - here[dimension])]
      reached = list(here[:dimension]) + [there[dimension]] + [1] * (8 - dimension)
      for lower in range(dimension + 1, 9):
        if there[lower] < 1:
          break # location is now past target
        parts.append(_DIMENSION_BREAKS[lower] * (there[lower] - 1))
        reached[lower] = there[lower]
      _set_coordinate(location, reached)
      return "".join(parts)

    def _advance_stepwise(self, location: Coordinate, compare: Coordinate) -> str:
      output = []
      while location < compare:
        if location.library < compare.library:
          output.append(Phext.LIBRARY_BREAK)
          location.libraryBreak()
          continue
        if location.shelf < compare.shelf:
          output.append(Phext.SHELF_BREAK)
          location.shelfBreak()
          continue
        if location.series < compare.series:
          output.append(Phext.SERIES_BREAK)
          location.seriesBreak()
          continue
        if location.collection < compare.collection:
          output.append(Phext.COLLECTION_BREAK)
          location.collectionBreak()
          continue
        if location.volume < compare.volume:
          output.append(Phext.VOLUME_BREAK)
          location.volumeBreak()
          continue
        if location.book < compare.book:
          output.append(Phext.BOOK_BREAK)
          location.bookBreak()
          continue
        if location.chapter < compare.chapter:
          output.append(Phext.CHAPTER_BREAK)
          location.chapterBreak()
          continue
        if location.section < compare.section:
          output.append(Phext.SECTION_BREAK)
          location.sectionBreak()
          continue
        if location.scroll < compare.scroll:
          output.append(Phext.SCROLL_BREAK)
          location.scrollBreak()
          continue
      return "".join(output)

    def append_scroll(self, entry: PositionedScroll, location: Coordinate) -> PositionedScroll:
      output = self._advance(location, entry.coord)
      if len(entry.text) > 0:
        output += entry.text
      return PositionedScroll(location, output)

    def dephokenize(self, stack: list[PositionedScroll]) -> str:
      result = []
      location = self.defaultCoordinate()
      for ps in stack:
        result.append(self._advance(location, ps.coord))
        result.append(ps.text)
      return "".join(result)

    def normalize(self, buffer:str) -> str:
      arr = self.phokenize(buffer)
      return self.dephokenize(arr)

    def update(self, buffer:str, coord:Coordinate, scroll:str, overwrite:bool) -> str:
      items = self.phokenize(buffer)
      result = []
      next = PositionedScroll(coord, scroll)
      appended = False
      for ps in items:
        if (ps.coord > coord) and (appended == False):
          result.append(next)
          appended = True
        if (ps.coord == coord) and (appended == False):
          if overwrite == False:
            next.text = ps.text + next.text
          result.append(next)
          appended = True
          continue
        result.append(ps)
      if appended == False:
        result.append(next)
        appended = True

      serialized = self.dephokenize(result)
      return serialized
    
    def insert(self, buffer:str, coord:Coordinate, scroll:str) -> str:
      return self.update(buffer, coord, scroll, False)
    
    def replace(self, buffer:str, coord:Coordinate, scroll:str) -> str:
      return self.update(buffer, coord, scroll, True)
    
    def remove(self, buffer:str, coord:Coordinate) -> str:
      intermediate = self.update(buffer, coord, "", True)
      return self.normalize(intermediate)
    
    def range_replace(self, buffer:str, range:Range, text:str) -> str:
      stack = self.phokenize(buffer)
      result = []
      appended = False      
      for ps in stack:
        if ps.coord < range.start and len(ps.text) > 0:
          result.append(ps)
        if ps.coord >= range.start and ps.coord <= range.end:          
          if appended == False and len(text) > 0:
            next = PositionedScroll(ps.coord, text)
            result.append(next)
            appended = True
        if ps.coord > range.end and len(ps.text) > 0:
          result.append(ps)
      return self.dephokenize(result)
    
    def next_scroll(self, buffer:str, coord:Coordinate) -> List[PositionedScroll]:
      found = False
      result = []
      for ps in self._iter_scrolls(buffer):
        if found == True:
          result.append(ps)
          return result
        if ps.coord >= coord:
          result.append(ps)
          found = True
      return result
    
    def get_subspace_coordinates(self, buffer:str, target:Coordinate):
      # The walker only moves on dimension breaks, so a run of scroll text gives the same
      # answer at every character: we visit its first character and skip the rest. Once
      # the target has been passed (stage 2) nothing can change, so we stop scanning.
      walker = list(self.defaultCoordinate().as_tuple())
      goal = target.as_tuple()
      best = self.defaultCoordinate().as_tuple()
      subspace_index = 0
      start = 0
      end = 0
      stage = 0
      max = len(buffer)

      while subspace_index < max:
        here = tuple(walker)
        if stage == 0:
          if here == goal:
            stage = 1
            start = subspace_index
            best = here
          elif here < goal:
            best = here
        if here > goal: # stage < 2 here
          if stage == 0:
            start = subspace_index - 1
          end = subspace_index - 1
          stage = 2
          break

        dimension = _BREAK_DIMENSION.get(buffer[subspace_index])
        if dimension is None:
          delimiter = _NEXT_DIMENSION_BREAK.search(buffer, subspace_index)
          subspace_index = delimiter.start() if delimiter else max
          continue

        _apply_break(walker, dimension)
        if tuple(walker) > goal:
          end = subspace_index
          stage = 2
          break

        subspace_index += 1

      if stage == 1 and tuple(walker) == goal:
        end = max
        stage = 2

      if stage == 0:
        start = max
        end = max

      result = SubspaceBeacon(start, end, Coordinate(*best))
      return result
    
    def merge(self, left: str, right:str) -> str:
      tl = self.phokenize(left)
      tr = self.phokenize(right)
      tli = 0
      tri = 0
      maxtl = len(tl)
      maxtr = len(tr)
      result = []
      coord = self.defaultCoordinate()

      while True:
        have_left = tli < maxtl
        have_right = tri < maxtr
        pick_left = have_left and (have_right == False or tl[tli].coord <= tr[tri].coord)
        pick_right = have_right and (have_left == False or tr[tri].coord <= tl[tli].coord)

        if pick_left:
          next = self.append_scroll(tl[tli], coord)
          result.append(next.text)
          coord = next.coord
          tli += 1
        if pick_right:
          next = self.append_scroll(tr[tri], coord)
          result.append(next.text)
          coord = next.coord
          tri += 1

        if pick_left == False and pick_right == False:
          break

      return "".join(result)
    
    def subtract(self, left:str, right:str) -> str:
      pl = self.phokenize(left)
      pr = self.phokenize(right)
      result = []
      pri = 0
      max = len(pr)
      coord = self.defaultCoordinate()
      for item in pl:
        do_append = pri == max
        if pri < max:
          compare = pr[pri]
          if item.coord < compare.coord:
            do_append = True
          elif item.coord == compare.coord:
            pri += 1
        if do_append:
          next = self.append_scroll(item, coord)
          result.append(next.text)
          coord = next.coord
      return "".join(result)
    
    def expand(self, buffer:str) -> str:
      return buffer.translate(_EXPAND_TABLE)
    
    def contract(self, buffer:str) -> str:
      return buffer.translate(_CONTRACT_TABLE)
    
    def create_summary(self, buffer:str) -> str:
      # everything up to the first line or dimension break
      first_break = _PHEXT_BREAK.search(buffer)
      summary = buffer if first_break is None else buffer[:first_break.start()]
      if len(summary) < len(buffer):
        summary += "..."
      return summary
    
    def navmap(self, urlbase:str, buffer:str) -> str:
      stack = self.phokenize(buffer)
      result = []
      max = len(stack)
      if max > 0:
        result.append("<ul>\n")
      for ps in stack:
        urlcoord = ps.coord.urlencoded()
        summary = self.create_summary(ps.text)
        result.append(f"<li><a href=\"{urlbase}{urlcoord}\">{ps.coord} {summary}</a></li>\n")
      if max > 0:
        result.append("</ul>\n")
      return "".join(result)

    def textmap(self, buffer:str) -> str:
      result = []
      for ps in self._iter_scrolls(buffer):
        summary = self.create_summary(ps.text)
        result.append(f"* {ps.coord}: {summary}\n")
      return "".join(result)
    
    def checksum(self, buffer:str) -> str:
      hash = xxhash.xxh3_128(buffer).hexdigest()
      return hash
    
    def manifest(self, buffer:str) -> str:
      stack = self.phokenize(buffer)
      for ps in stack:
        ps.text = self.checksum(ps.text)
      result = self.dephokenize(stack)
      return result
    
    def soundex_v1(self, buffer:str) -> str:
      stack = self.phokenize(buffer)
  
      for ps in stack:
        ps.text = self.soundex_internal(ps.text)

      return self.dephokenize(stack)
    
    def soundex_internal(self, buffer:str) -> str:
      letter1 = "bpfv"
      letter2 = "cskgjqxz"
      letter3 = "dt"
      letter4 = "l"
      letter5 = "mn"
      letter6 = "r"
      
      value = 1 # 1-100
      for byte in buffer:
        if byte in letter1:
          value += 1
        if byte in letter2:
          value += 2
        if byte in letter3:
          value += 3
        if byte in letter4:
          value += 4
        if byte in letter5:
          value += 5
        if byte in letter6:
          value += 6
      return str(value % 99)
    
    def explode(self, buffer:str) -> dict[Coordinate, str]:
      parts = self.phokenize(buffer)
      hash: dict[Coordinate, str] = {}
      for ps in parts:
        hash[ps.coord] = ps.text
      return hash
    
    def implode(self, hash: dict[Coordinate, str]) -> str:
      parts = []
      for coord in hash.keys():
        parts.append(PositionedScroll(coord, hash[coord]))
      return self.dephokenize(parts)
    
    def index_phokens(self, buffer:str) -> list[PositionedScroll]:
      offset = 0
      coord = list(self.defaultCoordinate().as_tuple())
      output = []
      for ps in self._iter_scrolls(buffer):
        reference = ps.coord.as_tuple()
        # advance each dimension in turn (library first), counting one delimiter per step;
        # phokenize never yields a dimension above 999, so no step saturates
        for dimension in range(9):
          if coord[dimension] < reference[dimension]:
            offset += reference[dimension] - coord[dimension]
            coord[dimension] = reference[dimension]
            for lower in range(dimension + 1, 9):
              coord[lower] = 1
        text = str(offset)
        output.append(PositionedScroll(Coordinate(*coord), text))
        offset += len(ps.text)

      return output

    def index(self, buffer:str) -> str:
      output = self.index_phokens(buffer)
      return self.dephokenize(output)
    
    def offset(self, buffer:str, coord:Coordinate) -> int:
      output = self.index_phokens(buffer)
      best = self.defaultCoordinate()
      fetch_coord = coord
      matched = False
      for ps in output:
        if ps.coord <= coord:
          best = copy.deepcopy(ps.coord)
        if ps.coord == coord:
          matched = True
      if matched == False:
        fetch_coord = best
      index = self.dephokenize(output)
      return int(self.fetch(index, fetch_coord))
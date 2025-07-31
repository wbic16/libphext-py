import copy

from dataclasses import dataclass
from typing import List

from libphext.coordinate import Coordinate
from libphext.positionedScroll import PositionedScroll
from libphext.range import Range

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
      phokens = self.phokenize(buffer)
      for ps in phokens:
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
    
    def phokenize(self, buffer:str) -> List[PositionedScroll]:
      result = []
      location = self.defaultCoordinate()
      next = self.defaultCoordinate()
      temp = ""
      # decoded = buffer.decode("utf-8")      
      for ch in buffer:
        dimension_break = False
        if ch == self.LIBRARY_BREAK:
          next.libraryBreak()
          dimension_break = True
        if ch == self.SHELF_BREAK:
          next.shelfBreak()
          dimension_break = True
        if ch == self.SERIES_BREAK:
          next.seriesBreak()
          dimension_break = True
        if ch == self.COLLECTION_BREAK:
          next.collectionBreak()
          dimension_break = True
        if ch == self.VOLUME_BREAK:
          next.volumeBreak()
          dimension_break = True
        if ch == self.BOOK_BREAK:
          next.bookBreak()
          dimension_break = True
        if ch == self.CHAPTER_BREAK:
          next.chapterBreak()
          dimension_break = True
        if ch == self.SECTION_BREAK:
          next.sectionBreak()
          dimension_break = True
        if ch == self.SCROLL_BREAK:
          next.scrollBreak()
          dimension_break = True
        
        if dimension_break == True:
          if len(temp) > 0:
            item = PositionedScroll(location, temp)
            result.append(item)
            temp = ""
        else:
          temp += str(ch)
          location = copy.deepcopy(next)

      if len(temp) > 0:
        item = PositionedScroll(location, temp)
        result.append(item)

      return result
    
    def append_scroll(self, entry: PositionedScroll, location: Coordinate) -> PositionedScroll:
      output = ""
      compare = entry.coord
      while location < entry.coord:
        if location.library < compare.library:
          output += Phext.LIBRARY_BREAK
          location.libraryBreak()
          continue
        if location.shelf < compare.shelf:
          output += Phext.SHELF_BREAK
          location.shelfBreak()
          continue
        if location.series < compare.series:
          output += Phext.SERIES_BREAK
          location.seriesBreak()
          continue
        if location.collection < compare.collection:
          output += Phext.COLLECTION_BREAK
          location.collectionBreak()
          continue
        if location.volume < compare.volume:
          output += Phext.VOLUME_BREAK
          location.volumeBreak()
          continue
        if location.book < compare.book:
          output += Phext.BOOK_BREAK
          location.bookBreak()
          continue
        if location.chapter < compare.chapter:
          output += Phext.CHAPTER_BREAK
          location.chapterBreak()
          continue
        if location.section < compare.section:
          output += Phext.SECTION_BREAK
          location.sectionBreak()
          continue
        if location.scroll < compare.scroll:
          output += Phext.SCROLL_BREAK
          location.scrollBreak()
          continue
      if len(entry.text) > 0:
        output += entry.text
      result = PositionedScroll(location, output)
      return result

    def dephokenize(self, phokens: list[PositionedScroll]) -> str:
      result = ""
      location = self.defaultCoordinate()
      for ps in phokens:
        next = self.append_scroll(ps, location)
        result += next.text
        location = next.coord
      return result

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
      stack = self.phokenize(buffer)
      found = False
      result = []
      for ps in stack:
        if found == True:
          result.append(ps)
          return result
        if ps.coord >= coord:
          result.append(ps)
          found = True
      return result
    
    def get_subspace_coordinates(self, buffer:str, target:Coordinate):
      walker = self.defaultCoordinate()
      best = self.defaultCoordinate()
      subspace_index = 0
      start = 0
      end = 0
      stage = 0
      max = len(buffer)

      while subspace_index < max:
        next = buffer[subspace_index]
        compare = next

        if stage == 0:
          if walker == target:
            stage = 1
            start = subspace_index
            best = copy.deepcopy(walker)
          if walker < target:
            best = copy.deepcopy(walker)
        if stage < 2 and walker > target:
          if stage == 0:
            start = subspace_index - 1
          end = subspace_index - 1;
          stage = 2    

        if self.isPhextBreak(next):
          if compare == self.SCROLL_BREAK:
            walker.scrollBreak()
          if compare == self.SECTION_BREAK:
            walker.sectionBreak()
          if compare == self.CHAPTER_BREAK:
            walker.chapterBreak()
          if compare == self.BOOK_BREAK:
            walker.bookBreak()
          if compare == self.VOLUME_BREAK:
            walker.volumeBreak()
          if compare == self.COLLECTION_BREAK:
            walker.collectionBreak()
          if compare == self.SERIES_BREAK:
            walker.seriesBreak()
          if compare == self.SHELF_BREAK:
            walker.shelfBreak()
          if compare == self.LIBRARY_BREAK:
            walker.libraryBreak()
        
        if stage < 2 and walker > target:
          end = subspace_index
          stage = 2
        
        subspace_index += 1

      if stage == 1 and walker == target:
        end = max
        stage = 2

      if stage == 0:
        start = max
        end = max

      result = SubspaceBeacon(start, end, best)
      return result
    
    def merge(self, left: str, right:str) -> str:
      tl = self.phokenize(left)
      tr = self.phokenize(right)
      tli = 0
      tri = 0
      maxtl = len(tl)
      maxtr = len(tr)
      result = ""
      coord = self.defaultCoordinate()

      while True:
        have_left = tli < maxtl
        have_right = tri < maxtr
        pick_left = have_left and (have_right == False or tl[tli].coord <= tr[tri].coord)
        pick_right = have_right and (have_left == False or tr[tri].coord <= tl[tli].coord)

        if pick_left:
          next = self.append_scroll(tl[tli], coord)
          result += next.text
          coord = next.coord
          tli += 1
        if pick_right:
          next = self.append_scroll(tr[tri], coord)
          result += next.text
          coord = next.coord
          tri += 1

        if pick_left == False and pick_right == False:
          break

      return result
    
    def subtract(self, left:str, right:str) -> str:
      pl = self.phokenize(left)
      pr = self.phokenize(right)
      result = ""
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
          result += next.text
          coord = next.coord
      return result
    
    def expand(self, buffer:str) -> str:
      result = ""
      for char in buffer:
        if char == self.LINE_BREAK:
          result += self.SCROLL_BREAK
        elif char == self.SCROLL_BREAK:
          result += self.SECTION_BREAK
        elif char == self.SECTION_BREAK:
          result += self.CHAPTER_BREAK
        elif char == self.CHAPTER_BREAK:
          result += self.BOOK_BREAK
        elif char == self.BOOK_BREAK:
          result += self.VOLUME_BREAK
        elif char == self.VOLUME_BREAK:
          result += self.COLLECTION_BREAK
        elif char == self.COLLECTION_BREAK:
          result += self.SERIES_BREAK
        elif char == self.SERIES_BREAK:
          result += self.SHELF_BREAK
        elif char == self.SHELF_BREAK:
          result += self.LIBRARY_BREAK
        else:
          result += char
      return result
import copy

from dataclasses import dataclass
from typing import List

from libphext.coordinate import Coordinate
from libphext.positionedScroll import PositionedScroll

@dataclass
class Phext:
    ready: bool
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
      ready = True

    def fetch(self, buffer, coord) -> dict[Coordinate, str]:
      phokens = self.phokenize(buffer)
      for ps in phokens:
        if ps.coord == coord:
          return ps.text
      return ""
    
    def phokenize(self, buffer) -> List[PositionedScroll]:
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
    
    def insert(self, buffer, coord, scroll):
      items = self.phokenize(buffer)
      result = []
      next = PositionedScroll(coord, scroll)
      for ps in items:
        if ps.coord > coord:
          result.append(next)
        if ps.coord == coord:
          result.append(next)
          continue
        result.append(ps)
      
      # todo add dephokenize and re-serialize
      return result
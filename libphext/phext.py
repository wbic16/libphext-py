import copy

from dataclasses import dataclass
from typing import List

from libphext.coordinate import Coordinate
from libphext.positionedScroll import PositionedScroll

LIBRARY_BREAK = "\x01"
SHELF_BREAK = "\x1F"
SERIES_BREAK = "\x1E"
COLLECTION_BREAK = "\x1D"
VOLUME_BREAK = "\x1C"
BOOK_BREAK = "\x1A"
CHAPTER_BREAK = "\x19"
SECTION_BREAK = "\x18"
SCROLL_BREAK = "\x17"

@dataclass
class Phext:
    ready: bool
    location: Coordinate
    
    def defaultCoordinate(self) -> Coordinate:
       return Coordinate(1,1,1, 1,1,1, 1,1,1)

    def __init__(self):
      location = self.defaultCoordinate()
      ready = True

    def fetch(self, buffer, coord) -> dict[Coordinate, str]:
       result = {}
       return result
    
    def phokenize(self, buffer) -> List[PositionedScroll]:
      result = []
      location = self.defaultCoordinate()
      next = self.defaultCoordinate()
      temp = ""
      # decoded = buffer.decode("utf-8")      
      for ch in buffer:
        dimension_break = False
        if ch == LIBRARY_BREAK:
          next.libraryBreak()
          dimension_break = True
        if ch == SHELF_BREAK:
          next.shelfBreak()
          dimension_break = True
        if ch == SERIES_BREAK:
          next.seriesBreak()
          dimension_break = True
        if ch == COLLECTION_BREAK:
          next.collectionBreak()
          dimension_break = True
        if ch == VOLUME_BREAK:
          next.volumeBreak()
          dimension_break = True
        if ch == BOOK_BREAK:
          next.bookBreak()
          dimension_break = True
        if ch == CHAPTER_BREAK:
          next.chapterBreak()
          dimension_break = True
        if ch == SECTION_BREAK:
          next.sectionBreak()
          dimension_break = True
        if ch == SCROLL_BREAK:
          next.scrollBreak()
          dimension_break = True
        
        if dimension_break == True:
          if len(temp) > 0:
            print("Dumping " + temp + " @ " + str(location))
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
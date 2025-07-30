import copy

from dataclasses import dataclass
from typing import List

from libphext.coordinate import Coordinate
from libphext.positionedScroll import PositionedScroll

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

    def update(self, buffer:str, coord:Coordinate, scroll:str, overwrite:bool):
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
    
    def insert(self, buffer:str, coord:Coordinate, scroll:str):
      return self.update(buffer, coord, scroll, False)
    
    def replace(self, buffer, coord, scroll):
      return self.update(buffer, coord, scroll, True)
    
    def remove(self, buffer, coord):
      intermediate = self.update(buffer, coord, "", True)
      return self.normalize(intermediate)
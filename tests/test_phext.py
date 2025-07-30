from libphext.coordinate import Coordinate
from libphext.positionedScroll import PositionedScroll
from libphext.phext import Phext
import pytest

def test_dead_reckoning():
  test = "random text in 1.1.1/1.1.1/1.1.1 that we can skip past"
  test += Phext.LIBRARY_BREAK
  test += "everything in here is at 2.1.1/1.1.1/1.1.1"
  test += Phext.SCROLL_BREAK
  test += "and now we're at 2.1.1/1.1.1/1.1.2"
  test += Phext.SCROLL_BREAK
  test += "moving on up to 2.1.1/1.1.1/1.1.3"
  test += Phext.BOOK_BREAK
  test += "and now over to 2.1.1/1.1.2/1.1.1"
  test += Phext.SHELF_BREAK
  test += "woot, up to 2.2.1/1.1.1/1.1.1"
  test += Phext.LIBRARY_BREAK
  test += "here we are at 3.1.1/1.1.1.1.1"
  test += Phext.LIBRARY_BREAK # 4.1.1/1.1.1/1.1.1
  test += Phext.LIBRARY_BREAK # 5.1.1/1.1.1/1.1.1
  test += "getting closer to our target now 5.1.1/1.1.1/1.1.1"
  test += Phext.SHELF_BREAK # 5.2.1
  test += Phext.SHELF_BREAK # 5.3.1
  test += Phext.SHELF_BREAK # 5.4.1
  test += Phext.SHELF_BREAK # 5.5.1
  test += Phext.SERIES_BREAK # 5.5.2
  test += Phext.SERIES_BREAK # 5.5.3
  test += Phext.SERIES_BREAK # 5.5.4
  test += Phext.SERIES_BREAK # 5.5.5
  test += "here we go! 5.5.5/1.1.1/1.1.1"
  test += Phext.COLLECTION_BREAK # 5.5.5/2.1.1/1.1.1
  test += Phext.COLLECTION_BREAK # 5.5.5/3.1.1/1.1.1
  test += Phext.COLLECTION_BREAK # 5.5.5/4.1.1/1.1.1
  test += Phext.BOOK_BREAK # 5.5.5/4.1.2/1.1.1
  test += Phext.BOOK_BREAK # 5.5.5/4.1.3/1.1.1
  test += Phext.BOOK_BREAK # 5.5.5/4.1.4/1.1.1
  test += "this test appears at 5.5.5/4.1.4/1.1.1"
  test += Phext.VOLUME_BREAK # 5.5.5/4.2.1/1.1.1
  test += Phext.VOLUME_BREAK # 5.5.5/4.3.1/1.1.1
  test += Phext.VOLUME_BREAK # 5.5.5/4.4.1/1.1.1
  test += Phext.VOLUME_BREAK # 5.5.5/4.5.1/1.1.1
  test += Phext.VOLUME_BREAK # 5.5.5/4.6.1/1.1.1
  test += Phext.CHAPTER_BREAK # 5.5.5/4.6.1/2.1.1
  test += Phext.CHAPTER_BREAK # 5.5.5/4.6.1/3.1.1
  test += Phext.CHAPTER_BREAK # 5.5.5/4.6.1/4.1.1
  test += Phext.CHAPTER_BREAK # 5.5.5/4.6.1/5.1.1
  test += Phext.BOOK_BREAK # 5.5.5/4.6.2/1.1.1
  test += Phext.BOOK_BREAK # 5.5.5/4.6.3/1.1.1
  test += Phext.BOOK_BREAK # 5.5.5/4.6.4/1.1.1
  test += Phext.BOOK_BREAK # 5.5.5/4.6.5/1.1.1
  test += Phext.BOOK_BREAK # 5.5.5/4.6.6/1.1.1
  test += Phext.BOOK_BREAK # 5.5.5/4.6.7/1.1.1
  test += Phext.CHAPTER_BREAK # 5.5.5/4.6.7/2.1.1
  test += Phext.CHAPTER_BREAK # 5.5.5/4.6.7/3.1.1
  test += Phext.CHAPTER_BREAK # 5.5.5/4.6.7/4.1.1
  test += Phext.CHAPTER_BREAK # 5.5.5/4.6.7/5.1.1
  test += Phext.SCROLL_BREAK # 5.5.5/4.6.7/5.1.2
  test += Phext.SCROLL_BREAK # 5.5.5/4.6.7/5.1.3
  test += Phext.SCROLL_BREAK # 5.5.5/4.6.7/5.1.4
  test += Phext.SCROLL_BREAK # 5.5.5/4.6.7/5.1.5
  test += Phext.SCROLL_BREAK # 5.5.5/4.6.7/5.1.6
  test += "here's a test at 5.5.5/4.6.7/5.1.6"
  test += Phext.SCROLL_BREAK  # 5.5.5/4.6.7/5.1.7
  test += Phext.CHAPTER_BREAK # 5.5.5/4.6.7/6.1.1
  test += Phext.CHAPTER_BREAK # 5.5.5/4.6.7/7.1.1
  test += Phext.CHAPTER_BREAK # 5.5.5/4.6.7/8.1.1
  test += Phext.CHAPTER_BREAK # 5.5.5/4.6.7/9.1.1
  test += Phext.SECTION_BREAK # 5.5.5/4.6.7/9.2.1
  test += Phext.SECTION_BREAK # 5.5.5/4.6.7/9.3.1
  test += Phext.SECTION_BREAK # 5.5.5/4.6.7/9.4.1
  test += Phext.SECTION_BREAK # 5.5.5/4.6.7/9.5.1
  test += Phext.SCROLL_BREAK  # 5.5.5/4.6.7/9.5.2
  test += Phext.SCROLL_BREAK  # 5.5.5/4.6.7/9.5.3
  test += Phext.SCROLL_BREAK  # 5.5.5/4.6.7/9.5.4
  test += Phext.SCROLL_BREAK  # 5.5.5/4.6.7/9.5.5
  test += Phext.SCROLL_BREAK  # 5.5.5/4.6.7/9.5.6
  test += Phext.SCROLL_BREAK  # 5.5.5/4.6.7/9.5.7
  test += Phext.SCROLL_BREAK  # 5.5.5/4.6.7/9.5.8
  test += Phext.SCROLL_BREAK  # 5.5.5/4.6.7/9.5.9
  test += "Expected Test Pattern Alpha Whisky Tango Foxtrot"
  coord = Coordinate.from_string("5.5.5/4.6.7/9.5.9")

  phext = Phext()
  result = phext.fetch(test, coord)
  assert result == "Expected Test Pattern Alpha Whisky Tango Foxtrot"

  coord2 = Coordinate.from_string("5.5.5/4.6.7/5.1.6")
  result2 = phext.fetch(test, coord2)
  assert result2 == "here's a test at 5.5.5/4.6.7/5.1.6"

def test_line_break():
  assert Phext.LINE_BREAK == '\n'

def test_more_cowbell():
  assert Phext.MORE_COWBELL == '\x07'

def test_coordinate_based_insert():
  phext = Phext()
  doc = "aaa\x01bbb\x17ccc"

  test1 = phext.phokenize(doc)
  precheck = [
    PositionedScroll(Coordinate(1,1,1, 1,1,1, 1,1,1), "aaa"),
    PositionedScroll(Coordinate(2,1,1, 1,1,1, 1,1,1), "bbb"),
    PositionedScroll(Coordinate(2,1,1, 1,1,1, 1,1,2), "ccc")
  ]
  assert test1 == precheck
  test2 = phext.dephokenize(test1)
  assert test2 == doc

  coord1 = Coordinate.from_string("2.1.1/1.1.1/1.1.3")
  update1 = phext.insert(doc, coord1, "ddd")
  assert update1 == "aaa\x01bbb\x17ccc\x17ddd"
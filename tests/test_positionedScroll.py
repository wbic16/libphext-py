from libphext.coordinate import Coordinate
from libphext.positionedScroll import PositionedScroll
import pytest

# Upstream tests covered by this module:
# test_scrolls, test_sections, test_chapters
# test_books, test_volumes, test_collections
# test_series, test_shelves, test_libraries

def test_scroll_interface():
  coord = Coordinate.from_string("1.2.3/4.5.6/7.8.9")
  text = "Hello World"
  ps = PositionedScroll(coord, text)
  assert ps.coord == coord
  assert ps.text == text

def test_positioned_scrolls():
  coord1 = Coordinate.from_string("1.1.1/1.1.1/1.1.1")
  coord2 = Coordinate.from_string("1.1.1/1.1.1/1.1.2")
  coord3 = Coordinate.from_string("1.1.1/1.1.1/1.1.3")
  text1 = "Scroll #1"
  text2 = "Scroll #2"
  text3 = "Scroll #3"
  data = [
     PositionedScroll(coord1, text1),
     PositionedScroll(coord2, text2),
     PositionedScroll(coord3, text3)
  ]
  assert data[0].coord == coord1
  assert data[1].coord == coord2
  assert data[2].coord == coord3
  assert data[0].text == text1
  assert data[1].text == text2
  assert data[2].text == text3

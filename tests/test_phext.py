from libphext.coordinate import Coordinate
from libphext.positionedScroll import PositionedScroll
from libphext.phext import Phext
import pytest

# Upstream tests covered by this module:
# test_dead_reckoning

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
  root = phext.defaultCoordinate()

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

  # append 'eee' after 'ddd'
  coord2 = Coordinate.from_string("2.1.1/1.1.1/1.1.4")
  update2 = phext.insert(update1, coord2, "eee")
  assert update2 == "aaa\x01bbb\x17ccc\x17ddd\x17eee"

  # append 'fff' after 'eee'
  coord3 = Coordinate.from_string("2.1.1/1.1.1/1.2.1")
  update3 = phext.insert(update2, coord3, "fff")
  assert update3 == "aaa\x01bbb\x17ccc\x17ddd\x17eee\x18fff"

  # append 'ggg' after 'fff'
  coord4 = Coordinate.from_string("2.1.1/1.1.1/1.2.2")
  update4 = phext.insert(update3, coord4, "ggg")
  assert update4 == "aaa\x01bbb\x17ccc\x17ddd\x17eee\x18fff\x17ggg"

  # append 'hhh' after 'ggg'
  coord5 = Coordinate.from_string("2.1.1/1.1.1/2.1.1")
  update5 = phext.insert(update4, coord5, "hhh")
  assert update5 == "aaa\x01bbb\x17ccc\x17ddd\x17eee\x18fff\x17ggg\x19hhh"

  # append 'iii' after 'eee'
  coord6 = Coordinate.from_string("2.1.1/1.1.1/1.1.5")
  update6 = phext.insert(update5, coord6, "iii")
  assert update6 == "aaa\x01bbb\x17ccc\x17ddd\x17eee\x17iii\x18fff\x17ggg\x19hhh"

  # extend 1.1.1/1.1.1/1.1.1 with '---AAA'
  update7 = phext.insert(update6, root, "---AAA")
  assert update7 == "aaa---AAA\x01bbb\x17ccc\x17ddd\x17eee\x17iii\x18fff\x17ggg\x19hhh"

  # extend 2.1.1/1.1.1/1.1.1 with '---BBB'
  coord8 = Coordinate.from_string("2.1.1/1.1.1/1.1.1")
  update8 = phext.insert(update7, coord8, "---BBB")
  assert update8 == "aaa---AAA\x01bbb---BBB\x17ccc\x17ddd\x17eee\x17iii\x18fff\x17ggg\x19hhh"

  # extend 2.1.1/1.1.1/1.1.2 with '---CCC'
  coord9 = Coordinate.from_string("2.1.1/1.1.1/1.1.2")
  update9 = phext.insert(update8, coord9, "---CCC")
  assert update9 == "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd\x17eee\x17iii\x18fff\x17ggg\x19hhh"

  # extend 2.1.1/1.1.1/1.1.3 with '---DDD'
  coord10 = Coordinate.from_string("2.1.1/1.1.1/1.1.3")
  update10 = phext.insert(update9, coord10, "---DDD")
  assert update10 == "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee\x17iii\x18fff\x17ggg\x19hhh"

  # extend 2.1.1/1.1.1/1.1.4 with '---EEE'
  coord11 = Coordinate.from_string("2.1.1/1.1.1/1.1.4")
  update11 = phext.insert(update10, coord11, "---EEE")
  assert update11 == "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee---EEE\x17iii\x18fff\x17ggg\x19hhh"

  # extend 2.1.1/1.1.1/1.1.5 with '---III'
  coord12 = Coordinate.from_string("2.1.1/1.1.1/1.1.5")
  update12 = phext.insert(update11, coord12, "---III")
  assert update12 == "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee---EEE\x17iii---III\x18fff\x17ggg\x19hhh"

  # extend 2.1.1/1.1.1/1.2.1 with '---FFF'
  coord13 = Coordinate.from_string("2.1.1/1.1.1/1.2.1")
  update13 = phext.insert(update12, coord13, "---FFF")
  assert update13 == "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee---EEE\x17iii---III\x18fff---FFF\x17ggg\x19hhh"

  # extend 2.1.1/1.1.1/1.2.2 with '---GGG'
  coord14 = Coordinate.from_string("2.1.1/1.1.1/1.2.2")
  update14 = phext.insert(update13, coord14, "---GGG")
  assert update14 == "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee---EEE\x17iii---III\x18fff---FFF\x17ggg---GGG\x19hhh"

  # extend 2.1.1/1.1.1/2.1.1 with '---HHH'
  coord15 = Coordinate.from_string("2.1.1/1.1.1/2.1.1")
  update15 = phext.insert(update14, coord15, "---HHH")
  assert update15 == "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee---EEE\x17iii---III\x18fff---FFF\x17ggg---GGG\x19hhh---HHH"

  # insert 'jjj' at 2.1.1/1.1.2/1.1.1
  coord16 = Coordinate.from_string("2.1.1/1.1.2/1.1.1")
  update16 = phext.insert(update15, coord16, "jjj")
  assert update16 == "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee---EEE\x17iii---III\x18fff---FFF\x17ggg---GGG\x19hhh---HHH\x1Ajjj"

  # insert 'kkk' at 2.1.1/1.2.1/1.1.1
  coord17 = Coordinate.from_string("2.1.1/1.2.1/1.1.1")
  update17 = phext.insert(update16, coord17, "kkk")
  assert update17 == "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee---EEE\x17iii---III\x18fff---FFF\x17ggg---GGG\x19hhh---HHH\x1Ajjj\x1Ckkk"

  # insert 'lll' at 2.1.1/2.1.1/1.1.1
  coord18 = Coordinate.from_string("2.1.1/2.1.1/1.1.1")
  update18 = phext.insert(update17, coord18, "lll")
  assert update18 == "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee---EEE\x17iii---III\x18fff---FFF\x17ggg---GGG\x19hhh---HHH\x1Ajjj\x1Ckkk\x1Dlll"

  # insert 'mmm' at 2.1.2/1.1.1/1.1.1
  coord19 = Coordinate.from_string("2.1.2/1.1.1/1.1.1")
  update19 = phext.insert(update18, coord19, "mmm")
  assert update19 == "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee---EEE\x17iii---III\x18fff---FFF\x17ggg---GGG\x19hhh---HHH\x1Ajjj\x1Ckkk\x1Dlll\x1Emmm"

  # insert 'nnn' at 2.2.1/1.1.1/1.1.1
  coord20 = Coordinate.from_string("2.2.1/1.1.1/1.1.1")
  update20 = phext.insert(update19, coord20, "nnn")
  assert update20 == "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee---EEE\x17iii---III\x18fff---FFF\x17ggg---GGG\x19hhh---HHH\x1Ajjj\x1Ckkk\x1Dlll\x1Emmm\x1Fnnn"

  # insert 'ooo' at 3.1.1/1.1.1/1.1.1
  coord21 = Coordinate.from_string("3.1.1/1.1.1/1.1.1")
  update21 = phext.insert(update20, coord21, "ooo")
  assert update21 == "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee---EEE\x17iii---III\x18fff---FFF\x17ggg---GGG\x19hhh---HHH\x1Ajjj\x1Ckkk\x1Dlll\x1Emmm\x1Fnnn\x01ooo"

def test_coordinate_based_replace():
  assert False

def test_coordinate_based_remove():
  assert False

def test_range_based_replace():
  assert False

def test_next_scroll():
  assert False

def test_last_empty_scroll():
  assert False

def test_merge():
  assert False

def test_subtract():
  assert False

def test_normalize():
  assert False

def test_expand():
  assert False

def test_contract():
  assert False

def test_fs_read_write():
  assert False

def test_replace_create():
  assert False

def test_summary():
  assert False

def test_navmap():
  assert False

def test_textmap():
  assert False

def test_larger_coordinates():
  assert False

def test_phext_index():
  assert False

def test_scroll_manifest():
  assert False

def test_phext_soundex_v1():
  assert False

def test_insert_performance_2k_scrolls():
  assert False

def test_insert_performance_medium_scrolls():
  assert False

def test_hash_support():
  assert False

def test_subspace_filter():
  assert False

def test_macrophext():
  # maybe add \x02 and \x03 support for very large phexts...?
  assert False

def test_phext_breaks():
  phext = Phext()
  assert phext.isPhextBreak("\n")
  assert phext.isPhextBreak("\x01")
  assert phext.isPhextBreak("\x17")
  assert phext.isPhextBreak("\x18")
  assert phext.isPhextBreak("\x19")
  assert phext.isPhextBreak("\x1a")
  assert phext.isPhextBreak("\x1c")
  assert phext.isPhextBreak("\x1d")
  assert phext.isPhextBreak("\x1e")
  assert phext.isPhextBreak("\x1f")
  assert phext.isPhextBreak(phext.LINE_BREAK)
  assert phext.isPhextBreak(phext.LIBRARY_BREAK)
  assert phext.isPhextBreak(phext.SHELF_BREAK)
  assert phext.isPhextBreak(phext.SERIES_BREAK)
  assert phext.isPhextBreak(phext.COLLECTION_BREAK)
  assert phext.isPhextBreak(phext.VOLUME_BREAK)
  assert phext.isPhextBreak(phext.BOOK_BREAK)
  assert phext.isPhextBreak(phext.CHAPTER_BREAK)
  assert phext.isPhextBreak(phext.SECTION_BREAK)
  assert phext.isPhextBreak(phext.SCROLL_BREAK)

def test_normalize():
  phext = Phext()
  doc1 = "\x17Scroll two\x18\x18\x18\x18"
  update1 = phext.normalize(doc1)
  assert update1 == "\x17Scroll two"
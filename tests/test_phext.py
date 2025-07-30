from libphext.coordinate import Coordinate
from libphext.positionedScroll import PositionedScroll
from libphext.phext import Phext
import pytest

# Upstream tests covered by this module:
# test_dead_reckoning
# test_line_break
# test_more_cowbell
# test_coordinate_based_insert
# test_coordinate_based_replace
# test_coordinate_based_remove
# test_range_based_replace
# test_next_scroll
# test_last_empty_scroll
# test_merge
# test_subtract
# test_normalize
# test_expand
# test_contract
# test_fs_read_write
# test_replace_create
# test_summary
# test_navmap
# test_textmap
# test_larger_coordinates
# test_phext_index
# test_scroll_manifest
# test_phext_soundex_v1
# test_insert_performance_2k_scrolls
# test_insert_performance_medium_scrolls
# test_hash_support
# test_subspace_filter

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
  phext = Phext()
  
  # replace 'AAA' with 'aaa'
  coord0 = Coordinate.from_string("1.1.1/1.1.1/1.1.1")
  update0 = phext.replace("AAA\x17bbb\x18ccc\x19ddd\x1Aeee\x1Cfff\x1Dggg\x1Ehhh\x1Fiii\x01jjj", coord0, "aaa")
  assert update0 == "aaa\x17bbb\x18ccc\x19ddd\x1Aeee\x1Cfff\x1Dggg\x1Ehhh\x1Fiii\x01jjj"

  # replace 'bbb' with '222'
  coord1 = Coordinate.from_string("1.1.1/1.1.1/1.1.2")
  update1 = phext.replace(update0, coord1, "222")
  assert update1 == "aaa\x17222\x18ccc\x19ddd\x1Aeee\x1Cfff\x1Dggg\x1Ehhh\x1Fiii\x01jjj"

  # replace 'ccc' with '3-'
  coord2 = Coordinate.from_string("1.1.1/1.1.1/1.2.1")
  update2 = phext.replace(update1, coord2, "3-")
  assert update2 == "aaa\x17222\x183-\x19ddd\x1Aeee\x1Cfff\x1Dggg\x1Ehhh\x1Fiii\x01jjj"

  # replace 'ddd' with 'delta'
  coord3 = Coordinate.from_string("1.1.1/1.1.1/2.1.1")
  update3 = phext.replace(update2, coord3, "delta")
  assert update3 == "aaa\x17222\x183-\x19delta\x1Aeee\x1Cfff\x1Dggg\x1Ehhh\x1Fiii\x01jjj"

  # replace 'eee' with 'a bridge just close enough'
  coord4 = Coordinate.from_string("1.1.1/1.1.2/1.1.1")
  update4 = phext.replace(update3, coord4, "a bridge just close enough")
  assert update4 == "aaa\x17222\x183-\x19delta\x1Aa bridge just close enough\x1Cfff\x1Dggg\x1Ehhh\x1Fiii\x01jjj"

  # replace 'fff' with 'nifty'
  coord5 = Coordinate.from_string("1.1.1/1.2.1/1.1.1")
  update5 = phext.replace(update4, coord5, "nifty")
  assert update5 == "aaa\x17222\x183-\x19delta\x1Aa bridge just close enough\x1Cnifty\x1Dggg\x1Ehhh\x1Fiii\x01jjj"

  # replace 'ggg' with 'G8'
  coord6 = Coordinate.from_string("1.1.1/2.1.1/1.1.1")
  update6 = phext.replace(update5, coord6, "G8")
  assert update6 == "aaa\x17222\x183-\x19delta\x1Aa bridge just close enough\x1Cnifty\x1DG8\x1Ehhh\x1Fiii\x01jjj"

  # replace 'hhh' with 'Hello World'
  coord7 = Coordinate.from_string("1.1.2/1.1.1/1.1.1")
  update7 = phext.replace(update6, coord7, "Hello World")
  assert update7 == "aaa\x17222\x183-\x19delta\x1Aa bridge just close enough\x1Cnifty\x1DG8\x1EHello World\x1Fiii\x01jjj"

  # replace 'iii' with '_o_'
  coord8 = Coordinate.from_string("1.2.1/1.1.1/1.1.1")
  update8 = phext.replace(update7, coord8, "_o_")
  assert update8 == "aaa\x17222\x183-\x19delta\x1Aa bridge just close enough\x1Cnifty\x1DG8\x1EHello World\x1F_o_\x01jjj"

  # replace 'jjj' with '/win'
  coord9 = Coordinate.from_string("2.1.1/1.1.1/1.1.1")
  update9 = phext.replace(update8, coord9, "/win")
  assert update9 == "aaa\x17222\x183-\x19delta\x1Aa bridge just close enough\x1Cnifty\x1DG8\x1EHello World\x1F_o_\x01/win"

  # the api editor has trouble with this input...
  coord_r0a = Coordinate.from_string("2.1.1/1.1.1/1.1.5")
  update_r0a = phext.replace("hello world\x17scroll two", coord_r0a, "2.1.1-1.1.1-1.1.5")
  assert update_r0a == "hello world\x17scroll two\x01\x17\x17\x17\x172.1.1-1.1.1-1.1.5"

  # regression from api testing
  # unit tests don't hit the failure I'm seeing through rocket...hmm - seems to be related to using library breaks
  coord_r1a = Coordinate.from_string("1.1.1/1.1.1/1.1.1")
  update_r1a = phext.replace("", coord_r1a, "aaa")
  assert update_r1a == "aaa"

  coord_r1b = Coordinate.from_string("1.1.1/1.1.1/1.1.2")
  update_r1b = phext.replace(update_r1a, coord_r1b, "bbb")
  assert update_r1b == "aaa\x17bbb"

  coord_r1c = Coordinate.from_string("1.2.3/4.5.6/7.8.9")
  update_r1c = phext.replace(update_r1b, coord_r1c, "ccc")
  assert update_r1c == "aaa\x17bbb\x1F\x1E\x1E\x1D\x1D\x1D\x1C\x1C\x1C\x1C\x1A\x1A\x1A\x1A\x1A\x19\x19\x19\x19\x19\x19\x18\x18\x18\x18\x18\x18\x18\x17\x17\x17\x17\x17\x17\x17\x17ccc"

  coord_r1d = Coordinate.from_string("1.4.4/2.8.8/4.16.16")
  update_r1d = phext.replace(update_r1c, coord_r1d, "ddd")
  assert update_r1d == "aaa\x17bbb\x1F\x1E\x1E\x1D\x1D\x1D\x1C\x1C\x1C\x1C\x1A\x1A\x1A\x1A\x1A\x19\x19\x19\x19\x19\x19\x18\x18\x18\x18\x18\x18\x18\x17\x17\x17\x17\x17\x17\x17\x17ccc\x1F\x1F\x1E\x1E\x1E\x1D\x1C\x1C\x1C\x1C\x1C\x1C\x1C\x1A\x1A\x1A\x1A\x1A\x1A\x1A\x19\x19\x19\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17ddd"

  coord_regression_1 = Coordinate.from_string("11.12.13/14.15.16/17.18.19")
  update_regression_1 = phext.replace(update_r1d, coord_regression_1, "eee")
  assert update_regression_1 == "aaa\x17bbb\x1F\x1E\x1E\x1D\x1D\x1D\x1C\x1C\x1C\x1C\x1A\x1A\x1A\x1A\x1A\x19\x19\x19\x19\x19\x19\x18\x18\x18\x18\x18\x18\x18\x17\x17\x17\x17\x17\x17\x17\x17ccc\x1F\x1F\x1E\x1E\x1E\x1D\x1C\x1C\x1C\x1C\x1C\x1C\x1C\x1A\x1A\x1A\x1A\x1A\x1A\x1A\x19\x19\x19\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17ddd" + \
  "\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01" + \
  "\x1F\x1F\x1F\x1F\x1F\x1F\x1F\x1F\x1F\x1F\x1F" + \
  "\x1E\x1E\x1E\x1E\x1E\x1E\x1E\x1E\x1E\x1E\x1E\x1E" + \
  "\x1D\x1D\x1D\x1D\x1D\x1D\x1D\x1D\x1D\x1D\x1D\x1D\x1D" + \
  "\x1C\x1C\x1C\x1C\x1C\x1C\x1C\x1C\x1C\x1C\x1C\x1C\x1C\x1C" + \
  "\x1A\x1A\x1A\x1A\x1A\x1A\x1A\x1A\x1A\x1A\x1A\x1A\x1A\x1A\x1A" + \
  "\x19\x19\x19\x19\x19\x19\x19\x19\x19\x19\x19\x19\x19\x19\x19\x19" + \
  "\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18\x18" + \
  "\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17\x17" + \
  "eee"

  # finally found the bugger!
  coord_regression_2 = Coordinate.from_string("1.1.1/1.1.2/1.1.2")
  regression_2_baseline = "1.1.11.1.21.1.31.1.41.2.11.2.21.2.31.2.4" + \
    "2.1.13.1.14.1.12/1.1.12/1.1.32.1/1.1.12.1.1/1.1.12/1.1.1/1.1.12.1/1.1.1/1.1.12.1.1/1.1.1/1.1.1"
  update_regression_2 = phext.replace(regression_2_baseline, coord_regression_2, "new content")
  assert update_regression_2, "1.1.1\x171.1.2\x171.1.3\x171.1.4\x181.2.1\x171.2.2\x171.2.3\x171.2.4\x192.1.1\x193.1.1\x194.1.1\x1a2/1.1.1\x17new content\x172/1.1.3\x1c2.1/1.1.1\x1d2.1.1/1.1.1\x1e2/1.1.1/1.1.1\x1f2.1/1.1.1/1.1.1\x012.1.1/1.1.1/1.1.1"

def test_coordinate_based_remove():
  phext = Phext()

  # replace 'aaa' with ''
  coord1 = Coordinate.from_string("1.1.1/1.1.1/1.1.1")
  update1 = phext.remove("aaa\x17bbb\x18ccc\x19ddd\x1Aeee\x1Cfff\x1Dggg\x1Ehhh\x1Fiii\x01jjj", coord1)
  assert update1 == "\x17bbb\x18ccc\x19ddd\x1Aeee\x1Cfff\x1Dggg\x1Ehhh\x1Fiii\x01jjj"

  # replace 'bbb' with ''
  coord2 = Coordinate.from_string("1.1.1/1.1.1/1.1.2")
  update2 = phext.remove(update1, coord2)
  assert update2 == "\x18ccc\x19ddd\x1Aeee\x1Cfff\x1Dggg\x1Ehhh\x1Fiii\x01jjj"

  # replace 'ccc' with ''
  coord3 = Coordinate.from_string("1.1.1/1.1.1/1.2.1")
  update3 = phext.remove(update2, coord3)
  assert update3 == "\x19ddd\x1Aeee\x1Cfff\x1Dggg\x1Ehhh\x1Fiii\x01jjj"

  # replace 'ddd' with ''
  coord4 = Coordinate.from_string("1.1.1/1.1.1/2.1.1")
  update4 = phext.remove(update3, coord4)
  assert update4 == "\x1Aeee\x1Cfff\x1Dggg\x1Ehhh\x1Fiii\x01jjj"

  # replace 'eee' with ''
  coord5 = Coordinate.from_string("1.1.1/1.1.2/1.1.1")
  update5 = phext.remove(update4, coord5)
  assert update5 == "\x1Cfff\x1Dggg\x1Ehhh\x1Fiii\x01jjj"

  # replace 'fff' with ''
  coord6 = Coordinate.from_string("1.1.1/1.2.1/1.1.1")
  update6 = phext.remove(update5, coord6)
  assert update6 == "\x1Dggg\x1Ehhh\x1Fiii\x01jjj"

  # replace 'ggg' with ''
  coord7 = Coordinate.from_string("1.1.1/2.1.1/1.1.1")
  update7 = phext.remove(update6, coord7)
  assert update7 == "\x1Ehhh\x1Fiii\x01jjj"

  # replace 'hhh' with ''
  coord8 = Coordinate.from_string("1.1.2/1.1.1/1.1.1")
  update8 = phext.remove(update7, coord8)
  assert update8 == "\x1Fiii\x01jjj"

  # replace 'iii' with ''
  coord9 = Coordinate.from_string("1.2.1/1.1.1/1.1.1")
  update9 = phext.remove(update8, coord9)
  assert update9 == "\x01jjj"

  # replace 'jjj' with ''
  coord10 = Coordinate.from_string("2.1.1/1.1.1/1.1.1")
  update10 = phext.remove(update9, coord10)
  assert update10 == ""

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
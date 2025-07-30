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

# todo: finish merging coordinate_based_insert tests
"""
// append 'eee' after 'ddd'
        let coord2 = phext::to_coordinate("2.1.1/1.1.1/1.1.4");
        let update2 = phext::insert(update1, coord2, "eee");
        assert_eq!(update2, "aaa\x01bbb\x17ccc\x17ddd\x17eee");

        // append 'fff' after 'eee'
        let coord3 = phext::to_coordinate("2.1.1/1.1.1/1.2.1");
        let update3 = phext::insert(update2, coord3, "fff");
        assert_eq!(update3, "aaa\x01bbb\x17ccc\x17ddd\x17eee\x18fff");

        // append 'ggg' after 'fff'
        let coord4 = phext::to_coordinate("2.1.1/1.1.1/1.2.2");
        let update4 = phext::insert(update3, coord4, "ggg");
        assert_eq!(update4, "aaa\x01bbb\x17ccc\x17ddd\x17eee\x18fff\x17ggg");

        // append 'hhh' after 'ggg'
        let coord5 = phext::to_coordinate("2.1.1/1.1.1/2.1.1");
        let update5 = phext::insert(update4, coord5, "hhh");
        assert_eq!(update5, "aaa\x01bbb\x17ccc\x17ddd\x17eee\x18fff\x17ggg\x19hhh");

        // append 'iii' after 'eee'
        let coord6 = phext::to_coordinate("2.1.1/1.1.1/1.1.5");
        let update6 = phext::insert(update5, coord6, "iii");
        assert_eq!(update6, "aaa\x01bbb\x17ccc\x17ddd\x17eee\x17iii\x18fff\x17ggg\x19hhh");

        // extend 1.1.1/1.1.1/1.1.1 with '---AAA'
        let update7 = phext::insert(update6, root, "---AAA");
        assert_eq!(update7, "aaa---AAA\x01bbb\x17ccc\x17ddd\x17eee\x17iii\x18fff\x17ggg\x19hhh");

        // extend 2.1.1/1.1.1/1.1.1 with '---BBB'
        let coord8 = phext::to_coordinate("2.1.1/1.1.1/1.1.1");
        let update8 = phext::insert(update7, coord8, "---BBB");
        assert_eq!(update8, "aaa---AAA\x01bbb---BBB\x17ccc\x17ddd\x17eee\x17iii\x18fff\x17ggg\x19hhh");

        // extend 2.1.1/1.1.1/1.1.2 with '---CCC'
        let coord9 = phext::to_coordinate("2.1.1/1.1.1/1.1.2");
        let update9 = phext::insert(update8, coord9, "---CCC");
        assert_eq!(update9, "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd\x17eee\x17iii\x18fff\x17ggg\x19hhh");

        // extend 2.1.1/1.1.1/1.1.3 with '---DDD'
        let coord10 = phext::to_coordinate("2.1.1/1.1.1/1.1.3");
        let update10 = phext::insert(update9, coord10, "---DDD");
        assert_eq!(update10, "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee\x17iii\x18fff\x17ggg\x19hhh");

        // extend 2.1.1/1.1.1/1.1.4 with '---EEE'
        let coord11 = phext::to_coordinate("2.1.1/1.1.1/1.1.4");
        let update11 = phext::insert(update10, coord11, "---EEE");
        assert_eq!(update11, "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee---EEE\x17iii\x18fff\x17ggg\x19hhh");

        // extend 2.1.1/1.1.1/1.1.5 with '---III'
        let coord12 = phext::to_coordinate("2.1.1/1.1.1/1.1.5");
        let update12 = phext::insert(update11, coord12, "---III");
        assert_eq!(update12, "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee---EEE\x17iii---III\x18fff\x17ggg\x19hhh");

        // extend 2.1.1/1.1.1/1.2.1 with '---FFF'
        let coord13 = phext::to_coordinate("2.1.1/1.1.1/1.2.1");
        let update13 = phext::insert(update12, coord13, "---FFF");
        assert_eq!(update13, "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee---EEE\x17iii---III\x18fff---FFF\x17ggg\x19hhh");

        // extend 2.1.1/1.1.1/1.2.2 with '---GGG'
        let coord14 = phext::to_coordinate("2.1.1/1.1.1/1.2.2");
        let update14 = phext::insert(update13, coord14, "---GGG");
        assert_eq!(update14, "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee---EEE\x17iii---III\x18fff---FFF\x17ggg---GGG\x19hhh");

        // extend 2.1.1/1.1.1/2.1.1 with '---HHH'
        let coord15 = phext::to_coordinate("2.1.1/1.1.1/2.1.1");
        let update15 = phext::insert(update14, coord15, "---HHH");
        assert_eq!(update15, "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee---EEE\x17iii---III\x18fff---FFF\x17ggg---GGG\x19hhh---HHH");

        // insert 'jjj' at 2.1.1/1.1.2/1.1.1
        let coord16 = phext::to_coordinate("2.1.1/1.1.2/1.1.1");
        let update16 = phext::insert(update15, coord16, "jjj");
        assert_eq!(update16, "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee---EEE\x17iii---III\x18fff---FFF\x17ggg---GGG\x19hhh---HHH\x1Ajjj");

        // insert 'kkk' at 2.1.1/1.2.1/1.1.1
        let coord17 = phext::to_coordinate("2.1.1/1.2.1/1.1.1");
        let update17 = phext::insert(update16, coord17, "kkk");
        assert_eq!(update17, "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee---EEE\x17iii---III\x18fff---FFF\x17ggg---GGG\x19hhh---HHH\x1Ajjj\x1Ckkk");

        // insert 'lll' at 2.1.1/2.1.1/1.1.1
        let coord18 = phext::to_coordinate("2.1.1/2.1.1/1.1.1");
        let update18 = phext::insert(update17, coord18, "lll");
        assert_eq!(update18, "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee---EEE\x17iii---III\x18fff---FFF\x17ggg---GGG\x19hhh---HHH\x1Ajjj\x1Ckkk\x1Dlll");

        // insert 'mmm' at 2.1.2/1.1.1/1.1.1
        let coord19 = phext::to_coordinate("2.1.2/1.1.1/1.1.1");
        let update19 = phext::insert(update18, coord19, "mmm");
        assert_eq!(update19, "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee---EEE\x17iii---III\x18fff---FFF\x17ggg---GGG\x19hhh---HHH\x1Ajjj\x1Ckkk\x1Dlll\x1Emmm");

        // insert 'nnn' at 2.2.1/1.1.1/1.1.1
        let coord20 = phext::to_coordinate("2.2.1/1.1.1/1.1.1");
        let update20 = phext::insert(update19, coord20, "nnn");
        assert_eq!(update20, "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee---EEE\x17iii---III\x18fff---FFF\x17ggg---GGG\x19hhh---HHH\x1Ajjj\x1Ckkk\x1Dlll\x1Emmm\x1Fnnn");

        // insert 'ooo' at 3.1.1/1.1.1/1.1.1
        let coord21 = phext::to_coordinate("3.1.1/1.1.1/1.1.1");
        let update21 = phext::insert(update20, coord21, "ooo");
        assert_eq!(update21, "aaa---AAA\x01bbb---BBB\x17ccc---CCC\x17ddd---DDD\x17eee---EEE\x17iii---III\x18fff---FFF\x17ggg---GGG\x19hhh---HHH\x1Ajjj\x1Ckkk\x1Dlll\x1Emmm\x1Fnnn\x01ooo");
"""

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
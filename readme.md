# Phext

Welcome to the Pythonic port of phext.

This port is a downstream artifact that tracks the Rust-based implementation of Phext. See https://github.com/wbic16/libphext-rs for more details.

## Getting Started

To use phext in your Python project, simply add `phext` as a dependency.

```pip install phext```

Refer to the `tests` folder for usage information.

```
import phext
from phext.coordinate import Coordinate
from phext.phext import Phext
phext = Phext()
test = "Hello\x17World"
coord = Coordinate.from_string("1.1.1/1.1.1/1.1.1")
scroll = phext.fetch(test, coord)
scrolls = phext.explode(test)
coord2 = Coordinate(1,1,1, 1,1,1, 1,1,2)
print(scroll + ", " + scrolls[coord2])
```

## Development

The project uses [uv](https://docs.astral.sh/uv/). From the repository root:

```bash
uv sync
```

This creates `.venv` with phext installed from this checkout (editable) and the `dev` dependency group (pytest).

### Test

```bash
uv run pytest
```

pytest comes from the `dev` group, so the tests run in the project's environment against this checkout. `pyproject.toml` also puts the checkout on pytest's path, so a pytest from somewhere else still tests this code rather than a `phext` it finds installed.

To time the core operations on a real file:

```bash
uv run python test/bench.py path/to/file.phext
```

It reports explode, implode, textmap, index, and fetch (of the last scroll). Name operations after the file to run only those, for example `explode fetch`.

### Build

1. Set the new version in both `pyproject.toml` and `phext/__init__.py`.
2. Build into an empty folder. `dist/` holds older builds that are checked into git, and `uv publish` would try to upload those too. Delete `release-dist` first if it is left over from a previous release.

   ```bash
   uv build --out-dir release-dist
   ```

3. Check the package metadata, then import the wheel in a throwaway environment (use the version you just built):

   ```bash
   uvx twine check release-dist/*
   ```

   ```bash
   uv run --isolated --no-project --with release-dist/phext-0.3.2-py3-none-any.whl python -c "import phext; print(phext.__version__)"
   ```

### Publish

```bash
uv publish release-dist/*
```

This needs a PyPI API token for the `phext` project: set `UV_PUBLISH_TOKEN`, or pass `--token`. To rehearse on TestPyPI first (it uses a separate account and token):

```bash
uv publish --publish-url https://test.pypi.org/legacy/ release-dist/*
```

## Data Types

* `Coordinate`: A 9-tuple of the form library.shelf.series/collection.volume.book/chapter.section.scroll. Represents the location of a given scroll of text within a larger phext file.
* `Phext`: The main entrypoint to interacting with phexts.
  * `fetch(buffer, coordinate)`: Fetches a scroll of text from the given serialized phext buffer
  * `phokenize(buffer)`: Extracts a list of positioned scrolls from the given phext
  * `append_scroll(entry, location)`: Emits the delimiters and text required to insert the positioned scroll, entry, into a phext stream (starting from the given location).
  * `dephokenize(stack)`: Serializes a stack of positioned scrolls
  * `normalize(str)`: Eliminates empty scrolls from a phext buffer
  * `update(buffer, coord, scroll, overwrite)`: Supports insert and update operations - places the scroll of text at the given coordinate, taking the current state of the buffer into account
  * `insert(buffer, coord, scroll)`: Inserts text at the end of the scroll located at coord within the buffer
  * `replace(buffer, coord, scroll)`: Replaces the text located at coord within the buffer
  * `remove(buffer, coord)`: Removes the contents of the scroll located at coord within the buffer
  * `range_replace(buffer, range, text)`: Removes scrolls located within the given range, without shifting content outside of the range - this differs from libphext-rs by design - a pair of missing methods needs to be added to resolve the conflict
  * `next_scroll(buffer, coord)`: Selects the next scroll after the given coordinate
  * `get_subspace_coordinates(buffer, target)`: Retrieves the subspace offsets cooresponding to the given target coordinate within the buffer
  * `merge(left, right)`: Zipper merges two phexts
  * `subtract(left, right)`: Removes the scrolls from left that are present in right (as measured by coordinate matching)
  * `expand(buffer)`: Dimensional increment for each phext break found in the buffer
  * `contract(buffer)`: Dimensional decrement for each phext break found in the buffer
  * `create_summary(buffer)`: Creates a one-line summary of a given scroll
  * `navmap(urlbase, buffer)`: Creates an HTML navigation map of the given buffer
  * `textmap(buffer)`: Creates a text-based navigation map of the given buffer
  * `checksum(buffer)`: Computes an xxh3_128 hash of a given scroll
  * `manifest(buffer)`: Computes a hierarchical hash of the given phext
  * `soundex_v1(buffer)`: Computes a hierarchical soundex of the given phext
  * `soundex_internal(buffer)`: Computes a low-level soundex of a given scroll
  * `explode(buffer)`: Explodes a phext into a dictionary of Coordinate -> str
  * `implode(hash)`: Implodes a dictionary of Coordinate -> str back into a phext
  * `index_phokens(buffer)`: Computes the offsets of each scroll in the given phext
  * `index(buffer)`: Computes a hierarchical map of scroll offsets in phext format
  * `offset(buffer, coord)`: Computes the offset of a specific scroll in the given phext
* `PositionedScroll`: A pair of `Coordinate` and a scroll of text.
* `Range`: A pair of coordinates denoting an inclusive range across subspace

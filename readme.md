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

## Indexed access

`fetch` walks the buffer for each query (stopping early at a match), and
`offset` rebuilds its index on every call. If you ask many questions of
one buffer, build the index once instead:

```
from phext.indexed import IndexedPhext
indexed = IndexedPhext(buffer)   # one pass over the buffer
scroll = indexed.fetch(coord)    # dictionary lookup + slice per query
```

The price is one full pass at construction plus one dictionary entry per
distinct coordinate, held while the object lives. For a single query,
plain `fetch` is the better tool: it pays no build cost and stops at the
first match. Offsets are character offsets into a string buffer, like
the rest of the library.

## Dense graphs

Dense graphs: phext is sparse by design. Coordinate components are
unbounded, but a fully-populated dense graph contains the product of its
dimensions' extents in scrolls — a dense block spanning 1000 in each of
9 dimensions implies 10^27 scrolls. Materializing, exploding, or indexing
such a graph costs memory proportional to its populated scroll count.
The old 999 cap never protected against this (999^9 was already
unreachable); sparsity does. Keep graphs sparse.

## Development

Every step below is one script in `scripts/`; the script is the procedure, and the underlying commands are listed so nothing has to be guessed. Run everything from the repository root.

**Prerequisites**

1. Python 3.10 or newer (`requires-python` in `pyproject.toml`).
2. [uv](https://docs.astral.sh/uv/) is the recommended tool. If uv is not installed, the scripts fall back automatically: they use an existing `.venv`, or create one with `python3 -m venv` and install this checkout with its dev extras via pip. No other setup is needed in either case.

### Test

1. Run:

   ```bash
   scripts/test.sh
   ```

2. What it does, in order: with uv — `uv sync` (creates `.venv` with phext installed from this checkout, editable, plus the `dev` dependency group with pytest; the first sync also refreshes `uv.lock` to the version in `pyproject.toml`), then `uv run pytest`. Without uv — `.venv/bin/python -m pytest` if `.venv` exists, otherwise it creates `.venv` and runs `pip install -e ".[dev]"` first.
3. Expected result: the full suite passes (80 tests at version 0.4.0). The script's exit code is pytest's exit code. `pyproject.toml` puts this checkout on pytest's path, so the tests always run against this code, never against a `phext` installed elsewhere.

To time the core operations on a real file (optional):

```bash
uv run python test/bench.py path/to/file.phext
```

It reports explode, implode, textmap, index, and fetch (of the last scroll). Name operations after the file to run only those, for example `explode fetch`.

### Build

1. Set the new version number in **both** `pyproject.toml` (`version = "..."`) and `phext/__init__.py` (`__version__ = "..."`). The build refuses to run if the two disagree.
2. Run:

   ```bash
   scripts/build.sh
   ```

3. What it does, in order: reads both version strings and fails loudly if they differ; deletes `release-dist/` so only this build can be published from it; builds with `uv build --out-dir release-dist` (fallback: `python -m build --outdir release-dist`, installing the `build` package into `.venv` if needed); lists the artifacts.
4. Expected result: exactly two artifacts, `release-dist/phext-<version>.tar.gz` (sdist) and `release-dist/phext-<version>-py3-none-any.whl` (wheel). Note: `dist/` in this repository holds old builds that are checked into git — never publish from `dist/`.
5. Optional checks before publishing: `uvx twine check release-dist/*`, and import the wheel in a throwaway environment (substitute the version you just built):

   ```bash
   uv run --isolated --no-project --with release-dist/phext-0.4.0-py3-none-any.whl python -c "import phext; print(phext.__version__)"
   ```

### Publish

1. Get a PyPI API token for the `phext` project. Credentials come from the environment or your keyring — never from a file in this repository.
2. Rehearse (no upload happens):

   ```bash
   scripts/publish.sh
   ```

   It runs `scripts/test.sh`, then `scripts/build.sh`, then prints the exact artifacts and version it would publish, and stops. If the tests fail, it stops there.
3. Publish for real:

   ```bash
   UV_PUBLISH_TOKEN=<token> PUBLISH_CONFIRM=1 scripts/publish.sh
   ```

   With uv it runs `uv publish release-dist/*`; without uv it runs `python -m twine upload release-dist/*` (set `TWINE_USERNAME=__token__` and `TWINE_PASSWORD=<token>` instead). Without `PUBLISH_CONFIRM=1` the script never uploads anything.
4. To rehearse against TestPyPI instead (separate account and token), run the publish command directly: `uv publish --publish-url https://test.pypi.org/legacy/ release-dist/*`.

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
  * `index_offsets(buffer)`: One pass building a dictionary of Coordinate -> (char_offset, length) for every scroll in the buffer
  * `indexed(buffer)`: Builds an `IndexedPhext` over the buffer (see Indexed access, below)
* `IndexedPhext` (in `phext/indexed.py`): A buffer plus its offset index, built once. `fetch(coord)` answers from the index (a dictionary lookup plus a slice, `""` if absent), `coordinates()` lists the indexed coordinates, `explode()` returns the same dictionary as `Phext.explode`, and `len()` counts the buffer's scrolls.
* `PositionedScroll`: A pair of `Coordinate` and a scroll of text.
* `Range`: A pair of coordinates denoting an inclusive range across subspace

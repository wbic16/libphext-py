# Phext

Welcome to the Pythonic port of phext.

This port is a downstream artifact that tracks the Rust-based implementation of Phext. See https://github.com/wbic16/phext-rs for more details.

## Tests

## Getting Started

To use phext in your Python project, simply add `phext` as a dependency.

```pip install phext```

Refer to the `tests` folder for usage information.

```import phext
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
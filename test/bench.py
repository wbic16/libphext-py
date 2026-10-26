# Benchmark the core phext operations on a given file.
#
# usage: python test/bench.py <file.phext> [op ...]
#   ops: explode implode textmap index fetch (default: all)
#
# fetch targets the last scroll in the document (the worst case for a linear scan).
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from phext.phext import Phext

OPS = ["explode", "implode", "textmap", "index", "fetch"]

def timed(label, fn):
  start = time.perf_counter()
  result = fn()
  elapsed = time.perf_counter() - start
  print(f"  {label:<8} {elapsed * 1000:12.1f} ms", flush=True)
  return result

def main():
  if len(sys.argv) < 2:
    print("usage: python test/bench.py <file.phext> [explode|implode|textmap|index|fetch ...]")
    sys.exit(1)
  path = sys.argv[1]
  ops = sys.argv[2:] or OPS
  # newline="" keeps \r\n intact so the buffer matches the file exactly
  with open(path, "r", encoding="utf-8", newline="") as f:
    buffer = f.read()
  phext = Phext()
  print(f"{path}: {len(buffer)} chars", flush=True)

  exploded = None
  if "explode" in ops:
    exploded = timed("explode", lambda: phext.explode(buffer))
    print(f"  ({len(exploded)} scrolls)", flush=True)
  if "implode" in ops:
    if exploded is None:
      exploded = phext.explode(buffer)
    timed("implode", lambda: phext.implode(exploded))
  if "textmap" in ops:
    timed("textmap", lambda: phext.textmap(buffer))
  if "index" in ops:
    timed("index", lambda: phext.index(buffer))
  if "fetch" in ops:
    if exploded is None:
      exploded = phext.explode(buffer)
    target = max(exploded.keys()) if exploded else phext.defaultCoordinate()
    timed("fetch", lambda: phext.fetch(buffer, target))

if __name__ == "__main__":
  main()

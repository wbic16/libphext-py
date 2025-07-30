from dataclasses import dataclass
from libphext.coordinate import Coordinate

@dataclass
class Range:
  start: Coordinate
  end: Coordinate
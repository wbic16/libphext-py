from dataclasses import dataclass
from libphext.coordinate import Coordinate

@dataclass
class Phext:
    ready: bool
    location: Coordinate
    
    def __init__(self):
      location = Coordinate(1,1,1, 1,1,1, 1,1,1)
      ready = True

    def fetch(self, buffer, coord) -> dict[Coordinate, str]:
       result = {}

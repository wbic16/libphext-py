from dataclasses import dataclass

@dataclass
class Coordinate:
    library: int
    shelf: int
    series: int
    collection: int
    volume: int
    book: int
    chapter: int
    section: int
    scroll: int

    @classmethod
    def from_string(ignored, coord_str: str):
        try:
            parts = coord_str.strip().split("/")
            if len(parts) != 3:
                raise ValueError("Coordinate must conform to Phext Standard Addressing")

            nums = []
            for part in parts:
                nums.extend(int(x) for x in part.split("."))

            if len(nums) != 9:
                raise ValueError("Coordinate must have exactly 9 numeric parts")

            if any(n < 1 or n > 999 for n in nums):
                raise ValueError("All coordinate values must be between 1 and 999")

            return Coordinate(nums[0], nums[1], nums[2], nums[3], nums[4], nums[5], nums[6], nums[7], nums[8])

        except Exception as e:
            raise ValueError(f"Invalid coordinate string: {coord_str} {e}") from e

    def __init__(self, lb, sf, sr, cn, vm, bk, ch, sn, sc):
        self.library = int(lb)
        self.shelf = int(sf)
        self.series = int(sr)
        self.collection = int(cn)
        self.volume = int(vm)
        self.book = int(bk)
        self.chapter = int(ch)
        self.section = int(sn)
        self.scroll = int(sc)

    def __str__(self) -> str:
        return f"{self.library}.{self.shelf}.{self.series}/" \
               f"{self.collection}.{self.volume}.{self.book}/" \
               f"{self.chapter}.{self.section}.{self.scroll}"
    
    def urlencoded(self) -> str:
        return f"{self.library}.{self.shelf}.{self.series};" \
               f"{self.collection}.{self.volume}.{self.book};" \
               f"{self.chapter}.{self.section}.{self.scroll}"
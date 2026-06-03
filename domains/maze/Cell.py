from dataclasses import dataclass

@dataclass
class Cell:
    row: int
    col: int

    top: bool = True
    right: bool = True
    bottom: bool = True
    left: bool = True
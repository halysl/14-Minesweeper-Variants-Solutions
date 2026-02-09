
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

@dataclass
class Cell:
    row: int
    col: int
    x: int # Screen X
    y: int # Screen Y
    w: int
    h: int
    state: str = "unknown" # unknown, safe, flag, bomb, 0-8

@dataclass
class Board:
    top_left: Tuple[int, int]
    width: int
    height: int
    rows: int
    cols: int
    cells: List[List[Cell]] = field(default_factory=list)

@dataclass
class GameState:
    total_mines: int = 0
    remaining_mines: int = 0
    remaining_cells: int = 0
    board: Optional[Board] = None
    
    # Raw header text if OCR is flaky
    header_raw_text: str = "" 

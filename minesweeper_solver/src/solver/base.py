
from abc import ABC, abstractmethod
from typing import List, Tuple, Dict

class Solver(ABC):
    @abstractmethod
    def solve(self, board_state: List[List[str]]) -> List[Dict]:
        """
        Analyzes the board state and returns a list of actions.
        Args:
            board_state: 2D array of cell strings (e.g. '1', 'F', ' ')
        Returns:
            List of actions: [{'type': 'click'|'flag', 'row': r, 'col': c}]
        """
        pass

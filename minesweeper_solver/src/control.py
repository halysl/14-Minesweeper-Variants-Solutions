
import logging
import pyautogui
import time
from typing import Tuple

logger = logging.getLogger(__name__)

class MouseController:
    def __init__(self, offset_x: int = 0, offset_y: int = 0):
        self.offset_x = offset_x
        self.offset_y = offset_y
        
        # Safety settings
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.05

    def set_offset(self, x: int, y: int):
        self.offset_x = x
        self.offset_y = y

    def move_to(self, x: int, y: int):
        """Moves mouse to relative coordinates."""
        abs_x = self.offset_x + x
        abs_y = self.offset_y + y
        pyautogui.moveTo(abs_x, abs_y)

    def left_click(self, x: int, y: int):
        """Moves and left clicks."""
        self.move_to(x, y)
        pyautogui.click()

    def right_click(self, x: int, y: int):
        """Moves and right clicks."""
        self.move_to(x, y)
        pyautogui.rightClick()

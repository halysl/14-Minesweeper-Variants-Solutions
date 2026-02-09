
import logging
import mss
import numpy as np
import cv2
import pygetwindow as gw
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class WindowCapturer:
    def __init__(self, window_title: str):
        self.window_title = window_title
        self.sct = mss.mss()
        self.window_rect = None

    def find_window(self) -> bool:
        """Finds the window and updates its position."""
        try:
            windows = gw.getWindowsWithTitle(self.window_title)
            if not windows:
                logger.warning(f"Window '{self.window_title}' not found.")
                return False
            
            # Use the first matching window
            window = windows[0]
            if window.isActive: 
                pass # Already active
            else:
                try:
                    window.activate()
                except Exception as e:
                    logger.warning(f"Could not activate window: {e}")

            # Define capture region
            # Adjust these offsets if necessary (e.g., to exclude title bar)
            self.window_rect = {
                "top": window.top,
                "left": window.left,
                "width": window.width,
                "height": window.height
            }
            logger.info(f"Window found at: {self.window_rect}")
            return True
        except Exception as e:
            logger.error(f"Error finding window: {e}")
            return False

    def capture(self) -> Optional[np.ndarray]:
        """Captures the window content and returns it as a BGR numpy array (OpenCV format)."""
        if not self.window_rect:
            if not self.find_window():
                return None

        try:
            # mss captures screenshot. 'monitor' takes a dict with top, left, width, height.
            screenshot = self.sct.grab(self.window_rect)
            
            # Convert to numpy array
            img = np.array(screenshot)
            
            # MSS returns BGRA, converting to BGR for OpenCV
            frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            return frame
        except Exception as e:
            logger.error(f"Capture failed: {e}")
            self.window_rect = None # Reset in case window moved/closed
            return None

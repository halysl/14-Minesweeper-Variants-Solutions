
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
            import sys
            if sys.platform == 'darwin':
                return self._find_window_macos()
            else:
                return self._find_window_generic()
            return True
        except Exception as e:
            logger.error(f"Error finding window: {e}")
            return False

    def _find_window_macos(self) -> bool:
        try:
            import Quartz
            # Get all windows
            windows = Quartz.CGWindowListCopyWindowInfo(
                Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements,
                Quartz.kCGNullWindowID
            )
            
            for win in windows:
                # Check title (kCGWindowName) and OwnerName
                win_name = win.get('kCGWindowName', '')
                owner_name = win.get('kCGWindowOwnerName', '')
                
                # Cleanup names for comparison (handle None)
                win_name = str(win_name) if win_name else ""
                owner_name = str(owner_name) if owner_name else ""

                if self.window_title in win_name or self.window_title in owner_name:
                    # ... match found code ...
                    bounds = win.get('kCGWindowBounds')
                    # ... 
                    # (Existing logic)
                    if bounds:
                        self.window_rect = {
                            "top": int(bounds['Y']),
                            "left": int(bounds['X']),
                            "width": int(bounds['Width']),
                            "height": int(bounds['Height'])
                        }
                        logger.info(f"Window found (macOS): {win_name} | Rect: {self.window_rect}")
                        return True
                
                # Debug logging for inspection
                # logger.debug(f"Checked: Name='{win_name}', Owner='{owner_name}'")
            
            logger.warning(f"Window '{self.window_title}' not found in Quartz window list.")
            return False
            
        except ImportError:
            logger.error("pyscreeze/pyobjc not installed correctly for macOS window capture.")
            return False

    def _find_window_generic(self) -> bool:
        try:
            windows = gw.getWindowsWithTitle(self.window_title)
            if not windows:
                logger.warning(f"Window '{self.window_title}' not found.")
                return False
            
            # Use the first matching window
            window = windows[0]
            if not window.isActive:
                try:
                    window.activate()
                except Exception as e:
                    logger.warning(f"Could not activate window: {e}")

            self.window_rect = {
                "top": window.top,
                "left": window.left,
                "width": window.width,
                "height": window.height
            }
            logger.info(f"Window found: {self.window_rect}")
            return True
        except AttributeError:
             # Fallback for platforms where pygetwindow might be partial
             logger.error("pygetwindow interface mismatch.")
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

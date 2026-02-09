
import unittest
import os
import sys
import numpy as np
import cv2
import logging

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from capture import WindowCapturer

# Configure logging to show info during tests
logging.basicConfig(level=logging.INFO)

class TestWindowCapture(unittest.TestCase):
    def setUp(self):
        # Use the specific window title known to exist
        self.window_title = "14 Minesweeper Variants"
        self.capturer = WindowCapturer(self.window_title)

    def test_find_window(self):
        """Test if the window can be found."""
        found = self.capturer.find_window()
        if not found:
            print(f"\nWARNING: Window '{self.window_title}' not found. Please ensure it is open.")
        self.assertTrue(found, f"Window '{self.window_title}' should be found")
        self.assertIsNotNone(self.capturer.window_rect)

    def test_capture_image(self):
        """Test if the window can be captured and saved."""
        found = self.capturer.find_window()
        if not found:
            self.skipTest("Window not found, skipping capture test.")

        image = self.capturer.capture()
        self.assertIsNotNone(image, "Captured image should not be None")
        self.IsInstance(image, np.ndarray)
        
        # Check image properties
        h, w, c = image.shape
        self.assertGreater(h, 0)
        self.assertGreater(w, 0)
        self.assertEqual(c, 3, "Image should have 3 channels (BGR)")

        # Save for manual verification
        output_filename = "capture_unit_test.png"
        cv2.imwrite(output_filename, image)
        self.assertTrue(os.path.exists(output_filename))
        print(f"\nSaved capture to {os.path.abspath(output_filename)}")

    def IsInstance(self, obj, cls):
        self.assertTrue(isinstance(obj, cls), f"Object {obj} is not instance of {cls}")

if __name__ == '__main__':
    unittest.main()

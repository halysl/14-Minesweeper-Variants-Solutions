
import sys
import os
import cv2
import pygetwindow as gw

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from capture import WindowCapturer

def list_windows():
    print("--- Available Windows ---")
    titles = gw.getAllTitles()
    for t in titles:
        if t.strip():
            print(f"[{t}]")
    print("-------------------------")

def test_capture(target_title):
    print(f"Attempting to capture window: '{target_title}'")
    cap = WindowCapturer(target_title)
    
    if cap.find_window():
        print("✅ Window found!")
        img = cap.capture()
        if img is not None:
            print(f"✅ Capture successful. Image shape: {img.shape}")
            filename = "capture_test.png"
            cv2.imwrite(filename, img)
            print(f"📸 Saved screenshot to {filename}")
        else:
            print("❌ Capture failed (returned None).")
    else:
        print(f"❌ Window '{target_title}' not found.")
        list_windows()

if __name__ == "__main__":
    target = "14 Minesweeper Variants"
    if len(sys.argv) > 1:
        target = sys.argv[1]
    
    test_capture(target)

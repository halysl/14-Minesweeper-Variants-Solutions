
import sys
import os
import cv2
import logging

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from recognition import GridDetector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_process_frame(image_path):
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return

    print(f"Loading image: {image_path}")
    img = cv2.imread(image_path)
    
    detector = GridDetector()
    state = detector.process_frame(img)
    
    print("\n--- Game State ---")
    print(f"Header Text: '{state.header_raw_text}'")
    print(f"Total Mines: {state.total_mines}")
    print(f"Remaining Mines: {state.remaining_mines}")
    print(f"Remaining Cells: {state.remaining_cells}")
    
    if state.board:
        print(f"Board: {state.board.cols}x{state.board.rows}")
        print(f"Top Left: {state.board.top_left}")
        
        # Verify cell data
        # Check a few cells
        if state.board.cells:
             # Check corner
             c00 = state.board.cells[0][0]
             print(f"Cell [0,0]: {c00}")
    else:
        print("Board not detected.")

if __name__ == "__main__":
    img_path = "capture_test.png"
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
    
    test_process_frame(img_path)

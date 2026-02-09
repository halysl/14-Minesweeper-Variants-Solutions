
import sys
import os
import cv2
import logging

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from recognition import GridDetector

# Configure logging
logging.basicConfig(level=logging.INFO)

def test_grid_detection(image_path):
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return

    print(f"Loading image: {image_path}")
    img = cv2.imread(image_path)
    
    detector = GridDetector()
    result = detector.detect_grid(img)
    
    if result:
        print(f"Grid detected!")
        board_rect = result.get('board_rect')
        cells = result.get('cells', [])
        print(f"Board Rect: {board_rect}")
        print(f"Cells found: {len(cells)}")
        
        # Draw results
        debug_img = img.copy()
        if board_rect:
            x, y, w, h = board_rect
            cv2.rectangle(debug_img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
        for (cx, cy, cw, ch) in cells:
            cv2.rectangle(debug_img, (cx, cy), (cx+cw, cy+ch), (0, 0, 255), 1)
            
        output_path = "grid_test_result.png"
        cv2.imwrite(output_path, debug_img)
        print(f"Saved debug image to {output_path}")
    else:
        print("Grid detection failed.")

if __name__ == "__main__":
    # Default to the captured image from previous test
    img_path = "capture_test.png"
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
    
    test_grid_detection(img_path)

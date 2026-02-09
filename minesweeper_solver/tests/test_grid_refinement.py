
import sys
import os
import cv2
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_grid_lines(image_path):
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return

    print(f"Loading image: {image_path}")
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 1. Edge Detection
    edges = cv2.Canny(gray, 50, 150)
    
    # Use the previously detected board rect (hardcoded from previous logs for test consistency)
    # Or re-detect roughly. Let's just use the whole image first to see peaks, 
    # but noise outside board will hurt.
    # Let's verify if we can re-use the detector to get the crop.
    
    sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
    from recognition import GridDetector
    detector = GridDetector()
    grid_info = detector.detect_grid(img)
    
    if not grid_info:
        print("Initial detection failed.")
        return

    bx, by, bw, bh = grid_info['board_rect']
    print(f"Focusing on Board Rect: {bx},{by} {bw}x{bh}")
    
    board_edges = edges[by:by+bh, bx:bx+bw]
    # board_gray = gray[by:by+bh, bx:bx+bw]
    
    # 2. Projection Profiles
    # Sum along rows (horizontal lines -> peaks in Y)
    h_proj = np.sum(board_edges, axis=1)
    
    # Sum along cols (vertical lines -> peaks in X)
    v_proj = np.sum(board_edges, axis=0)
    
    # Normalize
    h_proj = h_proj / h_proj.max()
    v_proj = v_proj / v_proj.max()
    
    # 3. Find Peaks / Grid Lines
    # Simple thresholding
    threshold = 0.2
    h_peaks = np.where(h_proj > threshold)[0]
    v_peaks = np.where(v_proj > threshold)[0]
    
    # Filter nearby peaks (non-max suppression or just grouping)
    def clean_peaks(peaks, min_gap=10):
        if len(peaks) == 0: return []
        cleaned = []
        curr_group = [peaks[0]]
        
        for i in range(1, len(peaks)):
            if peaks[i] - peaks[i-1] < min_gap:
                curr_group.append(peaks[i])
            else:
                cleaned.append(int(np.mean(curr_group)))
                curr_group = [peaks[i]]
        cleaned.append(int(np.mean(curr_group)))
        return cleaned

    # Assuming cells are at least 15px
    cleaned_h_peaks = clean_peaks(h_peaks, min_gap=15)
    cleaned_v_peaks = clean_peaks(v_peaks, min_gap=15)
    
    print(f"Found {len(cleaned_h_peaks)} Horizontal Lines")
    print(f"Found {len(cleaned_v_peaks)} Vertical Lines")
    
    # Deduce rows/cols
    # The number of cells is roughly spaces between lines
    # Ideally should correspond to 'rows + 1' lines or similar
    
    rows = len(cleaned_h_peaks) - 1
    cols = len(cleaned_v_peaks) - 1
    
    if rows <= 0 or cols <= 0:
        # Fallback method: FFT or Autocorrelation implies finding the *period*
        # If peaks are messy, let's try finding the median distance between peaks
        d_h = np.diff(cleaned_h_peaks)
        d_v = np.diff(cleaned_v_peaks)
        
        avg_h_gap = np.median(d_h) if len(d_h) > 0 else 0
        avg_v_gap = np.median(d_v) if len(d_v) > 0 else 0
        
        print(f"Median Spacing: Y={avg_h_gap}, X={avg_v_gap}")
        
        # If we trust the board_rect size:
        if avg_h_gap > 10:
            rows = int(round(bh / avg_h_gap))
        if avg_v_gap > 10:
            cols = int(round(bw / avg_v_gap))

    print(f"Refined Estimate: {rows} rows x {cols} cols")
    
    # Generate cells based on this exact division
    # This assumes the board is perfectly filled
    
    cell_w = bw / cols
    cell_h = bh / rows
    
    debug_img = img.copy()
    
    # Draw via floating point steps
    for r in range(rows):
        for c in range(cols):
            x = int(bx + c * cell_w)
            y = int(by + r * cell_h)
            w = int(cell_w)
            h = int(cell_h)
            
            # Draw precise box
            cv2.rectangle(debug_img, (x, y), (x+w, y+h), (0, 0, 255), 1)
            
    cv2.imwrite("debug_grid_refined.png", debug_img)
    print("Saved debug_grid_refined.png")

if __name__ == "__main__":
    img_path = "capture_test.png"
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
    
    test_grid_lines(img_path)

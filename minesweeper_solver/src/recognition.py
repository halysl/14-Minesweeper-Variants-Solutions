
import logging
import cv2
import numpy as np

logger = logging.getLogger(__name__)

class GridDetector:
    def __init__(self):
        pass

    def detect_grid(self, image: np.ndarray):
        """
        Detects the minesweeper grid in the image.
        Returns: 
            dict with:
            - 'top_left': (x, y)
            - 'bottom_right': (x, y)
            - 'cell_size': (w, h)
            - 'rows': int
            - 'cols': int
            - 'cells': List of cell rects [(x, y, w, h)]
        Or None if not found.
        """
        if image is None: return None
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours by area to find likely board
        # The board should be a large rectangle
        min_area = image.shape[0] * image.shape[1] * 0.1 # at least 10% of screen
        
        possible_boards = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > min_area:
                x, y, w, h = cv2.boundingRect(cnt)
                possible_boards.append((x, y, w, h))
        
        # Heuristic: The largest rectangle is likely the board
        if not possible_boards:
            logger.warning("No large rectangle found for grid.")
            return None
            
        # Sort by area (descending)
        possible_boards.sort(key=lambda r: r[2]*r[3], reverse=True)
        bx, by, bw, bh = possible_boards[0]
        
        # Now we need to find the cells inside this board
        # We can look for horizontal and vertical lines, or small squares
        
        board_roi = gray[by:by+bh, bx:bx+bw]
        
        # Use simple thresholding to find cell borders
        # In Minesweeper, cells often have a bevel effect.
        
        # Alternative: Assume standard grid and try to deduce cell size
        # Or find all small square contours inside the board_roi
        
        # Let's try finding many small squares
        roi_edges = cv2.Canny(board_roi, 50, 150)
        roi_contours, _ = cv2.findContours(roi_edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        cells = []
        for cnt in roi_contours:
            approx = cv2.approxPolyDP(cnt, 0.05 * cv2.arcLength(cnt, True), True)
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(cnt)
                # Filter useful cell sizes (e.g. 15x15 to 100x100)
                if 15 < w < 100 and 15 < h < 100:
                    # Check aspect ratio
                    ratio = float(w)/h
                    if 0.8 < ratio < 1.2:
                        cells.append((bx+x, by+y, w, h))
                        
        if not cells:
            logger.warning("No cells found within board.")
            # Fallback: divide board area by expected cell size? 
            # For now return board rect only
            return {'board_rect': (bx, by, bw, bh), 'cells': []}

        # Filter cells to remove duplicates and noise
        # (This is a simplified approach, might need grouping)
        
        logger.info(f"Found {len(cells)} potential cells.")
        
        # Estimate rows/cols from cells
        # This part requires more robust logic (e.g. clustering coordinates)
        
        return {
            'board_rect': (bx, by, bw, bh),
            'cells': cells # raw list for now
        }

class CellClassifier:
    def __init__(self):
        pass

    def classify_cell(self, cell_image: np.ndarray) -> str:
        """
        Classifies a single cell image.
        Returns: '0'-'8', 'flag', 'unknown', 'bomb'
        """
        # Placeholder for classification logic (e.g., template matching or OCR)
        return "unknown"

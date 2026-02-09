
import logging
import cv2
import numpy as np
from model.state import GameState, Board, Cell

logger = logging.getLogger(__name__)

class GridDetector:
    def __init__(self):
        pass

    def process_frame(self, image: np.ndarray) -> GameState:
        """
        Full processing pipeline:
        1. Detect Header ("R" line)
        2. Detect Grid
        3. Return GameState
        """
        state = GameState()
        
        # 1. Detect Grid
        grid_info = self.detect_grid(image)
        if grid_info:
            rows = grid_info['rows']
            cols = grid_info['cols']
            rect = grid_info['board_rect']
            
            # Construct Board object
            board_cells = [[None for _ in range(cols)] for _ in range(rows)]
            for c_rect in grid_info['cells']:
                c_x, c_y, c_w, c_h = c_rect
                
                # Relative to board
                rel_x = c_x - rect[0]
                rel_y = c_y - rect[1]
                
                # Approximate col/row
                c_idx = int(round(rel_x / grid_info['cell_size'][0]))
                r_idx = int(round(rel_y / grid_info['cell_size'][1]))
                
                if 0 <= r_idx < rows and 0 <= c_idx < cols:
                    cell = Cell(r_idx, c_idx, c_x, c_y, c_w, c_h)
                    board_cells[r_idx][c_idx] = cell
            
            state.board = Board(
                top_left=(rect[0], rect[1]),
                width=rect[2],
                height=rect[3],
                rows=rows,
                cols=cols,
                cells=board_cells
            )

        # 2. Detect Header Info
        # Based on analysis, header is at the top, typically y=45.
        # Scan top 200 pixels
        header_h_limit = 200
        if grid_info:
             # Stop before board starts
             header_h_limit = min(header_h_limit, grid_info['board_rect'][1])
             
        header_roi = image[0:header_h_limit, :]
        
        # Save debug
        cv2.imwrite("debug_header_area.png", header_roi)
        
        try:
            import pytesseract
            # Use image_to_data to find the line with "R"
            gray_header = cv2.cvtColor(header_roi, cv2.COLOR_BGR2GRAY)
            data = pytesseract.image_to_data(gray_header, output_type=pytesseract.Output.DICT)
            
            # Find the line containing "R"
            # We look for a token that contains "R" (e.g. "[R]")
            header_y = -1
            found_text = []
            
            n_boxes = len(data['text'])
            for i in range(n_boxes):
                text = data['text'][i].strip()
                if not text: continue
                
                # Check for "R" or "[R]"
                if "R" in text or "Remaining" in text: # flexible check
                    # Found potential header line
                    # Get the y coordinate of this line/block
                    header_y = data['top'][i]
                    # Get all text on this line (approximate by y)
                    break
            
            if header_y != -1:
                # Collect all text on roughly the same Y line (+- 10px)
                line_texts = []
                for i in range(n_boxes):
                    text = data['text'][i].strip()
                    if not text: continue
                    y = data['top'][i]
                    if abs(y - header_y) < 20: # Tolerance
                         line_texts.append(text)
                
                full_header_text = " ".join(line_texts)
                state.header_raw_text = full_header_text
                logger.info(f"Header Line Found: '{full_header_text}'")
                
                # Parse "R ... 10 ... 10/18" or similar
                # Extract all numbers
                # Treat "10/18" as "10" and "18"
                import re
                numbers = [int(n) for n in re.findall(r'\d+', full_header_text)]
                
                if len(numbers) >= 3:
                     # Usually: Total, Remaining Mines, Remaining Cells
                     # Or: [R] <Total> <RemainingMines>/<RemainingCells>
                     # From OCR: "[R] ... 10 ... 10/18" -> 10, 10, 18
                     state.total_mines = numbers[0]
                     state.remaining_mines = numbers[1]
                     state.remaining_cells = numbers[2]
                elif len(numbers) >= 2:
                     # Fallback if only two numbers found
                     state.total_mines = numbers[0]
                     state.remaining_mines = numbers[1]
            else:
                 logger.warning("Header 'R' line not found in top region.")

        except Exception as e:
            logger.error(f"OCR failed: {e}")
            
        # Debug: Draw grid on image and save
        if grid_info:
             debug_img = image.copy()
             # Draw board rect
             bx, by, bw, bh = grid_info['board_rect']
             cv2.rectangle(debug_img, (bx, by), (bx+bw, by+bh), (0, 255, 0), 2)
             
             # Draw cells
             for cell in grid_info['cells']:
                 cx, cy, cw, ch = cell
                 cv2.rectangle(debug_img, (cx, cy), (cx+cw, cy+ch), (0, 0, 255), 1)
                 
             cv2.imwrite("debug_grid_visual.png", debug_img)

        return state
                
        return state

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
            return None

        # Filter cells to remove duplicates and noise
        # (This is a simplified approach, might need grouping)
        
        logger.info(f"Found {len(cells)} potential cells.")
        
        # Heuristic: Find the most common width/height (mode)
        widths = [c[2] for c in cells]
        heights = [c[3] for c in cells]
        avg_w = np.median(widths)
        avg_h = np.median(heights)
        
        # Filter out outliers (cells that are too different from median size)
        valid_cells = []
        for c in cells:
            if 0.8 * avg_w < c[2] < 1.2 * avg_w and 0.8 * avg_h < c[3] < 1.2 * avg_h:
                valid_cells.append(c)
                        
        if len(valid_cells) < 10: # Minimum cells for a board
             logger.warning("Not enough valid cells found.")
             return None
             
        # Find bounds of the grid
        min_x = min(c[0] for c in valid_cells)
        min_y = min(c[1] for c in valid_cells)
        max_x = max(c[0] + c[2] for c in valid_cells)
        max_y = max(c[1] + c[3] for c in valid_cells)
        
        bw = max_x - min_x
        bh = max_y - min_y
        
        # --- Improved Grid Division using Projection Profiles ---
        # 1. Crop Board Area
        board_roi = gray[min_y:max_y, min_x:max_x]
        
        # 2. Edges of ROI
        board_edges = cv2.Canny(board_roi, 50, 150)
        
        # 3. Projection Sums
        h_proj = np.sum(board_edges, axis=1) # Rows
        v_proj = np.sum(board_edges, axis=0) # Cols
        
        # 4. Find approximate number of cells based on average size
        # This gives us a target number of splits.
        detected_cols = int(round(bw / avg_w))
        detected_rows = int(round(bh / avg_h))
        
        # 5. Precise Calculation
        # Instead of relying on peaks which might be noisy, let's use the bounds 
        # and the constrained count to calculate floating point cell sizes.
        # However, checking peaks helps align the grid if there's padding.
        # For Minesweeper, the grid is usually uniform.
        
        # Using simple precise division:
        cell_w_precise = bw / detected_cols
        cell_h_precise = bh / detected_rows
        
        logger.info(f"Refined Grid: {detected_rows}x{detected_cols}")
        logger.info(f"Precise Cell Size: {cell_w_precise:.2f}x{cell_h_precise:.2f}")
        
        full_cells = []
        for r in range(detected_rows):
            for c in range(detected_cols):
                # Use float arithmetic for accumulation
                cell_x = int(min_x + c * cell_w_precise)
                cell_y = int(min_y + r * cell_h_precise)
                
                # Careful with last cell to prevent rounding gaps? 
                # Actually floor is fine if we use the same formula.
                
                # We can also calculate width/height to fill gaps
                next_x = int(min_x + (c + 1) * cell_w_precise)
                next_y = int(min_y + (r + 1) * cell_h_precise)
                
                cell_w = next_x - cell_x
                cell_h = next_y - cell_y
                
                full_cells.append((cell_x, cell_y, cell_w, cell_h))
        
        return {
            'board_rect': (min_x, min_y, bw, bh),
            'cells': full_cells,
            'cell_size': (cell_w_precise, cell_h_precise),
            'rows': detected_rows,
            'cols': detected_cols
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

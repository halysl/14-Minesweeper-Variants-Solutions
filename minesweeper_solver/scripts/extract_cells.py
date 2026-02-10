
import sys
import os
import cv2
import numpy as np
import hashlib
import glob
import argparse

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from recognition import GridDetector

def get_image_hash(image):
    """Compute hash of image data."""
    return hashlib.md5(image.tobytes()).hexdigest()

def extract_cells(image_path, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Loading image: {image_path}")
    img = cv2.imread(image_path)
    if img is None:
        print("Failed to load image.")
        return
    
    detector = GridDetector()
    result = detector.detect_grid(img)
    
    if not result:
        print("Grid detection failed.")
        return

    cells = result['cells']
    print(f"Found {len(cells)} cells on board.")
    
    # Load existing hashes to prevent duplicates
    # We look for files like "label_hash.png" or "unknown_hash.png"
    existing_hashes = set()
    existing_files = glob.glob(os.path.join(output_dir, "*.png"))
    for f in existing_files:
        basename = os.path.splitext(os.path.basename(f))[0]
        parts = basename.split('_')
        if len(parts) >= 2:
            # Assume last part is hash
            existing_hashes.add(parts[-1])
            
    print(f"Loaded {len(existing_hashes)} existing unique templates.")
    
    new_count = 0
    # Process each cell
    STANDARD_SIZE = (40, 40)
    
    for i, (x, y, w, h) in enumerate(cells):
        if w < 5 or h < 5: continue
        
        cell_img = img[y:y+h, x:x+w]
        
        # Resize to standard size for consistent hashing and classification
        cell_norm = cv2.resize(cell_img, STANDARD_SIZE, interpolation=cv2.INTER_AREA)
        
        img_hash = get_image_hash(cell_norm)[:8]
        
        if img_hash not in existing_hashes:
            existing_hashes.add(img_hash)
            filename = os.path.join(output_dir, f"unknown_{img_hash}.png")
            cv2.imwrite(filename, cell_norm)
            print(f"saved: {filename}")
            new_count += 1
            
    print(f"Extracted {new_count} NEW unique cell images to {output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract unique cells from game screenshot.")
    parser.add_argument("image", nargs='?', default="capture_test.png", help="Path to screenshot")
    parser.add_argument("--out", default="data/cells", help="Output directory for templates")
    
    args = parser.parse_args()
    
    extract_cells(args.image, args.out)

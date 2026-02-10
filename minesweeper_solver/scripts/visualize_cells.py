
import os
import cv2
import glob
import math
import numpy as np

def create_montage(input_dir, output_file):
    files = glob.glob(os.path.join(input_dir, "*.png"))
    if not files:
        print("No images found.")
        return

    # Load all images
    images = []
    for f in sorted(files):
        img = cv2.imread(f)
        if img is not None:
            images.append(img)
            
    if not images:
        return

    count = len(images)
    cols = int(math.ceil(math.sqrt(count)))
    rows = int(math.ceil(count / cols))
    
    h, w, c = images[0].shape
    
    # Create empty montage
    montage = np.zeros((rows * h, cols * w, c), dtype=np.uint8)
    
    for i, img in enumerate(images):
        r = i // cols
        c = i % cols
        
        # Resize if necessary (should be same, but just in case)
        if img.shape != (h, w, c):
            img = cv2.resize(img, (w, h))
            
        montage[r*h:(r+1)*h, c*w:(c+1)*w] = img
        
    cv2.imwrite(output_file, montage)
    print(f"Saved montage of {count} images to {output_file}")

if __name__ == "__main__":
    create_montage("data/cells", "debug_cells_montage.png")

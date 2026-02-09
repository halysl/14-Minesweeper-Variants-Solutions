
import sys
import os
import cv2
import pytesseract
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_full_ocr(image_path):
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return

    print(f"Loading image: {image_path}")
    img = cv2.imread(image_path)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Try generic OCR
    print("Running Tesseract on full image...")
    data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
    
    found_r = False
    
    n_boxes = len(data['text'])
    for i in range(n_boxes):
        text = data['text'][i].strip()
        if text:
            conf = data['conf'][i]
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            print(f"Text: '{text}' @ ({x},{y},{w},{h}) Conf: {conf}")
            
            if "R" in text:
                print(f"--> POTENTIAL HEADER found: '{text}' at y={y}")
                found_r = True

if __name__ == "__main__":
    img_path = "capture_test.png"
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
    
    test_full_ocr(img_path)

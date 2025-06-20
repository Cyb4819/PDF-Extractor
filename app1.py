import fitz
import json
import re
import os
from PIL import Image
from io import BytesIO
import base64
import pytesseract
import cv2

def classify_block(block, page_height):
    block_type = 'Unknown'
    block_text = block[4]   # block[4] contains the actual text in the block
    block_type_code = block[6]  # block[6] contains the block type code
    
    # Image Block: If block type is image (block_type_code != 0)
    if block_type_code != 0:
        block_type = 'Image'
    
    # Text Block: If it is a text block (block_type_code == 0)
    elif block_type_code == 0:
        # Heuristic: If the block is near the top or bottom of the page, consider it as header or footer
        if block[1] < 0.1 * page_height:
            block_type = 'Header'
        elif block[3] > 0.9 * page_height:
            block_type = 'Footer'
        else:
            block_type = 'Text'
    
    return block_type

def sanitize_text(text):
    """Remove newline, tab characters, backslashes, and specific unwanted texts from the text."""
    unwanted_texts = [
        "TM-VE50T / Operating and Maintenance Instructions Manual"
    ]
    
    # Replace newline, tab, and backslash characters
    # text = text.replace('\n', ' ').replace('\t', ' ').replace('\\', '')
    
    # Remove specific unwanted texts
    for unwanted in unwanted_texts:
        text = text.replace(unwanted, '')

        text = re.sub(r'\\[\'"bfnrt]', '', text)
    
    return text.strip()  # Return the processed text

def save_image(image_bytes, image_ext, page_num, img_index):
    """Save image to a file and return the file path."""
    images_dir = "images"
    page_dir = os.path.join(images_dir, f"page_{page_num + 1}")
    os.makedirs(page_dir, exist_ok=True)
    
    image_filename = os.path.join(page_dir, f"img_{img_index + 1}.{image_ext}")
    with open(image_filename, "wb") as img_file:
        img_file.write(image_bytes)
    return image_filename

def preprocess_image_for_ocr(image_path):
    """Preprocess image for better OCR accuracy."""
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return thresh

def extract_text_from_image(image_path):
    """Extract text from an image using OCR."""
    processed_image = preprocess_image_for_ocr(image_path)
    text = pytesseract.image_to_string(processed_image)
    return text.strip()

def extract_and_classify(pdf_path):
    doc = fitz.open(pdf_path)
    pdf_data = []
    extracted_data = set()

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        page_height = page.rect.height
        page_data = {
            "page_number": page_num + 1,
            "blocks": []
        }
        
        text_blocks = page.get_text("blocks")
        # If no text blocks, treat as scanned page
        is_scanned = all(len(block[4].strip()) == 0 for block in text_blocks)
        
        if is_scanned:
            # Extract images and run OCR
            images = []
            for img_index, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image_path = save_image(image_bytes, image_ext, page_num, img_index)
                # OCR on saved image
                ocr_text = extract_text_from_image(image_path)
                block_data = {
                    "type": "OCR_Text",
                    "content": sanitize_text(ocr_text)
                }
                block_key = f"OCR_Text:{ocr_text}"
                if block_key not in extracted_data:
                    extracted_data.add(block_key)
                    page_data["blocks"].append(block_data)
                image_data = {
                    "image_index": img_index + 1,
                    "image_format": image_ext,
                    "image_data": image_path
                }
                images.append(image_data)
            page_data["images"] = images
            pdf_data.append(page_data)
            continue
        
        for block in text_blocks:
            block_type = classify_block(block, page_height)
            if block_type == "Footer":
                continue
            block_content = sanitize_text(block[4]) if block_type != 'Image' else 'Image Content'
            block_data = {
                "type": block_type,
                "content": block_content
            }
            block_key = f"{block_type}:{block_content}"
            if block_key not in extracted_data:
                extracted_data.add(block_key)
                page_data["blocks"].append(block_data)
        
        # Extract and encode images
        images = []
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            image_path = save_image(image_bytes, image_ext, page_num, img_index)
            image_data = {
                "image_index": img_index + 1,
                "image_format": image_ext,
                "image_data": image_path
            }
            images.append(image_data)
        page_data["images"] = images
        pdf_data.append(page_data)
    
    # Save data to JSON file
    with open("pdf_data.json", "w", encoding='utf-8') as json_file:
        json.dump(pdf_data, json_file, ensure_ascii=False, indent=4)

# Example usage
pdf_path = "ANY PDF FILE PATH HERE"
extract_and_classify(pdf_path)

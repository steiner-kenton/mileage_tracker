"""
OCR processing utilities using Tesseract
"""
import pytesseract
from PIL import Image, ImageEnhance, ImageOps
import re
import io

def auto_rotate_image(image):
    """
    Automatically rotate image to optimal orientation for OCR
    Tests all 4 orientations and returns the one with highest OCR confidence
    """
    best_image = image
    best_confidence = 0
    
    # Test all 4 possible orientations (0°, 90°, 180°, 270°)
    for angle in [0, 90, 180, 270]:
        # Rotate image
        if angle == 0:
            rotated_image = image
        else:
            rotated_image = image.rotate(-angle, expand=True)
        
        try:
            # Get OCR confidence for this orientation
            data = pytesseract.image_to_data(rotated_image, output_type=pytesseract.Output.DICT)
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            
            if confidences:
                avg_confidence = sum(confidences) / len(confidences)
                
                # If this orientation has better confidence, use it
                if avg_confidence > best_confidence:
                    best_confidence = avg_confidence
                    best_image = rotated_image
        except:
            # If OCR fails for this orientation, skip it
            continue
    
    return best_image

def process_receipt_ocr(image_file):
    """
    Use Tesseract OCR to extract store, date, and total from receipt image
    """
    try:
        # Reset file pointer to beginning
        image_file.seek(0)
        
        # Convert uploaded file to PIL Image
        image = Image.open(image_file)
        
        # Verify image is valid
        image.verify()
        
        # Reopen image (verify() closes the file)
        image_file.seek(0)
        image = Image.open(image_file)
        
        # Convert to RGB if image is in a different mode (RGBA, P, etc.)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Fix image orientation using EXIF data if available
        image = ImageOps.exif_transpose(image)
        
        # Auto-rotate image to best orientation for OCR
        image = auto_rotate_image(image)
        
        # Optional: Enhance image for better OCR results
        # Uncomment these lines if OCR accuracy is poor
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)  # Increase contrast
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(2.0)  # Increase sharpness
        
        # Perform OCR using Tesseract
        ocr_text = pytesseract.image_to_string(image)
        
        # Extract information using regex patterns
        extracted_data = extract_receipt_info(ocr_text)
        
        return {
            "success": True,
            "store_name": extracted_data.get("store_name", ""),
            "date": extracted_data.get("date", ""),
            "total": extracted_data.get("total", ""),
            "raw_text": ocr_text
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Error processing receipt: {str(e)}. Please try a different image format or ensure the image is not corrupted."
        }

def extract_receipt_info(ocr_text):
    """
    Extract store name, date, and total from OCR text using regex patterns
    """
    extracted = {}
    
    # Common store name patterns (add more as needed)
    store_patterns = [
        r'(WALMART|WAL-MART|TARGET|COSTCO|KROGER|SAFEWAY|WHOLE FOODS|CVS|WALGREENS|MCDONALD\'S|STARBUCKS|DOLLAR TREE)',
        r'^([A-Z][A-Z\s&]+)(?=\n|\r)',  # First line with all caps
    ]
    
    # Date patterns (MM/DD/YYYY, DD/MM/YYYY, YYYY-MM-DD, etc.)
    date_patterns = [
        r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
        r'(\d{2,4}[\/\-]\d{1,2}[\/\-]\d{1,2})',
        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{2,4}',
    ]
    
    # Total patterns (look for amounts near "total", "amount", etc.)
    total_patterns = [
        r'(?:TOTAL|Total|AMOUNT|Amount|BALANCE|Balance)[:\s]*\$?(\d+\.?\d*)',
        r'\$(\d+\.\d{2})\s*$',  # Dollar amount at end of line
        r'(\d+\.\d{2})\s*(?:TOTAL|Total|$)',  # Amount followed by total or end
    ]
    
    # Extract store name
    for pattern in store_patterns:
        match = re.search(pattern, ocr_text, re.IGNORECASE | re.MULTILINE)
        if match:
            extracted["store_name"] = match.group(1).strip()
            break
    
    # Extract date
    for pattern in date_patterns:
        match = re.search(pattern, ocr_text, re.IGNORECASE)
        if match:
            extracted["date"] = match.group(1).strip()
            break
    
    # Extract total
    for pattern in total_patterns:
        matches = re.findall(pattern, ocr_text, re.IGNORECASE | re.MULTILINE)
        if matches:
            # Get the highest amount (likely the total)
            amounts = [float(match) for match in matches if match.replace('.', '').isdigit()]
            if amounts:
                extracted["total"] = str(max(amounts))
                break
    
    return extracted

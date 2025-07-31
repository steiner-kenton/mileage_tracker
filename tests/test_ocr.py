"""
Sample test file for OCR utilities
Run with: pytest tests/
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.ocr_utils import extract_receipt_info

def test_extract_store_name():
    """Test store name extraction from OCR text"""
    ocr_text = "WALMART SUPERCENTER\n123 MAIN ST\nANYTOWN, ST 12345"
    result = extract_receipt_info(ocr_text)
    assert result.get("store_name") == "WALMART"

def test_extract_total():
    """Test total extraction from OCR text"""
    ocr_text = "ITEM 1 $5.99\nITEM 2 $12.50\nTOTAL $23.48"
    result = extract_receipt_info(ocr_text)
    assert result.get("total") == "23.48"

def test_extract_date():
    """Test date extraction from OCR text"""
    ocr_text = "RECEIPT\n01/15/2025 14:32:10\nTOTAL $23.48"
    result = extract_receipt_info(ocr_text)
    assert result.get("date") == "01/15/2025"

if __name__ == "__main__":
    # Simple test runner
    test_extract_store_name()
    test_extract_total()
    test_extract_date()
    print("All tests passed!")

"""
Test configuration and utilities
"""
import pytest
import sys
import os

# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test fixtures can go here
@pytest.fixture
def sample_ocr_text():
    """Sample OCR text for testing receipt processing"""
    return """
    WALMART SUPERCENTER
    123 MAIN ST
    ANYTOWN, ST 12345
    
    ITEM 1               $5.99
    ITEM 2               $12.50
    ITEM 3               $3.25
    
    SUBTOTAL             $21.74
    TAX                  $1.74
    TOTAL                $23.48
    
    01/15/2025 14:32:10
    """

@pytest.fixture
def sample_location_data():
    """Sample location data for testing"""
    return {
        "location_name": "Test Location",
        "location_address": "123 Test St, Test City, TS 12345"
    }

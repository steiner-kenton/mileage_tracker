# Mileage Manager

A Streamlit application for tracking mileage, managing locations, and processing receipts with OCR.

## Project Structure

```
mileage_tracker/
├── app.py                 # Main application file
├── config.py              # Configuration and Google Sheets authentication
├── google_api.py          # Google Maps API utilities (address lookup, distance calculation)
├── ocr_utils.py           # Tesseract OCR processing for receipts
├── sheets_utils.py        # Google Sheets data management utilities
├── ui_components.py       # Streamlit UI components and forms
├── mileage.py             # Original monolithic file (can be removed)
├── requirements.txt       # Python dependencies
├── .streamlit/
│   └── secrets.toml       # Configuration secrets (not in git)
└── README.md              # This file
```

## Features

- **Mileage Tracking**: Add trips between locations with automatic distance calculation
- **Location Management**: Search and store frequently used addresses
- **Receipt Processing**: Upload receipt images and extract store, date, and total using OCR
- **Google Sheets Integration**: All data is stored and synchronized with Google Sheets

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Tesseract** (for OCR):
   ```bash
   # macOS
   brew install tesseract
   
   # Ubuntu/Debian
   sudo apt-get install tesseract-ocr
   
   # Windows
   # Download from: https://github.com/UB-Mannheim/tesseract/wiki
   ```

3. **Configure Secrets**: Update `.streamlit/secrets.toml` with your API keys and credentials

4. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

## Module Descriptions

### `config.py`
- Loads configuration from Streamlit secrets
- Handles Google Sheets authentication
- Provides global client instance

### `google_api.py`
- Google Places API for address lookup
- Google Distance Matrix API for mileage calculation
- Trip existence checking

### `ocr_utils.py`
- Tesseract OCR processing
- Receipt information extraction using regex patterns
- Support for common store formats

### `sheets_utils.py`
- Google Sheets data retrieval and writing
- Automatic sheet creation
- Error handling for sheet operations

### `ui_components.py`
- Trip entry form
- Location management form
- Receipt processing interface
- Data display components

### `app.py`
- Main application entry point
- Session state management
- Layout coordination

## Google Sheets Structure

The application expects three sheets in your Google Spreadsheet:

1. **Mileage_Dictionary**: `location_name`, `location_address`
2. **mileage_log**: `trip_date`, `start_location_name`, `start_location_address`, `end_location_name`, `end_location_address`, `total_mileage`
3. **Receipts**: `date`, `store_name`, `total`, `upload_timestamp`

## API Requirements

- Google Maps API key with Places API and Distance Matrix API enabled
- Google Service Account with Google Sheets API access
- Tesseract OCR installed on the system

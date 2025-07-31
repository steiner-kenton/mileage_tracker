#!/bin/bash

# Development setup script for Mileage Tracker
echo "🚀 Setting up Mileage Tracker development environment..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📚 Installing requirements..."
pip install -r requirements.txt

# Install development dependencies
echo "🛠️ Installing development dependencies..."
pip install pytest black flake8

# Check if Tesseract is installed
if ! command -v tesseract &> /dev/null; then
    echo "⚠️ Tesseract OCR is not installed."
    echo "   Please install it with:"
    echo "   macOS: brew install tesseract"
    echo "   Ubuntu: sudo apt-get install tesseract-ocr"
else
    echo "✅ Tesseract OCR is installed"
fi

# Check if secrets file exists
if [ ! -f ".streamlit/secrets.toml" ]; then
    echo "⚠️ Secrets file not found at .streamlit/secrets.toml"
    echo "   Please create it with your API keys and credentials"
else
    echo "✅ Secrets file found"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To run the application:"
echo "  source venv/bin/activate"
echo "  streamlit run app.py"
echo ""
echo "To run tests:"
echo "  source venv/bin/activate"
echo "  python tests/test_ocr.py"

#!/bin/bash
# UniversalShield Setup Script
# Creates virtual environment and installs all dependencies

set -e  # Exit on error

echo "🛡️  UniversalShield Setup"
echo "========================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo ""
echo "✅ Setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To start the API server, run:"
echo "  uvicorn src.api.scam_detection_api:app --reload --port 8000"
echo ""
echo "To run tests, run:"
echo "  python tests/test_integration.py"
echo ""

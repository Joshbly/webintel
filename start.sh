#!/bin/bash

# WebIntel - HTML Analysis Tool Startup Script

echo "🔍 Starting WebIntel..."
echo ""

# Check if virtual environment exists
if [ ! -d "webintel-env" ]; then
    echo "❌ Virtual environment not found. Creating it..."
    python3 -m venv webintel-env
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source webintel-env/bin/activate

# Install/update dependencies if needed
echo "📦 Checking dependencies..."
pip install -r requirements.txt --quiet

echo "🚀 Starting Streamlit application..."
echo ""
echo "Your app will open automatically in your browser at:"
echo "👉 http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

# Start Streamlit
streamlit run app.py 
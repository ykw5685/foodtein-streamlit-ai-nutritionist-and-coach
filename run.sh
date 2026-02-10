#!/bin/bash

# Quick Start Script for Streamlit AI Nutritionist Testing UI

echo "========================================"
echo "AI Nutritionist Chat - Streamlit Testing UI"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or later"
    exit 1
fi

echo "[1/3] Installing dependencies..."
python3 -m pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo "✅ Dependencies installed"

echo ""
echo "[2/3] Checking setup..."
echo ""
echo "⚠️  Make sure the Go backend is running at http://localhost:8080"
echo "   In another terminal, run: go run main.go"
echo ""
read -p "Press Enter to continue..."

echo "[3/3] Starting Streamlit app..."
echo ""
echo "🚀 Opening http://localhost:8501"
echo "   (Press Ctrl+C in this window to stop)"
echo ""

python3 -m streamlit run app.py

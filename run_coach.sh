#!/bin/bash
# Run AI Coach Streamlit App
# Usage: ./run_coach.sh

cd "$(dirname "$0")/foodtein-streamlit-ai-nutritionist"
echo "🏋️  Starting AI Coach Streamlit App..."
echo "App will open at: http://localhost:8501"
streamlit run coach_app.py

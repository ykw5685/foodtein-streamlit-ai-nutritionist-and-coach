"""
Configuration for Streamlit AI Nutritionist Testing UI
"""

from datetime import datetime, timedelta
import pandas as pd

# ============================================================================
# API Configuration
# ============================================================================

API_BASE_URL = "http://localhost:8080/api"
AI_NUTRITIONIST_BASE = f"{API_BASE_URL}/ai-nutritionist"
AI_COACH_BASE = f"{API_BASE_URL}/ai-coach"

ENDPOINTS = {
    # Nutritionist endpoints
    "get_conversation": f"{AI_NUTRITIONIST_BASE}/conversation",
    "send_message": f"{AI_NUTRITIONIST_BASE}/conversation/messages",
    "send_message_with_data": f"{AI_NUTRITIONIST_BASE}/conversation/messages-with-data",
    "clear_conversation": f"{AI_NUTRITIONIST_BASE}/conversation/clear",
    # Coach endpoints
    "get_coach_conversation": f"{AI_COACH_BASE}/conversation",
    "send_coach_message": f"{AI_COACH_BASE}/conversation/messages",
    "send_coach_message_with_data": f"{AI_COACH_BASE}/conversation/messages-with-data",
    "clear_coach_conversation": f"{AI_COACH_BASE}/conversation/clear",
}

# ============================================================================
# Test Token Configuration
# ============================================================================
# Using ExternalAuthMiddleware with no endpoint configured,
# "bearer streamlit" token maps to user_streamlit_001 in the mock auth
# Any other token maps to user_123456 (default)
TEST_TOKEN = "bearer streamlit"


# ============================================================================
# Default Test Data
# ============================================================================

MOCK_HEALTH_DATA = [
    {"date": datetime.now().strftime("%Y-%m-%d"), "metric": "Steps", "value": "8234"},
    {"date": datetime.now().strftime("%Y-%m-%d"), "metric": "Sleep (hours)", "value": "7.5"},
    {"date": datetime.now().strftime("%Y-%m-%d"), "metric": "Heart Rate (bpm)", "value": "72"},
    {"date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"), "metric": "Steps", "value": "10234"},
]

MOCK_COACH_HEALTH_DATA = [
    {"date": "2026-02-07", "metric": "Steps", "value": "8500"},
    {"date": "2026-02-07", "metric": "Sleep Duration", "value": "7.5"},
    {"date": "2026-02-07", "metric": "Heart Rate", "value": "72"},
    {"date": "2026-02-07", "metric": "Blood Pressure Sys", "value": "120"},
    {"date": "2026-02-07", "metric": "Blood Pressure Dia", "value": "80"},
    {"date": "2026-02-07", "metric": "Body Fat", "value": "18.5"},
    {"date": "2026-02-07", "metric": "Oxygen Saturation", "value": "98.0"},
    {"date": "2026-02-06", "metric": "Steps", "value": "10200"},
    {"date": "2026-02-06", "metric": "Sleep Duration", "value": "8.0"},
    {"date": "2026-02-06", "metric": "Heart Rate", "value": "68"},
]

MOCK_COACH_WORKOUT_HISTORY = [
    {
        "date": "2026-02-07",
        "workout_name": "Full Body Strength",
        "category": "strength",
        "duration_mins": 45,
        "completed": True,
    },
    {
        "date": "2026-02-06",
        "workout_name": "Cardio Blast",
        "category": "cardio",
        "duration_mins": 30,
        "completed": True,
    },
    {
        "date": "2026-02-05",
        "workout_name": "Upper Body Focus",
        "category": "strength",
        "duration_mins": 40,
        "completed": True,
    },
]

MOCK_DIETARY_DATA = [
    {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "meal_type": "breakfast",
        "food_name": "Oatmeal with berries",
        "serving_size": 50,
        "unit": "g",
        "calories": 180,
        "protein": 6,
        "carbs": 35,
        "fat": 3,
    },
    {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "meal_type": "lunch",
        "food_name": "Grilled Chicken Breast with Brown Rice",
        "serving_size": 300,
        "unit": "g",
        "calories": 450,
        "protein": 52,
        "carbs": 43,
        "fat": 7,
    },
]

# ============================================================================
# UI Constants
# ============================================================================

MESSAGE_ROLE_USER = 0
MESSAGE_ROLE_ASSISTANT = 1

ROLE_DISPLAY_MAP = {
    MESSAGE_ROLE_USER: "👤 User",
    MESSAGE_ROLE_ASSISTANT: "🤖 Assistant",
}

ROLE_COLOR_MAP = {
    MESSAGE_ROLE_USER: "#e8f4f8",
    MESSAGE_ROLE_ASSISTANT: "#f0f8e8",
}

# ============================================================================
# CSV Format Specifications
# ============================================================================

HEALTH_CSV_COLUMNS = ["date", "metric", "value"]
HEALTH_CSV_EXAMPLE = pd.DataFrame([
    {"date": "2026-02-10", "metric": "Steps", "value": "8234"},
    {"date": "2026-02-10", "metric": "Sleep (hours)", "value": "7.5"},
    {"date": "2026-02-10", "metric": "Heart Rate (bpm)", "value": "72"},
    {"date": "2026-02-10", "metric": "Blood Pressure (mmHg)", "value": "120/80"},
    {"date": "2026-02-10", "metric": "Body Fat (%)", "value": "22.5"},
    {"date": "2026-02-10", "metric": "Oxygen Saturation (%)", "value": "98"},
])

DIETARY_CSV_COLUMNS = [
    "date", "meal_type", "food_name", "serving_size", "unit",
    "calories", "protein", "carbs", "fat", "fiber"
]
DIETARY_CSV_EXAMPLE = pd.DataFrame([
    # Feb 9, 2026
    {
        "date": "2026-02-09",
        "meal_type": "breakfast",
        "food_name": "Oatmeal with berries",
        "serving_size": 50,
        "unit": "g",
        "calories": 180,
        "protein": 6,
        "carbs": 35,
        "fat": 3,
        "fiber": 4,
    },
    {
        "date": "2026-02-09",
        "meal_type": "lunch",
        "food_name": "Grilled Chicken with Brown Rice",
        "serving_size": 300,
        "unit": "g",
        "calories": 450,
        "protein": 52,
        "carbs": 43,
        "fat": 7,
        "fiber": 5,
    },
    {
        "date": "2026-02-09",
        "meal_type": "dinner",
        "food_name": "Salmon with Sweet Potato",
        "serving_size": 350,
        "unit": "g",
        "calories": 520,
        "protein": 48,
        "carbs": 38,
        "fat": 18,
        "fiber": 6,
    },
    {
        "date": "2026-02-09",
        "meal_type": "snack",
        "food_name": "Greek Yogurt with Almonds",
        "serving_size": 150,
        "unit": "g",
        "calories": 220,
        "protein": 20,
        "carbs": 12,
        "fat": 10,
        "fiber": 2,
    },
    # Feb 10, 2026
    {
        "date": "2026-02-10",
        "meal_type": "breakfast",
        "food_name": "Eggs and Toast",
        "serving_size": 200,
        "unit": "g",
        "calories": 320,
        "protein": 18,
        "carbs": 28,
        "fat": 12,
        "fiber": 3,
    },
    {
        "date": "2026-02-10",
        "meal_type": "lunch",
        "food_name": "Tuna Salad",
        "serving_size": 280,
        "unit": "g",
        "calories": 280,
        "protein": 42,
        "carbs": 8,
        "fat": 9,
        "fiber": 3,
    },
    {
        "date": "2026-02-10",
        "meal_type": "dinner",
        "food_name": "Beef Stir-fry with Vegetables",
        "serving_size": 330,
        "unit": "g",
        "calories": 480,
        "protein": 46,
        "carbs": 32,
        "fat": 16,
        "fiber": 7,
    },
    {
        "date": "2026-02-10",
        "meal_type": "snack",
        "food_name": "Apple with Peanut Butter",
        "serving_size": 120,
        "unit": "g",
        "calories": 240,
        "protein": 8,
        "carbs": 28,
        "fat": 11,
        "fiber": 4,
    },
])

# ============================================================================
# Coach App CSV Examples
# ============================================================================

COACH_HEALTH_CSV_COLUMNS = ["date", "metric", "value"]
COACH_HEALTH_CSV_EXAMPLE = pd.DataFrame([
    {"date": "2026-02-10", "metric": "Steps", "value": "8500"},
    {"date": "2026-02-10", "metric": "Sleep Duration", "value": "7.5"},
    {"date": "2026-02-10", "metric": "Heart Rate", "value": "72"},
    {"date": "2026-02-10", "metric": "Blood Pressure Sys", "value": "120"},
    {"date": "2026-02-10", "metric": "Blood Pressure Dia", "value": "80"},
    {"date": "2026-02-10", "metric": "Body Fat", "value": "18.5"},
    {"date": "2026-02-10", "metric": "Oxygen Saturation", "value": "98.0"},
    {"date": "2026-02-09", "metric": "Steps", "value": "10200"},
    {"date": "2026-02-09", "metric": "Sleep Duration", "value": "8.0"},
    {"date": "2026-02-09", "metric": "Heart Rate", "value": "68"},
])

COACH_WORKOUT_CSV_COLUMNS = ["date", "workout_name", "category", "duration_mins", "completed"]
COACH_WORKOUT_CSV_EXAMPLE = pd.DataFrame([
    {
        "date": "2026-02-10",
        "workout_name": "Full Body Strength",
        "category": "strength",
        "duration_mins": 45,
        "completed": "true",
    },
    {
        "date": "2026-02-09",
        "workout_name": "Cardio Blast",
        "category": "cardio",
        "duration_mins": 30,
        "completed": "true",
    },
    {
        "date": "2026-02-08",
        "workout_name": "Upper Body Focus",
        "category": "strength",
        "duration_mins": 40,
        "completed": "true",
    },
    {
        "date": "2026-02-07",
        "workout_name": "HIIT Training",
        "category": "cardio",
        "duration_mins": 25,
        "completed": "true",
    },
    {
        "date": "2026-02-06",
        "workout_name": "Lower Body Strength",
        "category": "strength",
        "duration_mins": 50,
        "completed": "true",
    },
])

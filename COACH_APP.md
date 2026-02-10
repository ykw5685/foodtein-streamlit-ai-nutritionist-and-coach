# AI Fitness Coach Streamlit Application

A conversational interface for personalized fitness coaching backed by health data and workout recommendations.

## Overview

The AI Fitness Coach application is a Streamlit-based client that integrates with the Foodtein Backend to provide personalized workout recommendations. Unlike the traditional tool-based approach, this coach uses a **data-driven model** where all necessary data (health metrics, workout history, available workouts) is provided upfront, enabling fast, single-API-call responses.

## Key Features

### 📊 Data Management
- **Profile Information**: Input user name, age, gender, height, and weight
- **Health Data Upload**: Upload CSV files with health metrics (steps, sleep, heart rate, blood pressure, body fat, oxygen saturation)
- **Workout History Upload**: Upload CSV files with past workout sessions for context
- **Available Workouts**: Pre-loaded with the complete workout library from the backend
- **Demo Data**: Quick-load mock data for testing

### 💬 Coaching Conversation
- Real-time chat interface with message history
- Personalized coaching recommendations based on provided data
- Token usage tracking (input/output tokens)
- Conversation persistence across sessions
- One-click conversation clear/refresh

### ⚡ Performance
- **Single API Call**: Unlike the tool-based approach, sends all data upfront
- **Faster Response**: No iterative tool calling (1-5 API calls)
- **Lower Token Cost**: All context provided at once
- **Deterministic**: Consistent response time

## File Structure

```
foodtein-streamlit-ai-nutritionist/
├── coach_app.py              # Main Streamlit application for the coach
├── coach_api_client.py       # API client for coach endpoints
├── config.py                 # Configuration (updated with coach endpoints)
├── app.py                    # Existing nutritionist app
├── api_client.py             # Existing nutritionist API client
├── requirements.txt          # Python dependencies
├── run.sh / run.bat          # Run scripts
└── COACH_APP.md             # This file
```

## Setup & Installation

### Prerequisites
- Python 3.8+
- Streamlit
- pandas
- requests
- Foodtein Backend running on `http://localhost:8080`

### Installation

1. **Install dependencies** (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure backend is running**:
   ```bash
   cd foodtein-backend
   go run main.go
   ```

3. **Run the coach app**:
   ```bash
   streamlit run coach_app.py
   ```

   Or use the included scripts:
   ```bash
   # Linux/Mac
   ./run.sh coach_app

   # Windows
   run.bat coach_app
   ```

The app will open at `http://localhost:8501`

## Usage Guide

### 1. Authentication
1. In the sidebar, enter your **Bearer Token** in the authentication field
2. The app will authenticate and show a success message
3. Tokens are stored in the session for subsequent requests

### 2. Profile Information
1. Enter your profile information in the sidebar:
   - **Name**: Your name (optional)
   - **Age**: Your age in years
   - **Gender**: Select male, female, or other
   - **Height**: Height in centimeters
   - **Weight**: Weight in kilograms

### 3. Upload Health Data (CSV)

Create a CSV file with the following format:

**headers.csv**:
```csv
date,metric,value
2026-02-07,steps,10000
2026-02-07,sleep_duration,8.0
2026-02-07,heart_rate,72
2026-02-07,blood_pressure_sys,120
2026-02-07,blood_pressure_dia,80
2026-02-07,body_fat,18.5
2026-02-07,oxygen_saturation,98.0
2026-02-06,steps,9500
2026-02-06,sleep_duration,7.5
```

Supported metrics:
- `steps` - Daily step count
- `sleep_duration` - Sleep duration in hours
- `heart_rate` - Resting heart rate in bpm
- `blood_pressure_sys` - Systolic blood pressure
- `blood_pressure_dia` - Diastolic blood pressure
- `body_fat` - Body fat percentage
- `oxygen_saturation` - O2 saturation percentage

### 4. Upload Workout History (CSV)

Create a CSV file with the following format:

**workouts.csv**:
```csv
date,workout_name,category,duration_mins,completed
2026-02-07,Full Body Strength,strength,45,true
2026-02-06,Cardio Blast,cardio,30,true
2026-02-05,Upper Body Focus,strength,40,true
2026-02-04,HIIT Training,cardio,25,false
2026-02-03,Yoga & Flexibility,flexibility,30,true
```

Supported categories:
- `strength` - Strength training workouts
- `cardio` - Cardiovascular workouts
- `flexibility` - Stretching and flexibility workouts

### 5. Start Coaching Conversation

1. You'll have access to a full workout library with 5+ pre-configured workouts
2. Type your question or request in the chat input
3. Examples:
   - "Give me a workout for today based on my fitness level"
   - "What should I do for upper body development?"
   - "I only have 30 minutes, what workout do you recommend?"
   - "Suggest a workout considering my recent activity"

4. The coach will respond with personalized recommendations from the available workout library

### 6. Quick Start with Demo Data

Click the **"Load Demo Data"** button to populate the app with sample profile, health, and workout data for immediate testing.

## API Endpoint

### New Endpoint: `POST /api/ai-coach/conversation/messages-with-data`

**Description**: Send a message to the AI Coach with custom health, workout, and profile data

**Authentication**: Bearer token required

**Request Body**:
```json
{
  "message": "What workout should I do today?",
  "name": "Alex Johnson",
  "age": 28,
  "gender": "Male",
  "height": 178.0,
  "weight": 75.0,
  "health_data": [
    {
      "recorded_at": "2026-02-07",
      "steps_count": 10000,
      "sleep_duration": 8.0,
      "heart_rate": 72,
      "blood_pressure_sys": 120,
      "blood_pressure_dia": 80,
      "body_fat": 18.5,
      "oxygen_saturation": 98.0
    }
  ],
  "workout_history": [
    {
      "date": "2026-02-07",
      "started_at": "2026-02-07T08:00:00Z",
      "is_completed": true,
      "duration_seconds": 2700
    }
  ],
  "available_workouts": [
    {
      "id": 1,
      "name": "Full Body Strength",
      "category": "strength",
      "duration_minutes": 45,
      "difficulty_level": "intermediate",
      "primary_muscles": "chest, back, legs",
      "exercises": [...]
    }
  ]
}
```

**Response**:
```json
{
  "conversation_uuid": "uuid-here",
  "user_message": {
    "uuid": "msg-uuid",
    "role": 0,
    "content": "What workout should I do today?",
    "created_at": "2026-02-10T12:00:00Z"
  },
  "assistant_message": {
    "uuid": "msg-uuid",
    "role": 1,
    "content": "Based on your profile and recent activity...",
    "input_tokens": 450,
    "output_tokens": 150,
    "created_at": "2026-02-10T12:00:05Z"
  }
}
```

## Backend Implementation

The backend implementation includes:

### Models (`internal/models/ai_coach_message.go`)
- **SendCoachMessageWithDataRequest**: Request structure with health, workout, and profile data

### Service (`internal/services/ai_coach_service.go`)
- **SendMessageWithData()**: Main method handling single API call without tools
- **buildFitnessProfileDataContext()**: Formats profile + health data
- **buildWorkoutsDataContext()**: Formats available workouts
- **buildWorkoutHistoryDataContext()**: Formats workout history

### Handler (`internal/handlers/ai_coach_handler.go`)
- **SendMessageWithData()**: HTTP handler for the new endpoint

### Routes (`main.go`)
- **POST /api/ai-coach/conversation/messages-with-data**: New endpoint

## Comparison: Tool-Based vs Data-Driven

| Aspect | Tool-Based | Data-Driven |
|--------|-----------|------------|
| API Calls | 2-5 (iterative) | 1 (single) |
| Response Time | Slower | ⚡ Faster |
| Token Usage | Higher | 💰 Lower |
| Data Flexibility | Dynamic (LLM decides) | Fixed (all upfront) |
| Latency | Variable | Predictable |
| User Control | Limited | Full control |

## Token Usage Tracking

The app tracks token usage for each message:
- **Input Tokens**: Tokens used in the request
- **Output Tokens**: Tokens used in the response
- **Total Tokens**: Sum of input and output
- **Cumulative**: Total across all messages in the session

## Session State

All data is stored in Streamlit session state:
- Authentication token
- Conversation messages
- Health data
- Workout history
- Available workouts
- User profile
- Token usage statistics

Session state persists while the app is running but resets on page refresh or script rerun.

## Troubleshooting

### Authentication Error
- Ensure your bearer token is correct
- Check that the backend is running on `http://localhost:8080`

### CSV Upload Error
- Verify CSV format matches the specified templates
- Check that date format is `YYYY-MM-DD`
- Ensure metric names match the supported list

### No Available Workouts
- Workouts are pre-loaded from mock data
- If needed, ensure the ChatCompletionRequest includes the workouts array

### Slow Response
- Check backend logs for issues
- Verify health data isn't excessively large
- Reduce conversation history if needed

## Notes

- The coach uses the existing workout library from the backend
- System prompt is optimized for fitness coaching without tools
- Short, practical responses are emphasized in the system prompt
- All data is provided to the AI upfront for context
- Conversation history is limited to the last 6 messages before the current one for efficiency

## Future Enhancements

Potential improvements:
- Export conversation history as PDF
- Save coaching plans to backend
- Integration with wearable device APIs
- Progress tracking and analytics
- Multi-user comparisons
- Scheduled coaching sessions

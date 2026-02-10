# AI Coach Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Start the Backend
```bash
cd foodtein-backend
go run main.go
```
Backend will run on `http://localhost:8080`

### Step 2: Run the Coach App
```bash
cd foodtein-streamlit-ai-nutritionist
streamlit run coach_app.py
```
App will open at `http://localhost:8501`

### Step 3: Test with Demo Data
1. In the sidebar, enter your Bearer Token (ask your admin for a test token)
2. Click **"Load Demo Data"** button
3. Type a message like: "What workout should I do today?"
4. Watch the coach respond with personalized recommendations!

---

## 📊 Test with Your Own Data

### Health Data CSV
Create `health_data.csv`:
```csv
date,metric,value
2026-02-07,steps,8500
2026-02-07,sleep_duration,8.0
2026-02-07,heart_rate,72
2026-02-07,blood_pressure_sys,120
2026-02-07,blood_pressure_dia,80
2026-02-07,body_fat,18.5
2026-02-07,oxygen_saturation,98.0
2026-02-06,steps,10200
2026-02-06,sleep_duration,7.5
2026-02-06,heart_rate,68
```

### Workout History CSV
Create `workout_history.csv`:
```csv
date,workout_name,category,duration_mins,completed
2026-02-07,Full Body Strength,strength,45,true
2026-02-06,Cardio Blast,cardio,30,true
2026-02-05,Upper Body Focus,strength,40,true
```

### Upload Steps
1. **Profile**: Enter name, age, gender, height, weight
2. **Health Data**: Upload `health_data.csv` in sidebar
3. **Workout History**: Upload `workout_history.csv` in sidebar
4. **Available Workouts**: Pre-loaded automatically
5. **Chat**: Start asking for workout recommendations!

---

## 💡 Example Questions

- "What's a good workout for today given my fitness level?"
- "I only have 30 minutes, what can I do?"
- "Recommend an upper body focused workout"
- "What should I do to improve my cardio?"
- "Give me a full body strength routine"
- "I'm tired, what's a light workout for recovery?"
- "How does my recent workout history look?"

---

## 🔧 What's Different from the Nutritionist App?

| Feature | Nutritionist | Coach |
|---------|-------------|-------|
| Data Input | Dietary + Health | Health + Workouts |
| API Calls | Tools (2-5 calls) | Data-driven (1 call) |
| Recommendations | Meal & Nutrition | Fitness & Workouts |
| Speed | Variable | Fast & Predictable |

---

## 📁 File Overview

### Backend Changes
- ✅ Added `SendCoachMessageWithDataRequest` model
- ✅ Added `SendMessageWithData()` service method
- ✅ Added `POST /api/ai-coach/conversation/messages-with-data` endpoint

### New Streamlit Files
- ✅ `coach_api_client.py` - API communication
- ✅ `coach_app.py` - Main application
- ✅ `COACH_APP.md` - Full documentation

---

## 🐛 Troubleshooting

### "Unauthorized" Error
- Check your Bearer token is correct
- Token should be in format: `bearer xyz123...`

### CSV Upload Failed
- Check date format is `YYYY-MM-DD`
- Verify metric names match supported list
- Ensure no extra spaces in column names

### No Response from Coach
- Check backend is running on `http://localhost:8080`
- Check logs for errors
- Try with demo data first

### Workouts Not Showing
- Workouts are pre-loaded and included by default
- They appear automatically in the coach's recommendations

---

## 📞 Need Help?

Check these resources:
1. **Backend Issues**: See `foodtein-backend/QUICKSTART.md`
2. **App Documentation**: See `foodtein-streamlit-ai-nutritionist/COACH_APP.md`
3. **Implementation Details**: See `IMPLEMENTATION_SUMMARY.md`

---

## ✨ Key Features

🎯 **Smart Recommendations** - Personalized based on your profile and history
⚡ **Fast Response** - Single API call, no tool iterations
📊 **Track Progress** - See token usage and view conversation history
🔄 **Easy Data Input** - Simple CSV upload or manual entry
💾 **Persistent Chat** - Conversation history saved across sessions
🚀 **Demo Ready** - One-click demo data for instant testing

---

Enjoy your AI Fitness Coach! 🏋️💪

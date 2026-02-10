# AI Nutritionist Chat - Streamlit Testing UI

A comprehensive testing interface for the AI Nutritionist service. Test conversation flows, token usage, and message handling with a real-time UI that mimics the exact logic from the backend `SendMessage` function.

## Quick Start

### Prerequisites
- Python 3.8+
- Go backend running on `http://localhost:8080`
- The foodtein-backend API server started

### Installation

```bash
cd streamlit-test
pip install -r requirements.txt
```

### Run the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## Features

### 🔗 Backend Integration
- **Real API Connection**: Connects directly to your Go backend
- **Mock JWT Tokens**: Auto-generates test tokens for authentication
- **No Database Required**: Uses the backend's existing mock data
- **3 Core Endpoints**: Get conversation, send message, clear history

### 💬 Conversation Testing
- **Multi-turn Chat**: Leverages backend's conversation history management
- **Message Display**: Shows user and assistant messages with timestamps
- **Token Tracking**: Displays input/output tokens per message and cumulative totals
- **Auto-refresh**: Conversation loads and updates in real-time

### 📊 Data Management
- **CSV Upload**: Upload health metrics and dietary intake data
- **Data Preview**: View uploaded data in the sidebar
- **Templates**: Download example CSV templates for proper formatting
- **Session Persistence**: Data stays in session across messages

### 🤖 AI Features Tested
- **Function Calling**: Backend uses OpenAI function tools to fetch health/dietary data
- **Message Alternation**: Duplicate consecutive messages are filtered
- **Iterative Processing**: Up to 5 API calls for multi-step LLM reasoning
- **Response Formatting**: AI keeps responses short (no tables/markdown)

## How to Use

### 1. Start the Backend

```bash
# In your foodtein-backend directory
go run main.go
```

Wait for the server to start on port 8080.

### 2. Launch Streamlit

```bash
# In the streamlit-test directory
streamlit run app.py
```

### 3. Send a Message

Type a message in the text area and click **📤 Send**:

**Simple Query** (no tool use):
- "Hello!"
- "What's a healthy breakfast?"
- These trigger 1 API call

**Data-based Query** (triggers function calls):
- "Can you analyze my dietary intake?"
- "Based on my health data, what should I eat?"
- These trigger 2+ API calls as the LLM requests user data

### 4. Monitor Token Usage
- Each message shows input/output tokens
- Cumulative token count in the right sidebar
- Useful for tracking API costs

### 5. Upload Data (Optional)

The chat works without data, but to provide context:

1. Download the CSV template from the sidebar
2. Fill it with your test data
3. Upload the CSV
4. Data appears in the sidebar preview
5. Reference it in your message: "I've uploaded my health metrics, can you..."

**Health Data CSV Format**:
```
date,metric,value
2026-02-10,Age,30
2026-02-10,Weight,70
2026-02-10,Steps,8234
2026-02-10,Sleep (hours),7.5
```

**Dietary Data CSV Format**:
```
date,meal_type,food_name,serving_size,unit,calories,protein,carbs,fat,fiber
2026-02-10,breakfast,Oatmeal,50,g,180,6,35,3,4
2026-02-10,lunch,Chicken,300,g,450,52,43,7,3
```

### 6. Clear History
Click **🗑️ Clear Chat** to delete the conversation from the backend and reset token counts.

### 7. Generate New Session
Click the **🔄** button next to "User Config" to generate a new mock token and user ID, creating a fresh conversation.

## What Gets Tested?

### Backend Logic Replicated

The Streamlit UI tests these exact flows from `SendMessage`:

1. **Conversation Management**
   - ✅ Get or create conversation
   - ✅ Store user message
   - ✅ Store assistant response with tokens
   - ✅ Update conversation timestamp

2. **Message History**
   - ✅ Last 6 messages included in context
   - ✅ Duplicate message alternation filtering
   - ✅ System prompt initialization

3. **API Integration**
   - ✅ First API call with tools available
   - ✅ LLM decides whether to use get_user_health_profile or get_user_dietary_intake
   - ✅ Up to 5 iterations of tool calling
   - ✅ Tool responses fed back into conversation

4. **Token Tracking**
   - ✅ Input/output tokens per message
   - ✅ Cumulative token usage across all API calls
   - ✅ Display in response

5. **Error Handling**
   - ✅ Connection failure detection
   - ✅ Timeout handling (60s max for LLM)
   - ✅ Invalid token detection
   - ✅ Server error messages

## Architecture

```
streamlit-test/
├── app.py                 # Main Streamlit UI (conversations, messaging, data upload)
├── api_client.py          # HTTP client wrapper (3 endpoints, error handling)
├── config.py              # API endpoints, mock token generation, CSV schemas
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

### Data Flow

```
User Input
    ↓
[Streamlit UI] ← → [API Client] ← → [Go Backend]
    ↓                                    ↓
Display Message                    OpenAI LLM (with function tools)
Update Tokens                       Store in PostgreSQL
Store in Session State              Return response + tokens
```

## Testing Scenarios

### Scenario 1: Simple Greeting
```
User: "Hi there!"
→ 1 API call
→ LLM returns greeting
→ No tools needed
→ ~50-100 tokens used
```

### Scenario 2: Health-Based Question
```
User: "I've uploaded my health data. What should I eat today?"
→ 1st API call: LLM decides to call get_user_health_profile
→ 2nd API call: LLM receives health data, calls get_user_dietary_intake
→ 3rd API call: LLM receives both, generates response
→ ~800-1200 tokens used
```

### Scenario 3: Conversation Context
```
User: "What's a healthy breakfast?"
→ Response 1: AI suggests options
→ User: "Can I do that with eggs?"
→ Response 2: Last message + your question used together
→ Shows context usage
```

## Troubleshooting

### ❌ "Cannot connect to backend"
- Is the Go server running on `http://localhost:8080`?
- Check firewall settings
- Verify no port conflicts

### ❌ "Unauthorized - invalid token"
- Click the 🔄 button to regenerate a mock token
- Ensure backend is expecting Bearer token auth

### ❌ "Request timeout"
- LLM calls can take 30-60 seconds
- Wait for response or check backend logs
- Timeout is set to 60s in api_client.py

### ❌ CSV Upload Failed
- Verify column names match the templates exactly (case-sensitive)
- Check for proper date format: YYYY-MM-DD
- Download and use the provided template as base

### 🔍 Can't see uploaded data in conversation
- **Expected!** Data is shown in sidebar preview only
- AI references it based on context you provide
- If you want AI to use it, mention it in your message

## Configuration

### API Base URL
Edit in `config.py`:
```python
API_BASE_URL = "http://localhost:8080/api"  # Change if backend is on different host
```

### Mock Token Settings
Generate tokens with custom payload in `config.py`:
```python
def generate_mock_jwt_token():
    # Customize headers, payload, or signature here
    ...
```

### CSV Schemas
Modify expected columns in `config.py`:
```python
HEALTH_CSV_COLUMNS = ["date", "metric", "value"]
DIETARY_CSV_COLUMNS = [...]
```

## Performance Notes

- **First load**: ~2-3 seconds (loads conversation history)
- **Simple message**: ~1-5 seconds
- **Data-based message**: ~20-60 seconds (depends on LLM response time)
- **Token overhead**: ~150-200 per request (OpenAI API overhead)

## Limitations

- Mock JWT tokens are not validated by backend; backend must accept them
- CSV data is local only (sidebar preview); not uploaded to backend
- No real database integration (uses backend's mock data)
- Max 5 tool iterations to prevent infinite loops
- Session state resets on app restart

## Next Steps

1. **Test different queries** to see tool calling in action
2. **Monitor token usage** to estimate API costs
3. **Upload real data** from CSV to provide context
4. **Check backend logs** to see the exact LLM prompts and tool calls
5. **Generate conversation exports** for testing analytics

---

**Backend Reference**: See `/internal/handlers/ai_nutritionist_handler.go` and `/internal/services/ai_nutritionist_service.go` in foodtein-backend for implementation details.

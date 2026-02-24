"""
Streamlit AI Nutritionist Chat UI
Testing interface for the AI Nutritionist service using Streamlit Chat Elements
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from api_client import APIClient
from config import (
    TEST_TOKEN,
    MESSAGE_ROLE_USER,
    MESSAGE_ROLE_ASSISTANT,
    HEALTH_CSV_EXAMPLE,
    DIETARY_CSV_EXAMPLE,
)

# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title="AI Nutritionist Chat - Testing UI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# Session State Initialization
# ============================================================================

if "api_client" not in st.session_state:
    st.session_state.api_client = APIClient(TEST_TOKEN)
    st.session_state.token = TEST_TOKEN
    st.session_state.conversation_uuid = None
    st.session_state.messages = []
    st.session_state.total_input_tokens = 0
    st.session_state.total_output_tokens = 0
    st.session_state.health_data = HEALTH_CSV_EXAMPLE.copy()
    st.session_state.dietary_data = DIETARY_CSV_EXAMPLE.copy()
    st.session_state.initialized = False
    # Profile data
    st.session_state.profile_name = ""
    st.session_state.profile_age = 0
    st.session_state.profile_gender = ""
    st.session_state.profile_height = 0.0
    st.session_state.profile_weight = 0.0
    # Dietary preferences
    st.session_state.dietary_type = []  # Store as list
    st.session_state.food_allergies_text = ""
    st.session_state.disliked_foods_text = ""
    # Health conditions
    st.session_state.diseases_text = ""
    st.session_state.illnesses_text = ""

# ============================================================================
# Helper Functions
# ============================================================================

def load_initial_conversation():
    """Load conversation from backend on first load"""
    if not st.session_state.initialized:
        with st.spinner("Loading conversation..."):
            data, error = st.session_state.api_client.get_conversation()
            if data:
                st.session_state.conversation_uuid = data.get("uuid")
                st.session_state.messages = data.get("messages", [])
                st.session_state.initialized = True
            elif error:
                st.warning(f"Could not load conversation: {error}")
                st.session_state.initialized = True


def format_timestamp(iso_string: str) -> str:
    """Format ISO timestamp for display"""
    try:
        dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
        return dt.strftime("%H:%M:%S")
    except:
        return iso_string


def display_chat_messages():
    """Display all messages using Streamlit chat elements"""
    for msg in st.session_state.messages:
        role = msg.get("role", MESSAGE_ROLE_USER)
        content = msg.get("content", "")
        input_tokens = msg.get("input_tokens", 0)
        output_tokens = msg.get("output_tokens", 0)
        created_at = msg.get("created_at", "")
        
        # Determine role for st.chat_message
        if role == MESSAGE_ROLE_USER:
            avatar = "👤"
            name = "user"
        elif role == MESSAGE_ROLE_ASSISTANT:
            avatar = "🤖"
            name = "assistant"
        else:
            avatar = "❓"
            name = f"Unknown ({role})"
        
        with st.chat_message(name):
            # Display timestamp
            st.caption(f"🕐 {format_timestamp(created_at)}")
            
            # Display message content
            st.markdown(content)


def display_health_data_preview():
    """Display health data preview in sidebar"""
    st.subheader("📊 Health Data")
    
    if not st.session_state.health_data.empty:
        df = st.session_state.health_data
        
        if "date" in df.columns and "metric" in df.columns:
            # Get unique dates sorted
            unique_dates = sorted(df["date"].unique())
            
            # Keep only latest 7 days
            latest_7_dates = unique_dates[-7:] if len(unique_dates) > 7 else unique_dates
            
            # Show note about 7-day limit
            if len(unique_dates) > 7:
                st.caption(f"📌 Showing latest 7 of {len(unique_dates)} days")
            else:
                st.caption(f"📌 Showing {len(latest_7_dates)} day{'s' if len(latest_7_dates) != 1 else ''}")
            
            st.markdown(f"**Date Range:** {latest_7_dates[0]} to {latest_7_dates[-1]}")
            
            # Show data grouped by date with expanders (only latest 7 days)
            for date in latest_7_dates:
                with st.expander(f"📅 {date}"):
                    date_data = df[df["date"] == date]
                    for _, row in date_data.iterrows():
                        metric = row.get("metric", "")
                        value = row.get("value", "")
                        st.write(f"  • **{metric}:** {value}")
        else:
            st.info("No health data in records")
    else:
        st.info("No health data uploaded yet")


def display_dietary_data_preview():
    """Display dietary data preview in sidebar (up to 7 days)"""
    st.subheader("🍽️ Dietary Intake")
    
    if not st.session_state.dietary_data.empty:
        df = st.session_state.dietary_data
        
        if "date" in df.columns:
            # Get unique dates sorted
            unique_dates = sorted(df["date"].unique())
            
            # Keep only latest 7 days
            latest_7_dates = unique_dates[-7:] if len(unique_dates) > 7 else unique_dates
            
            # Show note about 7-day limit
            if len(unique_dates) > 7:
                st.caption(f"📌 Showing latest 7 of {len(unique_dates)} days")
            else:
                st.caption(f"📌 Showing {len(latest_7_dates)} day{'s' if len(latest_7_dates) != 1 else ''}")
            
            st.markdown(f"**Date Range:** {latest_7_dates[0]} to {latest_7_dates[-1]}")
            
            # Show meals grouped by date with expanders (only latest 7 days)
            for date in latest_7_dates:
                date_data = df[df["date"] == date]
                
                # Calculate daily totals
                daily_cals = date_data["calories"].sum() if "calories" in date_data.columns else 0
                daily_protein = date_data["protein"].sum() if "protein" in date_data.columns else 0
                
                with st.expander(f"📅 {date} | {daily_cals:.0f} cal"):
                    for _, row in date_data.iterrows():
                        meal_type = row.get("meal_type", "meal").title()
                        food_name = row.get("food_name", "")
                        serving_size = row.get("serving_size", "")
                        unit = row.get("unit", "")
                        calories = row.get("calories", 0)
                        protein = row.get("protein", 0)
                        carbs = row.get("carbs", 0)
                        fat = row.get("fat", 0)
                        
                        st.write(f"**{meal_type}** • {food_name}")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.caption(f"🔥 {calories:.0f} cal")
                        with col2:
                            st.caption(f"💪 {protein:.0f}g P")
                        with col3:
                            st.caption(f"🥕 {carbs:.0f}g C")
                        
                        if serving_size and unit:
                            st.caption(f"📏 {serving_size} {unit}")
                        st.divider()
        else:
            st.info("No date column in dietary data")
    else:
        st.info("No dietary data uploaded yet")


def parse_food_allergies(text: str) -> list:
    """
    Parse food allergies from text input
    Format: "peanuts:severe:swelling | shellfish:mild | tree nuts"
    Or simple list: "peanuts, shellfish, tree nuts"
    """
    if not text or not text.strip():
        return []
    
    allergies = []
    # Split by pipe or newline
    items = [item.strip() for item in text.replace('\n', '|').split('|') if item.strip()]
    
    for item in items:
        parts = [p.strip() for p in item.split(':')]
        allergy_dict = {"food_item": parts[0]}
        
        if len(parts) > 1:
            allergy_dict["severity"] = parts[1]
        if len(parts) > 2:
            allergy_dict["symptoms"] = parts[2]
        
        allergies.append(allergy_dict)
    
    return allergies


def parse_disliked_foods(text: str) -> list:
    """
    Parse disliked foods from text input
    Format: "broccoli:doesn't like texture | mushrooms:slimy texture"
    Or simple list: "broccoli, mushrooms, onions"
    """
    if not text or not text.strip():
        return []
    
    foods = []
    # Split by pipe or newline
    items = [item.strip() for item in text.replace('\n', '|').split('|') if item.strip()]
    
    for item in items:
        parts = [p.strip() for p in item.split(':')]
        food_dict = {"food_item": parts[0]}
        
        if len(parts) > 1:
            food_dict["reason"] = parts[1]
        
        foods.append(food_dict)
    
    return foods


def parse_diseases(text: str) -> list:
    """
    Parse diseases from text input
    Format: "diabetes:chronic:active:insulin | hypertension:chronic:managed"
    Or simpler: "diabetes:chronic | hypertension"
    """
    if not text or not text.strip():
        return []
    
    diseases = []
    items = [item.strip() for item in text.replace('\n', '|').split('|') if item.strip()]
    
    for item in items:
        parts = [p.strip() for p in item.split(':')]
        disease_dict = {"name": parts[0]}
        
        if len(parts) > 1:
            disease_dict["type"] = parts[1]  # chronic, acute, genetic, infectious
        if len(parts) > 2:
            disease_dict["status"] = parts[2]  # active, managed, cured, in_treatment
        if len(parts) > 3:
            disease_dict["medication"] = parts[3]
        
        diseases.append(disease_dict)
    
    return diseases


def parse_illnesses(text: str) -> list:
    """
    Parse illnesses from text input
    Format: "flu:moderate:recovering | cold:mild:active"
    Or simple: "flu | cold:mild"
    """
    if not text or not text.strip():
        return []
    
    illnesses = []
    items = [item.strip() for item in text.replace('\n', '|').split('|') if item.strip()]
    
    for item in items:
        parts = [p.strip() for p in item.split(':')]
        illness_dict = {"name": parts[0]}
        
        if len(parts) > 1:
            illness_dict["severity"] = parts[1]  # mild, moderate, severe
        if len(parts) > 2:
            illness_dict["status"] = parts[2]  # active, recovered, chronic
        
        illnesses.append(illness_dict)
    
    return illnesses


def filter_last_7_days(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter a pandas DataFrame to only include rows from the latest 7 calendar days.
    
    Args:
        df: DataFrame with a "date" column
        
    Returns:
        Filtered DataFrame with only the latest 7 days of data.
        If DataFrame is empty or has no "date" column, returns the original DataFrame.
    """
    if df.empty or "date" not in df.columns:
        return df
    
    try:
        # Get unique dates and sort them
        unique_dates = sorted(df["date"].unique())
        
        # If 7 or fewer unique dates, return all data
        if len(unique_dates) <= 7:
            return df
        
        # Get the latest 7 dates
        latest_7_dates = unique_dates[-7:]
        
        # Filter DataFrame to only include rows with dates in the latest 7
        filtered_df = df[df["date"].isin(latest_7_dates)].copy()
        
        return filtered_df
    except Exception as e:
        # If any error occurs, return original DataFrame
        st.warning(f"Error filtering data to 7 days: {e}")
        return df


# ============================================================================
# Main App Layout
# ============================================================================

# Title
st.title("🤖 AI Nutritionist Chat")
st.markdown("Test the AI Nutritionist service with real-time conversation tracking")

# Load initial conversation
load_initial_conversation()

# Sidebar Configuration
with st.sidebar:
    st.title("⚙️ Settings")
    
    # Connection Status
    is_connected, status_msg = st.session_state.api_client.check_connection()
    
    if is_connected:
        st.success(status_msg)
    else:
        st.error(status_msg)
        st.info("💡 Make sure the Go backend is running on http://localhost:8080")
    
    st.divider()
    
    # User Configuration
    st.subheader("👤 Test User")
    # st.caption(f"🔐 Token: `{TEST_TOKEN}`")
    st.caption("Backend authenticates as: `user_streamlit_001`")
    
    if st.session_state.conversation_uuid:
        st.caption(f"**Conv ID:**\n`{str(st.session_state.conversation_uuid)[:8]}...`")
    
    st.divider()
    
    # Profile Data
    st.subheader("📋 User Profile")
    st.session_state.profile_name = st.text_input("Name", value=st.session_state.profile_name)
    st.session_state.profile_age = st.number_input("Age", value=st.session_state.profile_age, min_value=0, max_value=150)
    st.session_state.profile_gender = st.selectbox("Gender", ["", "Male", "Female", "Other"], 
                                                     index=["", "Male", "Female", "Other"].index(st.session_state.profile_gender) if st.session_state.profile_gender in ["", "Male", "Female", "Other"] else 0)
    st.session_state.profile_height = st.number_input("Height (cm)", value=st.session_state.profile_height, min_value=0.0, step=0.1)
    st.session_state.profile_weight = st.number_input("Weight (kg)", value=st.session_state.profile_weight, min_value=0.0, step=0.1)
    
    st.divider()
    
    # Dietary Preferences
    st.subheader("🥗 Dietary Preferences")
    
    # Dietary Type (multiple selection)
    dietary_type_options = ["Halal", "Vegetarian", "Vegan", "Pescatarian", "Kosher"]
    st.session_state.dietary_type = st.multiselect(
        "Dietary Type (select one or more)",
        dietary_type_options,
        default=st.session_state.dietary_type,
        key="dietary_type_multiselect"
    )
    
    # Food Allergies
    st.markdown("**Food Allergies**")
    st.caption("Format: food:severity:symptoms (e.g., peanuts:severe:swelling) or simple list")
    st.session_state.food_allergies_text = st.text_area(
        "Food Allergies",
        value=st.session_state.food_allergies_text,
        placeholder="peanuts:severe:swelling\nshellfish:mild\ntree nuts",
        height=80,
        label_visibility="collapsed"
    )
    
    # Disliked Foods
    st.markdown("**Disliked Foods**")
    st.caption("Format: food:reason (e.g., broccoli:slimy texture) or simple list")
    st.session_state.disliked_foods_text = st.text_area(
        "Disliked Foods",
        value=st.session_state.disliked_foods_text,
        placeholder="broccoli:doesn't like texture\nmushrooms\nonions",
        height=80,
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Health Conditions
    st.subheader("🏥 Health Conditions")
    
    # Diseases
    st.markdown("**Chronic/Acute Diseases**")
    st.caption("Format: name:type:status:medication (e.g., diabetes:chronic:active:insulin) or simple")
    st.session_state.diseases_text = st.text_area(
        "Diseases",
        value=st.session_state.diseases_text,
        placeholder="diabetes:chronic:active:insulin\nhypertension:chronic:managed\narthritis",
        height=80,
        label_visibility="collapsed"
    )
    
    # Illnesses
    st.markdown("**Recent Illnesses**")
    st.caption("Format: name:severity:status (e.g., flu:moderate:recovering) or simple")
    st.session_state.illnesses_text = st.text_area(
        "Illnesses",
        value=st.session_state.illnesses_text,
        placeholder="flu:moderate:recovering\ncold:mild:active\nfever",
        height=80,
        label_visibility="collapsed"
    )
    
    st.divider()
    st.subheader("📤 Upload Data")
    
    # Health Data
    st.markdown("**Health Metrics**")
    health_file = st.file_uploader(
        "Upload health data CSV",
        type="csv",
        key="health_upload",
        label_visibility="collapsed"
    )
    
    if health_file:
        try:
            df = pd.read_csv(health_file)
            st.session_state.health_data = df
            st.success(f"✅ Loaded {len(df)} records")
        except Exception as e:
            st.error(f"Error: {e}")
    
    if st.button("📥 Download Health Template", key="health_template"):
        csv = HEALTH_CSV_EXAMPLE.to_csv(index=False)
        st.download_button(
            label="health_data_template.csv",
            data=csv,
            file_name="health_data_template.csv",
            mime="text/csv",
            key="download_health"
        )
    
    st.divider()
    
    # Dietary Data
    st.markdown("**Dietary Intake**")
    dietary_file = st.file_uploader(
        "Upload dietary data CSV",
        type="csv",
        key="dietary_upload",
        label_visibility="collapsed"
    )
    
    if dietary_file:
        try:
            df = pd.read_csv(dietary_file)
            st.session_state.dietary_data = df
            st.success(f"✅ Loaded {len(df)} records")
        except Exception as e:
            st.error(f"Error: {e}")
    
    if st.button("📥 Download Dietary Template", key="dietary_template"):
        csv = DIETARY_CSV_EXAMPLE.to_csv(index=False)
        st.download_button(
            label="dietary_data_template.csv",
            data=csv,
            file_name="dietary_data_template.csv",
            mime="text/csv",
            key="download_dietary"
        )
    
    st.divider()
    
    # Data Preview
    st.subheader("👁️ Data Preview")
    display_health_data_preview()
    st.divider()
    display_dietary_data_preview()
    
    # Clear confirmation modal function
    @st.dialog("⚠️ Clear Conversation", width="small")
    def clear_confirmation():
        st.write("**Are you sure you want to clear all messages?**")
        st.info("💡 Your health data, dietary data, and profile will remain saved. Only chat history will be deleted.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, Clear All", key="confirm_clear", use_container_width=True):
                with st.spinner("Clearing..."):
                    success, error = st.session_state.api_client.clear_conversation()
                if error:
                    st.error(error)
                else:
                    st.session_state.messages = []
                    st.session_state.total_input_tokens = 0
                    st.session_state.total_output_tokens = 0
                    st.success("✅ Conversation cleared!")
                    st.rerun()
        
        with col2:
            if st.button("❌ Cancel", key="cancel_clear", use_container_width=True):
                pass
    
    # Action Buttons
    st.divider()
    
    st.markdown("**🔄 Conversation Management**")
    st.caption("Clear chat history and reset tokens. Your data remains saved.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Refresh", key="refresh", use_container_width=True):
            with st.spinner("Loading conversation..."):
                data, error = st.session_state.api_client.get_conversation()
            if error:
                st.error(error)
            else:
                st.session_state.messages = data.get("messages", [])
                st.success("✅ Refreshed!")
                st.rerun()
    
    with col2:
        if st.button("🗑️ Clear", key="clear", use_container_width=True):
            clear_confirmation()

# ============================================================================
# Main Chat Area (using Streamlit chat elements)
# ============================================================================

# Display all messages
display_chat_messages()

# Chat input (positioned at bottom of page)
if prompt := st.chat_input("Ask about nutrition, meal planning, dietary advice..."):
    if not is_connected:
        st.error("❌ Cannot connect to backend. Is it running?")
    else:
        # Show user message immediately
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response with health and dietary data
        with st.spinner("🤖 Waiting for response..."):
            # Convert DataFrames to list of dicts for API, filtering to latest 7 days
            health_df_filtered = filter_last_7_days(st.session_state.health_data)
            dietary_df_filtered = filter_last_7_days(st.session_state.dietary_data)
            
            health_data_list = health_df_filtered.to_dict('records') if not health_df_filtered.empty else []
            dietary_data_list = dietary_df_filtered.to_dict('records') if not dietary_df_filtered.empty else []
            
            # Parse dietary preferences
            food_allergies = parse_food_allergies(st.session_state.food_allergies_text)
            disliked_foods = parse_disliked_foods(st.session_state.disliked_foods_text)
            
            # Parse health conditions
            diseases = parse_diseases(st.session_state.diseases_text)
            illnesses = parse_illnesses(st.session_state.illnesses_text)
            
            response_data, error = st.session_state.api_client.send_message_with_data(
                prompt,
                health_data=health_data_list,
                dietary_data=dietary_data_list,
                name=st.session_state.profile_name,
                age=st.session_state.profile_age,
                gender=st.session_state.profile_gender,
                height=st.session_state.profile_height,
                weight=st.session_state.profile_weight,
                dietary_type=", ".join(st.session_state.dietary_type) if st.session_state.dietary_type else "",
                food_allergies=food_allergies,
                disliked_foods=disliked_foods,
                diseases=diseases,
                illnesses=illnesses
            )
        
        if error:
            st.error(f"Error: {error}")
        else:
            # Update session state
            user_msg = response_data.get("user_message", {})
            assistant_msg = response_data.get("assistant_message", {})
            
            st.session_state.messages.append({
                "uuid": user_msg.get("uuid"),
                "role": MESSAGE_ROLE_USER,
                "content": user_msg.get("content"),
                "created_at": user_msg.get("created_at"),
                "input_tokens": 0,
                "output_tokens": 0,
            })
            
            st.session_state.messages.append({
                "uuid": assistant_msg.get("uuid"),
                "role": MESSAGE_ROLE_ASSISTANT,
                "content": assistant_msg.get("content"),
                "created_at": assistant_msg.get("created_at"),
                "input_tokens": assistant_msg.get("input_tokens", 0),
                "output_tokens": assistant_msg.get("output_tokens", 0),
            })
            
            st.session_state.total_input_tokens += assistant_msg.get("input_tokens", 0)
            st.session_state.total_output_tokens += assistant_msg.get("output_tokens", 0)
            st.session_state.conversation_uuid = response_data.get("conversation_uuid")
            
            st.rerun()

# st.divider()
# st.caption("""
# **About this UI:**
# - 🔗 Connects to real Go backend at `http://localhost:8080`
# - 🔐 Uses mock JWT tokens for testing
# - � Built with Streamlit Chat Elements (`st.chat_message`, `st.chat_input`)
# - 📊 Displays token usage per message
# - 📂 Upload CSV files for health/dietary context
# - 💾 Conversation history persists in session state
# """)

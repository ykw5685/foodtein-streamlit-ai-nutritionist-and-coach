"""
AI Coach Streamlit Application

A conversational interface for personalized fitness coaching with data upload capabilities
"""

import json
import os
from typing import Optional, List, Dict
import io

import streamlit as st
import pandas as pd

import config
from config import TEST_TOKEN, COACH_HEALTH_CSV_EXAMPLE, COACH_WORKOUT_CSV_EXAMPLE
from coach_api_client import CoachAPIClient


def filter_last_7_days_dict(data_list: List[Dict]) -> List[Dict]:
    """
    Filter a list of dictionaries to only include records from the latest 7 calendar days.
    
    Args:
        data_list: List of dictionaries with a "date" key
        
    Returns:
        Filtered list containing only records from the latest 7 calendar days.
        If list is empty or no dictionaries have a "date" key, returns the original list.
    """
    if not data_list or not isinstance(data_list, list):
        return data_list
    
    try:
        # Extract unique dates from the list
        dates = set()
        for item in data_list:
            if isinstance(item, dict) and "date" in item:
                dates.add(str(item["date"]))
        
        if not dates:
            # No date field found, return original list
            return data_list
        
        # Sort dates and get the latest 7
        sorted_dates = sorted(dates)
        
        # If 7 or fewer unique dates, return all data
        if len(sorted_dates) <= 7:
            return data_list
        
        # Get the latest 7 dates
        latest_7_dates = set(sorted_dates[-7:])
        
        # Filter the list to only include items with dates in the latest 7
        filtered_list = [item for item in data_list if isinstance(item, dict) and str(item.get("date", "")) in latest_7_dates]
        
        return filtered_list
    except Exception as e:
        # If any error occurs, return original list
        print(f"Error filtering data to 7 days: {e}")
        return data_list


def setup_page():
    """Setup Streamlit page configuration"""
    st.set_page_config(
        page_title="AI Fitness Coach",
        page_icon="🏋️",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def setup_session_state():
    """Setup Streamlit session state"""
    if "coach_auth_token" not in st.session_state:
        st.session_state.coach_auth_token = TEST_TOKEN
        st.session_state.coach_client = CoachAPIClient(auth_token=TEST_TOKEN)

    if "coach_messages" not in st.session_state:
        st.session_state.coach_messages = []

    if "coach_health_data" not in st.session_state:
        st.session_state.coach_health_data = []

    if "coach_available_workouts" not in st.session_state:
        st.session_state.coach_available_workouts = CoachAPIClient.create_mock_available_workouts()

    if "coach_profile" not in st.session_state:
        st.session_state.coach_profile = {
            "name": "",
            "age": 0,
            "gender": "",
            "height": 0.0,
            "weight": 0.0,
        }

    if "coach_conversation_uuid" not in st.session_state:
        st.session_state.coach_conversation_uuid = None

    if "coach_show_clear_confirmation" not in st.session_state:
        st.session_state.coach_show_clear_confirmation = False


def show_authentication_status():
    """Show authentication status"""
    st.sidebar.write("---")
    st.sidebar.subheader("� Test User")
    
    # Connection Status
    is_connected, status_msg = st.session_state.coach_client.check_connection()
    
    if is_connected:
        st.sidebar.success(status_msg)
    else:
        st.sidebar.error(status_msg)
        st.sidebar.info("💡 Make sure the Go backend is running on http://localhost:8080")
    
    st.sidebar.caption("Backend authenticates as: `user_streamlit_001`")
    
    if st.session_state.coach_conversation_uuid:
        st.sidebar.caption(f"**Conv ID:**\n`{str(st.session_state.coach_conversation_uuid)[:8]}...`")


def upload_profile_data():
    """Handle profile data input"""
    st.sidebar.write("---")
    st.sidebar.subheader("👤 Profile Information")

    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.session_state.coach_profile["name"] = st.text_input(
            "Name", value=st.session_state.coach_profile["name"]
        )
        st.session_state.coach_profile["age"] = st.number_input(
            "Age", value=st.session_state.coach_profile["age"], min_value=0, max_value=150
        )

    with col2:
        st.session_state.coach_profile["gender"] = st.selectbox(
            "Gender",
            ["", "Male", "Female", "Other"],
            index=0,
        )
        if st.session_state.coach_profile["gender"] == "":
            st.session_state.coach_profile["gender"] = None

    col1, col2 = st.sidebar.columns(2)
    with col1:
        st.session_state.coach_profile["height"] = st.number_input(
            "Height (cm)", value=st.session_state.coach_profile["height"], min_value=0.0
        )
    with col2:
        st.session_state.coach_profile["weight"] = st.number_input(
            "Weight (kg)", value=st.session_state.coach_profile["weight"], min_value=0.0
        )


def upload_csv_data():
    """Handle CSV file uploads"""
    st.sidebar.write("---")
    st.sidebar.subheader("📊 Health Data (CSV)")

    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("📥 Download Template", key="coach_health_template"):
            csv = COACH_HEALTH_CSV_EXAMPLE.to_csv(index=False)
            st.download_button(
                label="health_data_template.csv",
                data=csv,
                file_name="health_data_template.csv",
                mime="text/csv",
                key="coach_download_health"
            )
    
    with col2:
        st.write("")

    health_file = st.sidebar.file_uploader(
        "Upload Health Data (CSV)", type="csv", key="coach_health_csv", label_visibility="collapsed"
    )

    if health_file:
        try:
            df = pd.read_csv(health_file)
            health_data = st.session_state.coach_client.format_health_data_for_api(df)
            st.session_state.coach_health_data = health_data
            st.sidebar.success(f"✅ Loaded {len(health_data)} health record(s)")
        except Exception as e:
            st.sidebar.error(f"❌ Error loading health data: {str(e)}")


def display_coach_health_data_preview():
    """Display health data preview in sidebar"""
    st.sidebar.subheader("📊 Health Data")
    
    if st.session_state.coach_health_data:
        health_data = st.session_state.coach_health_data
        
        if len(health_data) > 0 and isinstance(health_data[0], dict):
            # Group by recorded_at date (the format returned by format_health_data_for_api)
            dates_dict = {}
            for record in health_data:
                date = record.get("recorded_at", "Unknown")
                if date not in dates_dict:
                    dates_dict[date] = record
                    
            # Get unique dates sorted
            unique_dates = sorted(dates_dict.keys())
            
            # Keep only latest 7 days
            latest_7_dates = unique_dates[-7:] if len(unique_dates) > 7 else unique_dates
            
            # Show note about 7-day limit
            if len(unique_dates) > 7:
                st.sidebar.caption(f"📌 Showing latest 7 of {len(unique_dates)} days")
            else:
                st.sidebar.caption(f"📌 Showing {len(latest_7_dates)} day{'s' if len(latest_7_dates) != 1 else ''}")
            
            if latest_7_dates:
                st.sidebar.markdown(f"**Date Range:** {latest_7_dates[0]} to {latest_7_dates[-1]}")
            
                # Show data grouped by date with expanders (ONLY: Steps, Sleep, Heart Rate)
                for date in latest_7_dates:
                    record = dates_dict.get(date, {})
                    with st.sidebar.expander(f"📅 {date}"):
                        # Only show metrics that the coach actually uses
                        if record.get("steps_count") is not None:
                            st.write(f"  • **Steps:** {record['steps_count']}")
                        if record.get("sleep_duration") is not None:
                            st.write(f"  • **Sleep Duration:** {record['sleep_duration']} hours")
                        if record.get("heart_rate") is not None:
                            st.write(f"  • **Heart Rate:** {record['heart_rate']} bpm")
        else:
            st.sidebar.info("No health data in expected format")
    else:
        st.sidebar.info("No health data uploaded yet")


def display_available_workouts_preview():
    """Display available workouts preview in sidebar with full details"""
    st.sidebar.subheader("💪 Available Workouts")
    
    if st.session_state.coach_available_workouts:
        workouts = st.session_state.coach_available_workouts
        st.sidebar.caption(f"📌 {len(workouts)} workouts available")
        
        # Group by category
        categories = {}
        for workout in workouts:
            category = workout.get("category", "Other")
            if category not in categories:
                categories[category] = []
            categories[category].append(workout)
        
        # Display by category
        for category in sorted(categories.keys()):
            category_workouts = categories[category]
            with st.sidebar.expander(f"📂 {category.title()} ({len(category_workouts)})"):
                for workout in category_workouts:
                    name = workout.get("name", "Unknown")
                    st.write(f"**{name}**")
                    
                    # Show key details
                    details = []
                    if workout.get("difficulty_level"):
                        details.append(f"💎 {workout['difficulty_level']}")
                    if workout.get("duration_minutes"):
                        details.append(f"⏱️ {workout['duration_minutes']} min")
                    if details:
                        st.caption(" | ".join(details))
                    
                    # Description
                    if workout.get("description"):
                        st.caption(f"__{workout['description']}__")
                    
                    # Muscle groups
                    muscles = []
                    if workout.get("primary_muscles"):
                        muscles.append(f"**Primary:** {workout['primary_muscles']}")
                    if workout.get("secondary_muscles"):
                        muscles.append(f"**Secondary:** {workout['secondary_muscles']}")
                    if muscles:
                        st.caption("\n".join(muscles))
                    
                    # Equipment
                    equipment = workout.get("equipment", [])
                    if equipment:
                        eq_names = [eq.get("name", "") for eq in equipment if isinstance(eq, dict)]
                        if eq_names:
                            st.caption(f"🎯 Equipment: {', '.join(eq_names)}")
                    else:
                        st.caption("🎯 Equipment: None (Bodyweight)")
                    
                    # Exercises
                    exercises = workout.get("exercises", [])
                    if exercises:
                        st.caption("**Exercises:**")
                        for i, ex in enumerate(exercises, 1):
                            ex_str = f"{i}. {ex.get('name', 'Unknown')}"
                            details = []
                            if ex.get("reps"):
                                details.append(f"{ex['reps']} reps")
                            if ex.get("sets"):
                                details.append(f"{ex['sets']} sets")
                            if ex.get("duration_seconds"):
                                details.append(f"{ex['duration_seconds']}s")
                            if details:
                                ex_str += f" ({', '.join(details)})"
                            st.caption(f"  • {ex_str}")
                    
                    st.divider()
    else:
        st.sidebar.info("No available workouts loaded")


def show_data_preview():
    """Show preview of loaded data"""
    st.sidebar.write("---")
    st.sidebar.subheader("📋 Data Preview")

    display_coach_health_data_preview()
    st.sidebar.divider()
    display_available_workouts_preview()

    if st.session_state.coach_profile["name"]:
        st.sidebar.divider()
        st.sidebar.subheader("👤 Profile")
        st.sidebar.write(f"✅ **{st.session_state.coach_profile['name']}**")
        
        # Calculate BMI
        height_m = st.session_state.coach_profile.get("height", 0) / 100
        weight = st.session_state.coach_profile.get("weight", 0)
        bmi = weight / (height_m ** 2) if height_m > 0 else 0
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.sidebar.caption(f"Age: {st.session_state.coach_profile['age']}")
            st.sidebar.caption(f"Gender: {st.session_state.coach_profile['gender']}")
        with col2:
            st.sidebar.caption(f"Height: {st.session_state.coach_profile['height']} cm")
            st.sidebar.caption(f"Weight: {st.session_state.coach_profile['weight']} kg")
        
        # Show BMI with color indicator
        st.sidebar.divider()
        bmi_color = "🟢" if bmi < 25 else "🟡" if bmi < 30 else "🔴"
        st.sidebar.metric("BMI", f"{bmi:.1f}")
        st.sidebar.caption(f"{bmi_color} {bmi:.1f}")



def show_clear_confirmation_modal():
    """Show clear confirmation modal in main area"""
    if st.session_state.coach_show_clear_confirmation:
        st.divider()
        st.write("**Are you sure you want to clear all messages?**")
        st.info("💡 Your health data, workout history, and profile will remain saved. Only chat history will be deleted.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, Clear All", key="coach_confirm_clear", use_container_width=True):
                with st.spinner("Clearing..."):
                    try:
                        st.session_state.coach_client.clear_conversation()
                    except:
                        pass
                st.session_state.coach_messages = []
                st.session_state.coach_show_clear_confirmation = False
                st.success("✅ Conversation cleared!")
                st.rerun()
        
        with col2:
            if st.button("❌ Cancel", key="coach_cancel_clear", use_container_width=True):
                st.session_state.coach_show_clear_confirmation = False
                st.rerun()


def show_conversation_controls():
    """Show conversation control buttons"""
    st.sidebar.write("---")
    st.sidebar.subheader("🗣️ Conversation")
    st.sidebar.caption("Clear chat history. Your data remains saved.")

    col1, col2 = st.sidebar.columns(2)

    with col1:
        if st.button("🔄 Refresh", key="coach_refresh_conv", use_container_width=True):
            with st.spinner("Loading conversation..."):
                try:
                    conversation = st.session_state.coach_client.get_conversation()
                    st.session_state.coach_conversation_uuid = conversation.get("uuid")
                    st.session_state.coach_messages = conversation.get("messages", [])
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    return
            st.success("✅ Refreshed!")
            st.rerun()

    with col2:
        if st.button("🗑️ Clear", key="coach_clear_conv", use_container_width=True):
            st.session_state.coach_show_clear_confirmation = True
            st.rerun()


def display_messages():
    """Display conversation messages"""
    for message in st.session_state.coach_messages:
        role = "🤖 Coach" if message["role"] == "assistant" else "👤 You"
        with st.chat_message(role):
            st.write(message["content"])


def send_message(user_message: str):
    """Send a message to the AI Coach"""
    if not st.session_state.coach_client or not st.session_state.coach_auth_token:
        st.error("❌ Please authenticate first")
        return

    if not user_message.strip():
        st.error("❌ Please enter a message")
        return

    # Validate profile data
    profile = st.session_state.coach_profile
    validation_errors = []
    
    if not profile.get("name") or not str(profile.get("name")).strip():
        validation_errors.append("Name")
    if not profile.get("age") or profile.get("age") <= 0:
        validation_errors.append("Age (must be > 0)")
    if not profile.get("gender") or not str(profile.get("gender")).strip():
        validation_errors.append("Gender")
    if not profile.get("height") or profile.get("height") <= 0:
        validation_errors.append("Height (must be > 0)")
    if not profile.get("weight") or profile.get("weight") <= 0:
        validation_errors.append("Weight (must be > 0)")
    
    if validation_errors:
        st.error(f"❌ Please fill in all profile fields:\n- " + "\n- ".join(validation_errors))
        return

    try:
        # Show loading state
        with st.spinner("🤔 Coach is thinking..."):
            # Filter health data to latest 7 days before sending to API
            health_data_filtered = filter_last_7_days_dict(st.session_state.coach_health_data)
            
            print(f"DEBUG: Sending message with {len(health_data_filtered)} health records")
            print(f"DEBUG: Profile: {profile}")
            
            response = st.session_state.coach_client.send_message_with_data(
                message=user_message,
                health_data=health_data_filtered,
                workout_history=[],
                available_workouts=st.session_state.coach_available_workouts,
                name=profile.get("name"),
                age=int(profile.get("age")),
                gender=profile.get("gender"),
                height=float(profile.get("height")),
                weight=float(profile.get("weight")),
            )
        
        print(f"DEBUG: Response type: {type(response)}")
        print(f"DEBUG: Response: {response}")

        if not response:
            st.error("❌ No response from server")
            return

        # Update conversation UUID
        st.session_state.coach_conversation_uuid = response.get("conversation_uuid")

        # Add user message
        user_msg = response.get("user_message", {})
        if not user_msg or not user_msg.get("content"):
            st.error("❌ Invalid response format from server")
            print(f"DEBUG: user_message missing or invalid: {user_msg}")
            return
            
        st.session_state.coach_messages.append({
            "role": "user",
            "content": user_msg.get("content"),
        })

        # Add assistant message
        assistant_msg = response.get("assistant_message", {})
        if not assistant_msg or not assistant_msg.get("content"):
            st.error("❌ No coach response received")
            print(f"DEBUG: assistant_message missing or invalid: {assistant_msg}")
            return
            
        st.session_state.coach_messages.append({
            "role": "assistant",
            "content": assistant_msg.get("content"),
        })

        st.success("✅ Message sent and response received!")
        st.rerun()

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        print(f"DEBUG: Exception: {str(e)}")
        import traceback
        traceback.print_exc()



def main():
    """Main Streamlit application"""
    setup_page()
    setup_session_state()

    # Header
    st.title("🏋️ AI Fitness Coach")
    st.markdown("Get personalized workout recommendations backed by your health data")

    # Sidebar
    with st.sidebar:
        st.header("Settings")

        show_authentication_status()
        upload_profile_data()
        upload_csv_data()
        show_data_preview()
        show_conversation_controls()

        # Demo data button
        st.write("---")
        if st.button("📌 Load Demo Data", key="coach_load_demo"):
            st.session_state.coach_health_data = CoachAPIClient.create_mock_health_data()
            st.session_state.coach_profile = {
                "name": "Alex Johnson",
                "age": 28,
                "gender": "Male",
                "height": 178.0,
                "weight": 75.0,
            }
            st.success("✅ Demo data loaded")

    # Main chat interface
    st.write("---")

    # Display messages
    if st.session_state.coach_messages:
        st.subheader("💬 Conversation")
        display_messages()
    else:
        st.info("👋 Start a conversation with your AI Coach! Upload your health and workout data to get personalized recommendations.")

    # Show clear confirmation modal if needed
    show_clear_confirmation_modal()

    # Message input
    st.write("---")
    user_input = st.chat_input("Ask your coach something...", key="coach_user_input")

    if user_input:
        send_message(user_input)


if __name__ == "__main__":
    main()

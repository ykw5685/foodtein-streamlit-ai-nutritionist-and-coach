"""
API Client for AI Nutritionist Service
Handles communication with the Go backend API
"""

import requests
import json
from typing import Optional, Dict, Any, Tuple, List
from datetime import datetime
import logging

from config import ENDPOINTS, TEST_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIClient:
    """Client for communicating with AI Nutritionist API"""
    
    def __init__(self, token: Optional[str] = None, user_id: Optional[str] = None):
        """
        Initialize API client
        
        Args:
            token: JWT Bearer token for authentication
            user_id: User UUID for requests (backend extracts actual user_id from token)
        """
        self.token = token or TEST_TOKEN
        self.user_id = user_id or "test-user"  # Placeholder, backend uses ExternalAuth user
        self.last_error = None
        self.connection_status = "disconnected"
        
    def get_headers(self) -> Dict[str, str]:
        """Get request headers with JWT token"""
        headers = {
            "Content-Type": "application/json",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def _convert_health_data(self, health_df_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert health data from Streamlit CSV format to backend HealthData format
        Keep only the latest 7 days to reduce token usage.
        
        Streamlit format: {date, metric, value}
        Backend format: {recorded_at, steps_count, sleep_duration, ...}
        """
        if not health_df_records:
            return []
        
        # Group records by date
        by_date = {}
        for record in health_df_records:
            date_str = record.get("date")
            if not date_str:
                continue
            
            # Convert date string to ISO 8601 timestamp (noon UTC)
            try:
                date_obj = None
                # Try multiple date formats
                date_formats = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%m-%d-%Y", "%d-%m-%Y"]
                for fmt in date_formats:
                    try:
                        date_obj = datetime.strptime(str(date_str), fmt)
                        break
                    except ValueError:
                        continue
                
                if date_obj:
                    # Set time to noon UTC
                    iso_timestamp = date_obj.replace(hour=12, minute=0, second=0).isoformat() + "Z"
                else:
                    iso_timestamp = str(date_str)
            except (ValueError, TypeError):
                iso_timestamp = str(date_str)
            
            if date_str not in by_date:
                by_date[date_str] = {"recorded_at": iso_timestamp}
            
            metric = record.get("metric", "").lower()
            value = record.get("value")
            
            # Map metric names to backend field names
            if "steps" in metric:
                try:
                    by_date[date_str]["steps_count"] = int(float(value))
                except (ValueError, TypeError):
                    pass
            elif "sleep" in metric:
                try:
                    by_date[date_str]["sleep_duration"] = float(value)
                except (ValueError, TypeError):
                    pass
            elif "heart" in metric or "hr" in metric:
                try:
                    by_date[date_str]["heart_rate"] = int(float(value))
                except (ValueError, TypeError):
                    pass
            elif "blood pressure" in metric or "bp" in metric:
                # Try to parse BP format
                try:
                    parts = str(value).split("/")
                    if len(parts) == 2:
                        by_date[date_str]["blood_pressure_sys"] = int(float(parts[0]))
                        by_date[date_str]["blood_pressure_dia"] = int(float(parts[1]))
                except (ValueError, TypeError, IndexError):
                    pass
            elif "body fat" in metric:
                try:
                    by_date[date_str]["body_fat"] = float(value)
                except (ValueError, TypeError):
                    pass
            elif "oxygen" in metric or "spo2" in metric:
                try:
                    by_date[date_str]["oxygen_saturation"] = float(value)
                except (ValueError, TypeError):
                    pass
        
        # Keep only the latest 7 days
        sorted_dates = sorted(by_date.keys())
        latest_7_days = sorted_dates[-7:] if len(sorted_dates) > 7 else sorted_dates
        
        # Return only data for latest 7 days
        return [by_date[date] for date in latest_7_days]
    
    def _convert_dietary_data(self, dietary_df_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert dietary data from Streamlit CSV format to backend DietaryRecord format
        Keep only the latest 7 days to reduce token usage.
        
        Streamlit format: {date, meal_type, food_name, serving_size, unit, calories, protein, carbs, fat, ...}
        Backend format: {recorded_at, meal_type, food_name, serving_size, serving_unit, calories, protein, carbohydrates, fat, ...}
        """
        if not dietary_df_records:
            return []
        
        converted = []
        for record in dietary_df_records:
            date_str = record.get("date")
            
            # Convert date string to ISO 8601 timestamp (noon UTC)
            try:
                date_obj = None
                # Try multiple date formats
                date_formats = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%m-%d-%Y", "%d-%m-%Y"]
                for fmt in date_formats:
                    try:
                        date_obj = datetime.strptime(str(date_str), fmt)
                        break
                    except ValueError:
                        continue
                
                if date_obj:
                    # Set time to noon UTC
                    iso_timestamp = date_obj.replace(hour=12, minute=0, second=0).isoformat() + "Z"
                else:
                    iso_timestamp = str(date_str)
            except (ValueError, TypeError):
                iso_timestamp = str(date_str)
            
            backend_record = {
                "recorded_at": iso_timestamp,
                "meal_type": record.get("meal_type", ""),
                "food_name": record.get("food_name", ""),
                "serving_size": float(record.get("serving_size", 0)),
                "serving_unit": record.get("unit", "g"),
                "calories": float(record.get("calories", 0)),
                "protein": float(record.get("protein", 0)),
                "carbohydrates": float(record.get("carbs", 0)),
                "fat": float(record.get("fat", 0)),
                "fiber": float(record.get("fiber", 0)),
                "sugar": float(record.get("sugar", 0)),
                "sodium": float(record.get("sodium", 0)),
            }
            converted.append(backend_record)
        
        # Keep only the latest 7 days
        if converted:
            unique_dates = sorted(set(record["recorded_at"][:10] for record in converted))
            latest_7_dates = unique_dates[-7:] if len(unique_dates) > 7 else unique_dates
            # Filter to only records from latest 7 days
            converted = [record for record in converted if record["recorded_at"][:10] in latest_7_dates]
        
        return converted
    
    def set_token(self, token: str, user_id: str):
        """Update token and user ID"""
        self.token = token
        self.user_id = user_id
    
    def check_connection(self) -> Tuple[bool, str]:
        """
        Check if backend is reachable
        
        Returns:
            Tuple of (is_connected: bool, status_message: str)
        """
        try:
            response = requests.get(
                ENDPOINTS["get_conversation"],
                headers=self.get_headers(),
                timeout=5
            )
            
            if response.status_code in [200, 401, 400]:
                self.connection_status = "connected"
                return True, "✅ Connected to backend"
            else:
                self.connection_status = "error"
                return False, f"❌ Backend returned {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            self.connection_status = "disconnected"
            return False, "❌ Cannot connect to backend (is it running?)"
        except requests.exceptions.Timeout:
            self.connection_status = "timeout"
            return False, "⏱️ Backend connection timeout"
        except Exception as e:
            self.connection_status = "error"
            return False, f"❌ Connection error: {str(e)}"
    
    def get_conversation(self) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Get the user's conversation with all messages
        
        Returns:
            Tuple of (conversation_data, error_message)
        """
        if not self.token or not self.user_id:
            return None, "❌ No token or user ID set"
        
        try:
            response = requests.get(
                ENDPOINTS["get_conversation"],
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                self.last_error = None
                return response.json(), None
            elif response.status_code == 401:
                error_msg = "❌ Unauthorized - invalid token"
                self.last_error = error_msg
                return None, error_msg
            elif response.status_code == 500:
                error_msg = f"❌ Server error: {response.text[:200]}"
                self.last_error = error_msg
                return None, error_msg
            else:
                error_msg = f"❌ Error {response.status_code}: {response.text[:200]}"
                self.last_error = error_msg
                return None, error_msg
                
        except requests.exceptions.Timeout:
            error_msg = "⏱️ Request timeout"
            self.last_error = error_msg
            return None, error_msg
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            self.last_error = error_msg
            return None, error_msg
    
    def send_message(self, message: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Send a message to the AI nutritionist
        
        Args:
            message: User message text
            
        Returns:
            Tuple of (response_data, error_message)
        """
        if not self.token or not self.user_id:
            return None, "❌ No token or user ID set"
        
        if not message or len(message.strip()) < 1:
            return None, "❌ Message cannot be empty"
        
        payload = {
            "message": message.strip()
        }
        
        try:
            response = requests.post(
                ENDPOINTS["send_message"],
                headers=self.get_headers(),
                json=payload,
                timeout=60  # LLM calls can take longer
            )
            
            if response.status_code == 200:
                self.last_error = None
                return response.json(), None
            elif response.status_code == 400:
                error_msg = f"❌ Bad request: {response.text[:200]}"
                self.last_error = error_msg
                return None, error_msg
            elif response.status_code == 401:
                error_msg = "❌ Unauthorized - invalid token"
                self.last_error = error_msg
                return None, error_msg
            elif response.status_code == 500:
                error_msg = f"❌ Server error: {response.text[:200]}"
                self.last_error = error_msg
                return None, error_msg
            else:
                error_msg = f"❌ Error {response.status_code}: {response.text[:200]}"
                self.last_error = error_msg
                return None, error_msg
                
        except requests.exceptions.Timeout:
            error_msg = "⏱️ Request timeout - AI response took too long"
            self.last_error = error_msg
            return None, error_msg
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            self.last_error = error_msg
            return None, error_msg
    
    def send_message_with_data(self, message: str, health_data: list = None, dietary_data: list = None, 
                               name: str = "", age: int = 0, gender: str = "", height: float = 0, weight: float = 0,
                               dietary_type: str = "", food_allergies: list = None, disliked_foods: list = None,
                               diseases: list = None, illnesses: list = None) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Send a message to the AI nutritionist with custom health and dietary data
        
        Args:
            message: User message text
            health_data: List of health data records (Streamlit format - will be converted)
            dietary_data: List of dietary records (Streamlit format - will be converted)
            name: User's name
            age: User's age
            gender: User's gender
            height: User's height in cm
            weight: User's weight in kg
            dietary_type: User's dietary preference (e.g., "halal", "vegetarian", "vegan")
            food_allergies: List of food allergies with details (e.g., [{"food_item": "peanuts", "severity": "severe", "symptoms": "swelling"}])
            disliked_foods: List of disliked foods (e.g., [{"food_item": "broccoli", "reason": "doesn't like texture"}])
            diseases: List of disease records (e.g., [{"name": "diabetes", "type": "chronic", "status": "active"}])
            illnesses: List of illness records (e.g., [{"name": "flu", "severity": "mild", "status": "recovering"}])
            
        Returns:
            Tuple of (response_data, error_message)
        """
        if not self.token or not self.user_id:
            return None, "❌ No token or user ID set"
        
        if not message or len(message.strip()) < 1:
            return None, "❌ Message cannot be empty"
        
        # Convert data from Streamlit format to backend format
        converted_health_data = self._convert_health_data(health_data or [])
        converted_dietary_data = self._convert_dietary_data(dietary_data or [])
        
        payload = {
            "message": message.strip(),
            "health_data": converted_health_data,
            "dietary_data": converted_dietary_data,
            "name": name,
            "age": age,
            "gender": gender,
            "height": height,
            "weight": weight,
            "dietary_type": dietary_type,
            "food_allergies": food_allergies or [],
            "disliked_foods": disliked_foods or [],
            "diseases": diseases or [],
            "illnesses": illnesses or []
        }
        
        try:
            response = requests.post(
                ENDPOINTS["send_message_with_data"],
                headers=self.get_headers(),
                json=payload,
                timeout=60  # LLM calls can take longer
            )
            
            if response.status_code == 200:
                self.last_error = None
                return response.json(), None
            elif response.status_code == 400:
                error_msg = f"❌ Bad request: {response.text[:200]}"
                self.last_error = error_msg
                return None, error_msg
            elif response.status_code == 401:
                error_msg = "❌ Unauthorized - invalid token"
                self.last_error = error_msg
                return None, error_msg
            elif response.status_code == 500:
                error_msg = f"❌ Server error: {response.text[:200]}"
                self.last_error = error_msg
                return None, error_msg
            else:
                error_msg = f"❌ Error {response.status_code}: {response.text[:200]}"
                self.last_error = error_msg
                return None, error_msg
                
        except requests.exceptions.Timeout:
            error_msg = "⏱️ Request timeout - AI response took too long"
            self.last_error = error_msg
            return None, error_msg
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            self.last_error = error_msg
            return None, error_msg
    
    def clear_conversation(self) -> Tuple[bool, Optional[str]]:
        """
        Clear conversation history
        
        Returns:
            Tuple of (success: bool, error_message)
        """
        if not self.token or not self.user_id:
            return False, "❌ No token or user ID set"
        
        try:
            response = requests.post(
                ENDPOINTS["clear_conversation"],
                headers=self.get_headers(),
                timeout=10
            )
            
            if response.status_code == 200:
                self.last_error = None
                return True, None
            elif response.status_code == 401:
                error_msg = "❌ Unauthorized - invalid token"
                self.last_error = error_msg
                return False, error_msg
            elif response.status_code == 500:
                error_msg = f"❌ Server error: {response.text[:200]}"
                self.last_error = error_msg
                return False, error_msg
            else:
                error_msg = f"❌ Error {response.status_code}: {response.text[:200]}"
                self.last_error = error_msg
                return False, error_msg
                
        except requests.exceptions.Timeout:
            error_msg = "⏱️ Request timeout"
            self.last_error = error_msg
            return False, error_msg
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            self.last_error = error_msg
            return False, error_msg




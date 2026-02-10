"""
Coach API Client for communicating with the Foodtein Backend

Handles authentication and API requests to the AI Coach endpoints
"""

import json
import requests
from typing import Optional, List, Dict, Any

import config


class CoachAPIClient:
    """Client for making requests to the Coach API"""

    def __init__(self, base_url: str = None, auth_token: str = None):
        """
        Initialize the Coach API Client

        Args:
            base_url: The base URL for the API (default from config)
            auth_token: The authentication token (optional, can be set later)
        """
        self.base_url = base_url or config.API_BASE_URL
        self.auth_token = auth_token
        self.headers = {
            "Content-Type": "application/json",
        }
        if self.auth_token:
            self.headers["Authorization"] = f"Bearer {self.auth_token}"

    def set_auth_token(self, token: str):
        """Set the authentication token"""
        self.auth_token = token
        self.headers["Authorization"] = f"Bearer {self.auth_token}"

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """
        Make an HTTP request to the API

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: The API endpoint (without base URL)
            data: Request body data
            params: Query parameters

        Returns:
            The response from the API

        Raises:
            requests.exceptions.RequestException: If the request fails
        """
        url = f"{self.base_url}{endpoint}"

        if method == "GET":
            response = requests.get(url, headers=self.headers, params=params)
        elif method == "POST":
            response = requests.post(
                url, headers=self.headers, json=data, params=params
            )
        elif method == "PUT":
            response = requests.put(
                url, headers=self.headers, json=data, params=params
            )
        elif method == "DELETE":
            response = requests.delete(url, headers=self.headers, params=params)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        # Log error response for debugging
        if not response.ok:
            try:
                error_body = response.text[:500]
                print(f"DEBUG: HTTP {response.status_code} error response: {error_body}")
            except:
                pass
        
        response.raise_for_status()
        return response

    def check_connection(self):
        """
        Check if backend is reachable
        
        Returns:
            Tuple of (is_connected: bool, status_message: str)
        """
        try:
            response = requests.get(
                f"{self.base_url}/ai-coach/conversation",
                headers=self.headers,
                timeout=5
            )
            
            if response.status_code in [200, 401, 400]:
                return True, "✅ Connected to backend"
            else:
                return False, f"❌ Backend returned {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return False, "❌ Cannot connect to backend (is it running?)"
        except requests.exceptions.Timeout:
            return False, "⏱️ Backend connection timeout"
        except Exception as e:
            return False, f"❌ Connection error: {str(e)}"

    # ==================== Coach Conversation Endpoints ====================

    def get_conversation(self) -> Dict[str, Any]:
        """
        Get the user's current coaching conversation

        Returns:
            The conversation data
        """
        response = self._make_request("GET", "/ai-coach/conversation")
        return response.json()

    def send_message(self, message: str) -> Dict[str, Any]:
        """
        Send a message to the AI Coach (uses tools to fetch data)

        Args:
            message: The message to send

        Returns:
            The coach's response
        """
        data = {"message": message}
        response = self._make_request(
            "POST", "/ai-coach/conversation/messages", data=data
        )
        return response.json()

    def send_message_with_data(
        self,
        message: str,
        health_data: List[Dict[str, Any]] = None,
        workout_history: List[Dict[str, Any]] = None,
        available_workouts: List[Dict[str, Any]] = None,
        name: str = None,
        age: int = None,
        gender: str = None,
        height: float = None,
        weight: float = None,
    ) -> Dict[str, Any]:
        """
        Send a message to the AI Coach with custom data (no tools)

        Args:
            message: The message to send
            health_data: List of health data records
            workout_history: List of workout session records
            available_workouts: List of available workouts
            name: User's name
            age: User's age
            gender: User's gender
            height: User's height in cm
            weight: User's weight in kg

        Returns:
            The coach's response
        """
        import json
        from datetime import datetime
        
        # Helper to format date fields to ISO 8601 with time component
        def ensure_iso_timestamp(date_str):
            """Convert date string to ISO 8601 format with time (T12:00:00Z)"""
            if not date_str:
                return None
            
            date_str = str(date_str).strip()
            
            # Already has time component
            if "T" in date_str:
                return date_str
            
            # Try to parse and add time
            try:
                date_formats = ["%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d", "%m-%d-%Y", "%d-%m-%Y"]
                for fmt in date_formats:
                    try:
                        date_obj = datetime.strptime(date_str, fmt)
                        return date_obj.strftime("%Y-%m-%dT12:00:00Z")
                    except ValueError:
                        continue
            except:
                pass
            
            # Fallback: assume YYYY-MM-DD format and add time
            if len(date_str) == 10 and date_str[4] == "-" and date_str[7] == "-":
                return f"{date_str}T12:00:00Z"
            
            return date_str
        
        # Format health data timestamps
        health_data_formatted = []
        for record in (health_data or []):
            if isinstance(record, dict):
                record_copy = record.copy()
                if "recorded_at" in record_copy:
                    record_copy["recorded_at"] = ensure_iso_timestamp(record_copy["recorded_at"])
                health_data_formatted.append(record_copy)
        
        # Format workout history timestamps
        workout_history_formatted = []
        for record in (workout_history or []):
            if isinstance(record, dict):
                record_copy = record.copy()
                if "date" in record_copy:
                    record_copy["date"] = ensure_iso_timestamp(record_copy["date"])
                if "started_at" in record_copy:
                    record_copy["started_at"] = ensure_iso_timestamp(record_copy["started_at"])
                workout_history_formatted.append(record_copy)
        
        data = {
            "message": message,
            "health_data": health_data_formatted,
            "workout_history": workout_history_formatted,
            "available_workouts": available_workouts or [],
        }

        if name:
            data["name"] = name
        if age:
            data["age"] = age
        if gender:
            data["gender"] = gender
        if height:
            data["height"] = height
        if weight:
            data["weight"] = weight

        print(f"DEBUG coach_api_client: Sending request with age={age} (type={type(age).__name__})")
        print(f"DEBUG coach_api_client: Data payload keys: {list(data.keys())}")
        print(f"DEBUG coach_api_client: Health data count: {len(data.get('health_data', []))}")
        print(f"DEBUG coach_api_client: Workout data count: {len(data.get('workout_history', []))}")
        print(f"DEBUG coach_api_client: Available workouts count: {len(data.get('available_workouts', []))}")
        if data.get('health_data'):
            print(f"DEBUG coach_api_client: First health record: {data['health_data'][0]}")
        if data.get('workout_history'):
            print(f"DEBUG coach_api_client: First workout record: {data['workout_history'][0]}")
        if data.get('available_workouts'):
            print(f"DEBUG coach_api_client: First available workout: {data['available_workouts'][0]}")
        
        print(f"DEBUG coach_api_client: Full JSON payload:\n{json.dumps(data, indent=2, default=str)[:2000]}")

        response = self._make_request(
            "POST", "/ai-coach/conversation/messages-with-data", data=data
        )
        return response.json()

    def clear_conversation(self) -> Dict[str, Any]:
        """
        Clear the user's coaching conversation

        Returns:
            Success message
        """
        response = self._make_request(
            "POST", "/ai-coach/conversation/clear", data={}
        )
        return response.json()

    # ==================== Helper Functions ====================

    def format_health_data_for_api(
        self, dataframe: Any
    ) -> List[Dict[str, Any]]:  # dataframe is pandas.DataFrame
        """
        Convert health data from DataFrame to API format

        Expected DataFrame columns:
        - date: Date of the health record
        - metric: Type of metric (steps, sleep_duration, heart_rate, etc.)
        - value: The metric value

        Returns:
            List of health data records in API format
        """
        from datetime import datetime
        
        health_records = {}

        for _, row in dataframe.iterrows():
            date_str = str(row["date"])
            metric = str(row["metric"]).lower().strip()
            value = row["value"]

            # Try to parse date in multiple formats and convert to ISO 8601 format with time
            date_iso = date_str
            try:
                # Try formats in order: DD/MM/YYYY is more common internationally, but MM/DD/YYYY is common in US
                # Since we see 10/2/2026, try MM/DD/YYYY first (10 = Oct, 2 = day), then DD/MM/YYYY
                date_formats = ["%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d", "%m-%d-%Y", "%d-%m-%Y"]
                for fmt in date_formats:
                    try:
                        date_obj = datetime.strptime(date_str, fmt)
                        # Convert to ISO 8601 with time component (noon UTC)
                        date_iso = date_obj.strftime("%Y-%m-%dT12:00:00Z")
                        break
                    except ValueError:
                        continue
            except Exception as e:
                print(f"Warning: Could not parse date '{date_str}': {e}")
                # Fallback: add time component if not present
                if "T" not in date_iso and "Z" not in date_iso:
                    date_iso = f"{date_iso}T12:00:00Z"

            if date_str not in health_records:
                health_records[date_str] = {
                    "recorded_at": date_iso,
                    "steps_count": None,
                    "sleep_duration": None,
                    "heart_rate": None,
                    "blood_pressure_sys": None,
                    "blood_pressure_dia": None,
                    "body_fat": None,
                    "oxygen_saturation": None,
                }
            # Map metric names to fields
            if "step" in metric:
                health_records[date_str]["steps_count"] = int(value)
            elif "sleep" in metric:
                health_records[date_str]["sleep_duration"] = float(value)
            elif "heart" in metric:
                health_records[date_str]["heart_rate"] = int(value)
            elif "systolic" in metric or "sys" in metric:
                health_records[date_str]["blood_pressure_sys"] = int(value)
            elif "diastolic" in metric or "dia" in metric:
                health_records[date_str]["blood_pressure_dia"] = int(value)
            elif "fat" in metric:
                health_records[date_str]["body_fat"] = float(value)
            elif "oxygen" in metric or "o2" in metric:
                health_records[date_str]["oxygen_saturation"] = float(value)

        return list(health_records.values())

    def format_workout_history_for_api(
        self, dataframe: Any
    ) -> List[Dict[str, Any]]:  # dataframe is pandas.DataFrame
        """
        Convert workout history from DataFrame to API format

        Expected DataFrame columns:
        - date: Date of the workout
        - workout_name: Name of the workout
        - category: Category of the workout
        - duration_mins: Duration in minutes
        - completed: Whether the workout was completed

        Returns:
            List of workout session records in API format
        """
        from datetime import datetime
        
        workout_records = []

        for _, row in dataframe.iterrows():
            date_str = str(row["date"])
            
            # Try to parse date in multiple formats and convert to ISO 8601 format with time
            date_iso = date_str
            try:
                # DD/MM/YYYY first (more international), then MM/DD/YYYY, then YYYY-MM-DD
                date_formats = ["%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%d", "%m-%d-%Y", "%d-%m-%Y"]
                for fmt in date_formats:
                    try:
                        date_obj = datetime.strptime(date_str, fmt)
                        date_iso = date_obj.strftime("%Y-%m-%d")
                        break
                    except ValueError:
                        continue
            except Exception as e:
                print(f"Warning: Could not parse workout date '{date_str}': {e}")
                date_iso = date_str
            
            # Create started_at in ISO 8601 format with time
            started_at = f"{date_iso}T00:00:00Z"
            
            record = {
                "date": date_iso,
                "started_at": started_at,
                "workout_name": str(row["workout_name"]),
                "category": str(row["category"]),
                "is_completed": bool(row.get("completed", False)),
            }

            if "duration_mins" in row.index and row["duration_mins"]:
                record["duration_seconds"] = int(row["duration_mins"] * 60)

            workout_records.append(record)

        return workout_records

    @staticmethod
    def create_mock_health_data() -> List[Dict[str, Any]]:
        """Create mock health data for testing"""
        return [
            {
                "recorded_at": "2026-02-03",
                "steps_count": 8500,
                "sleep_duration": 7.5,
                "heart_rate": 72,
                "blood_pressure_sys": 120,
                "blood_pressure_dia": 80,
                "body_fat": 18.5,
                "oxygen_saturation": 98.0,
            },
            {
                "recorded_at": "2026-02-04",
                "steps_count": 10200,
                "sleep_duration": 8.0,
                "heart_rate": 68,
                "blood_pressure_sys": 118,
                "blood_pressure_dia": 78,
                "body_fat": 18.4,
                "oxygen_saturation": 98.5,
            },
            {
                "recorded_at": "2026-02-05",
                "steps_count": 9100,
                "sleep_duration": 7.2,
                "heart_rate": 75,
                "blood_pressure_sys": 122,
                "blood_pressure_dia": 82,
                "body_fat": 18.5,
                "oxygen_saturation": 97.8,
            },
            {
                "recorded_at": "2026-02-06",
                "steps_count": 11500,
                "sleep_duration": 7.8,
                "heart_rate": 70,
                "blood_pressure_sys": 119,
                "blood_pressure_dia": 79,
                "body_fat": 18.3,
                "oxygen_saturation": 98.2,
            },
            {
                "recorded_at": "2026-02-07",
                "steps_count": 9800,
                "sleep_duration": 8.1,
                "heart_rate": 71,
                "blood_pressure_sys": 120,
                "blood_pressure_dia": 80,
                "body_fat": 18.2,
                "oxygen_saturation": 98.1,
            },
        ]

    @staticmethod
    def create_mock_workout_history() -> List[Dict[str, Any]]:
        """Create mock workout history for testing"""
        return [
            {
                "date": "2026-02-07",
                "started_at": "2026-02-07T08:00:00Z",
                "workout_name": "Full Body Strength",
                "category": "strength",
                "is_completed": True,
                "duration_seconds": 2700,
            },
            {
                "date": "2026-02-06",
                "started_at": "2026-02-06T10:30:00Z",
                "workout_name": "Cardio Blast",
                "category": "cardio",
                "is_completed": True,
                "duration_seconds": 1800,
            },
            {
                "date": "2026-02-05",
                "started_at": "2026-02-05T08:00:00Z",
                "workout_name": "Upper Body Focus",
                "category": "strength",
                "is_completed": True,
                "duration_seconds": 2400,
            },
            {
                "date": "2026-02-04",
                "started_at": "2026-02-04T18:00:00Z",
                "workout_name": "HIIT Training",
                "category": "cardio",
                "is_completed": False,
                "duration_seconds": None,
            },
            {
                "date": "2026-02-03",
                "started_at": "2026-02-03T08:30:00Z",
                "workout_name": "Yoga & Flexibility",
                "category": "flexibility",
                "is_completed": True,
                "duration_seconds": 1800,
            },
        ]

    @staticmethod
    def create_mock_available_workouts() -> List[Dict[str, Any]]:
        """Create mock available workouts for testing"""
        return [
            {
                "id": 1,
                "name": "Full Body Strength",
                "category": "strength",
                "duration_minutes": 45,
                "difficulty_level": "intermediate",
                "description": "A comprehensive full-body strength workout",
                "primary_muscles": "chest, back, legs",
                "secondary_muscles": "shoulders, arms",
                "sets_count": 3,
                "equipment": [
                    {"id": 1, "name": "Dumbbell"},
                    {"id": 2, "name": "Barbell"},
                ],
                "exercises": [
                    {
                        "id": 1,
                        "name": "Bench Press",
                        "reps": 10,
                        "sets": 3,
                        "rest_seconds": 90,
                        "equipment": [{"id": 2, "name": "Barbell"}],
                    },
                    {
                        "id": 2,
                        "name": "Deadlifts",
                        "reps": 8,
                        "sets": 3,
                        "rest_seconds": 120,
                        "equipment": [{"id": 2, "name": "Barbell"}],
                    },
                    {
                        "id": 3,
                        "name": "Squats",
                        "reps": 12,
                        "sets": 3,
                        "rest_seconds": 90,
                        "equipment": [{"id": 2, "name": "Barbell"}],
                    },
                ],
            },
            {
                "id": 2,
                "name": "Cardio Blast",
                "category": "cardio",
                "duration_minutes": 30,
                "difficulty_level": "beginner",
                "description": "Quick cardio workout to boost your heart rate",
                "primary_muscles": "cardiovascular",
                "secondary_muscles": "legs",
                "sets_count": 1,
                "equipment": [{"id": 3, "name": "Treadmill"}],
                "exercises": [
                    {
                        "id": 4,
                        "name": "Running",
                        "duration_seconds": 1800,
                        "equipment": [{"id": 3, "name": "Treadmill"}],
                    }
                ],
            },
            {
                "id": 3,
                "name": "Upper Body Focus",
                "category": "strength",
                "duration_minutes": 40,
                "difficulty_level": "intermediate",
                "description": "Focused workout for chest, back, and arms",
                "primary_muscles": "chest, back, arms",
                "secondary_muscles": "shoulders",
                "sets_count": 3,
                "equipment": [{"id": 1, "name": "Dumbbell"}],
                "exercises": [
                    {
                        "id": 5,
                        "name": "Dumbbell Chest Press",
                        "reps": 12,
                        "sets": 3,
                        "rest_seconds": 60,
                        "equipment": [{"id": 1, "name": "Dumbbell"}],
                    },
                    {
                        "id": 6,
                        "name": "Lat Pulldown",
                        "reps": 10,
                        "sets": 3,
                        "rest_seconds": 75,
                        "equipment": [],
                    },
                ],
            },
            {
                "id": 4,
                "name": "HIIT Training",
                "category": "cardio",
                "duration_minutes": 25,
                "difficulty_level": "advanced",
                "description": "High-intensity interval training for maximum burn",
                "primary_muscles": "full body",
                "secondary_muscles": "cardiovascular",
                "sets_count": 2,
                "equipment": [],
                "exercises": [
                    {
                        "id": 7,
                        "name": "Burpees",
                        "reps": 20,
                        "rest_seconds": 30,
                    },
                    {
                        "id": 8,
                        "name": "Mountain Climbers",
                        "duration_seconds": 60,
                        "rest_seconds": 30,
                    },
                    {
                        "id": 9,
                        "name": "Jump Squats",
                        "reps": 20,
                        "rest_seconds": 30,
                    },
                ],
            },
            {
                "id": 5,
                "name": "Yoga & Flexibility",
                "category": "flexibility",
                "duration_minutes": 30,
                "difficulty_level": "beginner",
                "description": "Relax and improve flexibility with gentle yoga",
                "primary_muscles": "full body",
                "secondary_muscles": "flexibility",
                "sets_count": 1,
                "equipment": [],
                "exercises": [
                    {
                        "id": 10,
                        "name": "Sun Salutation",
                        "duration_seconds": 600,
                    },
                    {
                        "id": 11,
                        "name": "Downward Dog",
                        "duration_seconds": 300,
                    },
                    {
                        "id": 12,
                        "name": "Child's Pose",
                        "duration_seconds": 300,
                    },
                ],
            },
        ]

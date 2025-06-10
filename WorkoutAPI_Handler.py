import requests
from datetime import datetime, timedelta
import os
from zoneinfo import ZoneInfo

class WorkoutAPI_Handler:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {"Authorization": api_key}

    def get_workouts_for_date(self, date_str=None, include_tomorrow=True):
        """Fetches workouts for a specific date or today (in Israel time) if none provided.
        
        Args:
            date_str (str, optional): Date in YYYY-MM-DD or YYYYMMDD format. Defaults to None (today).
            include_tomorrow (bool, optional): Whether to include tomorrow's workouts. Defaults to True.
            
        Returns:
            list: List of workout data dictionaries
        """
        try:
            israel = ZoneInfo("Asia/Jerusalem")
            israel_now = datetime.now(israel)
            
            if date_str is None:
                # Get today's date
                today_str = israel_now.strftime("%Y%m%d")
                if include_tomorrow:
                    # Get tomorrow's date
                    tomorrow = israel_now + timedelta(days=1)
                    tomorrow_str = tomorrow.strftime("%Y%m%d")
                    date_str = f"{today_str},{tomorrow_str}"
                else:
                    date_str = today_str
            else:
                # Convert YYYY-MM-DD to YYYYMMDD if needed
                if '-' in date_str:
                    date_str = date_str.replace('-', '')
                if include_tomorrow:
                    # Parse the input date and add tomorrow
                    input_date = datetime.strptime(date_str, "%Y%m%d")
                    tomorrow = input_date + timedelta(days=1)
                    tomorrow_str = tomorrow.strftime("%Y%m%d")
                    date_str = f"{date_str},{tomorrow_str}"

            workouts_url = f"{self.base_url}/workouts?dates={date_str}"
            print(f"Fetching workouts from: {workouts_url}")

            workouts_response = requests.get(workouts_url, headers=self.headers)
            workouts_response.raise_for_status()
            workouts_data = workouts_response.json()
            workouts = workouts_data.get("data", [])
            
            # If we're not including tomorrow, filter out tomorrow's workouts
            if not include_tomorrow:
                today_str = israel_now.strftime("%Y-%m-%d")
                workouts = [w for w in workouts if w.get("attributes", {}).get("scheduled_date", "").startswith(today_str)]
            
            return workouts
            
        except Exception as e:
            print(f"Error fetching workouts: {e}")
            return []

# Example usage (for testing this file individually)
if __name__ == '__main__':
    # This part would typically be in your main script
    from dotenv import load_dotenv
    load_dotenv()
    sugar_wod_api_key = os.getenv("SUGARWOD_API_KEY")
    base_url = "https://api.sugarwod.com/v2"

    if not sugar_wod_api_key:
        print("Error: SUGARWOD_API_KEY not found in environment variables.")
    else:
        handler = WorkoutAPI_Handler(base_url, sugar_wod_api_key)
        
        # Test 1: Get both today and tomorrow's workouts (default behavior)
        print("\nTest 1: Today and Tomorrow's Workouts")
        all_workouts = handler.get_workouts_for_date()
        print(f"Found {len(all_workouts)} workouts.")
        for w in all_workouts[:5]:
            title = w.get("attributes", {}).get("title", "N/A")
            date = w.get("attributes", {}).get("scheduled_date", "N/A")
            print(f"- {date}: {title}")
            
        # Test 2: Get only today's workouts
        print("\nTest 2: Today's Workouts Only")
        today_workouts = handler.get_workouts_for_date(include_tomorrow=False)
        print(f"Found {len(today_workouts)} workouts.")
        for w in today_workouts:
            title = w.get("attributes", {}).get("title", "N/A")
            print(f"- {title}")
            
        # Test 3: Get workouts for a specific date
        print("\nTest 3: Specific Date Workouts")
        specific_date = "2024-03-20"
        specific_workouts = handler.get_workouts_for_date(specific_date, include_tomorrow=False)
        print(f"Found {len(specific_workouts)} workouts for {specific_date}.")
        for w in specific_workouts:
            title = w.get("attributes", {}).get("title", "N/A")
            print(f"- {title}") 
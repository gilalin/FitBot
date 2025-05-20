import requests
from datetime import datetime
import os
from zoneinfo import ZoneInfo

class WorkoutAPI_Handler:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {"Authorization": api_key}

    def get_workouts_for_date(self, date_str=None):
        """Fetches workouts for a specific date or today (in Israel time) if none provided."""
        if date_str is None:
            # Get today's date in Israel time (Asia/Jerusalem)
            try:
                israel = ZoneInfo("Asia/Jerusalem")
                israel_now = datetime.now(israel)
                date_str = israel_now.strftime("%Y%m%d")
            except Exception as e:
                print(f"Error getting Israel time: {e}")
                # Fallback to UTC if timezone fails
                date_str = datetime.utcnow().strftime("%Y%m%d")
                print("Using UTC date as fallback.")

        workouts_url = f"{self.base_url}/workouts?dates={date_str}"
        print(f"Fetching workouts from: {workouts_url}")

        try:
            workouts_response = requests.get(workouts_url, headers=self.headers)
            workouts_response.raise_for_status() # Raise an exception for bad status codes
            workouts_data = workouts_response.json()
            workouts = workouts_data.get("data", [])
            return workouts
        except requests.exceptions.RequestException as e:
            print(f"Error fetching workouts: {e}")
            return []
        except Exception as e:
            print(f"Failed to decode JSON or other error: {e}")
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
        # Fetch workouts for today (in Israel time)
        today_workouts = handler.get_workouts_for_date()
        print("\nWorkouts for today (Israel time):")
        # You might want to pretty print or process these further in the main script
        # For now, just show a count and first few titles
        print(f"Found {len(today_workouts)} workouts.")
        for i, w in enumerate(today_workouts[:5]): # Print up to 5 titles
             title = w.get("attributes", {}).get("title", "N/A")
             print(f"- {title}")
        if len(today_workouts) > 5:
            print("...")

        # Example: Fetch workouts for a specific past date (e.g., 2024-05-18 UTC)
        # past_date_workouts = handler.get_workouts_for_date("20240518")
        # print("\nWorkouts for 20240518:")
        # print(f"Found {len(past_date_workouts)} workouts.") 
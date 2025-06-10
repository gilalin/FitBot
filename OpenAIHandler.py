import os
import openai
from dotenv import load_dotenv
from WorkoutAPI_Handler import WorkoutAPI_Handler
from datetime import datetime
from zoneinfo import ZoneInfo


class OpenAIHandler:
    def __init__(self):
        load_dotenv()
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
    def analyze_workout(self, workout_data):
        """Analyzes workout data using OpenAI's API and returns insights."""
        try:
            # Format the workout data into a prompt
            prompt = self._format_workout_prompt(workout_data)
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-4o",  # Using GPT-4
                messages=[
                    {"role": "system", "content": "You are a CrossFit coach and workout analyst. Analyze the workout and provide insights about the workout type, difficulty, target areas, and any tips for scaling or modifications."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error analyzing workout with OpenAI: {e}")
            return "Sorry, I couldn't analyze the workout at this time."
    
    def _format_workout_prompt(self, workout_data):
        """Formats workout data into a prompt for OpenAI."""
        prompt = "Please analyze the following CrossFit workout(s):\n\n"
        
        for workout in workout_data:
            title = workout.get("attributes", {}).get("title", "N/A")
            description = workout.get("attributes", {}).get("description", "N/A")
            prompt += f"Title: {title}\n"
            prompt += f"Description: {description}\n"
            prompt += "---\n"
            
        prompt += "\nPlease provide a short and short concise analysis of the workout:\n"
        prompt += "1. Estimated time to complete the workout for a beginner, intermediate and advanced\n"
        prompt += "2. Recomended strategies and pacing for the workout\n"
        prompt += "3. Scaling options for different fitness levels\n"

        
        return prompt

# Example usage
if __name__ == "__main__":
    handler = OpenAIHandler()
    test_workout = [{
        "attributes": {
            "title": "Test Workout",
            "description": "20 min AMRAP\n10 burpees\n20 air squats\n30 double unders"
        }
    }]
    
    # analysis = handler.analyze_workout(test_workout)

    load_dotenv()

    SUGARWOD_API_KEY = os.environ['SUGARWOD_API_KEY']
    SUGARWOD_API_URL = "https://api.sugarwod.com/v2"
    today_str = datetime.now(ZoneInfo("Asia/Jerusalem")).strftime("%Y-%m-%d")

    wod_handler = WorkoutAPI_Handler(SUGARWOD_API_URL, SUGARWOD_API_KEY)
    analysis = handler.analyze_workout(wod_handler.get_workouts_for_date(today_str, include_tomorrow=False))
    print(analysis) 
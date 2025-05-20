# a code to connect to the wod api, verify the API key using the /box endpoint, and fetch workouts using the provided link

import os
from dotenv import load_dotenv
import asyncio
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from WorkoutAPI_Handler import WorkoutAPI_Handler
from TelegramHandler import TelegramHandler

load_dotenv()

BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
# Keep personal chat ID for potential personal notifications
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
TELEGRAM_CHANNEL_ID = os.environ.get('TELEGRAM_CHANNEL_ID')
SUGARWOD_API_KEY = os.environ['SUGARWOD_API_KEY']

BASE_URL = "https://api.sugarwod.com/v2"

async def main():
    # Initialize handlers
    workout_api_handler = WorkoutAPI_Handler(BASE_URL, SUGARWOD_API_KEY)
    telegram_handler = TelegramHandler(BOT_TOKEN)

    # Get today's and tomorrow's dates in Israel time (Asia/Jerusalem)
    try:
        israel_tz = ZoneInfo("Asia/Jerusalem")
        today_date = datetime.now(israel_tz)
        tomorrow_date = today_date + timedelta(days=1)
        today_str = today_date.strftime("%Y%m%d")
        tomorrow_str = tomorrow_date.strftime("%Y%m%d")
    except Exception as e:
        print(f"Error getting Israel time for dates: {e}")
        # Fallback to UTC if timezone fails
        utc_now = datetime.utcnow()
        today_str = utc_now.strftime("%Y%m%d")
        tomorrow_str = (utc_now + timedelta(days=1)).strftime("%Y%m%d")
        print("Using UTC dates as fallback.")

    # Fetch today's and tomorrow's workouts
    today_workouts = workout_api_handler.get_workouts_for_date(today_str)
    tomorrow_workouts = workout_api_handler.get_workouts_for_date(tomorrow_str)

    # Combine workouts and prepare message
    all_workouts = today_workouts + tomorrow_workouts

    # Send workouts to the channel
    if TELEGRAM_CHANNEL_ID:
        await telegram_handler.send_workout_message(TELEGRAM_CHANNEL_ID, all_workouts, include_tomorrow_check=True)
    else:
        print("TELEGRAM_CHANNEL_ID not set in environment variables.")

    # Optional: Send to personal chat as well
    # if TELEGRAM_CHAT_ID:
    #     await telegram_handler.send_workout_message(TELEGRAM_CHAT_ID, all_workouts)
    # else:
    #     print("TELEGRAM_CHAT_ID not set in environment variables.")

if __name__ == '__main__':
    asyncio.run(main())

# Analyze the output above to determine next steps for filtering or debugging.
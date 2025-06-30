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

    # Get today's date in Israel time (Asia/Jerusalem)
    try:
        israel_tz = ZoneInfo("Asia/Jerusalem")
        today_date = datetime.now(israel_tz)
        today_str = today_date.strftime("%Y-%m-%d")
    except Exception as e:
        print(f"Error getting Israel time for dates: {e}")
        # Fallback to UTC if timezone fails
        utc_now = datetime.utcnow()
        today_str = utc_now.strftime("%Y-%m-%d")
        print("Using UTC dates as fallback.")

    # Fetch workouts (both today and tomorrow by default)
    workouts = workout_api_handler.get_workouts_for_date(today_str, include_tomorrow=True)

    # Send workouts to the channel
    if TELEGRAM_CHANNEL_ID:
        await telegram_handler.send_workout_message(TELEGRAM_CHANNEL_ID, workouts, include_tomorrow_check=True)
    else:
        print("TELEGRAM_CHANNEL_ID not set in environment variables.")

    # Optional: Send to personal chat as well
    if TELEGRAM_CHAT_ID:
        await telegram_handler.send_workout_message(TELEGRAM_CHAT_ID, workouts, include_tomorrow_check=True)
    else:
        print("TELEGRAM_CHAT_ID not set in environment variables.")

if __name__ == '__main__':
    asyncio.run(main())

# Analyze the output above to determine next steps for filtering or debugging.
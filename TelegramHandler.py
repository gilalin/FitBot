from telegram import Bot
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

class TelegramHandler:
    def __init__(self, bot_token):
        self.bot = Bot(token=bot_token)

    async def send_workout_message(self, chat_id, workouts, include_tomorrow_check=False):
        """Sends formatted workout message to the specified chat ID."""
        today_date_str_compare = datetime.now(ZoneInfo("Asia/Jerusalem")).strftime("%Y-%m-%d")
        tomorrow_date_str_compare = (datetime.now(ZoneInfo("Asia/Jerusalem")) + timedelta(days=1)).strftime("%Y-%m-%d")

        today_workouts = [w for w in workouts if w.get("attributes", {}).get("scheduled_date", "").startswith(today_date_str_compare)]
        tomorrow_workouts = [w for w in workouts if w.get("attributes", {}).get("scheduled_date", "").startswith(tomorrow_date_str_compare)]

        message = "🏋️‍♂️ *CrossFit Hatira WODs* 🏋️‍♀️\n\n"

        # Add Today's Workouts
        message += "📅 *Today's Workouts: ({})*\n\n".format(today_date_str_compare)
        if not today_workouts:
            message += "_No workouts found for today._\n"
        else:
            for w in today_workouts:
                attr = w.get("attributes", {})
                title = attr.get("title", "N/A")
                description = attr.get("description", "N/A")

                message += (
                    "🔹 *Title*: " + title + "\n" +
                    "📝 *Description*: " + description + "\n" +
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                )

        # Add Tomorrow's Workouts if requested
        if include_tomorrow_check:
            message += "\n📅 *Tomorrow's Workouts: ({})*\n\n".format(tomorrow_date_str_compare)
            if not tomorrow_workouts:
                message += "⚠️ _Sorry… Tomorrow's WOD hasn't been published yet._\n"
            else:
                for w in tomorrow_workouts:
                    attr = w.get("attributes", {})
                    title = attr.get("title", "N/A")
                    description = attr.get("description", "N/A")

                    message += (
                        "🔹 *Title*: " + title + "\n" +
                        "📝 *Description*: " + description + "\n" +
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    )

        try:
            await self.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')
            print(f"Workout message sent successfully to chat_id: {chat_id}")
        except Exception as e:
            print(f"Error sending message to chat_id {chat_id}: {e}")

# Example usage (for testing this file individually)
if __name__ == '__main__':
    # This part would typically be in your main script
    import asyncio
    from dotenv import load_dotenv
    load_dotenv()
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    personal_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    channel_id = os.getenv("TELEGRAM_CHANNEL_ID") # Use channel ID for testing

    if not bot_token:
        print("Error: TELEGRAM_BOT_TOKEN not found in environment variables.")
    elif not channel_id:
         print("Error: TELEGRAM_CHANNEL_ID not found in environment variables.")
    else:
        handler = TelegramHandler(bot_token)
        # Create a dummy workout list for testing
        dummy_workouts_today = [
            {
                "attributes": {
                    "title": "Test Workout Today",
                    "scheduled_date": datetime.now(ZoneInfo("Asia/Jerusalem")).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                    "description": "This is a test description for today's workout."
                }
            },
        ]
        dummy_workouts_tomorrow = [
            {
                "attributes": {
                    "title": "Test Workout Tomorrow",
                    "scheduled_date": (datetime.now(ZoneInfo("Asia/Jerusalem")) + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                    "description": "This is a test description for tomorrow's workout."
                }
            }
        ]
        
        print(f"Attempting to send dummy message (today + tomorrow check) to {channel_id}...")
        # Test sending with tomorrow check (should include both and no 'not published' message)
        asyncio.run(handler.send_workout_message(channel_id, dummy_workouts_today + dummy_workouts_tomorrow, include_tomorrow_check=True))

        print(f"\nAttempting to send dummy message (today only) to {channel_id}...")
        # Test sending only today's workout (should only include today's)
        asyncio.run(handler.send_workout_message(channel_id, dummy_workouts_today))

        print(f"\nAttempting to send dummy message (tomorrow not published) to {channel_id}...")
        # Test sending only today's workout with tomorrow check (should include today's + 'not published' message)
        asyncio.run(handler.send_workout_message(channel_id, dummy_workouts_today, include_tomorrow_check=True))

        print(f"\nAttempting to send dummy message (no workouts) to {channel_id}...")
        # Test sending with no workouts (should show 'No workouts found')
        asyncio.run(handler.send_workout_message(channel_id, [], include_tomorrow_check=True)) 
# a code to connect to the wod api, verify the API key using the /box endpoint, and fetch workouts using the provided link

import requests
import os
from datetime import datetime
from pprint import pprint
from telegram import Bot
from dotenv import load_dotenv
import asyncio

load_dotenv()

BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
CHAT_ID   = os.environ['TELEGRAM_CHAT_ID']   # your user ID or channel ID

# Use your API key directly for now
sugar_wod_api_key = "320e5969-fa6d-4ef4-8513-2b5af1f76f7c"
headers = {"Authorization": sugar_wod_api_key}

# Use api.sugarwod.com as the base URL
base_url = "https://api.sugarwod.com/v2"

# Step 1: Get /box info and extract tracks link
box_url = f"{base_url}/box"
# Request all workouts without filters
workouts_url = f"{base_url}/workouts"
workouts_response = requests.get(workouts_url, headers=headers)
try:
    workouts_data = workouts_response.json()
    workouts = workouts_data.get("data", [])
    if workouts:
        print("All Workouts:")
        for w in workouts:
            attr = w.get("attributes", {})
            title = attr.get("title", "N/A")
            date = attr.get("scheduled_date", "N/A")
            description = attr.get("description", "N/A")
            print(f"\nTitle: {title}\nDate: {date}\nDescription: {description}\n{'-'*40}")
    else:
        print("No workouts found.")
except Exception as e:
    print("Failed to decode JSON from /workouts response. Raw response:")
    print(workouts_response.text)
    exit()

# Send workouts to Telegram bot
async def send_workouts_to_telegram(workouts):
    bot = Bot(token=BOT_TOKEN)
    chat_id = os.environ['TELEGRAM_CHAT_ID']
    message = "Today's Workouts:\n\n"
    for w in workouts:
        attr = w.get("attributes", {})
        title = attr.get("title", "N/A")
        date = attr.get("scheduled_date", "N/A")
        description = attr.get("description", "N/A")
        message += f"Title: {title}\nDate: {date}\nDescription: {description}\n{'-'*40}\n"
    await bot.send_message(chat_id=chat_id, text=message)

# Run the async function to send workouts
if __name__ == '__main__':
    asyncio.run(send_workouts_to_telegram(workouts))

# Analyze the output above to determine next steps for filtering or debugging.
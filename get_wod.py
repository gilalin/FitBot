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
api_key = "320e5969-fa6d-4ef4-8513-2b5af1f76f7c"
headers = {"Authorization": api_key}

# Use api.sugarwod.com as the base URL
base_url = "https://api.sugarwod.com/v2"

# Step 1: Get /box info and extract tracks link
box_url = f"{base_url}/box"
box_response = requests.get(box_url, headers=headers)
try:
    box_data = box_response.json()
except Exception as e:
    print("Failed to decode JSON from /box response. Raw response:")
    print(box_response.text)
    exit()

tracks_url = box_data.get("links", {}).get("tracks")
if not tracks_url:
    print("No tracks link found in /box response.")
    exit()

# If the tracks_url is a relative path, prepend the base_url
if tracks_url.startswith("/"):
    tracks_url = base_url + tracks_url

# Step 2: Fetch tracks
tracks_response = requests.get(tracks_url, headers=headers)
try:
    tracks_data = tracks_response.json()
except Exception as e:
    print("Failed to decode JSON from /tracks response. Raw response:")
    print(tracks_response.text)
    exit()

# Step 3: Use the first track's id to fetch today's workouts
if "data" in tracks_data and tracks_data["data"]:
    track_id = tracks_data["data"][0]["id"]
    today = datetime.utcnow().strftime("%Y%m%d")
    workouts_url = f"{base_url}/workouts?dates={today}&track_id={track_id}"
    workouts_response = requests.get(workouts_url, headers=headers)
    try:
        workouts_data = workouts_response.json()
    except Exception as e:
        print("Failed to decode JSON from /workouts response. Raw response:")
        print(workouts_response.text)
        exit()
    workouts = workouts_data.get("data", [])
    if workouts:
        print("Workouts for today:")
        pprint(workouts)
    else:
        print("No workouts found for today.")
else:
    print("No tracks found for this affiliate.")

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
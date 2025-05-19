from telegram import Bot
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Get the bot token from environment variable
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not BOT_TOKEN:
    print("Error: TELEGRAM_BOT_TOKEN not found in environment variables")
    exit(1)

async def main():
    # Create bot instance and get updates
    bot = Bot(token=BOT_TOKEN)
    updates = await bot.get_updates()

    # Print all updates
    print("\nAll updates:")
    for update in updates:
        print(f"\nUpdate ID: {update.update_id}")
        if update.message:
            print(f"Chat ID: {update.message.chat.id}")
            print(f"From User: {update.message.from_user.username or update.message.from_user.first_name}")
            print(f"Message: {update.message.text}")
        print("-" * 50)

    if not updates:
        print("\nNo updates found. Try sending a message to your bot first!")

# Run the async function
if __name__ == '__main__':
    asyncio.run(main()) 
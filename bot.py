import os
import requests
from dotenv import load_dotenv
from telegram import Update, BotCommand, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext
from TelegramHandler import TelegramHandler
from WorkoutAPI_Handler import WorkoutAPI_Handler
from OpenAIHandler import OpenAIHandler
from datetime import datetime
from zoneinfo import ZoneInfo

load_dotenv()

BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
SUGARWOD_API_KEY = os.environ['SUGARWOD_API_KEY']
SUGARWOD_API_URL = "https://api.sugarwod.com/v2"
SUBSCRIBERS_FILE = 'subscribers.txt'
telegram_handler = TelegramHandler(BOT_TOKEN)
workout_api_handler = WorkoutAPI_Handler(SUGARWOD_API_URL, SUGARWOD_API_KEY)
openai_handler = OpenAIHandler()

def _load_subscribers():
    try:
        with open(SUBSCRIBERS_FILE) as f:
            return set(f.read().split())
    except FileNotFoundError:
        return set()


def _save_subscribers(subs):
    with open(SUBSCRIBERS_FILE, 'w') as f:
        f.write('\n'.join(subs))


async def start(update: Update, context: CallbackContext):
    chat_id = str(update.effective_chat.id)
    subs = _load_subscribers()
    if chat_id in subs:
        today_str = datetime.now(ZoneInfo("Asia/Jerusalem")).strftime("%Y-%m-%d")
        await update.message.reply_text("✅ You're already subscribed!", reply_markup=main_menu_keyboard())
    else:
        subs.add(chat_id)
        _save_subscribers(subs)
        await update.message.reply_text(
            "🎉 Subscribed! You'll get daily workouts here.\n\n"
            "Use the menu below to see available commands.",
            reply_markup=main_menu_keyboard()
        )

async def stop(update: Update, context: CallbackContext):
    chat_id = str(update.effective_chat.id)
    subs = _load_subscribers()
    if chat_id in subs:
        subs.remove(chat_id)
        _save_subscribers(subs)
        await update.message.reply_text("🛑 Unsubscribed. You will no longer receive messages.", reply_markup=main_menu_keyboard())
    else:
        await update.message.reply_text("ℹ️ You weren't subscribed.", reply_markup=main_menu_keyboard())

async def upload_workout(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "📤 Great! Send me a photo or data file of your workout, and I'll run it through our AI analyzer (coming soon...)",
        reply_markup=main_menu_keyboard()
    )
    # Future: MessageHandler for filters.PHOTO | filters.Document to handle uploads

async def get_wod(update: Update, context: CallbackContext):
    try:
        today_str = datetime.now(ZoneInfo("Asia/Jerusalem")).strftime("%Y-%m-%d")
        workout_data = workout_api_handler.get_workouts_for_date(today_str)
        if not workout_data:
            await update.message.reply_text(
                "ℹ️ No workouts found for today.",
                reply_markup=main_menu_keyboard()
            )
            return
        await telegram_handler.send_workout_message(update.effective_chat.id, workout_data, include_tomorrow_check=True)
    except Exception as e:
        await update.message.reply_text(
            f"❌ Sorry, there was an error fetching the workouts: {str(e)}",
            reply_markup=main_menu_keyboard()
        )

async def analyze_workout(update: Update, context: CallbackContext):
    """Analyzes today's workout using OpenAI."""
    try:
        today_str = datetime.now(ZoneInfo("Asia/Jerusalem")).strftime("%Y-%m-%d")
        workout_data = workout_api_handler.get_workouts_for_date(today_str, include_tomorrow=False)
        
        if not workout_data:
            await update.message.reply_text(
                "ℹ️ No workouts found for today to analyze.",
                reply_markup=main_menu_keyboard()
            )
            return
            
        # Send a "thinking" message
        thinking_message = await update.message.reply_text(
            "🤔 Analyzing today's workout... This might take a moment.",
            reply_markup=main_menu_keyboard()
        )
        
        # Get the analysis
        analysis = openai_handler.analyze_workout(workout_data)
        
        # Send the analysis
        await update.message.reply_text(
            f"📊 *Workout Analysis*\n\n{analysis}",
            parse_mode='Markdown',
            reply_markup=main_menu_keyboard()
        )
        
        # Delete the thinking message
        await thinking_message.delete()
        
    except Exception as e:
        await update.message.reply_text(
            f"❌ Sorry, there was an error analyzing the workout: {str(e)}",
            reply_markup=main_menu_keyboard()
        )

def main_menu_keyboard():
    buttons = [
        [KeyboardButton("/start"), KeyboardButton("/stop")],
        [KeyboardButton("/upload_workout")],
        [KeyboardButton("/get_wod")],
        [KeyboardButton("/analyze_workout")]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)

async def register_bot_commands(application: Application):
    commands = [
        BotCommand("start", "Subscribe to daily workouts"),
        BotCommand("stop", "Unsubscribe"),
        BotCommand("upload_workout", "Upload workout for AI analysis"),
        BotCommand("get_wod", "Get today's workout"),
        BotCommand("analyze_workout", "Get AI analysis of today's workout")
    ]
    await application.bot.set_my_commands(commands)


def main():
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(register_bot_commands)
        .build()
    )

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("get_wod", get_wod))
    application.add_handler(CommandHandler("stop", stop))
    application.add_handler(CommandHandler("upload_workout", upload_workout))
    application.add_handler(CommandHandler("analyze_workout", analyze_workout))

    # Placeholder for upload handler
    # application.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, handle_upload))

    # Start the bot
    application.run_polling()


if __name__ == "__main__":
    main()

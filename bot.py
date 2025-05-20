# bot.py
import os
import requests
from dotenv import load_dotenv
from telegram import (
    Update,
    BotCommand,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    CallbackContext,
)

load_dotenv()

BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
SUBSCRIBERS_FILE = 'subscribers.txt'


def _load_subscribers():
    try:
        with open(SUBSCRIBERS_FILE) as f:
            return set(f.read().split())
    except FileNotFoundError:
        return set()

def _save_subscribers(subs):
    with open(SUBSCRIBERS_FILE, 'w') as f:
        f.write('\n'.join(subs))


def start(update: Update, context: CallbackContext):
    chat_id = str(update.effective_chat.id)
    subs = _load_subscribers()
    if chat_id in subs:
        update.message.reply_text("✅ You're already subscribed!")
    else:
        subs.add(chat_id)
        _save_subscribers(subs)
        update.message.reply_text(
            "🎉 Subscribed! You'll get daily workouts here.\n\n"
            "Use the menu below to see available commands.",
            reply_markup=main_menu_keyboard()
        )

def stop(update: Update, context: CallbackContext):
    chat_id = str(update.effective_chat.id)
    subs = _load_subscribers()
    if chat_id in subs:
        subs.remove(chat_id)
        _save_subscribers(subs)
        update.message.reply_text("🛑 Unsubscribed. You will no longer receive messages.")
    else:
        update.message.reply_text("ℹ️ You weren't subscribed.")

def upload_workout(update: Update, context: CallbackContext):
    update.message.reply_text(
        "📤 Great! Send me a photo or data file of your workout, and I'll run it through our AI analyzer (coming soon…).",
        reply_markup=main_menu_keyboard()
    )
    # later, you'll add a MessageHandler here to catch and process the upload

def main_menu_keyboard():
    buttons = [
        [KeyboardButton("/start"), KeyboardButton("/stop")],
        [KeyboardButton("/upload_workout")]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)


def register_bot_commands(application: Application):
    commands = [
        BotCommand("start", "Subscribe to daily workouts"),
        BotCommand("stop", "Unsubscribe"),
        BotCommand("upload_workout", "Upload workout for AI analysis")
    ]
    application.bot.set_my_commands(commands)


def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop",  stop))
    application.add_handler(CommandHandler("upload_workout", upload_workout))

    # (future) application.add_handler(MessageHandler(Filters.photo | Filters.document, handle_upload))

    # set up the "/menu"
    register_bot_commands(application)

    # start
    application.run_polling()

if __name__ == "__main__":
    main()

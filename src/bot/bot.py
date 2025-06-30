import os
import requests
from dotenv import load_dotenv
from telegram import Update, BotCommand, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, ApplicationBuilder, CommandHandler, MessageHandler, 
    filters, CallbackContext, ConversationHandler, CallbackQueryHandler
)
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from database import init_db, get_db
from models import User, Workout, Class, ClassRegistration, WorkoutResult, Membership, MembershipPlan, Product, Order
from calendar_service import CalendarService
from payment_service import PaymentService
from TelegramHandler import TelegramHandler
from OpenAIHandler import OpenAIHandler

load_dotenv()
init_db()  # Initialize database tables

# Environment variables
BOT_TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
TIMEZONE = os.getenv('TIMEZONE', 'Asia/Jerusalem')

# Initialize services
calendar_service = CalendarService()
payment_service = PaymentService()
telegram_handler = TelegramHandler(BOT_TOKEN)
openai_handler = OpenAIHandler()

# Conversation states
REGISTER = range(1)
CLASS_REGISTRATION = range(1)
UPLOAD_RESULT = range(1)
PAYMENT = range(1)

def main_menu_keyboard():
    """Create the main menu keyboard."""
    buttons = [
        [KeyboardButton("/start"), KeyboardButton("/help")],
        [KeyboardButton("/get_wod"), KeyboardButton("/analyze_workout")],
        [KeyboardButton("/register_class"), KeyboardButton("/view_schedule")],
        [KeyboardButton("/upload_result"), KeyboardButton("/my_performance")],
        [KeyboardButton("/buy"), KeyboardButton("/my_membership")]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)

async def start(update: Update, context: CallbackContext):
    """Start the bot and register user."""
    chat_id = str(update.effective_chat.id)
    user = update.effective_user

    db = next(get_db())
    existing_user = db.query(User).filter(User.telegram_id == chat_id).first()

    if existing_user:
        await update.message.reply_text(
            f"Welcome back, {user.first_name}! How can I help you today?",
            reply_markup=main_menu_keyboard()
        )
    else:
        # Create new user
        new_user = User(
            name=f"{user.first_name} {user.last_name or ''}".strip(),
            telegram_id=chat_id,
            email=None  # Will be collected during registration
        )
        db.add(new_user)
        db.commit()

        await update.message.reply_text(
            "Welcome to FitBot! 🏋️‍♂️\n"
            "Please complete your registration by sending your email.",
            reply_markup=main_menu_keyboard()
        )
        return REGISTER

async def register_email(update: Update, context: CallbackContext):
    """Handle email registration."""
    email = update.message.text
    chat_id = str(update.effective_chat.id)

    if '@' not in email:
        await update.message.reply_text(
            "Please provide a valid email address.",
            reply_markup=main_menu_keyboard()
        )
        return REGISTER

    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == chat_id).first()
    user.email = email
    db.commit()

    await update.message.reply_text(
        "Registration complete! You can now use all bot features.",
        reply_markup=main_menu_keyboard()
    )
    return ConversationHandler.END

async def get_wod(update: Update, context: CallbackContext):
    """Get today's workout."""
    try:
        today = datetime.now(ZoneInfo(TIMEZONE))
        workouts = calendar_service.get_workouts(today)
        await telegram_handler.send_workout_message(update.effective_chat.id, workouts, include_tomorrow_check=True)
    except Exception as e:
        await update.message.reply_text(
            f"❌ Sorry, there was an error fetching the workouts: {str(e)}",
            reply_markup=main_menu_keyboard()
        )

async def view_schedule(update: Update, context: CallbackContext):
    """View available classes."""
    db = next(get_db())
    today = datetime.now(ZoneInfo(TIMEZONE))
    next_week = today + timedelta(days=7)

    classes = (
        db.query(Class)
        .filter(Class.start_time >= today)
        .filter(Class.start_time <= next_week)
        .order_by(Class.start_time)
        .all()
    )

    if not classes:
        await update.message.reply_text(
            "No classes scheduled for the next week.",
            reply_markup=main_menu_keyboard()
        )
        return

    message = "📅 Upcoming Classes:\n\n"
    for class_ in classes:
        available_spots = class_.capacity - len(class_.registrations)
        message += (
            f"🕒 {class_.start_time.strftime('%Y-%m-%d %H:%M')}\n"
            f"💪 {class_.workout.title}\n"
            f"👥 Available spots: {available_spots}\n"
            f"🆔 Class ID: {class_.id}\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
        )

    keyboard = [
        [InlineKeyboardButton("Register for Class", callback_data="register_class")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        message,
        reply_markup=reply_markup
    )

async def register_class_start(update: Update, context: CallbackContext):
    """Start class registration process."""
    await update.message.reply_text(
        "Please enter the Class ID you want to register for:",
        reply_markup=main_menu_keyboard()
    )
    return CLASS_REGISTRATION

async def register_class_finish(update: Update, context: CallbackContext):
    """Complete class registration."""
    class_id = update.message.text
    chat_id = str(update.effective_chat.id)

    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == chat_id).first()
    class_ = db.query(Class).filter(Class.id == class_id).first()

    if not class_:
        await update.message.reply_text(
            "Invalid Class ID. Please try again.",
            reply_markup=main_menu_keyboard()
        )
        return CLASS_REGISTRATION

    # Check if already registered
    existing_reg = (
        db.query(ClassRegistration)
        .filter(ClassRegistration.user_id == user.id)
        .filter(ClassRegistration.class_id == class_.id)
        .first()
    )

    if existing_reg:
        await update.message.reply_text(
            "You're already registered for this class!",
            reply_markup=main_menu_keyboard()
        )
        return ConversationHandler.END

    # Check available spots
    if len(class_.registrations) >= class_.capacity:
        await update.message.reply_text(
            "Sorry, this class is full.",
            reply_markup=main_menu_keyboard()
        )
        return ConversationHandler.END

    # Register for class
    registration = ClassRegistration(
        user_id=user.id,
        class_id=class_.id
    )
    db.add(registration)
    db.commit()

    await update.message.reply_text(
        f"✅ Successfully registered for class on {class_.start_time.strftime('%Y-%m-%d %H:%M')}",
        reply_markup=main_menu_keyboard()
    )
    return ConversationHandler.END

async def upload_result(update: Update, context: CallbackContext):
    """Start workout result upload process."""
    await update.message.reply_text(
        "Please send your workout result as text:",
        reply_markup=main_menu_keyboard()
    )
    return UPLOAD_RESULT

async def handle_result(update: Update, context: CallbackContext):
    """Handle workout result submission."""
    result_text = update.message.text
    chat_id = str(update.effective_chat.id)

    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == chat_id).first()

    # Get today's workout
    today = datetime.now(ZoneInfo(TIMEZONE))
    workout = db.query(Workout).filter(Workout.date == today.date()).first()

    if not workout:
        await update.message.reply_text(
            "No workout found for today. Please try again later.",
            reply_markup=main_menu_keyboard()
        )
        return ConversationHandler.END

    # Save result
    result = WorkoutResult(
        user_id=user.id,
        workout_id=workout.id,
        result_text=result_text
    )
    db.add(result)
    db.commit()

    # Get AI analysis
    analysis = openai_handler.analyze_workout([{
        "attributes": {
            "title": workout.title,
            "description": workout.description,
            "result": result_text
        }
    }])

    await update.message.reply_text(
        f"✅ Result saved!\n\n📊 Analysis:\n{analysis}",
        reply_markup=main_menu_keyboard()
    )
    return ConversationHandler.END

async def my_performance(update: Update, context: CallbackContext):
    """Show user's performance metrics."""
    chat_id = str(update.effective_chat.id)

    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == chat_id).first()

    # Get recent results
    results = (
        db.query(WorkoutResult)
        .filter(WorkoutResult.user_id == user.id)
        .order_by(WorkoutResult.created_at.desc())
        .limit(5)
        .all()
    )

    if not results:
        await update.message.reply_text(
            "No workout results found. Start logging your workouts!",
            reply_markup=main_menu_keyboard()
        )
        return

    message = "📊 Recent Performance:\n\n"
    for result in results:
        message += (
            f"📅 {result.created_at.strftime('%Y-%m-%d')}\n"
            f"🏋️‍♂️ {result.workout.title}\n"
            f"💪 Result: {result.result_text}\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
        )

    await update.message.reply_text(message, reply_markup=main_menu_keyboard())

async def buy(update: Update, context: CallbackContext):
    """Show available products and memberships."""
    db = next(get_db())
    
    # Get active membership plans
    plans = db.query(MembershipPlan).filter(MembershipPlan.active == True).all()
    
    # Get active products
    products = db.query(Product).filter(Product.active == True).all()

    message = "🛍️ Available Items:\n\n"
    message += "📋 Membership Plans:\n"
    for plan in plans:
        message += (
            f"- {plan.name}: ${plan.price_cents/100:.2f}/month\n"
            f"  {plan.description}\n"
        )

    message += "\n🏋️‍♂️ Products:\n"
    for product in products:
        message += (
            f"- {product.name}: ${product.price_cents/100:.2f}\n"
            f"  {product.description}\n"
        )

    keyboard = [
        [InlineKeyboardButton("Buy Membership", callback_data="buy_membership")],
        [InlineKeyboardButton("Buy Product", callback_data="buy_product")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        message,
        reply_markup=reply_markup
    )

async def my_membership(update: Update, context: CallbackContext):
    """Show user's membership status."""
    chat_id = str(update.effective_chat.id)

    db = next(get_db())
    user = db.query(User).filter(User.telegram_id == chat_id).first()

    # Get active membership
    membership = (
        db.query(Membership)
        .filter(Membership.user_id == user.id)
        .filter(Membership.active == True)
        .first()
    )

    if not membership:
        keyboard = [
            [InlineKeyboardButton("Buy Membership", callback_data="buy_membership")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "You don't have an active membership.",
            reply_markup=reply_markup
        )
        return

    message = (
        f"📋 Current Membership:\n"
        f"Plan: {membership.plan.name}\n"
        f"Start Date: {membership.start_date}\n"
        f"End Date: {membership.end_date}\n"
        f"Status: {'Active' if membership.active else 'Inactive'}"
    )

    await update.message.reply_text(message, reply_markup=main_menu_keyboard())

async def help_command(update: Update, context: CallbackContext):
    """Show help message."""
    help_text = """
🤖 FitBot Commands:

Basic Commands:
/start - Start the bot
/help - Show this help message

Workout Commands:
/get_wod - Get today's workout
/analyze_workout - Get AI analysis of today's workout
/upload_result - Log your workout result

Class Commands:
/view_schedule - View available classes
/register_class - Register for a class

Membership & Shop:
/buy - View products and memberships
/my_membership - Check your membership status

Performance:
/my_performance - View your recent results
    """
    await update.message.reply_text(help_text, reply_markup=main_menu_keyboard())

async def register_bot_commands(application: Application):
    """Register bot commands."""
    commands = [
        BotCommand("start", "Start the bot"),
        BotCommand("help", "Show help message"),
        BotCommand("get_wod", "Get today's workout"),
        BotCommand("analyze_workout", "Get AI analysis of today's workout"),
        BotCommand("view_schedule", "View available classes"),
        BotCommand("register_class", "Register for a class"),
        BotCommand("upload_result", "Log your workout result"),
        BotCommand("my_performance", "View your performance"),
        BotCommand("buy", "View products and memberships"),
        BotCommand("my_membership", "Check membership status")
    ]
    await application.bot.set_my_commands(commands)

def main():
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(register_bot_commands)
        .build()
    )

    # Basic handlers
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("get_wod", get_wod))
    application.add_handler(CommandHandler("view_schedule", view_schedule))
    application.add_handler(CommandHandler("my_performance", my_performance))
    application.add_handler(CommandHandler("buy", buy))
    application.add_handler(CommandHandler("my_membership", my_membership))

    # Registration conversation
    register_conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            REGISTER: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_email)]
        },
        fallbacks=[CommandHandler("start", start)]
    )
    application.add_handler(register_conv)

    # Class registration conversation
    class_conv = ConversationHandler(
        entry_points=[CommandHandler("register_class", register_class_start)],
        states={
            CLASS_REGISTRATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_class_finish)]
        },
        fallbacks=[CommandHandler("start", start)]
    )
    application.add_handler(class_conv)

    # Result upload conversation
    result_conv = ConversationHandler(
        entry_points=[CommandHandler("upload_result", upload_result)],
        states={
            UPLOAD_RESULT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_result)]
        },
        fallbacks=[CommandHandler("start", start)]
    )
    application.add_handler(result_conv)

    # Start the bot
    application.run_polling()

if __name__ == "__main__":
    main()

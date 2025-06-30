# FitBot - CrossFit Gym Management System

A comprehensive gym management system built with Python, featuring a Telegram bot interface for members and integration with various services for gym owners.

## Features

### For Gym Owners
- 📅 Publish workouts via Gmail Calendar integration
- 👥 Registration and membership management
- 💰 Payment system for memberships and products
- 📊 Analytics and reporting

### For Members
- 📱 Daily workout notifications via Telegram
- ✍️ Class registration and scheduling
- 📝 Workout result logging
- 📈 Performance analysis and AI insights
- 🛒 Product purchases

## Tech Stack

- **Backend**: Python with SQLAlchemy
- **Database**: PostgreSQL
- **Bot Framework**: python-telegram-bot
- **Integrations**:
  - Google Calendar API
  - Stripe for payments
  - OpenAI for insights
  - n8n for workflow automation

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fitbot.git
cd fitbot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
# Create database
createdb fitbot

# Run migrations
alembic upgrade head
```

6. Start the bot:
```bash
python bot.py
```

## Environment Variables

Required environment variables:

- `DATABASE_URL`: PostgreSQL connection string
- `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
- `GOOGLE_CALENDAR_ID`: Google Calendar ID for workouts
- `STRIPE_SECRET_KEY`: Stripe API key for payments
- `OPENAI_API_KEY`: OpenAI API key for insights

See `.env.example` for a complete list of required variables.

## Database Schema

The system uses PostgreSQL with the following main tables:

- `users`: Member information
- `membership_plans`: Available membership types
- `memberships`: Active member subscriptions
- `workouts`: Daily WODs
- `classes`: Scheduled classes
- `workout_results`: Member performance records
- `products`: Shop items
- `orders`: Purchase records

## Bot Commands

- `/start` - Subscribe to daily workouts
- `/stop` - Unsubscribe
- `/get_wod` - Get today's workout
- `/analyze_workout` - Get AI analysis of today's workout
- `/upload_result` - Log your workout result
- `/register_class` - Register for a class
- `/view_schedule` - View class schedule
- `/buy` - Purchase products or memberships

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, email support@yourgym.com or join our Telegram support channel. 
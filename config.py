import os

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
PUBLIC_CHANNEL_ID = "@velcavs"
PRIVATE_CHANNEL_INVITE_LINK = "https://t.me/+NY6vYNr8tOI2OWY0"
BOT_USERNAME = "Velprembot"
PRIVATE_CHANNEL_ID = "-1003985396091"
ADMIN_IDS = [8532465159]
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MPESA_PAYBILL = os.environ.get("MPESA_PAYBILL", "5678732")
MPESA_ACCOUNT_NAME = "VELCAVS VIP"
MPESA_CONSUMER_KEY = ""
MPESA_CONSUMER_SECRET = ""
MPESA_SHORTCODE = ""
MPESA_PASSKEY = ""
MPESA_CALLBACK_URL = ""
MPESA_SANDBOX = True
PLANS = {
    "daily": {"label": "Daily", "price": 100, "days": 1, "emoji": "⚡", "tagline": "Jaribu leo!"},
    "weekly": {"label": "Weekly", "price": 600, "days": 7, "emoji": "🔥", "tagline": "Most popular!"},
    "biweekly": {"label": "2 Weeks", "price": 1000, "days": 14, "emoji": "💎", "tagline": "Great value!"},
    "monthly": {"label": "Monthly", "price": 2000, "days": 30, "emoji": "👑", "tagline": "Best deal!"},
}
CHANNEL_NAME = "Velcavs"
CHANNEL_VIBE = "romantic fiction, heartbreak stories, relationship drama"
CHANNEL_LANGUAGES = "English, Kiswahili, and Sheng"
CHANNEL_AUDIENCE = "Kenyan adults who love romance and drama"
AUTO_POST_INTERVAL_HOURS = 3
EXPIRY_CHECK_INTERVAL_HOURS = 1
DATABASE_PATH = "subscribers.db"
STORY_CATEGORIES = [
    "heartbreak", "romantic_fiction", "situationship",
    "cheating_twist", "love_confession", "breakup",
    "late_night_thoughts", "relationship_drama",
]

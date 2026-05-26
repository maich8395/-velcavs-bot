# ============================================================
#  config.py  —  Velcavs Premium Bot Configuration
# ============================================================

# ─── Telegram ────────────────────────────────────────────────
BOT_TOKEN = os.environ.get("8960555819:AAHPVlLQHRRWsO2iwWiao30CO5aY8hjM6cs")         # From @BotFather — never share this

PUBLIC_CHANNEL_ID  = "@velcavs"
PRIVATE_CHANNEL_ID = "-100XXXXXXXXXX"      # Numeric ID of your private channel
PRIVATE_CHANNEL_INVITE_LINK = "https://t.me/+NY6vYNr8tOI2OWY0"

ADMIN_IDS = [int(x) for x in os.environ.get("ADMIN_IDS", "123456789").strip("[]").split(",")]

# ─── Anthropic / Claude ──────────────────────────────────────
ANTHROPIC_API_KEY = os.environ.get("sk-ant-api03-RtT...5gAA")

# ─── M-Pesa ──────────────────────────────────────────────────
MPESA_TILL NUMBER= os.environ.get("5678732")
MPESA_ACCOUNT_NAME = "Joseph Gichimu"

# Daraja API — fill when ready for real STK push
MPESA_CONSUMER_KEY    = "YOUR_DARAJA_CONSUMER_KEY"
MPESA_CONSUMER_SECRET = "YOUR_DARAJA_CONSUMER_SECRET"
MPESA_SHORTCODE       = "YOUR_SHORTCODE"
MPESA_PASSKEY         = "YOUR_PASSKEY"
MPESA_CALLBACK_URL    = "https://yourdomain.com/mpesa/callback"
MPESA_SANDBOX         = True   # Set False for production

# ─── Subscription Plans ──────────────────────────────────────
PLANS = {
    "daily": {
        "label": "Daily",
        "price": 100,
        "days":  1,
        "emoji": "⚡",
        "tagline": "Jaribu leo — taste the premium!"
    },
    "weekly": {
        "label": "Weekly",
        "price": 600,
        "days":  7,
        "emoji": "🔥",
        "tagline": "Most popular — worth every bob!"
    },
    "biweekly": {
        "label": "2 Weeks",
        "price": 1000,
        "days":  14,
        "emoji": "💎",
        "tagline": "Value ya real — two weeks non-stop!"
    },
    "monthly": {
        "label": "Monthly",
        "price": 2000,
        "days":  30,
        "emoji": "👑",
        "tagline": "Boss level — unlimited premium stories!"
    },
}

# ─── Channel Identity ─────────────────────────────────────────
CHANNEL_NAME       = "Velcavs"
CHANNEL_VIBE       = "romantic fiction, heartbreak stories, relationship drama, suggestive storytelling"
CHANNEL_LANGUAGES  = "English, Kiswahili, and Sheng"
CHANNEL_AUDIENCE   = "Kenyan adults who love romance, drama, and spicy stories"

# ─── Bot Behaviour ───────────────────────────────────────────
AUTO_POST_INTERVAL_HOURS   = 3
EXPIRY_CHECK_INTERVAL_HOURS = 1
DATABASE_PATH = "subscribers.db"

# Story categories rotated in auto-posts
STORY_CATEGORIES = [
    "heartbreak",
    "romantic_fiction",
    "relationship_drama",
    "situationship",
    "cheating_twist",
    "love_confession",
    "breakup",
    "late_night_thoughts",
]

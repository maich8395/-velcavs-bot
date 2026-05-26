# 🔥 Velcavs Premium Bot

Claude AI-powered Telegram bot for @velcavs — romantic fiction, heartbreak stories,
relationship drama, and M-Pesa subscriptions.

## Quick Setup (4 things to fill in config.py)

1. BOT_TOKEN         → From @BotFather on Telegram
2. ANTHROPIC_API_KEY → From console.anthropic.com
3. MPESA_PAYBILL     → Your Safaricom Till or Paybill number
4. ADMIN_IDS         → Your Telegram numeric ID (get from @userinfobot)

Everything else is already pre-configured for Velcavs.

## Run

```bash
pip install -r requirements.txt

# Terminal 1
python bot.py

# Terminal 2
python dashboard.py
# Open: http://localhost:5000?token=admin1234
```

## What the bot does automatically

Story post (every 3 hours) → Claude writes a fresh heartbreak/romance/situationship
story in English+Kiswahili+Sheng mix, posts to @velcavs with a VIP join button.

Promo post (every 1.5 hours after each story) → A standalone enticing message
pushing readers to join the premium channel.

Subscriber management → M-Pesa payment flow, expiry tracking, renewal reminders.

Admin commands → /stats /post /broadcast

User commands → /start /story /status /plans /help

## Story Categories (auto-rotated)

heartbreak · romantic_fiction · situationship · cheating_twist ·
love_confession · breakup · late_night_thoughts · relationship_drama

## Plans

| Plan    | Price    | Duration |
|---------|----------|----------|
| Daily   | KSH 100  | 1 day    |
| Weekly  | KSH 600  | 7 days   |
| 2 Weeks | KSH 1000 | 14 days  |
| Monthly | KSH 2000 | 30 days  |

## Posting Schedule (Nairobi time)

The bot rotates through story categories so every post feels fresh.
Claude rewrites each story from scratch — no repeats.

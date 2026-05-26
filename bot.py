import logging
import random
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, ContextTypes, filters, JobQueue
)
import config
import database as db
import claude_ai as ai
from mpesa import validate_kenyan_phone

logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

CHOOSING_PLAN, ENTERING_PHONE, AWAITING_CONFIRMATION = range(3)
_category_index = 0

def plans_keyboard():
    rows = []
    for key, plan in config.PLANS.items():
        rows.append([InlineKeyboardButton(
            f"{plan['emoji']} {plan['label']} · KSH {plan['price']:,} — {plan['tagline']}",
            callback_data=f"plan_{key}"
        )])
    return InlineKeyboardMarkup(rows)

def join_keyboard(label="🔥 Join VIP — Soma Full Stories"):
    return InlineKeyboardMarkup([[InlineKeyboardButton(label, callback_data="join_premium")]])

def renew_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Renew My VIP Access", callback_data="join_premium")]])

def access_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔐 Enter Velcavs VIP Channel", url=config.PRIVATE_CHANNEL_INVITE_LINK)]])

def story_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📖 Another Story", callback_data="random_story")],
        [InlineKeyboardButton("🔥 Join VIP for Full Stories", callback_data="join_premium")],
    ])

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db.init_db()
    user = update.effective_user
    msg = ai.welcome_message(user.first_name)
    await update.message.reply_text(msg, reply_markup=join_keyboard("🔥 Jiunge VIP — Soma Stories Zote"))

async def cmd_story(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ Naandika story yako... ngoja kidogo...")
    story = ai.generate_story()
    await update.message.reply_text(story, reply_markup=story_keyboard())

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    sub = db.get_active_subscriber(user.id)
    if not sub:
        old = db.get_subscriber(user.id)
        if old:
            plan_cfg = config.PLANS.get(old["plan"], {})
            await update.message.reply_text(ai.expired_message(user.first_name, plan_cfg.get("label", old["plan"])), reply_markup=renew_keyboard())
        else:
            await update.message.reply_text(f"Hujoin VIP bado, {user.first_name}!\nJiunge sasa 👇", reply_markup=join_keyboard())
        return
    expiry = datetime.fromisoformat(sub["expiry_date"])
    days_left = (expiry - datetime.now()).days
    plan_cfg = config.PLANS.get(sub["plan"], {})
    warning = "\n\n⚠️ Renew haraka!" if days_left <= 1 else f"\n\n🔔 {days_left} days zimebaki!" if days_left <= 3 else ""
    await update.message.reply_text(
        f"📊 *Velcavs VIP Status*\n\n👤 {user.first_name}\n📋 {plan_cfg.get('emoji','')} {plan_cfg.get('label','')}\n📅 Expires: {expiry.strftime('%d %B %Y')}\n⏳ Days left: {days_left}{warning}",
        parse_mode="Markdown", reply_markup=renew_keyboard() if days_left <= 3 else None)

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📖 *Commands*\n\n/start — Welcome\n/story — Random story\n/status — VIP status\n/plans — See plans\n/help — Help", parse_mode="Markdown")

async def cmd_plans(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(ai.plans_intro(), parse_mode="Markdown", reply_markup=join_keyboard())

async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in config.ADMIN_IDS:
        return
    s = db.get_stats()
    await update.message.reply_text(
        f"📊 *Velcavs Stats*\n\n👥 Total: {s['total']}\n✅ Active: {s['active']}\n❌ Expired: {s['expired']}\n\n💰 Leo: KSH {s['revenue_today']:,}\nWiki: KSH {s['revenue_week']:,}\nMwezi: KSH {s['revenue_month']:,}",
        parse_mode="Markdown")

async def cmd_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in config.ADMIN_IDS:
        return
    await update.message.reply_text("📝 Naandika...")
    content = ai.auto_post_story_with_promo()
    try:
        await context.bot.send_message(chat_id=config.PUBLIC_CHANNEL_ID, text=content, reply_markup=join_keyboard("🔥 Jiunge VIP"))
        await update.message.reply_text("✅ Imepost!")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")

async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in config.ADMIN_IDS:
        return
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
    await context.bot.send_message(chat_id=config.PUBLIC_CHANNEL_ID, text=text, reply_markup=join_keyboard())
    await update.message.reply_text("✅ Imetumwa!")

async def cb_join_premium(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(ai.plans_intro(), parse_mode="Markdown", reply_markup=plans_keyboard())
    return CHOOSING_PLAN

async def cb_plan_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    plan_key = query.data.replace("plan_", "")
    if plan_key not in config.PLANS:
        return CHOOSING_PLAN
    plan = config.PLANS[plan_key]
    context.user_data.update({"plan_key": plan_key, "plan": plan})
    await query.edit_message_text(
        f"✅ *{plan['emoji']} {plan['label']} — KSH {plan['price']:,}* imechaguliwa!\n\n📱 Ingiza *namba yako ya M-Pesa*:\n_(Mfano: 07XXXXXXXX)_",
        parse_mode="Markdown")
    return ENTERING_PHONE

async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    user = update.effective_user
    if not validate_kenyan_phone(phone):
        await update.message.reply_text("❌ Namba si sahihi. Ingiza kama *07XXXXXXXX*", parse_mode="Markdown")
        return ENTERING_PHONE
    plan = context.user_data["plan"]
    context.user_data["phone"] = phone
    instructions = ai.payment_instructions(user.first_name, f"{plan['emoji']} {plan['label']}", plan["price"], phone, config.MPESA_PAYBILL)
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Nililipa — Activate Access Yangu", callback_data="confirm_payment")],
        [InlineKeyboardButton("🔙 Badilisha Plan", callback_data="join_premium")]
    ])
    await update.message.reply_text(instructions, parse_mode="Markdown", reply_markup=keyboard)
    return AWAITING_CONFIRMATION

async def cb_confirm_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Inaprocess... ⏳")
    user = query.from_user
    plan_key = context.user_data.get("plan_key")
    plan = context.user_data.get("plan")
    phone = context.user_data.get("phone", "unknown")
    if not plan_key or not plan:
        await query.edit_message_text("⚠️ Session imeexpire. Anza tena na /start")
        return ConversationHandler.END
    expiry = datetime.now() + timedelta(days=plan["days"])
    db.upsert_subscriber(user_id=user.id, username=user.username or "", first_name=user.first_name, phone=phone, plan=plan_key, amount=plan["price"], expiry=expiry)
    db.log_payment(user.id, plan_key, plan["price"], phone)
    success = ai.success_message(user.first_name, f"{plan['emoji']} {plan['label']}", expiry.strftime("%d %B %Y"))
    await query.edit_message_text(success + f"\n\n📅 *Expires:* {expiry.strftime('%d %B %Y')}", parse_mode="Markdown", reply_markup=access_keyboard())
    for admin_id in config.ADMIN_IDS:
        try:
            await context.bot.send_message(chat_id=admin_id, text=f"💰 *Subscriber mpya!*\n👤 {user.first_name}\n📋 {plan['label']} — KSH {plan['price']:,}\n📱 {phone}\n📅 {expiry.strftime('%d %B %Y')}", parse_mode="Markdown")
        except Exception:
            pass
    context.user_data.clear()
    return ConversationHandler.END

async def cb_random_story(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Naandika story... ✍️")
    story = ai.generate_story()
    await context.bot.send_message(chat_id=query.message.chat_id, text=story, reply_markup=story_keyboard())

async def cb_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()
    await query.edit_message_text("Sawa! Type /start unapotaka kuendelea 😊")
    return ConversationHandler.END

async def job_auto_post(context: ContextTypes.DEFAULT_TYPE):
    global _category_index
    categories = config.STORY_CATEGORIES
    category = categories[_category_index % len(categories)]
    _category_index += 1
    try:
        content = ai.auto_post_story_with_promo()
        await context.bot.send_message(chat_id=config.PUBLIC_CHANNEL_ID, text=content, reply_markup=join_keyboard("🔥 Jiunge VIP — Soma Full Version"))
        logger.info(f"Auto-post sent: {category}")
    except Exception as exc:
        logger.error(f"Auto-post failed: {exc}")

async def job_promo(context: ContextTypes.DEFAULT_TYPE):
    try:
        promo = ai.promo_caption()
        await context.bot.send_message(chat_id=config.PUBLIC_CHANNEL_ID, text=promo, reply_markup=join_keyboard("💎 Jiunge Velcavs VIP Sasa"))
        logger.info("Promo sent.")
    except Exception as exc:
        logger.error(f"Promo failed: {exc}")

async def job_check_subs(context: ContextTypes.DEFAULT_TYPE):
    for sub in db.get_expiring_soon(hours=24):
        expiry = datetime.fromisoformat(sub["expiry_date"])
        hours_left = max(0, int((expiry - datetime.now()).total_seconds() / 3600))
        plan_cfg = config.PLANS.get(sub["plan"], {})
        msg = ai.expiry_warning(sub["first_name"], plan_cfg.get("label", sub["plan"]), hours_left)
        try:
            await context.bot.send_message(chat_id=sub["user_id"], text=msg, parse_mode="Markdown", reply_markup=renew_keyboard())
            db.mark_expiry_notified(sub["user_id"])
        except Exception:
            pass
    for sub in db.get_expired_subscribers():
        plan_cfg = config.PLANS.get(sub["plan"], {})
        msg = ai.expired_message(sub["first_name"], plan_cfg.get("label", sub["plan"]))
        try:
            await context.bot.send_message(chat_id=sub["user_id"], text=msg, parse_mode="Markdown", reply_markup=renew_keyboard())
        except Exception:
            pass
        db.deactivate_subscriber(sub["user_id"])

async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start", "Karibu Velcavs!"),
        BotCommand("story", "Pata story ya bure"),
        BotCommand("status", "Check VIP subscription yako"),
        BotCommand("plans", "Ona plan zote za VIP"),
        BotCommand("help", "Msaada & commands"),
    ])
    job_queue = application.job_queue
    job_queue.run_repeating(job_auto_post, interval=config.AUTO_POST_INTERVAL_HOURS * 3600, first=10)
    job_queue.run_repeating(job_promo, interval=config.AUTO_POST_INTERVAL_HOURS * 3600, first=5400)
    job_queue.run_repeating(job_check_subs, interval=3600, first=60)
    logger.info("Velcavs bot running 🔥")

def main():
    db.init_db()
    app = Application.builder().token(config.BOT_TOKEN).post_init(post_init).build()
    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_join_premium, pattern="^join_premium$")],
        states={
            CHOOSING_PLAN: [CallbackQueryHandler(cb_plan_selected, pattern="^plan_")],
            ENTERING_PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone),
                CallbackQueryHandler(cb_join_premium, pattern="^join_premium$"),
            ],
            AWAITING_CONFIRMATION: [
                CallbackQueryHandler(cb_confirm_payment, pattern="^confirm_payment$"),
                CallbackQueryHandler(cb_join_premium, pattern="^join_premium$"),
            ],
        },
        fallbacks=[CommandHandler("start", cmd_start), CallbackQueryHandler(cb_cancel, pattern="^cancel$")],
        per_user=True, per_chat=True, allow_reentry=True,
    )
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("story", cmd_story))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("plans", cmd_plans))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("post", cmd_post))
    app.add_handler(CommandHandler("broadcast", cmd_broadcast))
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(cb_random_story, pattern="^random_story$"))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    db.init_db()
    app = Application.builder().token(config.BOT_TOKEN).post_init(post_init).build()
    conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(cb_join_premium, pattern="^join_premium$")],
        states={
            CHOOSING_PLAN: [CallbackQueryHandler(cb_plan_selected, pattern="^plan_")],
            ENTERING_PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone),
                CallbackQueryHandler(cb_join_premium, pattern="^join_premium$"),
            ],
            AWAITING_CONFIRMATION: [
                CallbackQueryHandler(cb_confirm_payment, pattern="^confirm_payment$"),
                CallbackQueryHandler(cb_join_premium, pattern="^join_premium$"),
            ],
        },
        fallbacks=[CommandHandler("start", cmd_start), CallbackQueryHandler(cb_cancel, pattern="^cancel$")],
        per_user=True, per_chat=True, allow_reentry=True,
    )
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("story", cmd_story))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("plans", cmd_plans))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("post", cmd_post))
    app.add_handler(CommandHandler("broadcast", cmd_broadcast))
    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(cb_random_story, pattern="^random_story$"))
    app.run_polling(allowed_updates=Update.ALL_TYPES, stop_signals=None)

if __name__ == "__main__":
    main()import threading
from flask import Flask
server = Flask(__name__)

@server.route('/')
def home():
    return "Velcavs bot is running! 🔥"

threading.Thread(target=lambda: server.run(host='0.0.0.0', port=8080)).start()

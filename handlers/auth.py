from telegram import Update
from telegram.ext import ContextTypes
from database.models import (
    get_user, create_user, is_authorized,
    is_admin, redeem_auth_key, authorize_user
)
from utils.keyboards import main_menu_keyboard, admin_panel_keyboard
from utils.helpers import safe_edit

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ /start
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not get_user(user.id):
        create_user(user.id, user.username)

    if is_admin(user.id):
        await update.message.reply_text(
            "✦ *Master has arrived~* ♡\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Ara ara~ Welcome back~\n"
            "What shall we do today? ◈",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
        return

    if is_authorized(user.id):
        await update.message.reply_text(
            "✦ *Irasshaimase~* ♡\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Welcome back, you naughty little weeb~\n"
            "Ufufu~ What are we watching today? ◈",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
        return

    await update.message.reply_text(
        "✦ *Ara ara~ Who are you~?*\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "⁄ ⁄•⁄ω⁄•⁄ ⁄\n\n"
        "Looks like you don't have access yet,\n"
        "you sneaky little thing~\n\n"
        "Redeem your key using ▷\n"
        "`/auth your-code-here`\n\n"
        "Don't keep me waiting~ ♡",
        parse_mode="Markdown"
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ /auth [code]
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def auth_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if is_authorized(user.id):
        await update.message.reply_text(
            "✦ Ehehe~ You're already in~\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "No need to redeem again, silly~ ♡",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )
        return

    if not context.args:
        await update.message.reply_text(
            "✦ *Kyaa~* You forgot the code~\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Use it like this ▷\n"
            "`/auth your-code-here`\n\n"
            "Don't be so careless~ ♡",
            parse_mode="Markdown"
        )
        return

    code   = context.args[0].strip()
    result = redeem_auth_key(code, user.id)

    if result == "ok":
        authorize_user(user.id, code)
        await update.message.reply_text(
            "✦ *Kyaa~ It worked~!* ♡\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Welcome to the club, naughty weeb~\n"
            "Ufufu~ I've been waiting for you ◈",
            parse_mode="Markdown",
            reply_markup=main_menu_keyboard()
        )

    elif result == "expired":
        await update.message.reply_text(
            "✦ *Ara ara~ Too slow~* (｡•́︿•̀｡)\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "This key has expired~\n"
            "Ask your admin for a fresh one~ ♡",
            parse_mode="Markdown"
        )

    elif result == "used":
        await update.message.reply_text(
            "✦ *Ehehe~ Nice try~* ◇\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Someone already used this key~\n"
            "This one isn't yours, sneaky~ ♡",
            parse_mode="Markdown"
        )

    else:
        await update.message.reply_text(
            "✦ *Kyaa~ That's not right~* (｡•́︿•̀｡)\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Invalid key~ Did you make a mistake?\n"
            "Try again with `/auth your-code` ♡",
            parse_mode="Markdown"
        )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ MAIN MENU CALLBACK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await safe_edit(
        query,
        "✦ *Irasshaimase~* ♡\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Welcome back, you naughty little weeb~\n"
        "What are we watching today? ◈",
        reply_markup=main_menu_keyboard()
    )

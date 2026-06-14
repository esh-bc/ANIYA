from telegram import Update
from telegram.ext import ContextTypes
from database.models import is_authorized, get_recent_animes, get_all_animes
from utils.keyboards import anime_list_keyboard
from utils.helpers import safe_edit

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ RECENT UPLOADS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def recent_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    page          = int(query.data.split(":")[1])
    animes, total = get_recent_animes(page)

    if not animes:
        await safe_edit(
            query,
            "✦ *Ara ara~ Nothing here yet~* ◇\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "No recent uploads in the last 48 hours~\n"
            "Check back later, naughty~ ♡",
            reply_markup=anime_list_keyboard([], page, 0, "recent")
        )
        return

    await safe_edit(
        query,
        "✦ *Hot and Fresh~* ♡\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "These just dropped~ They disappear\n"
        "after 48 hours so hurry up~ ◈\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"◇ Showing {len(animes)} of {total} animes",
        reply_markup=anime_list_keyboard(animes, page, total, "recent")
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ ALL UPLOADS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def all_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    page          = int(query.data.split(":")[1])
    animes, total = get_all_animes(page)

    if not animes:
        await safe_edit(
            query,
            "✦ *Ehehe~ Empty in here~* ◇\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "No animes uploaded yet~\n"
            "Tell the admin to get to work~ ♡",
            reply_markup=anime_list_keyboard([], page, 0, "all")
        )
        return

    await safe_edit(
        query,
        "✦ *The Full Collection~* ♡\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Everything uploaded so far~\n"
        "Pick your poison, naughty weeb~ ◈\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"◇ Showing {len(animes)} of {total} animes",
        reply_markup=anime_list_keyboard(animes, page, total, "all")
    )

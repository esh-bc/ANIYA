from telegram import Update
from telegram.ext import ContextTypes
from database.models import get_anime_by_id, is_admin
from utils.keyboards import anime_detail_keyboard, confirm_delete_keyboard, main_menu_keyboard
from utils.captions import anime_detail_caption
from utils.helpers import safe_edit

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ ANIME DETAIL PAGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def anime_detail_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # callback_data format: anime:{anime_id}:{back_mode}:{back_page}
    parts     = query.data.split(":")
    anime_id  = parts[1]
    back_mode = parts[2]
    back_page = int(parts[3])

    anime = get_anime_by_id(anime_id)
    if not anime:
        await safe_edit(
            query,
            "✦ *Kyaa~ I couldn't find that~* ◇\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "This anime might have been deleted~\n"
            "Go back and try again~ ♡"
        )
        return

    caption  = anime_detail_caption(anime)
    admin    = is_admin(query.from_user.id)
    keyboard = anime_detail_keyboard(anime, admin, back_mode, back_page)

    if anime.get("banner_url"):
        try:
            await query.message.reply_photo(
                photo        = anime["banner_url"],
                caption      = caption,
                parse_mode   = "Markdown",
                reply_markup = keyboard
            )
            await query.message.delete()
            return
        except Exception:
            pass

    await safe_edit(query, caption, reply_markup=keyboard)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ DELETE ANIME (admin only)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def delete_anime_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        await query.answer("◈ Not allowed~", show_alert=True)
        return

    anime_id = query.data.split(":")[1]
    anime    = get_anime_by_id(anime_id)
    name     = anime["name"] if anime else "this anime"

    await safe_edit(
        query,
        f"✦ *Are you sure, Master~?* ◇\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"You're about to delete\n"
        f"*{name}* forever~\n\n"
        f"◈ This cannot be undone~ ♡",
        reply_markup=confirm_delete_keyboard(anime_id)
    )


async def delete_anime_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        await query.answer("◈ Not allowed~", show_alert=True)
        return

    from database.models import delete_anime
    anime_id = query.data.split(":")[1]
    anime    = get_anime_by_id(anime_id)
    name     = anime["name"] if anime else "That anime"

    delete_anime(anime_id)

    await safe_edit(
        query,
        f"✦ *Done~* ♡\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"*{name}* has been deleted~\n"
        f"Gone forever~ ◇",
        reply_markup=main_menu_keyboard()
    )

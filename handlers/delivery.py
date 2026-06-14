from telegram import Update
from telegram.ext import ContextTypes
from database.models import get_anime_by_id
from utils.captions import delivery_caption
from config import STORAGE_CHANNEL

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ SEASON FILE DELIVERY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def season_delivery_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # callback_data format: season:{anime_id}:{season_number}
    parts         = query.data.split(":")
    anime_id      = parts[1]
    season_number = int(parts[2])

    anime = get_anime_by_id(anime_id)
    if not anime:
        await query.answer("◈ Anime not found~", show_alert=True)
        return

    # find the matching season
    target_season = None
    for s in anime.get("seasons", []):
        if s["number"] == season_number:
            target_season = s
            break

    if not target_season or not target_season.get("file_id"):
        await query.answer("◈ Season file not found~", show_alert=True)
        return

    caption = delivery_caption(anime, season_number)

    try:
        # send the file using file_id — no forward tag
        await context.bot.send_document(
            chat_id    = query.message.chat_id,
            document   = target_season["file_id"],
            caption    = caption,
            parse_mode = "Markdown"
        )
    except Exception as e:
        await query.message.reply_text(
            "✦ *Kyaa~ Something went wrong~* ◇\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Couldn't send the file~\n"
            "Please try again later~ ♡",
            parse_mode="Markdown"
        )

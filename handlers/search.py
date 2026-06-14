from telegram import Update, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import ContextTypes
from database.models import search_animes, get_anime_by_id
from utils.keyboards import anime_list_keyboard, main_menu_keyboard
from utils.captions import _lang_label
from utils.helpers import safe_edit
import hashlib

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ SEARCH PROMPT (button tap)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def search_prompt_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    context.user_data["state"] = "searching"

    await safe_edit(
        query,
        "✦ *Searching~* ♡\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Ehehe~ Looking for something?\n"
        "Send me the anime name~\n"
        "I'll find it~ ◈\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "◇ Or use inline mode anywhere ▷\n"
        "`@yourbotname anime name`",
        reply_markup=main_menu_keyboard()
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ SEARCH MESSAGE HANDLER (text input)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def search_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("state") != "searching":
        return

    text          = update.message.text.strip()
    page          = 0
    animes, total = search_animes(text, page)

    context.user_data["search_query"] = text
    context.user_data["state"]        = None

    if not animes:
        await update.message.reply_text(
            "✦ *Ara ara~ Nothing found~* ◇\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"No results for *{text}*~\n"
            "Try a different name~ ♡",
            parse_mode   = "Markdown",
            reply_markup = main_menu_keyboard()
        )
        return

    await update.message.reply_text(
        f"✦ *Found something~* ♡\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"◈ Results for *{text}*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"◇ Showing {len(animes)} of {total} results",
        parse_mode   = "Markdown",
        reply_markup = anime_list_keyboard(animes, page, total, "search")
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ SEARCH PAGINATION CALLBACK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def search_page_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    page     = int(query.data.split(":")[1])
    search_q = context.user_data.get("search_query", "")

    if not search_q:
        await safe_edit(
            query,
            "✦ *Kyaa~ Search expired~* ◇\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Please search again~ ♡",
            reply_markup=main_menu_keyboard()
        )
        return

    animes, total = search_animes(search_q, page)

    await safe_edit(
        query,
        f"✦ *Results for {search_q}~* ♡\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"◇ Showing {len(animes)} of {total} results",
        reply_markup=anime_list_keyboard(animes, page, total, "search")
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ INLINE QUERY HANDLER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def inline_query_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query_text = update.inline_query.query.strip()

    if not query_text:
        return

    animes, _ = search_animes(query_text, page=0)
    results   = []

    for anime in animes[:10]:
        anime_id = str(anime["_id"])
        genres   = ", ".join(anime.get("genres", [])) or "N/A"
        lang     = _lang_label(anime.get("language"))
        uid      = hashlib.md5(anime_id.encode()).hexdigest()

        description = f"◈ {genres}  ▷  {lang}  ▷  {anime.get('year', 'N/A')}"

        message_text = (
            f"✦ *{anime.get('name', 'Unknown')}*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"◈ Genre   ▷  {genres}\n"
            f"◈ Type    ▷  *{lang}*\n"
            f"◈ Year    ▷  {anime.get('year', 'N/A')}\n"
            f"◈ Rating  ▷  {anime.get('rating', 'N/A')} ✦\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"◇ Find it in the bot~ ♡"
        )

        results.append(
            InlineQueryResultArticle(
                id          = uid,
                title       = anime.get("name", "Unknown"),
                description = description,
                thumb_url   = anime.get("banner_url"),
                input_message_content = InputTextMessageContent(
                    message_text = message_text,
                    parse_mode   = "Markdown"
                )
            )
        )

    await update.inline_query.answer(results, cache_time=30)

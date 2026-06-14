import random
import string
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from database.models import (
    is_admin, get_anime_by_id, insert_anime,
    update_anime, add_season_to_anime,
    create_auth_key
)
from utils.keyboards import (
    admin_panel_keyboard, upload_preview_keyboard,
    edit_anime_keyboard, language_keyboard,
    after_season_keyboard, main_menu_keyboard
)
from utils.captions import upload_preview_caption
from utils.tmdb import fetch_tmdb_data, extract_tmdb_id
from utils.progress import animate_progress
from utils.helpers import safe_edit
from config import STORAGE_CHANNEL

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ /admin COMMAND
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text(
            "✦ *Kyaa~ You can't go there~* ◇\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Admin only section~\n"
            "Nice try though~ ♡",
            parse_mode="Markdown"
        )
        return

    await update.message.reply_text(
        "✦ *Master has arrived~* ♡\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Ara ara~ Welcome to the admin panel~\n"
        "What shall we do today? ◈",
        parse_mode   = "Markdown",
        reply_markup = admin_panel_keyboard()
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ ADMIN PANEL CALLBACK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def admin_panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        await query.answer("◈ Not allowed~", show_alert=True)
        return

    await safe_edit(
        query,
        "✦ *Master has arrived~* ♡\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Ara ara~ Welcome to the admin panel~\n"
        "What shall we do today? ◈",
        reply_markup=admin_panel_keyboard()
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ UPLOAD ANIME — STEP 1: ASK TMDB LINK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def upload_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        await query.answer("◈ Not allowed~", show_alert=True)
        return

    context.user_data["state"] = "awaiting_tmdb"

    await safe_edit(
        query,
        "✦ *Upload Anime~* ♡\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Ooh~ Give me the TMDB link\n"
        "and I'll fetch everything~\n\n"
        "◈ Paste the link or ID below ▷\n"
        "`https://www.themoviedb.org/tv/46260`\n"
        "`https://www.themoviedb.org/movie/149870`\n\n"
        "I'm very talented, you know~ ◇"
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ UPLOAD ANIME — STEP 2: RECEIVE TMDB LINK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def handle_tmdb_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("state") != "awaiting_tmdb":
        return
    if not is_admin(update.effective_user.id):
        return

    text   = update.message.text.strip()
    result = extract_tmdb_id(text)

    if not result:
        await update.message.reply_text(
            "✦ *Kyaa~ Invalid link~* ◇\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "I couldn't read that~\n"
            "Send a valid TMDB link or ID~ ♡",
            parse_mode="Markdown"
        )
        return

    tmdb_id, media_type = result
    context.user_data["state"] = None

    # show progress bar
    prog_msg = await update.message.reply_text(
        "✦ Fetching data for you~ ♡\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "◌ ◌ ◌ ◌ ◌ ◌ ◌ ◌ ◌ ◌  0%"
    )
    await animate_progress(prog_msg)

    # fetch from TMDB
    data = fetch_tmdb_data(tmdb_id, media_type)

    if not data:
        await prog_msg.edit_text(
            "✦ *Kyaa~ TMDB fetch failed~* ◇\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Couldn't fetch data~\n"
            "Check the link and try again~ ♡",
            parse_mode="Markdown"
        )
        return

    # save draft to DB (no upload_date yet — set on publish)
    data["upload_date"] = None
    data["uploaded_by"] = update.effective_user.id
    anime_id = insert_anime(data)

    context.user_data["current_anime_id"] = anime_id

    caption  = upload_preview_caption(data)
    keyboard = upload_preview_keyboard(anime_id)

    if data.get("banner_url"):
        try:
            await update.message.reply_photo(
                photo        = data["banner_url"],
                caption      = caption,
                parse_mode   = "Markdown",
                reply_markup = keyboard
            )
            return
        except Exception:
            pass

    await update.message.reply_text(
        caption,
        parse_mode   = "Markdown",
        reply_markup = keyboard
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ UPLOAD — STEP 3: CONTINUE (pick language)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def upload_continue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    anime_id = query.data.split(":")[1]
    context.user_data["current_anime_id"] = anime_id

    text = (
        "✦ *Almost there~* ♡\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Nee nee~ Is this Hindi Dub,\n"
        "Hindi Sub, or both? ◈"
    )

    if query.message.photo:
        await query.edit_message_caption(
            caption      = text,
            parse_mode   = "Markdown",
            reply_markup = language_keyboard(anime_id)
        )
    else:
        await query.edit_message_text(
            text,
            parse_mode   = "Markdown",
            reply_markup = language_keyboard(anime_id)
        )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ UPLOAD — STEP 4: SET LANGUAGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LANG_LABELS = {
    "dub"  : "HINDI DUB",
    "sub"  : "HINDI SUB",
    "both" : "HINDI DUB + SUB",
}

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query    = update.callback_query
    await query.answer()

    parts    = query.data.split(":")
    lang     = parts[1]
    anime_id = parts[2]

    update_anime(anime_id, {"language": lang})
    context.user_data["current_anime_id"] = anime_id
    context.user_data["state"]            = "awaiting_season_file"
    context.user_data["current_season"]   = 1

    lang_str = LANG_LABELS.get(lang, lang.upper())

    prompt = (
        f"✦ *Set to {lang_str}~* ♡\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Kyaa~ Now send me the file\n"
        f"for *Season 1*~\n\n"
        f"◈ Just send the document ▷"
    )

    # always send a fresh text message so the photo doesn't linger
    await query.message.reply_text(prompt, parse_mode="Markdown")
    # try to clean up the previous message silently
    try:
        await query.message.delete()
    except Exception:
        pass

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ UPLOAD — STEP 5: RECEIVE SEASON FILE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def handle_season_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("state") != "awaiting_season_file":
        return
    if not is_admin(update.effective_user.id):
        return

    doc = update.message.document
    if not doc:
        await update.message.reply_text(
            "✦ *Kyaa~ That's not a file~* ◇\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Send me a document file please~ ♡",
            parse_mode="Markdown"
        )
        return

    anime_id      = context.user_data.get("current_anime_id")
    season_number = context.user_data.get("current_season", 1)
    file_id       = doc.file_id

    # forward to storage channel to get stable file_id
    try:
        fwd = await context.bot.send_document(
            chat_id   = STORAGE_CHANNEL,
            document  = file_id,
            caption   = f"◈ Stored: Season {season_number} | anime_id: {anime_id}"
        )
        stored_file_id = fwd.document.file_id
    except Exception:
        stored_file_id = file_id

    add_season_to_anime(anime_id, season_number, stored_file_id)

    context.user_data["state"]          = None
    context.user_data["current_season"] = season_number + 1

    await update.message.reply_text(
        f"✦ *Season {season_number} added~* ♡\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Ehehe~ File saved successfully~\n"
        f"What's next, Master? ◈",
        parse_mode   = "Markdown",
        reply_markup = after_season_keyboard(anime_id, season_number + 1)
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ ADD ANOTHER SEASON (from callback)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def add_season_next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts         = query.data.split(":")
    anime_id      = parts[1]
    season_number = int(parts[2])

    context.user_data["state"]            = "awaiting_season_file"
    context.user_data["current_anime_id"] = anime_id
    context.user_data["current_season"]   = season_number

    await safe_edit(
        query,
        f"✦ *Adding Season {season_number}~* ♡\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Kyaa~ Send me the file for\n"
        f"*Season {season_number}*~ ◈"
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ ADD SEASON FROM ANIME DETAIL (admin)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def add_season_from_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        await query.answer("◈ Not allowed~", show_alert=True)
        return

    anime_id = query.data.split(":")[1]
    anime    = get_anime_by_id(anime_id)

    next_season = len(anime.get("seasons", [])) + 1

    context.user_data["state"]            = "awaiting_season_file"
    context.user_data["current_anime_id"] = anime_id
    context.user_data["current_season"]   = next_season

    await query.message.reply_text(
        f"✦ *Adding Season {next_season}~* ♡\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Kyaa~ Send me the file for\n"
        f"*Season {next_season}*~ ◈",
        parse_mode="Markdown"
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ PUBLISH ANIME
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def publish_anime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    anime_id = query.data.split(":")[1]
    update_anime(anime_id, {"upload_date": datetime.utcnow()})

    anime = get_anime_by_id(anime_id)
    name  = anime["name"] if anime else "Anime"

    await safe_edit(
        query,
        f"✦ *Published~* ♡\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"*{name}* is now live~\n"
        f"Users can find it now~ ✦\n"
        f"Good job, Master~ ◈",
        reply_markup=admin_panel_keyboard()
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ EDIT ANIME MENU
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def edit_anime_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    anime_id = query.data.split(":")[1]

    await safe_edit(
        query,
        "✦ *Edit Mode~* ♡\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Ufufu~ What do you want\n"
        "to change, Master? ◈",
        reply_markup=edit_anime_keyboard(anime_id)
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ EDIT FIELD — PROMPT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FIELD_LABELS = {
    "name"      : "name",
    "banner_url": "banner URL (16:9 image link)",
    "genres"    : "genres (comma separated)",
    "year"      : "year",
    "language"  : "language (dub / sub / both)",
}

async def edit_field_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    parts    = query.data.split(":")
    field    = parts[1]
    anime_id = parts[2]

    context.user_data["state"]            = f"editing_{field}"
    context.user_data["current_anime_id"] = anime_id

    label = FIELD_LABELS.get(field, field)

    await safe_edit(
        query,
        f"✦ *Editing {label}~* ♡\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Send me the new {label}~\n"
        f"I'm listening~ ◈"
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ EDIT FIELD — RECEIVE VALUE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def edit_field_receive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get("state", "")
    if not state.startswith("editing_"):
        return
    if not is_admin(update.effective_user.id):
        return

    field    = state.replace("editing_", "")
    anime_id = context.user_data.get("current_anime_id")
    text     = update.message.text.strip()

    if field == "genres":
        value = [g.strip() for g in text.split(",")]
    else:
        value = text

    update_anime(anime_id, {field: value})
    context.user_data["state"] = None

    anime    = get_anime_by_id(anime_id)
    caption  = upload_preview_caption(anime)
    keyboard = upload_preview_keyboard(anime_id)

    if anime.get("banner_url"):
        try:
            await update.message.reply_photo(
                photo        = anime["banner_url"],
                caption      = caption,
                parse_mode   = "Markdown",
                reply_markup = keyboard
            )
            return
        except Exception:
            pass

    await update.message.reply_text(
        f"✦ *Updated~* ♡\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{caption}",
        parse_mode   = "Markdown",
        reply_markup = keyboard
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ GENERATE AUTH KEYS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def genkey_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        await query.answer("◈ Not allowed~", show_alert=True)
        return

    context.user_data["state"] = "awaiting_genkey"

    await safe_edit(
        query,
        "✦ *Generate Keys~* ♡\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Send the format below~\n\n"
        "◈ Format ▷\n"
        "`/genkey [days] [count]`\n\n"
        "◈ Examples ▷\n"
        "`/genkey 7 1`   — 1 key, 7 days\n"
        "`/genkey 30 5`  — 5 keys, 30 days\n"
        "`/genkey 1 10`  — 10 keys, 1 day\n\n"
        "◇ Max 20 keys at once~ ♡"
    )

async def genkey_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    args = context.args
    if len(args) < 2:
        await update.message.reply_text(
            "✦ *Usage~* ◇\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "`/genkey [days] [count]`\n"
            "Example: `/genkey 7 3`",
            parse_mode="Markdown"
        )
        return

    try:
        days  = int(args[0])
        count = min(int(args[1]), 20)
    except ValueError:
        await update.message.reply_text(
            "✦ *Kyaa~ Use numbers~* ◇\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Example: `/genkey 7 3`",
            parse_mode="Markdown"
        )
        return

    keys = []
    for _ in range(count):
        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=12))
        code = f"{code[:4]}-{code[4:8]}-{code[8:]}"
        create_auth_key(code, days, update.effective_user.id)
        keys.append(code)

    keys_text = "\n".join([f"◈ `{k}`" for k in keys])

    await update.message.reply_text(
        f"✦ *{count} Key(s) Generated~* ♡\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"◈ Expires in ▷ {days} day(s)\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{keys_text}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"◇ Share these with your users~ ♡",
        parse_mode="Markdown"
    )

import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    InlineQueryHandler,
    filters
)
from config import BOT_TOKEN
from handlers.auth    import start_handler, auth_handler, main_menu_callback
from handlers.browse  import recent_handler, all_handler
from handlers.anime   import anime_detail_handler, delete_anime_prompt, delete_anime_confirm
from handlers.delivery import season_delivery_handler
from handlers.search  import (
    search_prompt_handler, search_text_handler,
    search_page_handler, inline_query_handler
)
from handlers.admin   import (
    admin_command, admin_panel_callback,
    upload_start, upload_continue,
    set_language, publish_anime,
    add_season_next, add_season_from_detail,
    edit_anime_menu, edit_field_prompt, edit_field_receive,
    genkey_prompt, genkey_command,
    handle_tmdb_input, handle_season_file
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ LOGGING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

logging.basicConfig(
    format  = "%(asctime)s ◈ %(name)s ◈ %(levelname)s ◈ %(message)s",
    level   = logging.INFO
)
logger = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ SMART TEXT ROUTER
#    Routes text messages to correct handler
#    based on user_data state
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def smart_text_router(update, context):
    state = context.user_data.get("state", "")

    if state == "searching":
        await search_text_handler(update, context)

    elif state == "awaiting_tmdb":
        await handle_tmdb_input(update, context)

    elif state == "awaiting_season_file":
        # document handler covers this — skip text
        pass

    elif state.startswith("editing_"):
        await edit_field_receive(update, context)

async def smart_doc_router(update, context):
    state = context.user_data.get("state", "")
    if state == "awaiting_season_file":
        await handle_season_file(update, context)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ MAIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # ── Commands ──────────────────────────
    app.add_handler(CommandHandler("start",  start_handler))
    app.add_handler(CommandHandler("auth",   auth_handler))
    app.add_handler(CommandHandler("admin",  admin_command))
    app.add_handler(CommandHandler("genkey", genkey_command))

    # ── Inline query ──────────────────────
    app.add_handler(InlineQueryHandler(inline_query_handler))

    # ── Callback queries ──────────────────

    # navigation
    app.add_handler(CallbackQueryHandler(main_menu_callback,       pattern="^main_menu$"))
    app.add_handler(CallbackQueryHandler(recent_handler,           pattern="^recent:"))
    app.add_handler(CallbackQueryHandler(all_handler,              pattern="^all:"))
    app.add_handler(CallbackQueryHandler(search_prompt_handler,    pattern="^search$"))
    app.add_handler(CallbackQueryHandler(search_page_handler,      pattern="^search:"))

    # anime detail
    app.add_handler(CallbackQueryHandler(anime_detail_handler,     pattern="^anime:"))
    app.add_handler(CallbackQueryHandler(season_delivery_handler,  pattern="^season:"))

    # delete anime
    app.add_handler(CallbackQueryHandler(delete_anime_prompt,      pattern="^delanime:"))
    app.add_handler(CallbackQueryHandler(delete_anime_confirm,     pattern="^confirmdelete:"))

    # admin panel
    app.add_handler(CallbackQueryHandler(admin_panel_callback,     pattern="^admin_panel$"))
    app.add_handler(CallbackQueryHandler(upload_start,             pattern="^upload_start$"))
    app.add_handler(CallbackQueryHandler(upload_continue,          pattern="^upload_continue:"))
    app.add_handler(CallbackQueryHandler(set_language,             pattern="^setlang:"))
    app.add_handler(CallbackQueryHandler(publish_anime,            pattern="^publish:"))
    app.add_handler(CallbackQueryHandler(add_season_next,          pattern="^addseason_next:"))
    app.add_handler(CallbackQueryHandler(add_season_from_detail,   pattern="^addseason:"))
    app.add_handler(CallbackQueryHandler(edit_anime_menu,          pattern="^editanime:"))
    app.add_handler(CallbackQueryHandler(edit_field_prompt,        pattern="^edit:"))
    app.add_handler(CallbackQueryHandler(genkey_prompt,            pattern="^genkey_prompt$"))

    # ── Message handlers ──────────────────
    app.add_handler(MessageHandler(filters.Document.ALL, smart_doc_router))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, smart_text_router))

    # ── Start polling ─────────────────────
    logger.info("✦ Bot is running~ ♡")
    app.run_polling()

if __name__ == "__main__":
    main()

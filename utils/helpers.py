# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ SAFE EDIT HELPER
#    Telegram can't edit_message_text on a photo message.
#    This helper deletes the photo and sends a fresh text.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def safe_edit(query, text: str, reply_markup=None, parse_mode: str = "Markdown"):
    """
    Edit the current message regardless of whether it is a photo or text.
    - Photo message  → delete it, reply with new text
    - Text message   → edit in place
    """
    if query.message.photo:
        await query.message.delete()
        await query.message.reply_text(
            text,
            parse_mode   = parse_mode,
            reply_markup = reply_markup
        )
    else:
        await query.edit_message_text(
            text,
            parse_mode   = parse_mode,
            reply_markup = reply_markup
        )

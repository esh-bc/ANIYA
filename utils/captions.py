from datetime import datetime

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ LANGUAGE LABEL HELPER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _lang_label(lang: str | None) -> str:
    if lang == "dub":
        return "HINDI DUB"
    elif lang == "sub":
        return "HINDI SUB"
    elif lang == "both":
        return "HINDI DUB + SUB"
    return "Not set"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ CAPTION BUILDERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def anime_detail_caption(anime: dict) -> str:
    genres       = ", ".join(anime.get("genres", [])) or "N/A"
    lang_line    = f"*{_lang_label(anime.get('language'))}*"
    upload_date  = anime.get("upload_date")
    date_str     = upload_date.strftime("%d %b %Y") if upload_date else "N/A"
    season_count = len(anime.get("seasons", []))

    return (
        f"✦ *{anime.get('name', 'Unknown')}*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"◈ Genre    ▷  {genres}\n"
        f"◈ Type     ▷  {lang_line}\n"
        f"◈ Rating   ▷  {anime.get('rating', 'N/A')} ✦\n"
        f"◈ Year     ▷  {anime.get('year', 'N/A')}\n"
        f"◈ Seasons  ▷  {season_count} available\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"◈ Uploaded ▷  {date_str}"
    )


def delivery_caption(anime: dict, season_number: int) -> str:
    genres = ", ".join(anime.get("genres", [])) or "N/A"

    return (
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✦ Here's your treat~ ♡\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"◈ Name     ▷  *{anime.get('name', 'Unknown')}*\n"
        f"◈ Season   ▷  Season {season_number}\n"
        f"◈ Genre    ▷  {genres}\n"
        f"◈ Type     ▷  *{_lang_label(anime.get('language'))}*\n"
        f"◈ Year     ▷  {anime.get('year', 'N/A')}\n"
        f"◈ Rating   ▷  {anime.get('rating', 'N/A')} ✦\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Enjoy, naughty weeb~ ✧"
    )


def upload_preview_caption(anime: dict) -> str:
    genres = ", ".join(anime.get("genres", [])) or "N/A"

    return (
        f"✦ *Preview~ Check this out~* ♡\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"◈ Name     ▷  *{anime.get('name', 'Unknown')}*\n"
        f"◈ Genre    ▷  {genres}\n"
        f"◈ Type     ▷  {_lang_label(anime.get('language'))}\n"
        f"◈ Rating   ▷  {anime.get('rating', 'N/A')} ✦\n"
        f"◈ Year     ▷  {anime.get('year', 'N/A')}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"◈ Does everything look right, Master~? ♡"
    )

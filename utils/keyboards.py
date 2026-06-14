from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import PAGE_SIZE

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ CORRECT STYLE VALUES (v22.7+)
#  primary  = blue
#  success  = green
#  danger   = red
#  omitted  = default grey
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ MAIN MENU
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("◈  Recent Uploads",  callback_data="recent:0",  style="primary")],
        [InlineKeyboardButton("◈  All Uploads",     callback_data="all:0",     style="success")],
        [InlineKeyboardButton("◈  Search",          callback_data="search",    style="danger")],
    ])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ ANIME LIST WITH PAGINATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def anime_list_keyboard(animes: list, page: int, total: int, mode: str):
    buttons = []

    for anime in animes:
        buttons.append([
            InlineKeyboardButton(
                f"◈  {anime['name']}",
                callback_data=f"anime:{str(anime['_id'])}:{mode}:{page}",
                style="primary"
            )
        ])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("◁  Prev", callback_data=f"{mode}:{page - 1}"))
    if (page + 1) * PAGE_SIZE < total:
        nav.append(InlineKeyboardButton("Next  ▷", callback_data=f"{mode}:{page + 1}"))
    if nav:
        buttons.append(nav)

    buttons.append([
        InlineKeyboardButton("◈  Back", callback_data="main_menu")
    ])

    return InlineKeyboardMarkup(buttons)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ ANIME DETAIL PAGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def anime_detail_keyboard(anime: dict, is_admin: bool, back_mode: str, back_page: int):
    buttons = []

    season_row = []
    for s in sorted(anime.get("seasons", []), key=lambda x: x["number"]):
        season_row.append(
            InlineKeyboardButton(
                f"◈  S{s['number']}",
                callback_data=f"season:{str(anime['_id'])}:{s['number']}",
                style="success"
            )
        )
        if len(season_row) == 3:
            buttons.append(season_row)
            season_row = []
    if season_row:
        buttons.append(season_row)

    buttons.append([
        InlineKeyboardButton("◈  Back", callback_data=f"{back_mode}:{back_page}")
    ])

    if is_admin:
        buttons.append([
            InlineKeyboardButton("◈  Add Season", callback_data=f"addseason:{str(anime['_id'])}", style="primary"),
            InlineKeyboardButton("◈  Edit Anime", callback_data=f"editanime:{str(anime['_id'])}"),
        ])
        buttons.append([
            InlineKeyboardButton("◈  Delete Anime", callback_data=f"delanime:{str(anime['_id'])}", style="danger"),
        ])

    return InlineKeyboardMarkup(buttons)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ ADMIN PANEL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def admin_panel_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("◈  Upload Anime",       callback_data="upload_start",  style="primary")],
        [InlineKeyboardButton("◈  Generate Auth Keys", callback_data="genkey_prompt", style="success")],
        [InlineKeyboardButton("◈  Back",               callback_data="main_menu")],
    ])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ UPLOAD PREVIEW BUTTONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def upload_preview_keyboard(anime_id: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("◈  Continue",     callback_data=f"upload_continue:{anime_id}", style="success")],
        [InlineKeyboardButton("◈  Edit Details", callback_data=f"editanime:{anime_id}")],
    ])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ EDIT SUBMENU
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def edit_anime_keyboard(anime_id: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("◈  Edit Name",   callback_data=f"edit:name:{anime_id}")],
        [InlineKeyboardButton("◈  Edit Banner", callback_data=f"edit:banner_url:{anime_id}")],
        [InlineKeyboardButton("◈  Edit Genre",  callback_data=f"edit:genres:{anime_id}")],
        [InlineKeyboardButton("◈  Edit Year",   callback_data=f"edit:year:{anime_id}")],
        [InlineKeyboardButton("◈  Edit Sub/Dub",callback_data=f"edit:language:{anime_id}")],
        [InlineKeyboardButton("◈  Back",        callback_data=f"upload_preview:{anime_id}")],
    ])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ LANGUAGE PICKER  (Dub / Sub / Both)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def language_keyboard(anime_id: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("◈  HINDI DUB",        callback_data=f"setlang:dub:{anime_id}",  style="primary")],
        [InlineKeyboardButton("◈  HINDI SUB",         callback_data=f"setlang:sub:{anime_id}",  style="success")],
        [InlineKeyboardButton("◈  HINDI DUB + SUB",   callback_data=f"setlang:both:{anime_id}", style="danger")],
    ])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ AFTER SEASON UPLOADED
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def after_season_keyboard(anime_id: str, next_season: int):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"◈  Add Season {next_season}", callback_data=f"addseason_next:{anime_id}:{next_season}", style="primary")],
        [InlineKeyboardButton("◈  Publish Anime ✦",           callback_data=f"publish:{anime_id}",                     style="success")],
    ])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ CONFIRM DELETE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def confirm_delete_keyboard(anime_id: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("◈  Yes, Delete", callback_data=f"confirmdelete:{anime_id}", style="danger")],
        [InlineKeyboardButton("◈  Cancel",      callback_data=f"anime:{anime_id}:all:0")],
    ])

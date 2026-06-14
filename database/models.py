from datetime import datetime, timedelta
from bson import ObjectId
from database.db import users_col, auth_keys_col, animes_col
from config import RECENT_HOURS, PAGE_SIZE

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ USER FUNCTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_user(telegram_id: int):
    return users_col.find_one({"telegram_id": telegram_id})

def create_user(telegram_id: int, username: str = None):
    users_col.insert_one({
        "telegram_id"   : telegram_id,
        "username"      : username,
        "is_admin"      : False,
        "is_authorized" : False,
        "auth_key_used" : None,
        "authorized_at" : None
    })

def authorize_user(telegram_id: int, key_code: str):
    users_col.update_one(
        {"telegram_id": telegram_id},
        {"$set": {
            "is_authorized" : True,
            "auth_key_used" : key_code,
            "authorized_at" : datetime.utcnow()
        }}
    )

def is_authorized(telegram_id: int) -> bool:
    user = get_user(telegram_id)
    if not user:
        return False
    return user.get("is_authorized", False)

def is_admin(telegram_id: int) -> bool:
    from config import ADMIN_IDS
    return telegram_id in ADMIN_IDS

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ AUTH KEY FUNCTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_auth_key(code: str):
    return auth_keys_col.find_one({"code": code})

def create_auth_key(code: str, expires_days: int, created_by: int):
    auth_keys_col.insert_one({
        "code"        : code,
        "used"        : False,
        "used_by"     : None,
        "used_at"     : None,
        "expires_at"  : datetime.utcnow() + timedelta(days=expires_days),
        "created_at"  : datetime.utcnow(),
        "created_by"  : created_by
    })

def redeem_auth_key(code: str, telegram_id: int):
    """
    Returns:
        "ok"       - valid and redeemed
        "invalid"  - code not found
        "expired"  - code past expiry
        "used"     - already redeemed
    """
    key = get_auth_key(code)
    if not key:
        return "invalid"
    if key["used"]:
        return "used"
    if datetime.utcnow() > key["expires_at"]:
        return "expired"
    auth_keys_col.update_one(
        {"code": code},
        {"$set": {
            "used"    : True,
            "used_by" : telegram_id,
            "used_at" : datetime.utcnow()
        }}
    )
    return "ok"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ ANIME FUNCTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def insert_anime(data: dict) -> str:
    result = animes_col.insert_one(data)
    return str(result.inserted_id)

def get_anime_by_id(anime_id: str):
    return animes_col.find_one({"_id": ObjectId(anime_id)})

def update_anime(anime_id: str, update_data: dict):
    animes_col.update_one(
        {"_id": ObjectId(anime_id)},
        {"$set": update_data}
    )

def delete_anime(anime_id: str):
    animes_col.delete_one({"_id": ObjectId(anime_id)})

def add_season_to_anime(anime_id: str, season_number: int, file_id: str):
    animes_col.update_one(
        {"_id": ObjectId(anime_id)},
        {"$push": {"seasons": {"number": season_number, "file_id": file_id}}}
    )

def delete_season_from_anime(anime_id: str, season_number: int):
    animes_col.update_one(
        {"_id": ObjectId(anime_id)},
        {"$pull": {"seasons": {"number": season_number}}}
    )

def get_all_animes(page: int = 0):
    skip = page * PAGE_SIZE
    total = animes_col.count_documents({})
    animes = list(
        animes_col.find({})
        .sort("upload_date", -1)
        .skip(skip)
        .limit(PAGE_SIZE)
    )
    return animes, total

def get_recent_animes(page: int = 0):
    cutoff = datetime.utcnow() - timedelta(hours=RECENT_HOURS)
    query  = {"upload_date": {"$gte": cutoff}}
    skip   = page * PAGE_SIZE
    total  = animes_col.count_documents(query)
    animes = list(
        animes_col.find(query)
        .sort("upload_date", -1)
        .skip(skip)
        .limit(PAGE_SIZE)
    )
    return animes, total

def search_animes(query: str, page: int = 0):
    import re
    regex  = {"$regex": re.escape(query), "$options": "i"}
    q      = {"name": regex}
    skip   = page * PAGE_SIZE
    total  = animes_col.count_documents(q)
    animes = list(
        animes_col.find(q)
        .sort("upload_date", -1)
        .skip(skip)
        .limit(PAGE_SIZE)
    )
    return animes, total

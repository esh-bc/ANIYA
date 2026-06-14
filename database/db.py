from pymongo import MongoClient
from config import MONGO_URI, DB_NAME

client = MongoClient(MONGO_URI)
db     = client[DB_NAME]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ COLLECTIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

users_col     = db["users"]
auth_keys_col = db["auth_keys"]
animes_col    = db["animes"]

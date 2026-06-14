import os
from dotenv import load_dotenv

load_dotenv()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ BOT CONFIGURATION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BOT_TOKEN         = os.getenv("BOT_TOKEN")
MONGO_URI         = os.getenv("MONGO_URI")
TMDB_API_KEY      = os.getenv("TMDB_API_KEY")
STORAGE_CHANNEL   = int(os.getenv("STORAGE_CHANNEL"))   # private channel id e.g. -1001234567890
ADMIN_IDS         = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ CONSTANTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PAGE_SIZE         = 8       # animes per page
RECENT_HOURS      = 48      # hours before anime leaves recent
DB_NAME           = "animebot"

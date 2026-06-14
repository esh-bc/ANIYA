import requests
from config import TMDB_API_KEY

BASE_URL     = "https://api.themoviedb.org/3"
BANNER_BASE  = "https://image.tmdb.org/t/p/w1280"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ FETCH ANIME/MOVIE DATA FROM TMDB
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def fetch_tmdb_data(tmdb_id: int, media_type: str = "tv") -> dict | None:
    """
    Fetches TV show or movie details from TMDB by ID.
    media_type: "tv" or "movie"
    Returns a clean dict ready to store in MongoDB.
    """
    url    = f"{BASE_URL}/{media_type}/{tmdb_id}"
    params = {"api_key": TMDB_API_KEY, "language": "en-US"}

    try:
        res  = requests.get(url, params=params, timeout=10)
        data = res.json()
    except Exception:
        return None

    if "id" not in data:
        return None

    genres = [g["name"] for g in data.get("genres", [])]

    # 16:9 banner (backdrop) — preferred over poster
    backdrop = data.get("backdrop_path")
    banner   = (BANNER_BASE + backdrop) if backdrop else None

    # field names differ between TV and movie
    if media_type == "movie":
        name = data.get("title", "Unknown")
        year = data.get("release_date", "")[:4]
    else:
        name = data.get("name", "Unknown")
        year = data.get("first_air_date", "")[:4]

    return {
        "tmdb_id"    : data["id"],
        "media_type" : media_type,
        "name"       : name,
        "banner_url" : banner,
        "genres"     : genres,
        "rating"     : round(data.get("vote_average", 0.0), 1),
        "year"       : year,
        "language"   : None,
        "seasons"    : [],
    }

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ◈ EXTRACT TMDB ID + TYPE FROM URL OR INT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def extract_tmdb_id(text: str) -> tuple[int, str] | None:
    """
    Accepts:
      - Raw ID           : "46260"         → (46260, "tv")  default
      - TMDB TV URL      : "https://www.themoviedb.org/tv/46260"
      - TMDB Movie URL   : "https://www.themoviedb.org/movie/149870"
      - URL with slug    : ".../tv/46260-naruto"

    Returns (tmdb_id, media_type) or None.
    """
    text = text.strip()

    if text.isdigit():
        return int(text), "tv"

    for media_type in ("movie", "tv"):
        segment = f"themoviedb.org/{media_type}/"
        if segment in text:
            try:
                part    = text.split(f"/{media_type}/")[1]
                id_part = part.split("-")[0].split("?")[0]
                return int(id_part), media_type
            except (IndexError, ValueError):
                return None

    return None

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from scraper import scrape_all_results
from cache import get_cache, set_cache
from database import init_db, get_result_from_db, save_result_to_db

app = FastAPI()

# ------------------ CORS ------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ STARTUP ------------------
@app.on_event("startup")
async def startup():
    await init_db()

# ------------------ ROOT ------------------
@app.get("/")
def root():
    return {"status": "JNTUH Results API running"}

# ------------------ NORMALIZER ------------------
def normalize(htno: str, raw: list):
    """
    raw = output from scrape_all_results()
    """

    if not raw or not raw[0].get("meta"):
        return None

    meta = raw[0]["meta"]

    return {
        "hallTicket": htno,
        "name": meta.get("name"),
        "fatherName": meta.get("fatherName"),
        "collegeCode": meta.get("collegeCode"),
        "branch": meta.get("branch"),
        "semesters": [
            {
                "semester": r["semester"],
                "subjects": r["subjects"],
            }
            for r in raw
        ],
    }

# ------------------ RESULT API ------------------
@app.get("/result/{htno}")
async def get_result(htno: str):
    htno = htno.strip().upper()

    # ⚡ 1. CACHE
    cached = get_cache(htno)
    if cached:
        return {
            "cached": True,
            "source": "cache",
            "data": cached,
        }

    # 💾 2. DATABASE
    db_result = await get_result_from_db(htno)
    if db_result:
        set_cache(htno, db_result)
        return {
            "cached": True,
            "source": "db",
            "data": db_result,
        }

    # 🌐 3. SCRAPER
    raw = await scrape_all_results(htno)
    if not raw:
        raise HTTPException(status_code=404, detail="Result not found")

    normalized = normalize(htno, raw)
    if not normalized:
        raise HTTPException(status_code=404, detail="Invalid result structure")

    # 💾 SAVE
    await save_result_to_db(htno, normalized)
    set_cache(htno, normalized)

    return {
        "cached": False,
        "source": "scraper",
        "data": normalized,
    }

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import traceback

from scraper import scrape_all_results
from cache import get_cache, set_cache
from database import init_db, get_result_from_db, save_result_to_db

app = FastAPI(title="JNTUH Results API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- STARTUP ----------------
@app.on_event("startup")
async def startup():
    await init_db()


# ---------------- ROOT ----------------
@app.get("/")
def root():
    return {"status": "Server Working Brooo!!"}


# ---------------- NORMALIZE ----------------
def normalize(htno: str, raw: list):
    if not raw:
        return None

    meta = raw[0].get("meta", {})

    return {
        "hallTicket": htno,
        "name": meta.get("name"),
        "fatherName": meta.get("fatherName"),
        "college": meta.get("college"),
        "collegeCode": meta.get("collegeCode"),
        "branch": meta.get("branch"),
        "semesters": [
            {
                "semester": r.get("semester"),
                "subjects": r.get("subjects", [])
            }
            for r in raw
        ]
    }


# ---------------- RESULT API ----------------
@app.get("/result/{htno}")
async def get_result(htno: str):
    htno = htno.strip().upper()

    # 1️⃣ CACHE
    cached = get_cache(htno)
    if cached:
        return {
            "cached": True,
            "source": "cache",
            "data": cached
        }

    # 2️⃣ DATABASE
    db_data = await get_result_from_db(htno)
    if db_data:
        set_cache(htno, db_data)
        return {
            "cached": True,
            "source": "db",
            "data": db_data
        }

    # 3️⃣ SCRAPER
    try:
        raw = await scrape_all_results(htno)
        print("SCRAPER RAW OUTPUT:", raw)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Scraper crashed. Check backend logs."
        )

    if not raw:
        raise HTTPException(
            status_code=404,
            detail="Result not found or blocked by JNTUH"
        )

    normalized = normalize(htno, raw)
    if not normalized:
        raise HTTPException(
            status_code=404,
            detail="Result parsing failed"
        )

    # 4️⃣ SAVE
    await save_result_to_db(htno, normalized)
    set_cache(htno, normalized)

    return {
        "cached": False,
        "source": "scraper",
        "data": normalized
    }

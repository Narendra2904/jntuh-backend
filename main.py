from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from scraper import scrape_all_results
from cache import get_cache, set_cache
from database import init_db, get_result_from_db, save_result_to_db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await init_db()


@app.get("/")
def root():
    return {"status": "JNTUH Results API running"}


# ---------------- NORMALIZER ----------------

def normalize(htno, raw):
    if not raw:
        return None

    meta = raw[0].get("meta", {})

    return {
        "hallTicket": htno,
        "name": meta.get("name"),
        "fatherName": meta.get("fatherName"),
        "college": meta.get("college"),
        "branch": meta.get("branch"),
        "semesters": [
            {
                "semester": r["semester"],
                "semesterType": r.get("semesterType"),
                "subjects": r["subjects"]
            }
            for r in raw
        ]
    }


# ---------------- API ----------------

@app.get("/result/{htno}")
async def get_result(htno: str):
    htno = htno.strip()

    # ⚡ REDIS CACHE
    cached = get_cache(htno)
    if cached:
        return {
            "cached": True,
            "source": "redis",
            "data": cached
        }

    # 💾 SQLITE DB
    db_result = await get_result_from_db(htno)
    if db_result:
        set_cache(htno, db_result)
        return {
            "cached": True,
            "source": "db",
            "data": db_result
        }

    # 🌐 SCRAPER
    raw = await scrape_all_results(htno)
    if not raw:
        raise HTTPException(404, "Result not found")

    normalized = normalize(htno, raw)

    # SAVE
    await save_result_to_db(htno, normalized)
    set_cache(htno, normalized)

    return {
        "cached": False,
        "source": "scraper",
        "data": normalized
    }

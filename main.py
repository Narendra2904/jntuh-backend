import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import traceback
from upstash_redis import Redis  # Make sure this is in requirements.txt

# --- IMPORTS FROM YOUR OTHER FILES ---
from scraper import scrape_all_results
# We don't need cache.py anymore because we are doing everything with Redis here directly
# from database import ... (DELETED: This caused the crash)

app = FastAPI(title="JNTUH Results API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- REDIS CONNECTION ---
# Vercel automatically sets these env variables if you linked the store
redis = Redis(
    url=os.environ.get("https://tight-dassie-18459.upstash.io"),
    token=os.environ.get("AUgbAAIncDI5NTNmNzg1ZjdmNjk0ODJmODBhNmE5MWNjZmI3NTk1OXAyMTg0NTk")
)

# ---------------- STARTUP ----------------
@app.on_event("startup")
async def startup():
    # No need to init_db() anymore because Redis is serverless!
    print("🚀 Server starting up... Redis connected.")

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

    # 1️⃣ & 2️⃣ CACHE/DB CHECK (Redis serves as both)
    # logic: Try to get from Redis
    try:
        cached_data = redis.get(htno)
        if cached_data:
            print(f"✅ Found {htno} in Redis")
            # Redis might return a string or a dict depending on how it was saved.
            # If it's a string, we parse it back to JSON.
            if isinstance(cached_data, str):
                cached_data = json.loads(cached_data)
                
            return {
                "cached": True,
                "source": "redis-cache",
                "data": cached_data
            }
    except Exception as e:
        print(f"⚠️ Redis Read Error: {e}")
        # If redis fails, we just continue to scraping (don't crash app)

    # 3️⃣ SCRAPER
    print(f"🔄 Scraping {htno} from JNTUH...")
    try:
        raw = await scrape_all_results(htno)
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

    # 4️⃣ SAVE TO REDIS
    try:
        # Save to Redis with a 24-hour expiration (86400 seconds) or keep forever
        # json.dumps ensures it's stored as a valid string
        redis.set(htno, json.dumps(normalized)) 
        print(f"💾 Saved {htno} to Redis")
    except Exception as e:
        print(f"⚠️ Redis Write Error: {e}")

    return {
        "cached": False,
        "source": "scraper",
        "data": normalized
    }

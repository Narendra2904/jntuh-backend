🎓 JNTUH B.Tech Results Portal

A fast, modern, mobile-friendly JNTUH results website built with a custom backend, intelligent caching, and a clean UI inspired by student-first platforms.

🔗 Live Site: https://btech-jntuh-results.vercel.app

🚀 Features

🔍 Instant Hall Ticket Search

📚 Semester-wise Results View

⚡ Ultra-fast responses using Redis Cache

🗄️ SQLite database for persistent storage

🧠 Smart cache (DB → Redis → Scraper fallback)

📱 Fully Mobile-Responsive UI

🖨️ Clean Print / PDF Mode (White background, Black text)

🔄 Automatic backend caching (12-hour TTL)

🌍 Deployed on Vercel + Render

📊 Vercel Analytics enabled


🏗️ Tech Stack
Frontend

HTML5

CSS3 (Custom, Mobile-First)

Vanilla JavaScript

Deployed on Vercel

Backend

Python

FastAPI

Redis (Upstash – Free Tier)

SQLite (Free, Lightweight DB)

Deployed on Render


How It Works (Architecture)
User Request
     ↓
Redis Cache (Fastest)
     ↓ (if not found)
SQLite Database
     ↓ (if not found)
Live JNTUH Scraper
     ↓
Cache Result (Redis + DB)
     ↓
Response to User


✔️ First request may take time
✔️ Subsequent requests are blazing fast

📂 Project Structure
Backend
backend/
├── main.py           # FastAPI entry point
├── scraper.py        # JNTUH results scraper
├── cache.py          # Redis cache logic
├── database.py       # SQLite DB handler
├── exam_codes.py     # Exam code mapping
├── requirements.txt
└── start.sh

Frontend
frontend/
├── index.html
├── assets/
│   ├── logo.jpg
│   └── fav.png

🔐 Environment Variables (Backend)

Set these in Render / local .env

REDIS_URL=rediss://default:<token>@<endpoint>:6379
CACHE_TTL=43200

👨‍💻 Author

Narendra Yenagandula
Final-year B.Tech Student
Interested in Full-Stack Development, Backend Systems & Cloud

⭐ Support

If you find this useful:

⭐ Star the repo

🍴 Fork it

🐛 Report issues / suggest features

🎬 Final Note

“Built by a student, for students — fast, clean, and reliable.”

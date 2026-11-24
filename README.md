# 🎓 JNTUH B.Tech Results Portal

[![Live Demo](https://img.shields.io/badge/Live%20Site-btech--jntuh--results.vercel.app-FACC15?style=for-the-badge&logo=vercel&logoColor=black)](https://btech-jntuh-results.vercel.app)
[![Backend](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Render-009688?style=for-the-badge&logo=fastapi&logoColor=white)](#)
[![Cache](https://img.shields.io/badge/Cache-Redis%20(Upstash)-DC382D?style=for-the-badge&logo=redis&logoColor=white)](#)
[![Database](https://img.shields.io/badge/Database-SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](#)

> **"Built by a student, for students — fast, clean, and reliable."**  
> A fast, modern, and mobile-friendly **JNTUH B.Tech Results Portal** powered by a custom Python FastAPI backend, multi-layer caching (Redis + SQLite), and a distraction-free, print-ready frontend.

---

## 📖 Overview

Official university result portals often slow down or crash during peak result announcements. **JNTUH B.Tech Results Portal** solves this with a resilient **multi-tier caching architecture**. Once a student's results are fetched from the JNTUH servers, they are stored in both **Upstash Redis** (for sub-second retrieval) and **SQLite** (for persistent fallback), ensuring blazing-fast performance even under heavy traffic.

---

## ✨ Key Features

- **🔍 Instant Hall Ticket Search:** Quickly fetch complete academic records using just a JNTUH Hall Ticket Number.
- **📚 Semester-Wise Results View:** Clean, structured breakdown of subjects, internal/external marks, credits, grades, and SGPA/CGPA across all semesters.
- **⚡ Multi-Tier Smart Caching (`Redis → SQLite → Scraper`):**
  - Ultra-fast in-memory responses via **Upstash Redis** with an automatic **12-hour TTL (`43200s`)**.
  - Persistent local storage via **SQLite** to minimize redundant scraping.
- **🖨️ Clean Print / PDF Mode:** Built-in print stylesheet that automatically formats results into a crisp, high-contrast **white background and black text** layout for instant PDF saving or printing.
- **📱 Mobile-First Responsive UI:** Designed to work seamlessly across smartphones, tablets, and desktops.
- **📊 Traffic & Performance Insights:** Integrated **Vercel Analytics** to monitor real-time usage during peak result days.

---

## 🏗️ System Architecture

```text
                    ┌─────────────────────┐
                    │    User Request     │
                    │ (Hall Ticket Query) │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐      HIT       ┌──────────────────────┐
                    │     Redis Cache     │───────────────▶│  Blazing-Fast JSON   │
                    │   (Upstash - 12h)   │                │  Response to Client  │
                    └──────────┬──────────┘                └──────────────────────┘
                               │ MISS                                 ▲
                               ▼                                      │
                    ┌─────────────────────┐      HIT                  │
                    │   SQLite Database   │───────────────────────────┤
                    │ (Persistent Store)  │                           │
                    └──────────┬──────────┘                           │
                               │ MISS                                 │
                               ▼                                      │
                    ┌─────────────────────┐                           │
                    │ Live JNTUH Scraper  │───────────────────────────┘
                    │   (FastAPI Engine)  │   (Saves to SQLite + Redis)
                    └─────────────────────┘

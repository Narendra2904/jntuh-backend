# 🎓 Backbenchers — JNTUH B.Tech Results Portal & AI Academic Assistant

[![Live Demo](https://img.shields.io/badge/Live%20Site-btech--jntuh--results.vercel.app-FACC15?style=for-the-badge&logo=vercel&logoColor=black)](https://btech-jntuh-results.vercel.app/)
[![GitHub Repo](https://img.shields.io/badge/GitHub-btech--frontend-181717?style=for-the-badge&logo=github)](https://github.com/Narendra2904/btech-frontend)
[![Node.js](https://img.shields.io/badge/Node.js-18%2B-339933?style=for-the-badge&logo=node.js&logoColor=white)](#)
[![Python FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](#)
[![Google Gemini](https://img.shields.io/badge/AI-Backbenchers%20AI%202.0-4285F4?style=for-the-badge&logo=google&logoColor=white)](#)

> **"Fast. Free. Reliable. Intelligent JNTUH Academic Assistant built by students, for students."**  
> A comprehensive academic results analytics platform, multi-tool student dashboard, and **Google Gemini-powered AI Academic Assistant** engineered for **JNTUH (R18 & R22)** B.Tech students.

---

## 📖 Overview

Checking university results on peak announcement days often means dealing with crashed portals, scattered PDFs, and manual credit calculations. **Backbenchers (`btech-frontend`)** solves this by combining a high-speed results engine with a complete suite of academic analytics tools—including **Class Results**, **Backlog Tracking**, **Credit & Detention Eligibility Checkers**, **Peer Comparison**, and **Backbenchers AI 2.0**—all accessible from a mobile-first dark UI with zero logins required.

---

## ✨ Core Modules & Features

### 📊 1. Academic Results & Analytics Suite
- **🔍 All Results (`result.html`):** Instant Hall Ticket search displaying complete semester-wise performance, internal/external marks, credits, grades, SGPA, and overall CGPA.
- **⚡ Live Results (`liveresults.html`):** Real-time feed of the latest exam notifications and newly published JNTUH server updates (`exams.json`).
- **🏫 Class Results (`classresult.html`):** Batch/range-based Hall Ticket lookup allowing students and faculty to view and compare results across an entire class at once.
- **⚠️ Backlog Report (`backlog.html`):** Automatically scans all semesters to isolate and list active backlogs/failed subjects in a single consolidated view.
- **🛡️ Credit Checker (`creditChecker.html`):** Calculates total earned credits against JNTUH **R18 & R22** promotion thresholds to evaluate promotion and detention eligibility.
- **⚖️ Peer Comparison (`compare.html`):** Side-by-side academic comparison tool to benchmark SGPA, CGPA, credits, and subject grades with a friend.
- **🖨️ Clean Print / PDF Mode:** Built-in print media styling that converts the dark dashboard into a crisp, high-contrast **white-background, black-text** layout for instant PDF exports.

### 🤖 2. Backbenchers AI 2.0 (`ai-bot.js` & `ai-bot.css`)
An integrated, voice-and-text conversational AI assistant tailored to JNTUH R18 & R22 regulations:
- **⚠️ Supply & Failure Root Cause Analysis:** Identifies active backlogs and pinpoints weak subject areas.
- **📈 CGPA Boost & Improvement Advisor:** Highlights passed subjects with low grades where improvement exams yield the highest CGPA jump.
- **🛡️ Promotion / Detention & Grace Marks Audit:** Evaluates credit deficits, grace mark rules, and subject exemption eligibility.
- **🎮 Interactive What-If CGPA Simulator:** Simulates how clearing supplies or scoring target grades impacts final CGPA.
- **🎯 Target CGPA Solver:** Calculates the exact SGPA required in upcoming semesters to hit a target graduation CGPA.
- **💼 Campus Placement & Career Readiness Scan:** Evaluates academic standing against standard campus recruitment cutoffs.
- **📚 Integrated Study Notes & Video Links:** Directly links weak subjects to curated notes on [Back.Benchers Notes](https://btech-notes.vercel.app/) and YouTube tutorials.
- **🎙️ Voice & Text Input:** Supports hands-free Hall Ticket queries via Web Speech recognition alongside quick-action prompt chips.

### 📱 3. Ecosystem Integrations
- **Android App (`v1.0.2`):** Direct APK download prompt for native mobile access.
- **Telegram Bot Integration:** Instant result alerts and updates via Telegram.
- **Study Materials Hub:** Seamless cross-navigation to the companion [B.Tech Notes Portal](https://btech-notes.vercel.app/).

---

## 🏗️ System Architecture

The platform uses a decoupled full-stack architecture separating the Vercel-hosted frontend/proxy layer from the Render-hosted Python scraping & caching engine:

```text
┌──────────────────────────────────────────────────────────────────┐
│                     Frontend (btech-frontend)                    │
│   HTML5 • CSS3 • Vanilla JS • Backbenchers AI 2.0 • Node/Express │
│                        (Hosted on Vercel)                        │
└───────────────────┬──────────────────────────────┬───────────────┘
                    │ /api/* Proxy                 │ Gemini AI API
                    ▼                              ▼
┌────────────────────────────────────┐   ┌─────────────────────────┐
│    Backend Engine (jntuh-backend)  │   │  Google Gemini LLM      │
│  Python FastAPI • Uvicorn (Render) │   │ (Academic & R18/R22 Bot)│
└─────────┬──────────────────────────┘   └─────────────────────────┘
          │
          ├──▶ 1. Upstash Redis Cache (12h TTL — Sub-second HIT)
          ├──▶ 2. SQLite Database (Persistent fallback storage)
          └──▶ 3. Live JNTUH Server Scraper (On cache MISS)

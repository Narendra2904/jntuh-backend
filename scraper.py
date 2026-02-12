import asyncio
import aiohttp
from bs4 import BeautifulSoup
import pdfplumber
from pathlib import Path

from exam_codes import EXAM_CODES
from branch_codes import get_branch_name


# =========================
# CONSTANTS
# =========================

RESULT_URL = "http://results.jntuh.ac.in/resultAction"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html",
}

COLLEGE_PDF = Path("data/btech_mba_centers_reviewed.pdf")


# =========================
# COLLEGE MAP
# =========================

_COLLEGE_MAP = None


def load_college_map():
    global _COLLEGE_MAP

    if _COLLEGE_MAP is not None:
        return _COLLEGE_MAP

    _COLLEGE_MAP = {}

    if not COLLEGE_PDF.exists():
        print("⚠️ College PDF not found")
        return _COLLEGE_MAP

    with pdfplumber.open(COLLEGE_PDF) as pdf:
        for page in pdf.pages:
            table = page.extract_table()

            if not table:
                continue

            for row in table[1:]:
                if not row or len(row) < 2:
                    continue

                code = row[0]
                college_name = row[1]

                if code and college_name:
                    code = code.strip()
                    college_name = college_name.strip()

                    if len(code) == 2:
                        _COLLEGE_MAP[code] = college_name

    print(f"✅ Loaded {len(_COLLEGE_MAP)} college names from PDF")
    return _COLLEGE_MAP


# =========================
# SCRAPER
# =========================

class ResultScraper:
    def __init__(self, roll_number: str):
        self.roll_number = roll_number.upper()
        self.college_map = load_college_map()
        self.results = []
        self._meta = None

    # ---------------------
    async def fetch(self, session, semester, exam_code, attempt_type):
        """
        Try r22 → r18 → r17 dynamically.
        Whichever returns valid result page will be used.
        """

        for etype in ["r22", "r18", "r17"]:

            url = (
                f"{RESULT_URL}?"
                f"examCode={exam_code}"
                f"&degree=btech"
                f"&etype={etype}"
                f"&result=null"
                f"&grad=null"
                f"&type=intgrade"
                f"&htno={self.roll_number}"
            )

            try:
                async with session.get(url, ssl=False, timeout=8) as r:
                    html = await r.text()

                    # If valid result page
                    if html and "SUBJECT CODE" in html:
                        return semester, exam_code, html, attempt_type

            except Exception:
                continue

        return None

    # ---------------------
    def parse_html(self, semester, exam_code, html, attempt_type):
        if not html or "SUBJECT CODE" not in html:
            return

        soup = BeautifulSoup(html, "lxml")
        tables = soup.find_all("table")

        if len(tables) < 2:
            return

        # -------- META --------
        if self._meta is None:
            try:
                details = tables[0].find_all("tr")
                htno = details[0].find_all("td")[1].text.strip()
                name = details[0].find_all("td")[3].text.strip()
                father = details[1].find_all("td")[1].text.strip()
                college_code = details[1].find_all("td")[3].text.strip()

                self._meta = {
                    "hallTicket": htno,
                    "name": name,
                    "fatherName": father,
                    "collegeCode": college_code,
                    "college": self.college_map.get(college_code),
                    "branch": get_branch_name(htno),
                }
            except Exception:
                return

        # -------- SUBJECTS --------
        rows = tables[1].find_all("tr")
        header = [b.text.strip() for b in rows[0].find_all("b")]

        subjects = []

        for row in rows[1:]:
            cols = row.find_all("td")
            if not cols:
                continue

            subject = {
                "subjectCode": cols[header.index("SUBJECT CODE")].text.strip(),
                "subjectName": cols[header.index("SUBJECT NAME")].text.strip(),
                "examCode": exam_code,
                "grade": cols[header.index("GRADE")].text.strip(),
                "credits": cols[header.index("CREDITS(C)")].text.strip(),
                "semester": semester,
                "attempt": attempt_type,
            }

            if "INTERNAL" in header:
                subject["internal"] = cols[header.index("INTERNAL")].text.strip()
            if "EXTERNAL" in header:
                subject["external"] = cols[header.index("EXTERNAL")].text.strip()
            if "TOTAL" in header:
                subject["total"] = cols[header.index("TOTAL")].text.strip()

            subjects.append(subject)

        if subjects:
            self.results.append({
                "semester": semester,
                "meta": self._meta,
                "subjects": subjects,
            })

    # ---------------------
    async def scrape_all(self):
    timeout = aiohttp.ClientTimeout(total=20)

    semaphore = asyncio.Semaphore(5)  # LIMIT TO 5 REQUESTS AT A TIME

    async with aiohttp.ClientSession(headers=HEADERS, timeout=timeout) as session:

        async def safe_fetch(semester, code, attempt):
            async with semaphore:
                await asyncio.sleep(0.4)  # small delay to avoid block
                return await self.fetch(session, semester, code, attempt)

        tasks = []

        for semester, exam_codes in EXAM_CODES.items():
            for code in exam_codes:
                tasks.append(safe_fetch(semester, code, "regular"))
                tasks.append(safe_fetch(semester, code, "rcrv"))

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        for item in responses:
            if isinstance(item, tuple) and len(item) == 4:
                semester, exam_code, html, attempt_type = item
                self.parse_html(semester, exam_code, html, attempt_type)


    # ---------------------
    async def run(self):
        await self.scrape_all()
        return self.results if self.results else None


# =========================
# USED BY main.py
# =========================

async def scrape_all_results(htno: str):
    scraper = ResultScraper(htno)
    return await scraper.run()

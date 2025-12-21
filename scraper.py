import aiohttp
import asyncio
from bs4 import BeautifulSoup
from exam_codes import EXAM_CODES

BASE_URL = "http://results.jntuh.ac.in/resultAction"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}

VALID_COMBOS = [
    ("r22", "grade"),
    ("r18", "grade"),
    ("r17", "intgrade"),
]

# --------------------------------------------------
# UTILS
# --------------------------------------------------

def has_result(html: str) -> bool:
    soup = BeautifulSoup(html, "lxml")
    tables = soup.find_all("table")
    return len(tables) >= 2 and len(tables[1].find_all("tr")) > 1


# --------------------------------------------------
# PARSER (LABEL BASED — THIS IS THE KEY FIX)
# --------------------------------------------------

def parse_html(html: str):
    soup = BeautifulSoup(html, "lxml")
    tables = soup.find_all("table")

    if len(tables) < 2:
        return None

    details_table = tables[0]

    name = None
    father_name = None
    college = None
    branch = None

    # 🔥 LABEL BASED EXTRACTION
    for row in details_table.find_all("tr"):
        cells = [td.text.strip() for td in row.find_all("td")]

        for i, cell in enumerate(cells):
            key = cell.lower()

            if key == "name" and i + 1 < len(cells):
                name = cells[i + 1]

            elif "father" in key and i + 1 < len(cells):
                father_name = cells[i + 1]

            elif "college" in key and i + 1 < len(cells):
                college = cells[i + 1]

            elif "branch" in key and i + 1 < len(cells):
                branch = cells[i + 1]

    # --------------------------------------------------
    # SUBJECT TABLE
    # --------------------------------------------------

    subjects = []
    subject_rows = tables[1].find_all("tr")[1:]

    for row in subject_rows:
        tds = [td.text.strip() for td in row.find_all("td")]
        if len(tds) < 6:
            continue

        subjects.append({
            "subjectCode": tds[0],
            "subjectName": tds[1],
            "internal": tds[2],
            "external": tds[3],
            "total": tds[4],
            "grade": tds[5],
            "credits": tds[6] if len(tds) > 6 else "0"
        })

    if not subjects:
        return None

    return {
        "meta": {
            "name": name,
            "fatherName": father_name,
            "college": college,
            "branch": branch
        },
        "subjects": subjects
    }


# --------------------------------------------------
# FETCH
# --------------------------------------------------

async def fetch(session, url):
    try:
        async with session.get(url, ssl=False) as r:
            return await r.text()
    except:
        return None


# --------------------------------------------------
# MAIN SCRAPER
# --------------------------------------------------

async def scrape_all_results(htno: str):
    timeout = aiohttp.ClientTimeout(total=12)
    connector = aiohttp.TCPConnector(limit=20, ssl=False)

    results = []

    async with aiohttp.ClientSession(
        timeout=timeout,
        headers=HEADERS,
        connector=connector
    ) as session:

        for semester, exam_codes in EXAM_CODES.items():
            tasks = []

            for code in exam_codes:
                for etype, rtype in VALID_COMBOS:
                    url = (
                        f"{BASE_URL}"
                        f"?examCode={code}"
                        f"&degree=btech"
                        f"&etype={etype}"
                        f"&type={rtype}"
                        f"&result=null"
                        f"&grad=null"
                        f"&htno={htno}"
                    )
                    tasks.append(fetch(session, url))

            responses = await asyncio.gather(*tasks)

            sem_subjects = []
            sem_meta = None

            for html in responses:
                if not html or not has_result(html):
                    continue

                parsed = parse_html(html)
                if not parsed:
                    continue

                if not sem_meta:
                    sem_meta = parsed["meta"]

                for s in parsed["subjects"]:
                    s["semester"] = semester
                    sem_subjects.append(s)

            if sem_subjects:
                # 🔁 REGULAR / SUPPLY DETECTION
                seen = set()
                for s in sem_subjects:
                    if s["subjectCode"] in seen:
                        s["attempt"] = "supply"
                    else:
                        s["attempt"] = "regular"
                        seen.add(s["subjectCode"])

                results.append({
                    "semester": semester,
                    "subjects": sem_subjects,
                    "meta": sem_meta
                })

    return results

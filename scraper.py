import aiohttp
import asyncio
from bs4 import BeautifulSoup
from exam_codes import EXAM_CODES

BASE_URL = "http://results.jntuh.ac.in/resultAction"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
}

VALID_COMBOS = [
    ("r22", "grade"),
    ("r18", "grade"),
    ("r17", "intgrade"),
]

# ------------------------------------------------
def has_result(html: str) -> bool:
    soup = BeautifulSoup(html, "lxml")
    return len(soup.find_all("table")) >= 2


# ------------------------------------------------
def extract_value(row_text: str, key: str):
    """
    Extract value after label safely
    Example: 'Father Name : RAMESH' -> RAMESH
    """
    row_text = row_text.replace("\xa0", " ").strip()
    if key.lower() not in row_text.lower():
        return None

    # split by colon
    if ":" in row_text:
        return row_text.split(":", 1)[1].strip()

    # fallback: last word chunk
    return row_text.replace(key, "").strip()


# ------------------------------------------------
def parse_html(html: str):
    soup = BeautifulSoup(html, "lxml")
    tables = soup.find_all("table")
    if len(tables) < 2:
        return None

    details_table = tables[0]
    results_table = tables[1]

    meta = {
        "name": None,
        "fatherName": None,
        "collegeCode": None,
        "branch": None,
    }

    # ---------- STUDENT DETAILS (TEXT BASED) ----------
    for row in details_table.find_all("tr"):
        row_text = row.get_text(" ", strip=True)

        if not meta["name"] and "name" in row_text.lower():
            meta["name"] = extract_value(row_text, "Name")

        if not meta["fatherName"] and "father" in row_text.lower():
            meta["fatherName"] = extract_value(row_text, "Father Name")

        if not meta["collegeCode"] and "college" in row_text.lower():
            meta["collegeCode"] = extract_value(row_text, "College Code")

        if not meta["branch"] and "branch" in row_text.lower():
            meta["branch"] = extract_value(row_text, "Branch")

    # HARD GUARD
    if not meta["name"]:
        return None

    # ---------- SUBJECTS ----------
    subjects = []
    for r in results_table.find_all("tr")[1:]:
        tds = [td.get_text(strip=True) for td in r.find_all("td")]
        if len(tds) < 6:
            continue

        subjects.append({
            "subjectCode": tds[0],
            "subjectName": tds[1],
            "internal": tds[2],
            "external": tds[3],
            "total": tds[4],
            "grade": tds[5],
            "credits": tds[6] if len(tds) > 6 else "0",
        })

    if not subjects:
        return None

    return {
        "meta": meta,
        "subjects": subjects,
    }


# ------------------------------------------------
async def fetch(session, url):
    try:
        async with session.get(url, ssl=False, timeout=8) as r:
            return await r.text()
    except:
        return None


# ------------------------------------------------
async def scrape_all_results(htno: str):
    results = []

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        for sem, codes in EXAM_CODES.items():
            tasks = []

            for code in codes:
                for etype, rtype in VALID_COMBOS:
                    url = (
                        f"{BASE_URL}"
                        f"?examCode={code}"
                        f"&degree=btech"
                        f"&etype={etype}"
                        f"&type={rtype}"
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

                sem_meta = parsed["meta"]

                for s in parsed["subjects"]:
                    s["semester"] = sem
                    sem_subjects.append(s)

            if sem_subjects:
                seen = set()
                for s in sem_subjects:
                    if s["subjectCode"] in seen:
                        s["attempt"] = "supply"
                    else:
                        s["attempt"] = "regular"
                        seen.add(s["subjectCode"])

                results.append({
                    "semester": sem,
                    "subjects": sem_subjects,
                    "meta": sem_meta,
                })

    return results

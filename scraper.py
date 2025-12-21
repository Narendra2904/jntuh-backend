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


# ------------------ UTILS ------------------

def has_result(html: str) -> bool:
    soup = BeautifulSoup(html, "lxml")
    tables = soup.find_all("table")
    return len(tables) >= 2 and len(tables[1].find_all("tr")) > 1


def get_td(details, row, col):
    try:
        return details[row].find_all("td")[col].text.strip()
    except:
        return None


# ------------------ PARSER ------------------

def parse_html(html: str):
    soup = BeautifulSoup(html, "lxml")
    tables = soup.find_all("table")

    if len(tables) < 2:
        return None

    # -------- STUDENT DETAILS TABLE --------
    details = tables[0].find_all("tr")

    name = get_td(details, 0, 3)
    hallticket = get_td(details, 0, 1)

    father_name = get_td(details, 1, 1)
    college = get_td(details, 1, 3)

    branch = get_td(details, 2, 1)

    # -------- SUBJECT TABLE --------
    subjects = []
    rows = tables[1].find_all("tr")[1:]

    for r in rows:
        tds = [td.text.strip() for td in r.find_all("td")]
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
            "hallTicket": hallticket,
            "fatherName": father_name,
            "college": college,
            "branch": branch
        },
        "subjects": subjects
    }


# ------------------ FETCH ------------------

async def fetch(session, url):
    try:
        async with session.get(url, ssl=False) as r:
            return await r.text()
    except:
        return None


# ------------------ MAIN SCRAPER ------------------

async def scrape_all_results(htno: str):
    timeout = aiohttp.ClientTimeout(total=10)
    connector = aiohttp.TCPConnector(limit=20, ssl=False)

    semesters = []
    student_meta = None

    async with aiohttp.ClientSession(
        timeout=timeout,
        headers=HEADERS,
        connector=connector
    ) as session:

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
                        f"&result=null"
                        f"&grad=null"
                        f"&htno={htno}"
                    )
                    tasks.append(fetch(session, url))

            responses = await asyncio.gather(*tasks)

            sem_subjects = []

            for html in responses:
                if not html or not has_result(html):
                    continue

                parsed = parse_html(html)
                if not parsed:
                    continue

                if not student_meta:
                    student_meta = parsed["meta"]

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

                semesters.append({
                    "semester": sem,
                    "subjects": sem_subjects
                })

    if not semesters or not student_meta:
        return None

    return {
        "hallTicket": htno,
        "name": student_meta["name"],
        "fatherName": student_meta["fatherName"],
        "college": student_meta["college"],
        "branch": student_meta["branch"],
        "semesters": semesters
    }

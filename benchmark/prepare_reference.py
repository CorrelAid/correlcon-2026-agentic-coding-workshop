"""Build the fixed benchmark inputs in cache/ (identical for every model).

1. download the Babylotse survey (same pinned URL + checksum as example/scripts/get_data.py)
2. reference pseudonymisation -> cache/babylotse_pseudonymised.csv (input for the categories task)
3. fixed sample of 100 negative comments (seed 20261114) -> cache/sample_negative_100.csv
"""
import csv, hashlib, html, random, re, urllib.request
from pathlib import Path

CACHE = Path(__file__).resolve().parent / "cache"
URL = ("https://raw.githubusercontent.com/CorrelAid/workshop-babylotse/"
       "83a0507eeb4fa240d8b4b6cda6c797035183517c/data/Umfrage%20DE%20submissions%202024-07-31%2000_25.csv")
SHA256 = "d98d099ccd126507db24327508a160c36b5a7e3a2fc9bd5ddc380a2c36d92b85"
G = "Das gefällt mir gut mit Baby in Frankfurt"
B = "Das gefällt mir nicht gut mit Baby in Frankfurt"
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
PHONE = re.compile(r"(?<!\w)\+?\d[\d\s/()-]{6,}\d")
URLS = re.compile(r"(https?://\S+|www\.\S+)")


def mask(t: str) -> str:
    return PHONE.sub("[PHONE]", EMAIL.sub("[EMAIL]", URLS.sub("[URL]", t)))


CACHE.mkdir(exist_ok=True)
raw = CACHE / "babylotse_survey_2024.csv"
if not raw.exists():
    data = urllib.request.urlopen(URL, timeout=60).read()
    assert hashlib.sha256(data).hexdigest() == SHA256, "checksum mismatch"
    raw.write_bytes(data)

rows = list(csv.DictReader(open(raw, encoding="utf-8")))
with open(CACHE / "babylotse_pseudonymised.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["row_id", "month", "district", G, B])
    w.writeheader()
    for i, x in enumerate(rows, 1):
        w.writerow({"row_id": i, "month": x["Date Created"][:7],
                    "district": html.unescape(x["Ich wohne im Stadtteil"]), G: mask(x[G]), B: mask(x[B])})

proc = [r for r in csv.DictReader(open(CACHE / "babylotse_pseudonymised.csv", encoding="utf-8")) if r[B].strip()]
random.seed(20261114)
sample = sorted(random.sample(proc, 100), key=lambda r: int(r["row_id"]))
with open(CACHE / "sample_negative_100.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["row_id", B])
    w.writeheader()
    for r in sample:
        w.writerow({"row_id": r["row_id"], B: r[B]})
print("cache ready:", sorted(p.name for p in CACHE.iterdir()))

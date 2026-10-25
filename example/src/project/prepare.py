"""Step 1 – prepare the raw survey (ready-made, no LLM).

- decode HTML entities, trim whitespace, normalise line breaks
- map the free-text district to an official district and a region (`districts.py`,
  taken from the 2024 pipeline) – unknown districts are a first spam signal
- coarsen the date to month, drop the original ID
- mask obvious contact details (e-mail, phone, URL) with regex – a first, deterministic
  privacy layer before any text is sent to an LLM

Output: data/interim/01_prepared.csv (see docs/pipeline.md for the columns).
"""

from __future__ import annotations

import html
import logging
import re

import pandas as pd

from project import paths
from project.districts import stadtteil_mapping_func, stadtteil_region_mapping

COLUMNS = {
    "Date Created": "date",
    "Ich wohne im Stadtteil": "district_raw",
    "Das gefällt mir gut mit Baby in Frankfurt": "positive",
    "Das gefällt mir nicht gut mit Baby in Frankfurt": "negative",
}

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
PHONE = re.compile(r"(?<!\w)\+?\d[\d\s/()-]{6,}\d")
URL = re.compile(r"(https?://\S+|www\.\S+)")


def clean_text(value: object) -> str:
    """Decode HTML entities, normalise whitespace; missing values become ''."""
    if not isinstance(value, str):
        return ""
    text = html.unescape(value).replace("\r\r\n", ". ").replace("\r\n", " ").replace("\n", " ")
    return re.sub(r"\s+", " ", text).strip()


def mask_contacts(text: str) -> str:
    """Replace e-mail addresses, URLs and phone numbers with placeholders."""
    text = URL.sub("[URL]", text)
    text = EMAIL.sub("[EMAIL]", text)
    return PHONE.sub("[PHONE]", text)


def prepare(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw[list(COLUMNS)].rename(columns=COLUMNS)
    # district: only unescape + strip, exactly like the 2024 pipeline (its mapping keys
    # contain double spaces); free text: full whitespace normalisation
    df["district_raw"] = df["district_raw"].fillna("").map(html.unescape).str.strip()
    for col in ("positive", "negative"):
        df[col] = df[col].map(clean_text)
    df["district"] = df["district_raw"].map(stadtteil_mapping_func)
    df["region"] = df["district"].map(stadtteil_region_mapping)
    df["district_known"] = df["district"] != "SPAM"
    for col in ("positive", "negative"):
        df[col] = df[col].map(mask_contacts)
    df["month"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m")
    df.insert(0, "row_id", range(1, len(df) + 1))
    # district_raw is dropped: it sometimes contains street addresses
    return df[["row_id", "month", "district", "region", "district_known", "positive", "negative"]]


def run() -> pd.DataFrame:
    from project.districts import GEOJSON

    missing = [p for p in (paths.SURVEY, GEOJSON) if not p.exists()]
    if missing:
        names = ", ".join(str(p.relative_to(paths.ROOT)) for p in missing)
        raise SystemExit(f"Missing {names} – run `uv run python scripts/get_data.py` first.")
    logging.getLogger("project.districts").setLevel(logging.WARNING)
    df = prepare(pd.read_csv(paths.SURVEY))
    paths.INTERIM.mkdir(parents=True, exist_ok=True)
    df.to_csv(paths.PREPARED, index=False)
    return df

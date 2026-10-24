"""File locations of the pipeline – one place, so every step agrees on them."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"  # original survey – never read by the agent
INTERIM = ROOT / "data" / "interim"  # steps 1–2, may still contain personal data – blocked too
PROCESSED = ROOT / "data" / "processed"  # from step 3 on: cleaned, PII masked
OUTPUTS = ROOT / "outputs"  # charts and reports

SURVEY = RAW / "babylotse_survey_2024.csv"
PREPARED = INTERIM / "01_prepared.csv"
SPAM = INTERIM / "02_spam.csv"
CLEAN = PROCESSED / "03_clean.csv"
SAMPLE = PROCESSED / "04_sample.csv"
CATEGORIES = PROCESSED / "categories_v1.json"
CLASSIFIED = PROCESSED / "05_classified.csv"
REPORT = OUTPUTS / "report.html"

---
name: privacy-check
description: Checks datasets for personal data and pseudonymises them before they are sent to an LLM or shared. Use whenever data from data/raw/ is processed, sent to a language model or exported.
---

# Privacy check before using an LLM

Goal: no personal data (names, emails, phone numbers, addresses, IDs, free text with
identifying details) leaves the machine unchecked.

## Steps

1. **Do not look at the raw data yourself.** Write a script in `src/project/` that runs
   locally and only prints a summary: column names, dtypes, row count, share of missing
   values. Never print cell contents.
2. **Classify columns** (agree with the person at the keyboard):
   - *directly identifying* (name, email, phone, address, ID) → drop or hash
   - *quasi-identifying* (district, age, date) → coarsen (e.g. date → month)
   - *free text* → mask patterns (see below), have a human review a sample
3. **Mask free text** with regex, at least:
   - email → `[EMAIL]`, phone number → `[PHONE]`, URL → `[URL]`
   - optional: person names via spaCy NER → `[PERSON]`
4. Write the result to `data/processed/`; the original stays in `data/raw/`.
5. Add a test in `tests/` asserting that no email/phone patterns remain in the result.
6. Document in `docs/data-processing.md`: which columns, which measures, date.

## Afterwards

Only now may data from `data/processed/` go to the LLM (via `src/project/llm.py`).

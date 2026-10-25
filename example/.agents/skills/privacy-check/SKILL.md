---
name: privacy-check
description: Check a dataset for personal data and pseudonymise it before any LLM sees it. Use for step 3 of the pipeline, whenever a new data source is added, and before data is sent to a language model or shared.
---

# Privacy check before using an LLM

Goal: no personal data (names, e-mails, phone numbers, addresses, IDs, identifying free
text) reaches a language model or a shared file unchecked.

## Steps

1. **Don't look at the data yourself.** Files in `data/raw/` and `data/interim/` are blocked
   for you. Write code that runs locally and prints only a summary: columns, dtypes, row
   count, missing values, number of pattern matches – never cell contents.
2. **Classify the columns** and confirm with the person at the keyboard:
   - directly identifying (name, e-mail, phone, address, ID) → drop or hash
   - quasi-identifying (district, age, exact date) → coarsen (date → month)
   - free text → mask (next step) and flag
3. **Mask free text.** Reuse `mask_contacts()` from `src/project/prepare.py` (e-mail, phone,
   URL) – don't write a second regex. Add what is missing for this dataset, e.g. street +
   house number → `[ADDRESS]`, postcodes → `[POSTCODE]`, person names → `[NAME]` (names
   only via the topic model or spaCy, regex can't find them).
4. **Test the hard cases, not the easy ones.** Unusual formats slip through regexes that
   pass their own tests. Put real-looking edge cases in `tests/`, at least:
   `+371) 29 66 79 38`, `+371 25 927 529`, `0049 (0)69 123456`, `Seilerstraße 18`,
   `60313 Frankfurt`, `Frau Müller`.
5. **Flag, don't silently drop:** columns `pii_flag` and `pii_types`, so a human can review.
6. Write the result to `data/processed/` – only data there may be inspected or sent on.
7. Print counts per PII type and ask the person to spot-check 10 flagged rows.

## Afterwards

Only data from `data/processed/` goes to an LLM, and only via `src/project/llm.py`.

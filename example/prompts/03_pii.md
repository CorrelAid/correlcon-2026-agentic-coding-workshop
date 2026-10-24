# Step 3 – flag personal data (optional)

```text
Use the privacy-check skill. Implement step 3 in src/project/pii.py (contracts in
docs/pipeline.md).

- Read data/interim/02_spam.csv with code and keep only rows with is_spam == False.
- Step 1 already masked e-mails, phones and URLs. Flag what is still personal:
  remaining digits that look like phone numbers or house numbers, street names with
  numbers, postcodes, and – with --llm – person names, via the topic model in batches of 20.
- Columns pii_flag (bool) and pii_types (";"-separated, e.g. "name;address").
  Mask flagged parts with [NAME], [ADDRESS] … in the text.
- Write data/processed/03_clean.csv. Print only counts, never text.
- Tests in tests/test_pii.py with the hard cases: "+371 25 927 529", "Seilerstraße 18",
  "60313", "Frau Müller".

Run `uv run pytest`, then `uv run python scripts/03_pii.py`.
```

**Skipping this step?** Ask the agent: *"Write a minimal step 3 that only drops spam rows
and sets pii_flag to False."*

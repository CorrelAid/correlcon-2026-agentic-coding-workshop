---
name: privacy-check
description: Check a new dataset for personal data and pseudonymise it before any LLM sees it. Use when a new data source is added, before free text is sent to a language model, and before data is shared.
---

# Privacy check before using an LLM

Goal: no personal data (names, e-mails, phone numbers, addresses, IDs, identifying free
text) reaches a language model or a shared file unchecked.

## Steps

1. **Don't look at the data yourself.** Put the new file in `data/raw/` (blocked for you).
   Write code that runs locally and prints only a summary: columns, dtypes, row count,
   missing values, number of pattern matches – never cell contents.
2. **Classify the columns** and confirm with the person at the keyboard:
   - directly identifying (name, e-mail, phone, address, ID) → drop or hash
   - quasi-identifying (district, age, exact date) → coarsen (date → month)
   - free text → mask (next step)
3. **Mask free text.** Reuse `mask_contacts()` from `src/project/prepare.py` (e-mail, phone,
   URL) – don't write a second regex. Add only what this dataset needs, e.g. street + house
   number → `[ADDRESS]`, postcodes → `[POSTCODE]`. Person names can't be found reliably
   with regex – say so and let the person decide (e.g. spaCy NER or the topic model).
4. **Test the hard cases, not the easy ones.** Unusual formats slip through regexes that
   pass their own tests, e.g. `+371) 29 66 79 38`, `0049 (0)69 123456`, `Seilerstraße 18`,
   `60313 Frankfurt`.
5. Write the masked result to `data/interim/` and print counts per masked type.
   Ask the person to spot-check 10 masked rows themselves.

## Afterwards

Masked data goes to an LLM only via `src/project/llm.py` (EU provider).

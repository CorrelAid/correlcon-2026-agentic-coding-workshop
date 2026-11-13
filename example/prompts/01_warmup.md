# Warm-up – a first small test (≈ 1 min, ≈ €0.02)

Checks that your setup works end to end: the agent reads the project, writes code, the ruff
hook runs, tests pass. No data, no analysis model.

```text
Write a function mask_contacts(text: str) -> str in src/project/text.py that replaces
e-mail addresses with [EMAIL] and phone numbers with [PHONE]. Add a few tests in
tests/test_text.py (German and international phone formats) and run
`uv run pytest -q tests/test_text.py`.
```

**Look at:** did the agent read `AGENTS.md`'s rules (quiet output, absolute imports)? Did the
ruff hook fix or report anything? Which phone formats did its tests cover – and which not?

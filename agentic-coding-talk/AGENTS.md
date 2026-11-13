# AGENTS.md

Two Quarto (reveal.js) decks for CorrelAid at CorrelCon 2026 in Karlsruhe (Nov 13–15, 2026), both on Nov 14:
- `index.qmd` – “Coding Agents: best practices, discussion” (10:45–11:15, 30 min incl. discussion)
- `workshop.qmd` – “Coding Agents: intro workshop” (11:30–12:30, hands-on)

Each deck must be self-contained: people may attend only one of the two sessions.

## Commands
- Live preview: `quarto preview index.qmd` (or `workshop.qmd`)
- Build: `quarto render` → output in `_site/`
- PDF export: append `?print-pdf` to the URL and print from the browser
- Publish: `quarto publish gh-pages` (by hand – GitHub Actions are disabled in the CorrelAid org)

## Conventions
- All content in English (CorrelAid is English-first)
- One slide = one message; max. ~6 bullets
- Every content slide has `::: notes` with a time estimate that fits its session slot
- Graphics are hand-written SVGs in `img/`, colours from `theme.scss` (#0f7c8c teal, #e07a2f orange, #1d2433 ink)
- Numbers from studies only with a reference on the sources slide; don't round in ways that change the message
- Use the layout blocks from `theme.scss` (`.cards`, `.card`, `.term`, `.todo`) instead of inline styles
- Card titles use `[Title]{.ct}`, never `#`–`####` headings (a heading inside a card creates an extra slide)

## Don't
- Commit generated output (`_site/`, `index.html`, `*_files/`)
- Invent facts about the workshop setup (models, prices, repo paths) – ask Michael & Benjamin

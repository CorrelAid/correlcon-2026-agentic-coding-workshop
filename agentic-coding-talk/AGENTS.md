# AGENTS.md

Quarto (reveal.js) deck for the CorrelAid talk “Coding Agents and Best Practices” (20 min input + 40 min workshop) at CorrelCon 2026 in Karlsruhe (Nov 13–15, 2026; session on Nov 14).

## Commands
- Live preview: `quarto preview index.qmd`
- Build: `quarto render` → output in `_site/`
- PDF export: append `?print-pdf` to the URL and print from the browser
- Publish: `quarto publish gh-pages` (by hand – GitHub Actions are disabled in the CorrelAid org)

## Conventions
- All content in English (CorrelAid is English-first)
- One slide = one message; max. ~6 bullets
- Every content slide has `::: notes` with a time estimate; content slides sum to ≤ 20 min
- Graphics are hand-written SVGs in `img/`, colours from `theme.scss` (#0f7c8c teal, #e07a2f orange, #1d2433 ink)
- Numbers from studies only with a reference on the sources slide; don't round in ways that change the message
- Use the layout blocks from `theme.scss` (`.cards`, `.card`, `.term`, `.todo`) instead of inline styles
- Card titles use `[Title]{.ct}`, never `#`–`####` headings (a heading inside a card creates an extra slide)

## Don't
- Commit generated output (`_site/`, `index.html`, `*_files/`)
- Invent content for the placeholder slides – Michael & Benjamin fill those in

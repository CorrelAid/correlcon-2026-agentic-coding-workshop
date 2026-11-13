# Coding Agents and Best Practices – CorrelCon 2026

Slides for the two CorrelAid sessions at **CorrelCon 2026** in Karlsruhe (Nov 13–15, 2026), both on **Nov 14**:

| Time | Session | Deck |
|---|---|---|
| 10:45 – 11:15 | Coding Agents: best practices, discussion | `index.qmd` |
| 11:30 – 12:30 | Coding Agents: intro workshop (hands-on) | `workshop.qmd` |

Each deck stands on its own, since people may join only one session.

Speakers: Michael Aydinbas & Benjamin Fries

The slides are written in Markdown and built with [Quarto](https://quarto.org), which turns them into a [reveal.js](https://revealjs.com) presentation that runs in the browser.

---

## 1. Setup

You only need Quarto. You don't need R, Python or Jupyter, because the deck contains no executable code.

### Install Quarto (version 1.5 or newer, tested with 1.8)

| OS | Command |
|---|---|
| macOS | `brew install --cask quarto` |
| Windows | `winget install --id Posit.Quarto` |
| Linux (Debian/Ubuntu) | Download the `.deb` from <https://quarto.org/docs/get-started/> and run `sudo apt install ./quarto-*.deb` |

Or download the installer for your system directly from <https://quarto.org/docs/get-started/>.

Check that it works:

```bash
quarto --version
```

### Editor (optional)

Any text editor works. Two editors give you a live preview:

- **VS Code** or **Positron**: install the "Quarto" extension.
- **RStudio**: Quarto is built in, so you can click "Render" or "Preview".

## 2. Work on the slides

```bash
git clone git@github.com:CorrelAid/<repo>.git
cd <repo>
quarto preview index.qmd      # discussion deck
quarto preview workshop.qmd   # workshop deck
```

This opens the deck in your browser and reloads it every time you save `index.qmd`.

To build the static version without the live preview, run `quarto render`. The output goes to `_site/index.html` (discussion) and `_site/workshop.html` (workshop).

### Where things are

| File | Content |
|---|---|
| `index.qmd` | discussion deck (slides + speaker notes) |
| `workshop.qmd` | workshop deck (slides + speaker notes) |
| `theme.scss` | colours, fonts and layout blocks (cards, glossary, placeholders) |
| `img/*.svg` | graphics: autonomy chart, timeline, agentic loop, entry points, workshop setup & pipeline |
| `_quarto.yml` | presentation settings: size, footer, slide numbers |
| `AGENTS.md` | instructions for coding agents; also a live example in the talk |
| `CLAUDE.md` | only points to `AGENTS.md` |
| `.github/workflows/publish.yml` | automatic publishing to GitHub Pages |

### Slide syntax in a nutshell

```markdown
## Slide title                 ← every `##` starts a new slide

Normal Markdown: **bold**, lists, links, code …

::: {.cards .c2}               ← grid with 2 columns (.c3 = 3 columns)
::: {.card .accent}            ← card; variants: .accent .warn .good
[Card title]{.ct}

Card text
:::
:::

::: notes
Speaker notes – only visible in speaker view (key S)
:::
```

Inside a card, use `[Title]{.ct}` for the title and not `####`. A heading inside a card would create an extra, empty slide.

## 3. Present

Open the deck with `quarto preview index.qmd` or from the published URL.

| Key | Action |
|---|---|
| `→` / `Space` | next slide |
| `S` | speaker view with notes and timer (opens a second window) |
| `F` | fullscreen |
| `O` / `Esc` | slide overview |
| `B` | black screen |

**PDF export:** add `?print-pdf` to the URL, for example `http://localhost:4200/?print-pdf`. Then print from Chrome and choose "Save as PDF", landscape, with no margins.

## 4. Publish (GitHub Pages, by hand)

GitHub Actions are disabled in the CorrelAid org, so publish from your machine:

```bash
quarto publish gh-pages
```

This renders both decks, pushes them to the `gh-pages` branch and asks you to confirm. One-time: in the repo go to **Settings → Pages** and set the source to branch `gh-pages`, folder `/ (root)`. The decks are then at `https://correlaid.github.io/<repo>/` (discussion) and `…/<repo>/workshop.html` (workshop).

> The GitHub Pages site is public, even if the repo is private.

## Troubleshooting

- **`quarto: command not found`**: open a new terminal after installing. On Windows, restart VS Code too.
- **Fonts look different offline**: the deck loads Inter and JetBrains Mono from Google Fonts. Without internet access, a system font is used instead.
- **An extra empty slide appears**: a `#`, `##`, `###` or `####` heading is probably inside a card. Use `[Title]{.ct}` instead.
- **A slide is too full**: reveal.js doesn't scroll. Cut text or split the slide (see `AGENTS.md`: one slide = one message).

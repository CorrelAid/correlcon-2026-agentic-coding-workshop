"""Transparent cost estimate for the workshop and for projects.

    uv run python scripts/costs.py                        # workshop (20 people, 1.5 h)
    uv run python scripts/costs.py --people 12 --hours 2
    uv run python scripts/costs.py --texts 1974           # LLM categorisation run
    uv run python scripts/costs.py --markdown             # table for docs

Prices: list prices per 1M tokens, net, as of PRICES_AS_OF.
Double-check on the provider websites before using them in budgets or grant applications.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass

PRICES_AS_OF = "2026-10-23"


@dataclass(frozen=True)
class Price:
    provider: str
    model: str
    input: float  # per 1M input tokens
    output: float  # per 1M output tokens
    currency: str = "EUR"
    note: str = ""


PRICES: list[Price] = [
    Price("IONOS (DE)", "Qwen3-Coder-Next 80B", 0.15, 0.80, note="recommended coding model"),
    Price("IONOS (DE)", "gpt-oss-120b", 0.15, 0.65, note="analysis / categorisation"),
    Price("IONOS (DE)", "Qwen3.5-397B-A17B", 0.60, 3.60, note="strongest, pricier"),
    Price("STACKIT (DE)", "Qwen3.8 27B", 0.45, 0.65),
    Price("STACKIT (DE)", "gpt-oss-120b", 0.45, 0.65),
    Price("Scaleway (FR)", "qwen3.6-35b-a3b", 0.25, 1.50, note="1M tokens free"),
    Price("Scaleway (FR)", "glm-5.3", 1.80, 5.50),
    Price("OVHcloud (FR)", "gpt-oss-120b", 0.08, 0.40),
    Price("OVHcloud (FR)", "Qwen3.5-397B-A17B", 0.60, 3.60),
    Price("Mistral (FR)", "Devstral 2", 0.40, 2.00, "USD", "third-party price source, verify"),
]

# Token usage of a coding agent per person and hour of active use. Agents resend the
# conversation context with every step, so input tokens dominate. EU providers barely
# offer cheaper cached input, so we calculate without caching (conservative).
# Reference measurement (IONOS, 2026-10-23): one small task (write function + tests,
# run pytest) = ~120k input + ~2k output tokens in 46 s.
SCENARIOS = {
    "light": (1_000_000, 30_000),
    "typical": (3_000_000, 80_000),
    "heavy": (6_000_000, 150_000),
}

# Categorisation: system prompt + category list + one comment -> short JSON answer
TOKENS_PER_TEXT = (800, 40)


def cost(p: Price, input_tokens: float, output_tokens: float) -> float:
    return input_tokens / 1e6 * p.input + output_tokens / 1e6 * p.output


def fmt(amount: float, currency: str) -> str:
    return f"{'€' if currency == 'EUR' else '$'}{amount:,.2f}"


def table(header: list[str], rows: list[list[str]], markdown: bool) -> str:
    if markdown:
        out = ["| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
        out += ["| " + " | ".join(r) + " |" for r in rows]
        return "\n".join(out)
    widths = [max(len(str(x)) for x in col) for col in zip(header, *rows, strict=True)]

    def line(r: list[str]) -> str:
        return "  ".join(str(x).ljust(w) for x, w in zip(r, widths, strict=True))

    return "\n".join([line(header), line(["-" * w for w in widths])] + [line(r) for r in rows])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    ap.add_argument("--people", type=int, default=20)
    ap.add_argument("--hours", type=float, default=1.5, help="active agent use per person")
    ap.add_argument("--texts", type=int, default=0, help="number of texts to categorise")
    ap.add_argument("--markdown", action="store_true")
    a = ap.parse_args()

    person_hours = a.people * a.hours
    print(f"\nWorkshop: {a.people} people × {a.hours:g} h = {person_hours:g} person-hours")
    print(f"List prices, net, as of {PRICES_AS_OF}\n")
    header = ["Provider", "Model", "In/Out per 1M"] + [f"Workshop {s}" for s in SCENARIOS]
    rows = []
    for p in PRICES:
        values = [cost(p, i * person_hours, o * person_hours) for i, o in SCENARIOS.values()]
        rows.append(
            [p.provider, p.model, f"{fmt(p.input, p.currency)} / {fmt(p.output, p.currency)}"]
            + [fmt(v, p.currency) for v in values]
        )
    print(table(header, rows, a.markdown))

    if a.texts:
        i, o = TOKENS_PER_TEXT
        print(f"\nCategorising {a.texts} texts (~{i}+{o} tokens each):\n")
        rows = [
            [p.provider, p.model, fmt(cost(p, i * a.texts, o * a.texts), p.currency)]
            for p in PRICES
        ]
        print(table(["Provider", "Model", "Cost"], rows, a.markdown))

    i, o = SCENARIOS["typical"]
    print(
        f"\nAssumption 'typical': {i / 1e6:g}M input and {o / 1e3:g}k output tokens per person "
        "and hour. After the workshop, check real usage with `opencode stats` or the provider "
        "dashboard and update this script."
    )


if __name__ == "__main__":
    main()

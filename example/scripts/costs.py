"""Transparent cost estimate for the workshop and for projects.

    uv run python scripts/costs.py                        # workshop (20 people)
    uv run python scripts/costs.py --people 12
    uv run python scripts/costs.py --texts 1974           # LLM categorisation run (1 text/request)
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

# Coding agents resend the whole conversation with every step (tool call), so input tokens
# dominate. IONOS has no prompt caching, so every step pays for the full context.
# Measured with `opencode stats` (IONOS, Qwen3-Coder-Next, 2026-10-25, one prep day with a
# fresh session per pipeline step): 526 steps = 28.7M input + 172k output tokens = €4.44,
# i.e. ~55k input + ~330 output tokens per step. The fixed part (OpenCode system prompt,
# tools, AGENTS.md) is only ~7k tokens – the rest is file contents and command output that
# pile up during a session.
TOKENS_PER_STEP = (55_000, 330)

# Agent steps per person during the hands-on part (4–5 pipeline steps, ~40–70 steps each).
SCENARIOS = {"light": 100, "typical": 200, "heavy": 350}

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
    ap.add_argument("--texts", type=int, default=0, help="number of texts to categorise")
    ap.add_argument("--markdown", action="store_true")
    a = ap.parse_args()

    step_in, step_out = TOKENS_PER_STEP
    print(f"\nWorkshop: {a.people} people; agent steps per person: {SCENARIOS}")
    print(f"List prices, net, as of {PRICES_AS_OF}\n")
    header = ["Provider", "Model", "In/Out per 1M"] + [f"Workshop {s}" for s in SCENARIOS]
    rows = []
    for p in PRICES:
        values = [
            cost(p, step_in * n * a.people, step_out * n * a.people) for n in SCENARIOS.values()
        ]
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

    print(
        f"\nAssumption: ~{step_in / 1e3:g}k input + ~{step_out} output tokens per agent step "
        "(measured). After the workshop, check real usage with `opencode stats --cost` or the "
        "provider dashboard and update TOKENS_PER_STEP / SCENARIOS."
    )


if __name__ == "__main__":
    main()

"""Step 3 stability analysis – run multiple iterations with different seeds.

This helps assess how stable the discovered categories are across different samples.
"""

from __future__ import annotations

import json
from pathlib import Path

from project.data import load_valid_answers
from project.topics import draw_sample, find_topics


def run_stability_analysis(n_runs: int = 5, sample_size: int = 100) -> list[dict]:
    """Run step 3 multiple times with different seeds to assess category stability.

    Args:
        n_runs: Number of iterations with different seeds
        sample_size: Sample size per run (default 100)

    Returns:
        List of category results for each run
    """
    results = []

    # Load valid answers once
    df = load_valid_answers()

    for i, seed in enumerate(range(42, 42 + n_runs), start=1):
        print(f"\n{'=' * 60}")
        print(f"Run {i}/{n_runs} (seed={seed})")
        print("=" * 60)

        # Draw sample with this seed
        sample_df = draw_sample(df, sample_size, seed)

        # Find topics
        result = find_topics(sample_df)

        # Store results
        categories_list = [c.model_dump() for c in result.categories]
        results.append(
            {
                "seed": seed,
                "n_categories": len(result.categories),
                "categories": categories_list,
            }
        )

        # Save individual run results
        run_dir = Path("data/processed/stability")
        run_dir.mkdir(parents=True, exist_ok=True)

        # Save sample for this run
        sample_df[["row_id", "polarity", "text"]].to_csv(
            run_dir / f"sample_seed{seed}.csv", index=False
        )

        # Save categories for this run
        categories_file = run_dir / f"categories_seed{seed}.json"
        with open(categories_file, "w", encoding="utf-8") as f:
            json.dump(categories_list, f, indent=2, ensure_ascii=False)

        print(f"  Saved: {categories_file}")
        print(f"  Found {len(result.categories)} categories")

    # Save all results summary
    summary_file = run_dir / "stability_summary.json"
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 60}")
    print(f"Summary saved: {summary_file}")
    print("=" * 60)

    return results


def analyze_stability(results: list[dict]) -> None:
    """Analyze category stability across runs.

    Prints:
    - Number of categories per run
    - Category name overlap between runs
    """
    print("\n" + "=" * 60)
    print("STABILITY ANALYSIS")
    print("=" * 60)

    # Collect all category names
    all_names = [set(c["name"] for c in r["categories"]) for r in results]

    print(f"\nRuns: {len(results)}")
    print(f"Categories per run: {[r['n_categories'] for r in results]}")

    # Calculate pairwise overlap
    print("\nPairwise Jaccard similarity (category name overlap):")
    for i in range(len(all_names)):
        for j in range(i + 1, len(all_names)):
            intersection = len(all_names[i] & all_names[j])
            union = len(all_names[i] | all_names[j])
            jaccard = intersection / union if union > 0 else 0
            print(
                f"  Seed {results[i]['seed']} vs {results[j]['seed']}: "
                f"{intersection}/{union} = {jaccard:.2f}"
            )

    # Find categories that appear in all runs
    common = all_names[0]
    for names in all_names[1:]:
        common = common & names

    if common:
        print(f"\nCategories appearing in ALL runs ({len(common)}):")
        for name in sorted(common):
            print(f"  - {name}")
    else:
        print("\nNo categories appear in ALL runs.")

    # Find most frequent categories
    from collections import Counter

    all_category_names = []
    for r in results:
        all_category_names.extend(c["name"] for c in r["categories"])

    freq = Counter(all_category_names)
    print("\nTop 10 most frequent categories across all runs:")
    for name, count in freq.most_common(10):
        print(f"  {name}: {count}/{len(results)} runs")


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--n-runs", type=int, default=5, help="Number of iterations (default: 5)")
    ap.add_argument(
        "--sample-size", type=int, default=100, help="Sample size per run (default: 100)"
    )

    args = ap.parse_args()

    results = run_stability_analysis(n_runs=args.n_runs, sample_size=args.sample_size)
    analyze_stability(results)

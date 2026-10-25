"""Step 5 – analysis and report.

Input:  data/processed/04_classified.csv, valid answers (src/project/data.py), district GeoJSON
Output: outputs/report.html
"""

from __future__ import annotations

import json
import logging
from datetime import datetime

import pandas as pd
import plotly.express as px

from project.districts import GEOJSON, get_stadtteile_gdf
from project.paths import INTERIM, OUTPUTS, PROCESSED

logger = logging.getLogger(__name__)


def load_valid_answers_with_districts() -> pd.DataFrame:
    """Load valid answers with district information.

    Reads from 02_spam.csv if available (step 2 done), otherwise from 01_prepared.csv.
    Only loads row_id, district, region columns to avoid privacy issues.
    """
    spam_file = INTERIM / "02_spam.csv"
    prepared_file = INTERIM / "01_prepared.csv"

    if spam_file.exists():
        logger.info(f"Input: {spam_file.name} (step 2 available)")
        df = pd.read_csv(spam_file, usecols=["row_id", "district", "region", "is_spam"])
        df = df[df["is_spam"] == False]  # noqa: E712
        logger.info(f"Loaded {len(df)} rows with is_spam == False")
    else:
        logger.info(f"Input: {prepared_file.name} (step 2 skipped)")
        df = pd.read_csv(prepared_file, usecols=["row_id", "district", "region", "district_known"])
        df = df[df["district_known"] == True]  # noqa: E712
        logger.info(f"Loaded {len(df)} rows with district_known == True")

    return df


def load_classified_data() -> pd.DataFrame:
    """Load classified data from step 4."""
    file = PROCESSED / "04_classified.csv"
    logger.info(f"Input: {file.name}")
    df = pd.read_csv(file)
    logger.info(f"Loaded {len(df)} classified answers")
    return df


def load_categories() -> list[dict]:
    """Load category definitions."""
    file = PROCESSED / "categories_v1.json"
    logger.info(f"Loading categories from {file.name}")
    with open(file, encoding="utf-8") as f:
        return json.load(f)


def compute_key_figures(classified_df: pd.DataFrame, valid_df: pd.DataFrame) -> dict:
    """Compute key figures for the report."""
    # Total responses in valid answers
    total_responses = len(valid_df)

    # Count unique row_ids to get number of valid answers
    # (each row can have both positive and negative, so 2 entries per row)
    answers_count = len(classified_df)

    # Count spam removed:
    # Valid answers come from 02_spam.csv (is_spam == False) or
    # 01_prepared.csv (district_known == True)
    spam_count = total_responses - len(valid_df)

    # Count classified
    classified_count = answers_count

    return {
        "total_responses": total_responses,
        "spam_removed": spam_count,
        "valid_answers": len(valid_df),
        "classified_answers": classified_count,
    }


def compute_category_shares(classified_df: pd.DataFrame) -> pd.DataFrame:
    """Compute share of answers mentioning each category, by polarity."""
    # Split multi-label categories
    records = []
    for _, row in classified_df.iterrows():
        categories = [c.strip() for c in row["category"].split(";")]
        for cat in categories:
            records.append({"polarity": row["polarity"], "category": cat})

    cats_df = pd.DataFrame(records)

    # Total answers per polarity
    total_by_polarity = classified_df.groupby("polarity").size()

    # Count per category per polarity using pivot_table
    counts = cats_df.groupby(["polarity", "category"]).size().unstack(fill_value=0)

    # Compute shares - divide each row by the total for that polarity
    # Reset index to make polarity a column
    counts_reset = counts.reset_index()
    counts_reset["total"] = counts_reset["polarity"].map(total_by_polarity)

    # Compute share as percentage
    for col in counts_reset.columns:
        if col not in ["polarity", "category", "total"]:
            counts_reset[col] = counts_reset[col] / counts_reset["total"] * 100

    # Melt back to long format
    shares = counts_reset.melt(
        id_vars=["polarity"],
        value_vars=[c for c in counts_reset.columns if c not in ["polarity", "total"]],
        var_name="category",
        value_name="share",
    )

    return shares


def build_category_bar_chart(shares_df: pd.DataFrame) -> str:
    """Build bar chart showing category shares by polarity."""
    logger.info("Building category bar chart")

    fig = px.bar(
        shares_df,
        x="category",
        y="share",
        color="polarity",
        barmode="group",
        labels={
            "category": "Kategorie",
            "share": "Anteil der Antworten (%)",
            "polarity": "Sentiment",
        },
        color_discrete_map={"positive": "#2ecc71", "negative": "#e74c3c"},
    )

    fig.update_layout(
        title="Anteil der Antworten pro Kategorie (nach Sentiment)",
        yaxis_range=[0, 100],
        legend_title_text="",
        showlegend=True,
        height=500,
        margin=dict(l=50, r=50, t=50, b=100),
    )

    # Rotate x-axis labels
    fig.update_xaxes(tickangle=-45)

    return fig.to_html(full_html=False, include_plotlyjs="cdn")


def compute_heatmap_data(classified_df: pd.DataFrame, valid_df: pd.DataFrame) -> pd.DataFrame:
    """Compute heatmap data: negative categories × region."""
    # Merge classified with valid to get district/region info
    # Need to join on row_id, but we need to preserve polarity
    # So we create a mapping: {row_id: district, region} from valid_df
    district_map = valid_df.set_index("row_id")[["district", "region"]].to_dict("index")

    # Add district/region to classified data
    classified_df = classified_df.copy()
    classified_df["district"] = classified_df["row_id"].map(
        lambda x: district_map.get(x, {}).get("district", "Unbekannt")
    )
    classified_df["region"] = classified_df["row_id"].map(
        lambda x: district_map.get(x, {}).get("region", "Unbekannt")
    )

    # Filter for negative polarity
    neg_df = classified_df[classified_df["polarity"] == "negative"].copy()

    # Split categories
    records = []
    for _, row in neg_df.iterrows():
        categories = [c.strip() for c in row["category"].split(";")]
        region = row.get("region", "Unbekannt")
        for cat in categories:
            records.append({"category": cat, "region": region})

    cats_df = pd.DataFrame(records)

    # Count per category per region
    counts = cats_df.groupby(["region", "category"]).size().unstack(fill_value=0)

    # Compute shares: each column (category) sums to 100%
    # Share of negative comments in that category from each region
    shares = counts.div(counts.sum(axis=0), axis=1) * 100
    shares = shares.stack().reset_index()
    shares.columns = ["region", "category", "share"]

    return shares


def build_heatmap(heatmap_df: pd.DataFrame) -> str:
    """Build heatmap of negative categories by region."""
    logger.info("Building heatmap")

    # Define region order
    region_order = ["Nord", "Mitte", "Ost", "West", "Süd", "Umland", "Unbekannt"]
    region_order = [r for r in region_order if r in heatmap_df["region"].values]

    # Define category order (sort by total count)
    category_totals = heatmap_df.groupby("category")["share"].sum()
    category_order = category_totals.sort_values(ascending=False).index.tolist()

    # Reorder
    heatmap_df = heatmap_df.copy()
    heatmap_df["region"] = pd.Categorical(
        heatmap_df["region"], categories=region_order, ordered=True
    )
    heatmap_df["category"] = pd.Categorical(
        heatmap_df["category"], categories=category_order, ordered=True
    )
    heatmap_df = heatmap_df.sort_values(["region", "category"])

    fig = px.density_heatmap(
        heatmap_df,
        x="category",
        y="region",
        z="share",
        histfunc="avg",
        labels={
            "category": "Kategorie",
            "region": "Region",
            "z": "Anteil (%)",
        },
        color_continuous_scale="RdYlGn_r",
    )

    fig.update_layout(
        title="Negative Kategorien nach Region (Anteil innerhalb der Kategorie)",
        height=500,
        margin=dict(l=150, r=50, t=50, b=100),
    )

    return fig.to_html(full_html=False, include_plotlyjs="cdn")


def build_map(valid_df: pd.DataFrame) -> str:
    """Build map of responses per district."""
    logger.info("Building district map")

    # Count responses per district
    district_counts = valid_df.groupby("district").size().reset_index(name="count")

    # Load GeoJSON
    logger.info(f"Loading GeoJSON from {GEOJSON.name}")
    gdf = get_stadtteile_gdf()

    # Merge counts
    gdf = gdf.merge(district_counts, left_on="STTLNAME", right_on="district", how="left")
    gdf["count"] = gdf["count"].fillna(0)

    # Create map
    fig = px.choropleth_map(
        gdf,
        geojson=gdf.geometry,
        locations=gdf.index,
        color="count",
        hover_name="STTLNAME",
        hover_data={"count": True},
        color_continuous_scale="Blues",
        range_color=(0, gdf["count"].quantile(0.95)),
        center={"lat": 50.1109, "lon": 8.6821},
        zoom=10,
        labels={"count": "Antworten"},
    )

    fig.update_layout(
        title="Antworten pro Stadtteil",
        margin=dict(l=0, r=0, t=50, b=0),
        height=500,
    )

    return fig.to_html(full_html=False, include_plotlyjs="cdn")


def get_example_quotes(
    classified_df: pd.DataFrame, categories: list[dict], max_length: int = 200
) -> dict[str, dict]:
    """Get example quotes for each category."""
    logger.info("Extracting example quotes")

    categories_text = [c["name"] for c in categories]
    quotes = {cat: {"positive": None, "negative": None} for cat in categories_text}

    for _, row in classified_df.iterrows():
        row_categories = [c.strip() for c in row["category"].split(";")]

        for cat in row_categories:
            if cat not in quotes:
                continue

            text = row["text"]
            if len(text) > max_length:
                text = text[:max_length] + "…"

            if row["polarity"] == "positive" and quotes[cat]["positive"] is None:
                quotes[cat]["positive"] = text
            elif row["polarity"] == "negative" and quotes[cat]["negative"] is None:
                quotes[cat]["negative"] = text

        # Check if we have all quotes
        if all(q["positive"] and q["negative"] for q in quotes.values()):
            break

    return quotes


def build_report_html(
    key_figures: dict,
    bar_chart: str,
    heatmap: str,
    map_html: str,
    quotes: dict[str, dict],
    categories: list[dict],
) -> str:
    """Build the complete HTML report."""
    logger.info("Building HTML report")

    # Date and version info
    today = datetime.now().strftime("%d.%m.%Y")

    # Category list
    category_list = (
        "<ul>" + "".join(f"<li>{c['name']}: {c['description']}</li>" for c in categories) + "</ul>"
    )

    # Quotes HTML
    quotes_html = ""
    for cat, q in quotes.items():
        pos_quote = q["positive"] if q["positive"] else "Keine positive Aussage"
        neg_quote = q["negative"] if q["negative"] else "Keine negative Aussage"
        quotes_html += f"""
        <div class="category-quotes">
            <h3>{cat}</h3>
            <div class="quote positive">
                <strong>Positiv:</strong> "{pos_quote}"
            </div>
            <div class="quote negative">
                <strong>Negativ:</strong> "{neg_quote}"
            </div>
        </div>
        """

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Babylotse Frankfurt 2024 – Umfragenauswertung</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                Oxygen, Ubuntu, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }}
        h1 {{ color: #2c3e50; }}
        h2 {{ color: #34495e; margin-top: 40px; }}
        h3 {{ color: #7f8c8d; }}
        .key-figures {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .figure {{
            margin: 30px 0;
        }}
        .category-quotes {{
            margin: 20px 0;
            padding: 15px;
            border-radius: 8px;
            background: #f8f9fa;
        }}
        .quote {{
            margin: 10px 0;
            padding: 10px;
            border-left: 4px solid;
        }}
        .quote.positive {{ border-color: #2ecc71; background: #e8f8f0; }}
        .quote.negative {{ border-color: #e74c3c; background: #fceae9; }}
        .methods {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-top: 40px;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            font-size: 0.9em;
            color: #666;
        }}
    </style>
</head>
<body>
    <h1>Babylotse Frankfurt 2024 – Umfragenauswertung</h1>
    <p>Auswertung der Elternbefragung zu Leben mit Baby in Frankfurt.</p>

    <h2>1. Kennzahlen</h2>
    <div class="key-figures">
        <div class="kf-item">
            <h3>{key_figures["total_responses"]}</h3>
            <p>Gesamtantworten</p>
        </div>
        <div class="kf-item">
            <h3>{key_figures["spam_removed"]}</h3>
            <p>Spam / ungültig entfernt</p>
        </div>
        <div class="kf-item">
            <h3>{key_figures["valid_answers"]}</h3>
            <p>Valide Antworten</p>
        </div>
        <div class="kf-item">
            <h3>{key_figures["classified_answers"]}</h3>
            <p>Klassifizierte Antworten</p>
        </div>
    </div>

    <h2>2. Themenverteilung</h2>
    <p>Anzahl der Antworten, die jedes Thema erwähnen (nach Sentiment).
       Eine Antwort kann mehrere Themen enthalten.</p>
    <div class="figure">
        {bar_chart}
    </div>

    <h2>3. Regionale Verteilung negativer Themen</h2>
    <p>Anteil der negativen Aussagen pro Kategorie, aufgeteilt nach Region.
       Eine Antwort kann mehrere Kategorien enthalten.</p>
    <div class="figure">
        {heatmap}
    </div>

    <h2>4. Antworten pro Stadtteil</h2>
    <div class="figure">
        {map_html}
    </div>

    <h2>5. Beispielaussagen</h2>
    {quotes_html}

    <h2>6. Methodische Hinweise</h2>
    <div class="methods">
        <p><strong>Daten:</strong> Babylotse Frankfurt 2024, 987 Antworten, CC BY 4.0</p>
        <p><strong>Analyse-Modell:</strong> gpt-oss-120b (IONOS AI Model Hub)</p>
        <p><strong>Prompt-Version:</strong> TOPICS_V1</p>
        <p><strong>Datum der Auswertung:</strong> {today}</p>
        <p><strong>Kategorien:</strong> {len(categories)} Themen</p>
        <p>{category_list}</p>
    </div>

    <div class="footer">
        <p>© CorrelAid 2026 – Daten: CC BY 4.0, Babylotse Frankfurt</p>
    </div>
</body>
</html>
    """

    return html


def run() -> None:
    """Build a self-contained HTML report with charts and example quotes."""
    # Load data
    classified_df = load_classified_data()
    categories = load_categories()

    # Load valid answers with district info
    valid_df = load_valid_answers_with_districts()
    logger.info(f"Valid answers loaded: {len(valid_df)} rows")

    # Compute key figures
    key_figures = compute_key_figures(classified_df, valid_df)
    logger.info(f"Key figures: {key_figures}")

    # Compute category shares
    shares_df = compute_category_shares(classified_df)
    logger.info(f"Category shares computed: {len(shares_df)} records")

    # Build charts
    bar_chart = build_category_bar_chart(shares_df)

    # Compute and build heatmap
    heatmap_df = compute_heatmap_data(classified_df, valid_df)
    heatmap = build_heatmap(heatmap_df)

    # Build map
    map_html = build_map(valid_df)

    # Get example quotes
    quotes = get_example_quotes(classified_df, categories)
    logger.info("Example quotes extracted")

    # Build HTML
    html = build_report_html(key_figures, bar_chart, heatmap, map_html, quotes, categories)

    # Write output
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUTS / "report.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
    logger.info(f"Output: {output_file.name} written")

    # Sanity checks
    assert output_file.exists(), "Report file not written"
    assert output_file.stat().st_size > 1000, "Report file too small"

    # Check all sections present
    with open(output_file, encoding="utf-8") as f:
        content = f.read()

    required_sections = [
        "1. Kennzahlen",
        "2. Themenverteilung",
        "3. Regionale Verteilung negativer Themen",
        "4. Antworten pro Stadtteil",
        "5. Beispielaussagen",
        "6. Methodische Hinweise",
    ]
    for section in required_sections:
        assert section in content, f"Missing section: {section}"

    # Check all categories shown
    category_names = {c["name"] for c in categories}
    for cat_name in category_names:
        assert cat_name in content, f"Missing category in report: {cat_name}"

    logger.info("Sanity checks passed: all sections present, all categories shown")

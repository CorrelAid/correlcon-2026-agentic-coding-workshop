# Step 5 – report

```text
Implement step 5 in src/project/report.py: a self-contained HTML report
outputs/report.html built with plotly (no server, works offline after creation).

Content:
1. Key figures: responses, spam removed, answers classified.
2. Bar chart: share of each category, positive vs. negative side by side.
3. Heatmap: negative categories × region (share per region, not counts).
4. Map: number of responses per district, using data/reference/ffmstadtteilewahlen.geojson
   and get_stadtteile_gdf() from src/project/districts.py.
5. Per category two example quotes (positive and negative), shortened to 200 characters.
6. A short methods note: models used, prompt versions, date, data licence (CC BY 4.0,
   Babylotse Frankfurt).

Readable for an NGO board: German labels, no jargon. Add a test that the report file is
created from a tiny fake data set.

- Show the user what is happening: logging (INFO: input files and row counts, each
  chart/section built, output file). No comment text in logs.

Run `uv run pytest -q`, then tell me the command to build the report.
```

**Look at:** open `outputs/report.html`. What would the NGO do with it?

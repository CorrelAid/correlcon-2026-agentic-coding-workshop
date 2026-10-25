"""Step 5 – build the report.  uv run python scripts/05_report.py"""

from project import paths, report

report.run()
print(f"Open {paths.REPORT.relative_to(paths.ROOT)} in your browser.")

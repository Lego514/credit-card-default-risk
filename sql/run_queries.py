"""Execute the five analysis queries against the cleaned dataset.

Queries are written in PostgreSQL-compatible ANSI SQL and executed locally with
DuckDB (an in-process analytical engine — no database server to install).
Results are saved to sql/results/ and Tableau-ready copies to data/tableau/.
"""

import shutil
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed" / "credit_default_clean.csv"
RESULTS = ROOT / "sql" / "results"
TABLEAU = ROOT / "data" / "tableau"


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    TABLEAU.mkdir(exist_ok=True)

    con = duckdb.connect()
    con.execute(f"CREATE VIEW credit AS SELECT * FROM read_csv_auto('{PROCESSED.as_posix()}')")

    for sql_file in sorted((ROOT / "sql").glob("*.sql")):
        df = con.execute(sql_file.read_text(encoding="utf-8")).df()
        out = RESULTS / f"{sql_file.stem}.csv"
        df.to_csv(out, index=False)
        print(f"\n=== {sql_file.name} ({len(df)} rows) ===")
        print(df.to_string(index=False))
        shutil.copy(out, TABLEAU / out.name)

    # Slim customer-level extract for the Tableau scatter view (30K rows).
    con.execute(
        """
        COPY (
            SELECT id, age, sex_label, education_label, marriage_label,
                   limit_bal, utilization, max_delay, n_months_delayed,
                   delay_trend, default_next_month
            FROM credit
        ) TO '{path}' (HEADER, DELIMITER ',')
        """.format(path=(TABLEAU / "customer_level.csv").as_posix())
    )
    print(f"\nTableau extracts -> {TABLEAU.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

import polars as pl
import sqlite3
from whisky_api import distilleries_info, distillery_data


def run_ingestion():
    conn = sqlite3.connect("whisky_data.db")

    print("Step 1: Fetching Master List...")
    all_dist = distilleries_info()

    all_dist.to_pandas().to_sql(
        "master_distilleries", conn, if_exists="replace", index=False
    )

    distilleries = all_dist["slug"].to_list()

    print(f"Step 2: Syncing {len(distilleries)} distilleries...")

    for distillery in distilleries:
        try:
            df = distillery_data(distillery)

            if df.is_empty():
                continue

            df = df.with_columns(pl.lit(distillery).alias("distillery_slug"))

            pdf = df.to_pandas()

            # 1. DELETE existing records
            conn.execute(
                """
                DELETE FROM distillery_stats
                WHERE distillery_slug = ?
            """,
                (distillery,),
            )

            # 2. INSERT fresh data
            pdf.to_sql("distillery_stats", conn, if_exists="append", index=False)

            print(f"Success: {distillery}")

        except Exception as e:
            print(f"Failed: {distillery} - {e}")

    conn.commit()
    conn.close()

    print("ETL Complete")


if __name__ == "__main__":
    run_ingestion()

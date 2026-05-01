import polars as pl
import sqlite3
from whisky_api import distilleries_info, distillery_data


def run_ingestion():
    conn = sqlite3.connect("whisky_data.db")

    print("Step 1: Fetching Master List...")
    all_dist = distilleries_info()
    # Save the master list to SQL for the dropdown later
    all_dist.to_pandas().to_sql(
        "master_distilleries", conn, if_exists="replace", index=False
    )

    slugs = all_dist["slug"].to_list()
    master_records = []

    print(f"Step 2: Syncing {len(slugs)} distilleries to Local DB...")
    for slug in slugs:
        try:
            df = distillery_data(slug)
            if not df.is_empty():
                df = df.with_columns(pl.lit(slug).alias("distillery_slug"))
                master_records.append(df)
                print(f" Success: {slug}")
        except Exception as e:
            print(f" Failed: {slug} - {e}")
            continue

    if master_records:
        full_df = pl.concat(master_records)
        # Load to SQL
        full_df.to_pandas().to_sql(
            "distillery_stats", conn, if_exists="replace", index=False
        )
        print(f"\n✅ ETL Complete! {len(full_df)} records saved to whisky_data.db")

    conn.close()


if __name__ == "__main__":
    run_ingestion()

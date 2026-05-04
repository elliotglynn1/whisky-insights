import sqlite3
import polars as pl

DB_PATH = "whisky_data.db"


class WhiskyDataEngine:
    """Handles logic for database-centric data retrieval."""

    @staticmethod
    def get_all_distilleries() -> pl.DataFrame:
        """Reads master list from local SQLite."""
        conn = sqlite3.connect(DB_PATH)
        distillery_info = pl.read_database("SELECT * FROM master_distilleries", conn)
        conn.close()
        return distillery_info

    @staticmethod
    def get_distillery_metrics(slug) -> pl.DataFrame:
        """Targeted SQL query for specific distillery deep-dive."""
        conn = sqlite3.connect(DB_PATH)
        query = f"SELECT * FROM distillery_stats WHERE distillery_slug = '{slug}'"
        distillery_metrics = pl.read_database(query, conn)
        conn.close()

        if not distillery_metrics.is_empty():
            return distillery_metrics.with_columns(
                pl.col("dt").str.to_date("%Y-%m-%d").alias("Timestamp")
            )
        return pl.DataFrame()

    @staticmethod
    def get_market_rankings() -> pl.DataFrame:
        """Calculates top performers from the entire local dataset."""
        conn = sqlite3.connect(DB_PATH)
        distillery_stats = pl.read_database("SELECT * FROM distillery_stats", conn)
        conn.close()
        return distillery_stats

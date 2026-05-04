import sqlite3
import polars as pl

DB_PATH = "whisky_data.db"


class WhiskyDataEngine:
    """Handles logic for database-centric data retrieval."""

    def _conn(self):
        return sqlite3.connect(DB_PATH)

    def get_all_distilleries(self) -> pl.DataFrame:
        """Reads master list from local SQLite."""
        conn = self._conn()
        distillery_info = pl.read_database("SELECT * FROM master_distilleries", conn)
        conn.close()
        return distillery_info

    def get_distillery_metrics(self, slug) -> pl.DataFrame:
        query = f"SELECT * FROM distillery_stats WHERE distillery_slug = '{slug}'"

        conn = self._conn()
        distillery_metrics = pl.read_database(query, conn)
        conn.close()

        if not distillery_metrics.is_empty():
            return distillery_metrics.with_columns(
                pl.col("dt").str.to_date("%Y-%m-%d").alias("Timestamp")
            )

        return pl.DataFrame()

    def get_market_rankings(self) -> pl.DataFrame:
        """Calculates top performers from the entire local dataset."""
        conn = self._conn()
        distillery_stats = pl.read_database("SELECT * FROM distillery_stats", conn)
        conn.close()
        return distillery_stats

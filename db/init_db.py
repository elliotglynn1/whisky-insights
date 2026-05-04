import sqlite3


def init_db(db_path="whisky_data.db"):
    conn = sqlite3.connect(db_path)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS distillery_stats (
        dt TEXT,
        winning_bid_max REAL,
        winning_bid_min REAL,
        winning_bid_mean REAL,
        trading_volume REAL,
        lots_count INTEGER,
        slug TEXT,
        name TEXT,
        distillery_slug TEXT,
        PRIMARY KEY (distillery_slug, dt)
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS master_distilleries (
        slug TEXT PRIMARY KEY,
        name TEXT
    )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized.")

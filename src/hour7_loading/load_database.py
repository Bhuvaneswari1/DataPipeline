import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import create_engine, text

from common.config import DATABASE_URL, WAREHOUSE_DIR
from common.utils import read_data
from hour3_data_cleaning.clean_orders import clean_orders


DEMO_TABLE = "orders_full_demo"

ORDER_COLUMNS = """
    order_id VARCHAR(64) PRIMARY KEY,
    customer TEXT,
    product TEXT,
    order_date TEXT,
    quantity INTEGER
"""

SCHEMA = [
    f"CREATE TABLE IF NOT EXISTS orders ({ORDER_COLUMNS})",
    """
    CREATE TABLE IF NOT EXISTS shipments (
        shipment_id VARCHAR(64) PRIMARY KEY,
        order_id VARCHAR(64),
        ship_date TEXT,
        delivery_date TEXT,
        status TEXT
    )
    """,
    f"CREATE TABLE IF NOT EXISTS {DEMO_TABLE} ({ORDER_COLUMNS})",
]


def get_engine():
    WAREHOUSE_DIR.mkdir(parents=True, exist_ok=True)
    return create_engine(DATABASE_URL)


def init_db(engine):
    """Create the warehouse tables if they are missing."""
    with engine.begin() as conn:
        for ddl in SCHEMA:
            conn.execute(text(ddl))


def full_load_demo(df, engine):
    """Reload the demo table from the complete orders DataFrame."""
    with engine.begin() as conn:
        conn.execute(text(f"DELETE FROM {DEMO_TABLE}"))
        df.to_sql(DEMO_TABLE, conn, if_exists="append", index=False)

    return len(df)


def table_counts(engine):
    with engine.connect() as conn:
        return {
            table: conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar_one()
            for table in ("orders", "shipments", DEMO_TABLE)
        }


if __name__ == "__main__":
    engine = get_engine()
    try:
        init_db(engine)
        orders = clean_orders(read_data("orders.csv"))
        loaded = full_load_demo(orders, engine)

        print(f"Loaded {loaded} rows into {DEMO_TABLE}")
        print(table_counts(engine))
    finally:
        engine.dispose()
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
from sqlalchemy import inspect, text

from common.config import ORDERS_FILE
from common.utils import read_data
from hour3_data_cleaning.clean_orders import clean_orders
from hour3_data_cleaning.clean_shipments import clean_shipments
from hour4_reconciliation.orphan_shipments import find_orphans
from hour4_reconciliation.overdue_deliveries import find_overdue
from hour4_reconciliation.unshipped_orders import find_unshipped
from hour7_loading.incremental_load import incremental_load, upsert
from hour7_loading.load_database import get_engine, init_db
from hour7_loading.load_parquet import write_parquet


def extract_and_clean():
    """Read the input CSVs and clean the orders and shipments."""
    orders = clean_orders(read_data(ORDERS_FILE))
    shipments = clean_shipments(read_data("shipments.csv"))
    sla = read_data("sla_rules.csv")

    return orders, shipments, sla


def load_warehouse(engine, orders, shipments):
    """Load new orders and insert or update shipment records."""
    orders_loaded = incremental_load(
        orders, engine, "orders", "order_id", "order_date"
    )
    shipments_loaded = upsert(
        shipments, engine, "shipments", "shipment_id"
    )

    return orders_loaded, shipments_loaded


def reconcile_from_warehouse(engine, sla):
    """Compare all stored orders with all stored shipments."""
    with engine.connect() as conn:
        orders = pd.read_sql_query(
            text("SELECT * FROM orders"),
            conn,
            parse_dates=["order_date"],
        )
        shipments = pd.read_sql_query(
            text("SELECT * FROM shipments"),
            conn,
            parse_dates=["ship_date", "delivery_date"],
        )

    return (
        find_unshipped(orders, shipments),
        find_orphans(orders, shipments),
        find_overdue(orders, shipments, sla),
    )


def publish_results(engine, unshipped, orphan, overdue):
    """Refresh the SQL report tables and write matching Parquet files."""
    reports = {
        "unshipped_orders": unshipped,
        "orphan_shipments": orphan,
        "overdue_deliveries": overdue,
    }

    # Create missing report tables before the refresh transaction.
    with engine.begin() as conn:
        for name, df in reports.items():
            if not inspect(conn).has_table(name):
                df.head(0).to_sql(name, conn, if_exists="fail", index=False)

    with engine.begin() as conn:
        for name, df in reports.items():
            conn.execute(text(f"DELETE FROM {name}"))
            df.to_sql(name, conn, if_exists="append", index=False)

    for name, df in reports.items():
        path = write_parquet(df, name)
        print(f"Saved {len(df)} rows to {path}")


def run():
    engine = get_engine()

    try:
        init_db(engine)

        orders, shipments, sla = extract_and_clean()
        orders_loaded, shipments_loaded = load_warehouse(
            engine, orders, shipments
        )
        print(
            f"Loaded {orders_loaded} order rows and "
            f"processed {shipments_loaded} shipment rows"
        )

        unshipped, orphan, overdue = reconcile_from_warehouse(engine, sla)
        publish_results(engine, unshipped, orphan, overdue)

        print(
            f"Results: unshipped={len(unshipped)} | "
            f"orphan={len(orphan)} | overdue={len(overdue)}"
        )

        with engine.connect() as conn:
            counts = {
                table: conn.execute(
                    text(f"SELECT COUNT(*) FROM {table}")
                ).scalar_one()
                for table in ("orders", "shipments")
            }

        print(f"Warehouse row counts: {counts}")
        return unshipped, orphan, overdue

    finally:
        engine.dispose()


if __name__ == "__main__":
    run()
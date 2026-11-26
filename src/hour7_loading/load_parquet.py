import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from common.config import PARQUET_DIR
from common.utils import read_data
from hour3_data_cleaning.clean_orders import clean_orders


def write_parquet(df, name):
    PARQUET_DIR.mkdir(parents=True, exist_ok=True)
    path = PARQUET_DIR / f"{name}.parquet"
    df.to_parquet(path, index=False)
    return path


if __name__ == "__main__":
    raw_orders = read_data("orders.csv")
    csv_date_type = raw_orders["order_date"].dtype

    orders = clean_orders(raw_orders)
    path = write_parquet(orders, "orders_demo")
    restored_orders = pd.read_parquet(path)

    print(f"Saved to: {path}")
    print(f"order_date after reading CSV:     {csv_date_type}")
    print(f"order_date after cleaning:        {orders['order_date'].dtype}")
    print(f"order_date after reading Parquet: {restored_orders['order_date'].dtype}")
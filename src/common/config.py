import os
from pathlib import Path

from dotenv import load_dotenv

from common.utils import BASE_DIR

load_dotenv(BASE_DIR / ".env")

WAREHOUSE_DIR = BASE_DIR / "warehouse"

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"sqlite:///{WAREHOUSE_DIR / 'reconciliation.db'}",
)

PARQUET_DIR = BASE_DIR / Path(os.getenv("PARQUET_DIR", "warehouse/parquet"))
ORDERS_FILE = os.getenv("ORDERS_FILE", "orders.csv")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
SCHEDULE_TZ = os.getenv("SCHEDULE_TZ", "Asia/Kolkata")
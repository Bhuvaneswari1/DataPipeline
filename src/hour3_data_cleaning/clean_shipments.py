import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
from common.utils import read_data

def clean_shipments(df):
    df = df.copy()
    df["order_id"] = df["order_id"].str.strip().str.upper()
    df["ship_date"] = pd.to_datetime(df["ship_date"], errors="coerce")
    df["delivery_date"] = pd.to_datetime(df["delivery_date"], errors="coerce")
    df = df.drop_duplicates(subset=["shipment_id"])
    return df

if __name__ == "__main__":
    raw = read_data("shipments.csv")
    cleaned = clean_shipments(raw)
    print("Rows before: ",len(raw),"| Rows after: ",len(cleaned))
    print(cleaned.dtypes)
    print(cleaned)
    
    
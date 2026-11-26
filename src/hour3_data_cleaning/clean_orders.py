import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
from common.utils import read_data

def clean_orders(df):
    df = df.copy()
    df["order_id"] = df["order_id"].str.strip().str.upper()
    df["customer"] = df["customer"].fillna("Unknown").str.strip()
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df = df.drop_duplicates(subset=["order_id"])
    return df

if __name__ == "__main__":
    raw = read_data("orders.csv")
    cleaned = clean_orders(raw)
    print("Rows before: ",len(raw),"| Rows after: ",len(cleaned))
    print(cleaned)
    
    
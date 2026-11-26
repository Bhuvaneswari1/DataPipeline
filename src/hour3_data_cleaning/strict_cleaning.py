import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd
from common.utils import read_data, save_output
from clean_orders import clean_orders

def clean_orders_strict(df):
    df = clean_orders(df)
    df["product"] = df["product"].str.strip().str.title()
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    
    reason = pd.Series("",index=df.index)
    reason[df["quantity"].isna()] = "Quantity is not a number"
    reason[df["quantity"] <= 0] = "Quantity must be positive"
    reason[df["order_date"].isna()] = "Order date is invalid"
    
    rejected = df[reason != ""].assign(reject_reason=reason[reason != ""])
    good = df[reason == ""].copy()
    good["quantity"] = good["quantity"].astype(int)
    return good, rejected

if __name__ == "__main__":
    raw = read_data("orders.csv")
    extra = pd.DataFrame([
        {"order_id": "O2001", "customer": "Alice", "product": "  laptop  ", "quantity": 2, "order_date": "2026-11-10"},
        {"order_id": "O2002", "customer": "Bob", "product": "Smartphone", "quantity": -1, "order_date": "2026-11-11"},
        {"order_id": "O2003", "customer": "Charlie", "product": "Tablet", "quantity": 3, "order_date": "invalid_date"},
        {"order_id": "O2004", "customer": "David", "product": "Headphones", "quantity": "two", "order_date": "2026-11-12"},
        {"order_id": "O2005", "customer": "Eve", "product": "Monitor", "quantity": 1, "order_date": None},
    ])
    
    raw = pd.concat([raw, extra], ignore_index=True)
    good,rejected = clean_orders_strict(raw)
    print("Input rows: ",len(raw),"| Good rows: ",len(good),"| Rejected rows: ",len(rejected))
    print(rejected[["order_id","reject_reason"]].to_string(index=False))
    save_output(rejected,"rejected_orders.csv")
    
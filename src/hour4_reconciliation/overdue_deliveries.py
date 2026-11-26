import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from common.utils import read_data, AS_OF_DATE
from hour3_data_cleaning.clean_orders import clean_orders
from hour3_data_cleaning.clean_shipments import clean_shipments

def find_overdue(orders, shipments, sla, as_of=AS_OF_DATE):
    merged = orders.merge(shipments, on="order_id", how="inner")
    merged = merged.merge(sla, on="product" , how="left")
    
    end_date = merged["delivery_date"].fillna(as_of)
    merged["days_taken"] = (end_date - merged["order_date"]).dt.days
    merged["days_late"] = merged["days_taken"] - merged["sla_days"]
    #Laptop - days-taken(6) , sla-days(5) , days_late(1)
    
    overdue = merged[merged["days_late"] > 0]
    return overdue[["order_id", "customer", "product", "order_date", "ship_date", "delivery_date", "days_taken", "days_late"]]

if __name__ == "__main__":
    orders = clean_orders(read_data("orders.csv"))
    shipments = clean_shipments(read_data("shipments.csv"))
    sla = read_data("sla_rules.csv")
    
    overdue = find_overdue(orders, shipments, sla)
    print(overdue)
    
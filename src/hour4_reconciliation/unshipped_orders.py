import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from common.utils import read_data
from hour3_data_cleaning.clean_orders import clean_orders
from hour3_data_cleaning.clean_shipments import clean_shipments

def find_unshipped(orders, shipments):
    return orders[~orders["order_id"].isin(shipments["order_id"])]

if __name__ == "__main__":
    orders = clean_orders(read_data("orders.csv"))
    shipments = clean_shipments(read_data("shipments.csv"))
    print(find_unshipped(orders, shipments))
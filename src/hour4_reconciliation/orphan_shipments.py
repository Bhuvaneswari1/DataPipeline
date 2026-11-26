import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from common.utils import read_data
from hour3_data_cleaning.clean_orders import clean_orders
from hour3_data_cleaning.clean_shipments import clean_shipments

def find_orphans(orders, shipments):
    return shipments[~shipments["order_id"].isin(orders["order_id"])]

if __name__ == "__main__":
    orders = clean_orders(read_data("orders.csv"))
    #print(orders)
    shipments = clean_shipments(read_data("shipments.csv"))
    print(find_orphans(orders, shipments))
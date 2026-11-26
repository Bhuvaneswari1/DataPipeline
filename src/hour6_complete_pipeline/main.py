import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from common.utils import read_data
from hour3_data_cleaning.clean_orders import clean_orders
from hour3_data_cleaning.clean_shipments import clean_shipments
from hour4_reconciliation.unshipped_orders import find_unshipped
from hour4_reconciliation.orphan_shipments import find_orphans
from hour4_reconciliation.overdue_deliveries import find_overdue
from hour5_reporting.generate_reports import print_report
from hour5_reporting.export_csv import export_all

def run():
    print("Pipeline Started")
    
    #1. Extract
    orders = read_data("orders.csv")
    shipments = read_data("shipments.csv")
    sla = read_data("sla_rules.csv")
    
    #Transform(clean)
    orders = clean_orders(orders)
    shipments = clean_shipments(shipments)
    
    #Reconciliation
    unshipped = find_unshipped(orders, shipments)
    orphan = find_orphans(orders, shipments)
    overdue = find_overdue(orders, shipments, sla)
    
    #Load(report + export)
    print_report(unshipped, orphan, overdue)
    export_all(unshipped, orphan, overdue)
    
    print("Pipeline Completed")
    
if __name__ == "__main__":
    run()
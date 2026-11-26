import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from common.utils import read_data, save_output

def export_all(unshipped, orphan, overdue):
    save_output(unshipped, "unshipped_orders.csv")
    save_output(orphan, "orphan_shipments.csv")
    save_output(overdue, "overdue_deliveries.csv")
    

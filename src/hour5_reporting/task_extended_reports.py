import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import pandas as pd
from common.utils import read_data, save_output, OUTPUT_DIR, AS_OF_DATE
from hour3_data_cleaning.clean_orders import clean_orders
from hour3_data_cleaning.clean_shipments import clean_shipments
from hour4_reconciliation.unshipped_orders import find_unshipped
from hour4_reconciliation.orphan_shipments import find_orphans
from hour4_reconciliation.overdue_deliveries import find_overdue

def build_summary(unshipped, orphan, overdue):
    summary = {
        "unshipped_orders": len(unshipped),
        "orphan_shipments": len(orphan),
        "overdue_deliveries": len(overdue)
    }
    return pd.DataFrame([summary])

def overdue_by_product(overdue):
    return (overdue.groupby("product")
            .agg(
                overdue_count=("order_id", "count"),
                avg_days_late=("days_late", "mean"),
                worst_days_late=("days_late", "max"))
            .reset_index()
            .sort_values(["overdue_count", "avg_days_late"], ascending=[False,False]))
    
def export_excel(sheets, filename="reconciliation_report.xlsx"):
    OUTPUT_DIR.mkdir(exist_ok=True)
    with pd.ExcelWriter(OUTPUT_DIR / filename) as writer:
        for sheet_name, df in sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    print(f"Saved {len(sheets)} sheets -> output/{filename}")

def exports_dated_csv(df, name, as_of=AS_OF_DATE):
    save_output(df, f"{name}_{as_of.strftime('%Y%m%d')}.csv")

if __name__ == "__main__":
    orders = clean_orders(read_data("orders.csv"))
    shipments = clean_shipments(read_data("shipments.csv"))
    sla = read_data("sla_rules.csv")
    
    unshipped = find_unshipped(orders, shipments)
    orphan = find_orphans(orders, shipments)
    overdue = find_overdue(orders, shipments, sla)
    
    summary = build_summary(unshipped, orphan, overdue)
    overdue_product = overdue_by_product(overdue)
    print(summary.to_string(index=False))
    print()
    print(overdue_product.to_string(index=False))
    
    export_excel({
        "summary": summary,
        "unshipped_orders": unshipped,
        "orphan_shipments": orphan,
        "overdue_deliveries": overdue,
        "overdue_by_product": overdue_product
    })
    
    exports_dated_csv(unshipped, "unshipped_orders")
    exports_dated_csv(orphan, "orphan_shipments")
    exports_dated_csv(overdue, "overdue_deliveries")
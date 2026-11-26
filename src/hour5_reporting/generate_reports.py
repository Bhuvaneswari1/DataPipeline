def print_report(unshipped, orphan, overdue):
    print("="*50)
    print("ORDER RECONCILIATION REPORT")
    print("="*50)
    print(f"Unshipped Orders: {len(unshipped)}")
    print(f"Orphan Shipments: {len(orphan)}")
    print(f"Overdue Deliveries: {len(overdue)}")
    
    print("\nUnshipped Orders:")
    print(unshipped[["order_id", "customer", "order_date"]].to_string(index=False))
    print("\nOrphan Shipments:")
    print(orphan[["shipment_id", "order_id", "status"]].to_string(index=False))
    print("\nOverdue Deliveries:")
    print(overdue[["order_id", "customer", "product", "order_date", "ship_date", "delivery_date", "days_taken", "days_late"]].to_string(index=False))
    
    
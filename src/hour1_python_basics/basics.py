#variable
company_name = "TechCorp"
order_count = 5

#List
products = ["Laptop", "Smartphone", "Tablet"]
orders = [1001, 1002, 1003]
shipped = [1001, 1002]

#Dictionary (one record = key-value pair)
order = {"order_id": 1001, "product": "Laptop", "quantity": 2}

#Loop
for order_id in orders:
    print(f"Processing order: {order_id}")

#condition
for order_id in orders:#1001
    if order_id in shipped:#if 1001 in [1001,1002]
        print(f"Order {order_id} has been shipped.")
    else:
        print(f"Order {order_id} is pending shipment.")

#Function
def greet_customer(name):
    return f"Hello, {name}! Thank you for shopping with {company_name}."

print(greet_customer("Alice"))

#Bridge to Hour4: the reconciliation of the orders and shipped lists
unshipped_orders = [order_id for order_id in orders if order_id not in shipped]
print(f"Unshipped orders: {unshipped_orders}")


#order-date = 2026-10-06
#delivery-date = 2026-10-20
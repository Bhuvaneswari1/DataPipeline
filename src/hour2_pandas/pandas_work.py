from io import StringIO

import pandas as pd


def read_orders(path):
    try:
        orders = pd.read_csv(path)
    except FileNotFoundError:
        return {"Error": f"File not found: {path}"}

    info_buffer = StringIO()
    orders.info(buf=info_buffer)

    #select the columns needed for the analysis
    selected_columns = orders[["order_id", "product", "quantity"]]
    
    #Filter the rows by quantity
    positive_quantity_rows = selected_columns.loc[
        selected_columns["quantity"] > 0
    ]
    
    #Filter the rows by quantity which is zero or negative quantities
    negative_quantity_rows = selected_columns.loc[
            selected_columns["quantity"] <= 0
        ]
    
    #Group by product, count rows, calculate total units
    product_summary = (
        positive_quantity_rows.groupby("product", as_index=False)
        .agg(
            order_rows = ("order_id","size"),
            total_units = ("quantity", "sum"),
        )
        .sort_values("total_units",ascending=False)
    )
    
    return {
        "First 5 rows": orders.head(5),
        "Dataset information": info_buffer.getvalue(),
        "Selected columns": selected_columns,
        "Rows with positive quantities": positive_quantity_rows,
        "Rows with negative quantities": negative_quantity_rows,
        "Product Summary sorted by total units": product_summary
    }


report = read_orders("data/orders.csv")

for title, result in report.items():
    print(f"\n{title}")
    print(result)
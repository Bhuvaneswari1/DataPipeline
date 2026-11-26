# Orphan Shipment Reconciliation

`orphan_shipments.py` compares the order and shipment datasets and finds **orphan shipments**: shipment records whose `order_id` does not exist in the cleaned order dataset.

This check identifies shipments that may belong to a deleted order, use an incorrect order ID, or come from a different system.

## Input Data

The script reads two CSV files from the project's `data/` directory:

| File | Required purpose | Required columns |
|---|---|---|
| `data/orders.csv` | Source of valid order IDs | `order_id` |
| `data/shipments.csv` | Shipment records to validate | `shipment_id`, `order_id`, `ship_date`, `delivery_date`, `status` |

The cleaning functions also use these additional order columns when they exist:

- `customer`
- `product`
- `order_date`
- `quantity`

### Orders CSV Example

```csv
order_id,customer,product,order_date,quantity
O1001,Ravi,Laptop,2026-10-01,1
O1002,Meena,Phone,Oct 02 2026,2
o1008 ,Arjun,Phone,2026-10-08,1
O1003,Kiran,Laptop,2026-10-03,1
```

The order data may contain:

- Leading or trailing spaces in `order_id`.
- Lowercase order IDs.
- Blank customer names.
- Duplicate order IDs.
- Common date formats that pandas can recognize.
- Invalid or missing date values.

Before reconciliation, `clean_orders()`:

1. Copies the DataFrame so the original data is not modified.
2. Removes spaces from `order_id`.
3. Converts `order_id` to uppercase.
4. Replaces missing customers with `"Unknown"` and trims customer names.
5. Converts `order_date` to a pandas datetime value.
6. Invalid dates become `NaT` because `errors="coerce"` is used.
7. Removes duplicate rows using `order_id`, keeping the first occurrence.

### Shipments CSV Example

```csv
shipment_id,order_id,ship_date,delivery_date,status
S5001,O1001,2026-10-02,2026-10-05,Delivered
S5008,O9999,2026-10-10,2026-10-13,Delivered
```

The shipment data may contain:

- Leading or trailing spaces in `order_id`.
- Lowercase order IDs.
- Missing delivery dates for shipments that are still in transit.
- Duplicate shipment IDs.
- Invalid shipment or delivery dates.

Before reconciliation, `clean_shipments()`:

1. Copies the DataFrame so the original data is not modified.
2. Removes spaces from `order_id`.
3. Converts `order_id` to uppercase.
4. Converts `ship_date` to pandas datetime values.
5. Converts `delivery_date` to pandas datetime values.
6. Invalid dates become `NaT`.
7. Removes duplicate rows using `shipment_id`, keeping the first occurrence.

Matching is performed only after cleaning. For example, `o1008 ` in the orders file is cleaned to `O1008`, so it correctly matches `O1008` in the shipments file.

## Source Code, Explained Line by Line

```python
import sys
```

Imports Python's `sys` module, which provides access to system and interpreter settings such as `sys.path`.

```python
from pathlib import Path
```

Imports `Path` for creating, resolving, and working with file-system paths in a platform-independent way.

```python
sys.path.append(str(Path(__file__).resolve().parents[1]))
```

- `__file__` is the path of `orphan_shipments.py`.
- `.resolve()` converts that path to an absolute path.
- `.parents[1]` selects the `src/` directory.
- `str(...)` converts the `Path` object to a string.
- `sys.path.append(...)` adds `src/` to Python's module-search path.

This allows imports such as `common.utils` and `hour3_data_cleaning.clean_orders` to work even when the script is run from a different working directory.

```python
from common.utils import read_data
```

Imports `read_data()`. That helper reads a named CSV from the project's `data/` directory and returns a pandas DataFrame.

```python
from hour3_data_cleaning.clean_orders import clean_orders
```

Imports `clean_orders()`, which standardizes order IDs and order dates and removes duplicate orders.

```python
from hour3_data_cleaning.clean_shipments import clean_shipments
```

Imports `clean_shipments()`, which standardizes shipment order IDs and date columns and removes duplicate shipments.

```python
def find_orphans(orders, shipments):
```

Defines a function named `find_orphans`.

- `orders` is the cleaned orders DataFrame.
- `shipments` is the cleaned shipments DataFrame.
- The function returns another DataFrame containing only orphan shipments.

```python
    return shipments[~shipments["order_id"].isin(orders["order_id"])]
```

This line performs the reconciliation:

- `shipments["order_id"]` selects shipment order IDs.
- `orders["order_id"]` selects valid order IDs.
- `.isin(...)` creates a boolean value for each shipment indicating whether its order ID exists in the orders table.
- `~` reverses those boolean values, so `True` means “order ID was not found.”
- `shipments[...]` keeps only rows for which the result is `True`.

The original columns and data types of the matching shipment rows are preserved.

```python
if __name__ == "__main__":
```

Runs the following block only when this file is executed directly.

It prevents the reconciliation code from running automatically when another Python file imports this module.

```python
    orders = clean_orders(read_data("orders.csv"))
```

- `read_data("orders.csv")` loads `data/orders.csv` into a DataFrame.
- `clean_orders(...)` cleans that DataFrame.
- The result is assigned to `orders`.

```python
    shipments = clean_shipments(read_data("shipments.csv"))
```

- `read_data("shipments.csv")` loads `data/shipments.csv` into a DataFrame.
- `clean_shipments(...)` cleans that DataFrame.
- The result is assigned to `shipments`.

```python
    print(find_orphans(orders, shipments))
```

Calls `find_orphans()` and prints the orphan shipment DataFrame in the terminal.

## Expected Output

Using the project's current sample data, shipment `S5008` has order ID `O9999`. Because `O9999` is not present in `orders.csv`, the script prints:

```text
  shipment_id order_id  ship_date delivery_date     status
7        S5008    O9999 2026-10-10    2026-10-13  Delivered
```

The exact row number and formatting may vary with pandas and with the CSV contents.

## Setup and Run

Run all commands from the project root:

```bash
cd /Users/bhuvaneswarigokul/Desktop/Gen-AI/Hexaware/Data_Pipeline/order-reconciliation
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 src/hour4_reconciliation/orphan_shipments.py
```

The virtual environment is optional, but it keeps this project's Python packages separate from global Python packages.

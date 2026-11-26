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

## Setup and run commands

Run these commands from the extracted `order-reconciliation` folder, which contains `requirements.txt` and `src/`. Create a fresh virtual environment for your operating system.

**macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

**Windows PowerShell**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Hour 1 — Python basics

```bash
python src/hour1_python_basics/basics.py
```

### Hour 2 — Read and explore orders with pandas

```bash
python src/hour2_pandas/read_orders.py
python src/hour2_pandas/pandas_work.py
```

### Hour 3 — Clean orders and shipments

```bash
python src/hour3_data_cleaning/clean_orders.py
python src/hour3_data_cleaning/clean_shipments.py
python src/hour3_data_cleaning/strict_cleaning.py
```

### Hour 4 — Run each reconciliation check

```bash
python src/hour4_reconciliation/unshipped_orders.py
python src/hour4_reconciliation/orphan_shipments.py
python src/hour4_reconciliation/overdue_deliveries.py
```

### Hour 5 — Export Excel and dated CSV reports

```bash
python src/hour5_reporting/task_extended_reports.py
```

The console report and standard CSV export helpers are called by Hour 6.

### Hour 6 — Run the complete CSV pipeline

```bash
python src/hour6_complete_pipeline/main.py
```

### Hour 7 — Load and reconcile the warehouse

If `DATABASE_URL` in `.env` points to MySQL, start MySQL and create the configured database and user first. The user needs permission to create tables and select, insert, and delete rows in that database. The pipeline creates its tables. Without a configured database URL, the project uses local SQLite.

```bash
python src/hour7_loading/etl_load_pipeline.py
```

Run the full-load database demo or Parquet demo separately.

```bash
python src/hour7_loading/load_database.py
python src/hour7_loading/load_parquet.py
```

### Hour 8 — Run once or schedule the job

Before running Hour 8, make sure every product in the configured orders CSV has a matching row in `data/sla_rules.csv`. If your orders contain `Monitor`, add a `Monitor` rule with the applicable delivery deadline in days.

**Run immediately**

```bash
python src/hour8_automation/pipeline_job.py
```

**Test the scheduler with two runs, 10 seconds apart**

```bash
python src/hour8_automation/schedule_job.py --every-seconds 10 --max-runs 2
```

**Run daily at 2:00 AM**

```bash
python src/hour8_automation/schedule_job.py
```

**Run daily at a custom time, such as 6:30 PM**

```bash
python src/hour8_automation/schedule_job.py --cron "30 18 * * *"
```

The scheduler uses `SCHEDULE_TZ` from `.env` and defaults to `Asia/Kolkata`. Keep the process running for scheduled jobs to fire. Press **Ctrl+C** to stop it.

**Run the retry demo**

```bash
python src/hour8_automation/retry.py
```

**Watch the pipeline log from a second terminal**

On macOS:

```bash
tail -n 30 -f logs/pipeline.log
```

In Windows PowerShell:

```powershell
Get-Content .\logs\pipeline.log -Tail 30 -Wait
```

Look for `finished: SUCCESS` for the newest run ID. If it says `FAILED`, read the error above it. To check the latest run in MySQL Workbench, run:

```sql
SELECT run_id, started_at, status, error
FROM reconciliation.pipeline_runs
ORDER BY run_id DESC
LIMIT 1;
```

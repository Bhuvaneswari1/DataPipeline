from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

pd.Timestamp.today()
AS_OF_DATE = pd.Timestamp("2026-11-10")
#order-date=2026-10-05

def read_data(filename):
    return pd.read_csv(DATA_DIR / filename)

def save_output(df, filename):
    OUTPUT_DIR.mkdir(exist_ok=True)
    df.to_csv(OUTPUT_DIR / filename, index=False)
    print(f"Saved {len(df)} rows -> output/{filename}")


import pandas as pd
from sqlalchemy import text


def get_watermark(engine, table, column):
    """Return the latest stored date, or None if the table is empty."""
    with engine.connect() as conn:
        value = conn.execute(
            text(f"SELECT MAX({column}) FROM {table}")
        ).scalar_one()

    return pd.Timestamp(value) if value is not None else None


def upsert(df, engine, table, key):
    """Replace rows for incoming keys and insert rows for new keys."""
    if df.empty:
        return 0

    key_params = [{"key_value": value} for value in df[key]]

    with engine.begin() as conn:
        conn.execute(
            text(f"DELETE FROM {table} WHERE {key} = :key_value"),
            key_params,
        )
        df.to_sql(table, conn, if_exists="append", index=False)

    return len(df)


def incremental_load(df, engine, table, key, watermark_col, lookback_days=0):
    """Load rows at or after the watermark, including any lookback window."""
    watermark = get_watermark(engine, table, watermark_col)

    if watermark is None:
        fresh = df
    else:
        cutoff = watermark - pd.Timedelta(days=lookback_days)
        incoming_dates = pd.to_datetime(df[watermark_col], errors="raise")
        fresh = df.loc[incoming_dates >= cutoff]

    return upsert(fresh, engine, table, key)
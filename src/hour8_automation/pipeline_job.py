import logging
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from common.config import LOG_LEVEL
from common.logger import setup_logging
from hour7_loading.load_database import get_engine, init_db
from hour7_loading.etl_load_pipeline import (
    extract_and_clean,
    load_warehouse,
    publish_results,
    reconcile_from_warehouse,
)
from hour8_automation.retry import retry


log = logging.getLogger("pipeline")

RUNS_DDL = """
CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id VARCHAR(64) PRIMARY KEY,
    started_at VARCHAR(32),
    finished_at VARCHAR(32),
    status VARCHAR(16),
    seconds REAL,
    orders_loaded INTEGER,
    unshipped INTEGER,
    orphan INTEGER,
    overdue INTEGER,
    error TEXT
)
"""

retry_db = retry(times=3, delay=1.0, exceptions=(OperationalError,))
load_with_retry = retry_db(load_warehouse)
publish_with_retry = retry_db(publish_results)


def validate_inputs(orders, sla):
    """Check that every ordered product has an SLA rule."""
    missing = sorted(set(orders["product"]) - set(sla["product"]))
    if missing:
        raise ValueError(f"No SLA rule for product(s): {missing}")


def record_run(engine, run):
    """Save one pipeline run to the warehouse."""
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO pipeline_runs (
                    run_id, started_at, finished_at, status, seconds,
                    orders_loaded, unshipped, orphan, overdue, error
                )
                VALUES (
                    :run_id, :started_at, :finished_at, :status, :seconds,
                    :orders_loaded, :unshipped, :orphan, :overdue, :error
                )
            """),
            run,
        )


def run_pipeline():
    """Run the pipeline once and return True if publishing succeeds."""
    started = datetime.now()
    clock = time.perf_counter()
    engine = None

    run = {
        "run_id": started.strftime("%Y%m%d-%H%M%S-%f"),
        "started_at": started.isoformat(timespec="seconds"),
        "status": "FAILED",
        "orders_loaded": 0,
        "unshipped": 0,
        "orphan": 0,
        "overdue": 0,
        "error": None,
    }

    log.info("Run %s started", run["run_id"])

    try:
        engine = get_engine()
        init_db(engine)

        with engine.begin() as conn:
            conn.execute(text(RUNS_DDL))

        orders, shipments, sla = extract_and_clean()
        log.info("Cleaned %d orders and %d shipments", len(orders), len(shipments))

        validate_inputs(orders, sla)

        orders_loaded, shipments_loaded = load_with_retry(
            engine, orders, shipments
        )
        run["orders_loaded"] = orders_loaded
        log.info(
            "Loaded %d order rows and %d shipment rows",
            orders_loaded,
            shipments_loaded,
        )

        unshipped, orphan, overdue = reconcile_from_warehouse(engine, sla)
        run.update(
            unshipped=len(unshipped),
            orphan=len(orphan),
            overdue=len(overdue),
        )
        log.info(
            "Reconciled: unshipped=%d orphan=%d overdue=%d",
            run["unshipped"],
            run["orphan"],
            run["overdue"],
        )

        publish_with_retry(engine, unshipped, orphan, overdue)
        run["status"] = "SUCCESS"

    except Exception as error:
        run["error"] = f"{type(error).__name__}: {error}"
        log.exception("Run %s failed", run["run_id"])

    finally:
        run["seconds"] = round(time.perf_counter() - clock, 2)
        run["finished_at"] = datetime.now().isoformat(timespec="seconds")

        if engine is not None:
            try:
                record_run(engine, run)
            except Exception:
                log.exception("Could not write the run history")
            finally:
                engine.dispose()

        log.info(
            "Run %s finished: %s in %.2fs",
            run["run_id"],
            run["status"],
            run["seconds"],
        )

    return run["status"] == "SUCCESS"


if __name__ == "__main__":
    setup_logging(LOG_LEVEL)
    sys.exit(0 if run_pipeline() else 1)
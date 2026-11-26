"""Schedule the order reconciliation pipeline."""

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from common.config import LOG_LEVEL, SCHEDULE_TZ
from common.logger import setup_logging
from hour8_automation.pipeline_job import run_pipeline


log = logging.getLogger("scheduler")


def main():
    parser = argparse.ArgumentParser(description="Schedule the reconciliation job")
    schedule = parser.add_mutually_exclusive_group()
    schedule.add_argument(
        "--cron",
        default="0 2 * * *",
        help="Cron expression. The default runs daily at 02:00.",
    )
    schedule.add_argument(
        "--every-seconds",
        type=int,
        help="Run every N seconds for the classroom demo.",
    )
    parser.add_argument(
        "--max-runs",
        type=int,
        default=0,
        help="Stop after N completed runs. Use 0 to keep scheduling.",
    )
    args = parser.parse_args()

    if args.every_seconds is not None and args.every_seconds < 1:
        parser.error("--every-seconds must be at least 1")
    if args.max_runs < 0:
        parser.error("--max-runs must be 0 or greater")

    setup_logging(LOG_LEVEL)

    if args.every_seconds is not None:
        trigger = IntervalTrigger(
            seconds=args.every_seconds,
            timezone=SCHEDULE_TZ,
        )
    else:
        trigger = CronTrigger.from_crontab(args.cron, timezone=SCHEDULE_TZ)

    scheduler = BlockingScheduler(timezone=SCHEDULE_TZ)
    completed_runs = 0

    def on_finished(event):
        nonlocal completed_runs
        completed_runs += 1

        if event.exception is not None:
            log.error("Run %d raised an exception: %s", completed_runs, event.exception)
        elif event.retval is False:
            log.error("Run %d failed. See the pipeline log.", completed_runs)
        else:
            log.info("Run %d succeeded", completed_runs)

        if args.max_runs and completed_runs >= args.max_runs:
            log.info("Reached %d runs. Stopping the scheduler.", completed_runs)
            scheduler.shutdown(wait=False)

    scheduler.add_listener(on_finished, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
    scheduler.add_job(
        run_pipeline,
        trigger,
        id="order_reconciliation",
        max_instances=1,
        coalesce=True,
        misfire_grace_time=300,
    )

    log.info("Starting scheduler with trigger %s in %s", trigger, SCHEDULE_TZ)
    try:
        scheduler.start()
    except KeyboardInterrupt:
        if scheduler.running:
            scheduler.shutdown()


if __name__ == "__main__":
    main()
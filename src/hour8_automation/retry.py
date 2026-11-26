import functools
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

log = logging.getLogger(__name__)


def retry(times=3, delay=1.0, backoff=2.0, exceptions=(Exception,)):
    """Run a function up to `times` attempts, including the first call."""
    if times < 1:
        raise ValueError("times must be at least 1")

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            wait = delay

            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as error:
                    if attempt == times:
                        log.error(
                            "%s failed after %d attempts: %s",
                            func.__name__, times, error,
                        )
                        raise

                    log.warning(
                        "%s failed (attempt %d of %d): %s. Retrying in %.1fs",
                        func.__name__, attempt, times, error, wait,
                    )
                    time.sleep(wait)
                    wait *= backoff

        return wrapper

    return decorator


if __name__ == "__main__":
    from common.logger import setup_logging

    setup_logging("INFO")
    attempts = {"count": 0}

    @retry(times=3, delay=0.5, exceptions=(ConnectionError,))
    def flaky_load():
        attempts["count"] += 1

        if attempts["count"] < 3:
            raise ConnectionError("Simulated temporary connection failure")

        return "loaded"

    result = flaky_load()
    print(f"Result: {result} after {attempts['count']} attempts")
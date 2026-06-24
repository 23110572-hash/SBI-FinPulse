"""Background scheduler for proactive engagement scans.

Uses APScheduler. Runs services.engagement.scan_all() once per day at
SCHEDULER_DAILY_HOUR:SCHEDULER_DAILY_MINUTE. If SCHEDULER_INTERVAL_MINUTES is
set to a positive number, an additional interval job is added (useful for
tests or for short-cadence demos).
"""
from __future__ import annotations

import logging

from config import settings

log = logging.getLogger("finpulse.scheduler")

_scheduler = None


def start_scheduler() -> None:
    global _scheduler
    if not settings.enable_scheduler:
        log.info("Scheduler disabled (ENABLE_SCHEDULER=false).")
        return
    if _scheduler is not None:
        return
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
    except Exception as e:
        log.warning("APScheduler not installed (%s); proactive scans disabled.", e)
        return

    from services.engagement import scan_all

    _scheduler = BackgroundScheduler(daemon=True)

    # Daily cron sweep — the workhorse.
    _scheduler.add_job(
        scan_all, "cron",
        hour=settings.scheduler_daily_hour,
        minute=settings.scheduler_daily_minute,
        id="engagement_scan_daily", max_instances=1, coalesce=True,
    )
    log.info("Proactive scan scheduled daily at %02d:%02d.",
             settings.scheduler_daily_hour, settings.scheduler_daily_minute)

    # Optional short-cadence interval (off by default).
    if settings.scheduler_interval_minutes and settings.scheduler_interval_minutes > 0:
        _scheduler.add_job(
            scan_all, "interval",
            minutes=settings.scheduler_interval_minutes,
            id="engagement_scan_interval", max_instances=1, coalesce=True,
        )
        log.info("Interval scan also scheduled every %s min.",
                 settings.scheduler_interval_minutes)

    _scheduler.start()


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None

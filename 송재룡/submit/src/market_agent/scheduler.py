from dataclasses import dataclass
from datetime import datetime, time

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from market_agent.config import KST


MARKET_OPEN = time(9, 0)
MARKET_CLOSE = time(15, 30)


@dataclass(frozen=True)
class SchedulerJobDefinition:
    id: str
    description: str
    trigger: CronTrigger


def is_regular_session_tracking_time(value: datetime) -> bool:
    kst_value = value.astimezone(KST)
    if kst_value.weekday() >= 5:
        return False
    current = kst_value.time()
    return MARKET_OPEN <= current <= MARKET_CLOSE


def scheduler_job_definitions() -> list[SchedulerJobDefinition]:
    return [
        SchedulerJobDefinition(
            "premarket-report",
            "08:00 Asia/Seoul premarket report",
            CronTrigger(day_of_week="mon-fri", hour=8, minute=0, timezone=KST),
        ),
        SchedulerJobDefinition(
            "hourly-tracking",
            "Hourly simulated tracking during 09:00-15:30 KST",
            CronTrigger(day_of_week="mon-fri", hour="9-15", minute=0, timezone=KST),
        ),
        SchedulerJobDefinition(
            "closing-summary",
            "Closing summary after Korean regular session",
            CronTrigger(day_of_week="mon-fri", hour=15, minute=35, timezone=KST),
        ),
    ]


def build_scheduler(premarket_job, hourly_job, closing_job) -> BlockingScheduler:
    scheduler = BlockingScheduler(timezone=KST)
    jobs = scheduler_job_definitions()
    callbacks = {
        "premarket-report": premarket_job,
        "hourly-tracking": hourly_job,
        "closing-summary": closing_job,
    }
    for job in jobs:
        scheduler.add_job(callbacks[job.id], job.trigger, id=job.id, replace_existing=True)
    return scheduler

from datetime import datetime, timezone

from market_agent.config import KST
from market_agent.scheduler import is_regular_session_tracking_time, scheduler_job_definitions


def test_regular_session_tracking_time_uses_kst_weekdays() -> None:
    assert is_regular_session_tracking_time(datetime(2026, 4, 30, 9, 0, tzinfo=KST))
    assert is_regular_session_tracking_time(datetime(2026, 4, 30, 15, 30, tzinfo=KST))
    assert not is_regular_session_tracking_time(datetime(2026, 4, 30, 8, 59, tzinfo=KST))
    assert not is_regular_session_tracking_time(datetime(2026, 4, 30, 15, 31, tzinfo=KST))
    assert not is_regular_session_tracking_time(datetime(2026, 5, 2, 10, 0, tzinfo=KST))


def test_regular_session_tracking_time_converts_from_utc() -> None:
    utc_value = datetime(2026, 4, 30, 1, 0, tzinfo=timezone.utc)

    assert is_regular_session_tracking_time(utc_value)


def test_scheduler_definitions_are_explicit() -> None:
    jobs = {job.id: job for job in scheduler_job_definitions()}

    assert set(jobs) == {"premarket-report", "hourly-tracking", "closing-summary"}
    assert "08:00" in jobs["premarket-report"].description
    assert "09:00-15:30" in jobs["hourly-tracking"].description
    assert "Closing" in jobs["closing-summary"].description

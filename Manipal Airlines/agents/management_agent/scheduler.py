"""APScheduler entry point for autonomous airline operations."""
from apscheduler.schedulers.blocking import BlockingScheduler

from shared.config import (DAILY_FLIGHT_HOUR, DAILY_REPORT_HOUR,
                           SCHEDULE_TIMEZONE, WEEKLY_LOYALTY_DAY,
                           WEEKLY_LOYALTY_HOUR)
from .agent import run_management_agent


def create_scheduler():
    scheduler = BlockingScheduler(timezone=SCHEDULE_TIMEZONE)
    scheduler.add_job(run_management_agent, 'cron', args=['schedule'], hour=DAILY_FLIGHT_HOUR, id='daily-schedule')
    scheduler.add_job(run_management_agent, 'cron', args=['loyalty'], day_of_week=WEEKLY_LOYALTY_DAY, hour=WEEKLY_LOYALTY_HOUR, id='weekly-loyalty')
    scheduler.add_job(run_management_agent, 'cron', args=['report'], hour=DAILY_REPORT_HOUR, id='daily-report')
    return scheduler


if __name__ == '__main__':
    create_scheduler().start()
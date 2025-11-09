"""Celery application configuration"""
from celery import Celery
from celery.schedules import crontab
from config.settings import settings

# Create Celery app
celery_app = Celery(
    'debbie_ta',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        'app.tasks.deal_tasks',
        'app.tasks.email_tasks',
        'app.tasks.notification_tasks',
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Chicago',  # MSP timezone
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Configure periodic tasks
celery_app.conf.beat_schedule = {
    # Check for new deals every 12 hours
    'check-travel-deals': {
        'task': 'app.tasks.deal_tasks.check_travel_deals',
        'schedule': settings.DEAL_CHECK_INTERVAL * 3600,  # Convert hours to seconds
    },

    # Parse RSS feeds every 6 hours
    'parse-rss-feeds': {
        'task': 'app.tasks.deal_tasks.parse_rss_feeds',
        'schedule': settings.RSS_CHECK_INTERVAL * 3600,
    },

    # Scan Gmail for dispute emails every hour
    'scan-dispute-emails': {
        'task': 'app.tasks.email_tasks.scan_dispute_emails',
        'schedule': settings.EMAIL_SCAN_INTERVAL * 3600,
    },

    # Send daily summary at 8 AM CST
    'send-daily-summary': {
        'task': 'app.tasks.notification_tasks.send_daily_summary',
        'schedule': crontab(hour=8, minute=0),
    },

    # Clean up expired deals daily at 2 AM
    'cleanup-expired-deals': {
        'task': 'app.tasks.deal_tasks.cleanup_expired_deals',
        'schedule': crontab(hour=2, minute=0),
    },
}

"""Celery tasks for notifications"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models import Deal, Dispute
from app.services.notification_service import notification_service


@celery_app.task(name='app.tasks.notification_tasks.send_daily_summary')
def send_daily_summary():
    """Send daily summary of deals and disputes"""
    print("Sending daily summary...")

    db = SessionLocal()

    try:
        # Get deals from last 24 hours
        yesterday = datetime.now() - timedelta(days=1)
        recent_deals = db.query(Deal).filter(
            Deal.created_at >= yesterday,
            Deal.status == 'active'
        ).all()

        # Get active disputes
        active_disputes = db.query(Dispute).filter(
            Dispute.status.in_(['draft', 'submitted', 'in_review', 'waiting_response'])
        ).all()

        # Prepare deal data
        deals_data = [
            {
                'title': deal.title,
                'price': float(deal.deal_price) if deal.deal_price else None,
                'points': deal.points_required,
                'origin_airport': deal.origin_airport,
                'destination_region': deal.destination_region,
            }
            for deal in recent_deals
        ]

        # Prepare dispute data
        disputes_data = [
            {
                'client_name': dispute.client.full_name if dispute.client else 'Unknown',
                'provider_name': dispute.provider_name,
                'status': dispute.status,
                'dispute_type': dispute.dispute_type,
            }
            for dispute in active_disputes
        ]

        # Send summary
        success = notification_service.send_daily_summary(
            deals=deals_data,
            disputes=disputes_data
        )

        print(f"Daily summary sent: {len(deals_data)} deals, {len(disputes_data)} disputes")

        return {
            'success': success,
            'deals_count': len(deals_data),
            'disputes_count': len(disputes_data),
        }

    except Exception as e:
        print(f"Error sending daily summary: {e}")
        raise
    finally:
        db.close()


@celery_app.task(name='app.tasks.notification_tasks.send_test_alert')
def send_test_alert():
    """Send a test alert to verify notifications are working"""
    print("Sending test alert...")

    test_deal = {
        'title': 'Test Deal: MSP to Paris',
        'price': 450.00,
        'origin_airport': 'MSP',
        'destination_city': 'Paris',
        'destination_region': 'Europe',
        'airline': 'Delta',
        'travel_class': 'economy',
        'link': 'https://example.com',
    }

    result = notification_service.send_deal_alert(
        deal_data=test_deal,
        via_email=True,
        via_sms=True
    )

    return result

"""Celery tasks for deal monitoring and alerts"""
from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session

from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models import Deal, DealAlert, AlertThreshold
from app.services.rss_service import rss_service
from app.services.notification_service import notification_service
from config.settings import settings


@celery_app.task(name='app.tasks.deal_tasks.parse_rss_feeds')
def parse_rss_feeds():
    """Parse RSS feeds and save new deals to database"""
    print("Starting RSS feed parsing...")

    db = SessionLocal()

    try:
        # Fetch latest deals from RSS
        deals = rss_service.get_latest_msp_deals(limit=50)

        new_deals_count = 0
        updated_deals_count = 0

        for deal_data in deals:
            # Check if deal already exists (by URL)
            existing_deal = db.query(Deal).filter(
                Deal.source_url == deal_data.get('link')
            ).first()

            if existing_deal:
                # Update existing deal
                existing_deal.status = 'active'
                updated_deals_count += 1
            else:
                # Create new deal
                new_deal = Deal(
                    source=deal_data.get('source_name', 'RSS'),
                    source_url=deal_data.get('link'),
                    original_post_date=deal_data.get('published_date'),
                    deal_type=deal_data.get('deal_type', 'flight'),
                    title=deal_data.get('title', ''),
                    description=deal_data.get('description', ''),
                    origin_airport=deal_data.get('origin_airport'),
                    destination_airport=deal_data.get('destination_airport'),
                    destination_city=deal_data.get('destination_city'),
                    destination_region=deal_data.get('destination_region'),
                    deal_price=deal_data.get('price'),
                    points_required=deal_data.get('points'),
                    airline=deal_data.get('airline'),
                    travel_class=deal_data.get('travel_class'),
                    status='active',
                    expires_at=datetime.now() + timedelta(days=7),  # Default 7 day expiry
                )

                db.add(new_deal)
                new_deals_count += 1

        db.commit()

        print(f"RSS parsing complete: {new_deals_count} new deals, {updated_deals_count} updated")

        # Check if any new deals match alert thresholds
        check_deal_thresholds.delay()

        return {
            'new_deals': new_deals_count,
            'updated_deals': updated_deals_count,
        }

    except Exception as e:
        print(f"Error parsing RSS feeds: {e}")
        db.rollback()
        raise
    finally:
        db.close()


@celery_app.task(name='app.tasks.deal_tasks.check_travel_deals')
def check_travel_deals():
    """
    Check for travel deals matching user criteria
    This would integrate with flight search APIs like Amadeus
    """
    print("Checking for travel deals...")

    # This is a placeholder - would integrate with Amadeus or similar API
    # to search for actual flight deals

    db = SessionLocal()

    try:
        # Example: Search for flights from MSP to popular destinations
        # For now, we'll just trigger threshold checking on existing deals
        check_deal_thresholds.delay()

        return {'status': 'completed'}

    finally:
        db.close()


@celery_app.task(name='app.tasks.deal_tasks.check_deal_thresholds')
def check_deal_thresholds():
    """Check if any active deals meet alert threshold criteria"""
    print("Checking deal thresholds...")

    db = SessionLocal()

    try:
        # Get all active alert thresholds
        thresholds = db.query(AlertThreshold).filter(
            AlertThreshold.is_active == True
        ).all()

        # Get active deals from last 7 days
        recent_deals = db.query(Deal).filter(
            Deal.status == 'active',
            Deal.created_at >= datetime.now() - timedelta(days=7)
        ).all()

        alerts_sent = 0

        for threshold in thresholds:
            matching_deals = _find_matching_deals(threshold, recent_deals)

            for deal in matching_deals:
                # Check if we already sent an alert for this deal
                existing_alert = db.query(DealAlert).filter(
                    DealAlert.deal_id == deal.id,
                    DealAlert.threshold_name == threshold.name
                ).first()

                if not existing_alert:
                    # Send alert
                    send_deal_alert.delay(deal.id, threshold.id)
                    alerts_sent += 1

        print(f"Threshold check complete: {alerts_sent} alerts triggered")

        return {'alerts_sent': alerts_sent}

    except Exception as e:
        print(f"Error checking thresholds: {e}")
        raise
    finally:
        db.close()


def _find_matching_deals(threshold: AlertThreshold, deals: List[Deal]) -> List[Deal]:
    """Find deals that match a specific threshold"""
    matching = []

    for deal in deals:
        # Check origin airports
        if threshold.origin_airports and deal.origin_airport:
            if deal.origin_airport not in threshold.origin_airports:
                continue

        # Check destination regions
        if threshold.destination_regions and deal.destination_region:
            if deal.destination_region not in threshold.destination_regions:
                continue

        # Check airlines
        if threshold.airlines and deal.airline:
            if deal.airline not in threshold.airlines:
                continue

        # Check price thresholds
        if threshold.max_cash_price and deal.deal_price:
            if deal.deal_price > float(threshold.max_cash_price):
                continue

        if threshold.max_miles_price and deal.points_required:
            if deal.points_required > threshold.max_miles_price:
                continue

        # Check travel class
        if threshold.travel_classes and deal.travel_class:
            if deal.travel_class not in threshold.travel_classes:
                continue

        # If we got here, deal matches all criteria
        matching.append(deal)

    return matching


@celery_app.task(name='app.tasks.deal_tasks.send_deal_alert')
def send_deal_alert(deal_id: int, threshold_id: int):
    """Send alert for a specific deal"""
    db = SessionLocal()

    try:
        deal = db.query(Deal).filter(Deal.id == deal_id).first()
        threshold = db.query(AlertThreshold).filter(AlertThreshold.id == threshold_id).first()

        if not deal or not threshold:
            print(f"Deal or threshold not found: deal_id={deal_id}, threshold_id={threshold_id}")
            return

        # Prepare deal data
        deal_data = {
            'title': deal.title,
            'description': deal.description,
            'price': float(deal.deal_price) if deal.deal_price else None,
            'points': deal.points_required,
            'origin_airport': deal.origin_airport,
            'destination_airport': deal.destination_airport,
            'destination_city': deal.destination_city,
            'destination_region': deal.destination_region,
            'airline': deal.airline,
            'travel_class': deal.travel_class,
            'link': deal.source_url,
        }

        # Send notification
        result = notification_service.send_deal_alert(
            deal_data=deal_data,
            via_email=True,
            via_sms=True
        )

        # Create alert record
        alert = DealAlert(
            deal_id=deal.id,
            alert_type='threshold_met',
            threshold_name=threshold.name,
            deal_snapshot=deal_data,
            notification_method='both' if result['email_sent'] and result['sms_sent'] else 'email' if result['email_sent'] else 'sms',
            sent_to_email=settings.ALERT_EMAIL,
            sent_to_sms=settings.ALERT_SMS,
            status='sent' if (result['email_sent'] or result['sms_sent']) else 'failed',
            sent_at=datetime.now()
        )

        db.add(alert)
        db.commit()

        print(f"Alert sent for deal {deal.id}: {threshold.name}")

        return result

    except Exception as e:
        print(f"Error sending deal alert: {e}")
        db.rollback()
        raise
    finally:
        db.close()


@celery_app.task(name='app.tasks.deal_tasks.cleanup_expired_deals')
def cleanup_expired_deals():
    """Mark expired deals as inactive"""
    db = SessionLocal()

    try:
        expired_count = db.query(Deal).filter(
            Deal.status == 'active',
            Deal.expires_at < datetime.now()
        ).update({'status': 'expired'})

        db.commit()

        print(f"Marked {expired_count} deals as expired")

        return {'expired_count': expired_count}

    except Exception as e:
        print(f"Error cleaning up deals: {e}")
        db.rollback()
        raise
    finally:
        db.close()

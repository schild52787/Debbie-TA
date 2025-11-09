"""Celery tasks for email processing"""
from datetime import datetime
from sqlalchemy.orm import Session

from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models import Dispute, Client
from app.services.gmail_service import gmail_service
from app.services.legal_research_service import legal_research_service
from app.services.social_media_service import social_media_service


@celery_app.task(name='app.tasks.email_tasks.scan_dispute_emails')
def scan_dispute_emails():
    """Scan Gmail for emails related to travel disputes"""
    print("Scanning Gmail for dispute emails...")

    db = SessionLocal()

    try:
        # Search for dispute-related emails from last 7 days
        dispute_emails = gmail_service.search_dispute_emails(days_back=7)

        new_disputes = 0

        for email in dispute_emails:
            # Check if we've already processed this email
            existing = db.query(Dispute).filter(
                Dispute.source_email_id == email['id']
            ).first()

            if existing:
                continue

            # Extract dispute information
            dispute_info = gmail_service.extract_dispute_info(
                email['body'],
                email['subject']
            )

            # Try to match to existing client by email
            # Extract sender email
            from_email = email['from']
            # Simple email extraction (in production, use proper parsing)
            if '<' in from_email and '>' in from_email:
                sender_email = from_email.split('<')[1].split('>')[0]
            else:
                sender_email = from_email

            client = db.query(Client).filter(Client.email == sender_email).first()

            # Skip if no matching client (or create a placeholder)
            if not client:
                print(f"No client found for email: {sender_email}")
                continue

            # Determine provider from email sender
            provider_name = _extract_provider_from_email(email['from'])
            provider_type = _determine_provider_type(provider_name)

            # Create dispute record
            dispute = Dispute(
                client_id=client.id,
                dispute_type=dispute_info.get('issue_type', 'unknown'),
                provider_type=provider_type,
                provider_name=provider_name,
                incident_date=datetime.now(),  # Would parse from email
                booking_reference=dispute_info.get('confirmation_number'),
                flight_number=dispute_info.get('flight_number'),
                route=dispute_info.get('route'),
                issue_description=email['snippet'],
                status='draft',
                source_email_id=email['id'],
            )

            db.add(dispute)
            new_disputes += 1

        db.commit()

        print(f"Email scan complete: {new_disputes} new disputes created")

        # For each new dispute, trigger research
        if new_disputes > 0:
            # Trigger dispute research for new disputes
            pass

        return {'new_disputes': new_disputes}

    except Exception as e:
        print(f"Error scanning emails: {e}")
        db.rollback()
        raise
    finally:
        db.close()


@celery_app.task(name='app.tasks.email_tasks.research_dispute')
def research_dispute(dispute_id: int):
    """Research legal options and strategies for a dispute"""
    print(f"Researching dispute {dispute_id}...")

    db = SessionLocal()

    try:
        dispute = db.query(Dispute).filter(Dispute.id == dispute_id).first()

        if not dispute:
            print(f"Dispute {dispute_id} not found")
            return

        # Perform legal research
        legal_research = legal_research_service.research_dispute_legal_options(
            provider_type=dispute.provider_type,
            provider_name=dispute.provider_name,
            issue_type=dispute.dispute_type,
            route=dispute.route
        )

        # Store legal research results
        dispute.applicable_laws = legal_research.get('applicable_laws', [])
        dispute.airline_policy = legal_research.get('provider_policy', {})

        # Research social media strategies
        social_research = social_media_service.generate_dispute_research_report(
            provider=dispute.provider_name,
            issue_type=dispute.dispute_type
        )

        # Store successful strategies
        dispute.successful_strategies = social_research.get('successful_cases', [])

        # Update status
        dispute.status = 'researched'

        db.commit()

        print(f"Research complete for dispute {dispute_id}")

        return {
            'dispute_id': dispute_id,
            'legal_options_found': len(legal_research.get('applicable_laws', [])),
            'strategies_found': len(social_research.get('successful_cases', [])),
        }

    except Exception as e:
        print(f"Error researching dispute: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def _extract_provider_from_email(from_email: str) -> str:
    """Extract provider name from email address"""
    # Simple provider detection
    providers = {
        'delta': 'Delta',
        'aa.com': 'American Airlines',
        'united': 'United Airlines',
        'marriott': 'Marriott',
        'hyatt': 'Hyatt',
        'viking': 'Viking Cruises',
    }

    from_lower = from_email.lower()

    for key, name in providers.items():
        if key in from_lower:
            return name

    return 'Unknown Provider'


def _determine_provider_type(provider_name: str) -> str:
    """Determine if provider is airline, hotel, cruise, etc."""
    airlines = ['delta', 'american', 'united', 'lufthansa', 'air france']
    hotels = ['marriott', 'hyatt', 'hilton', 'ihg', 'melia']
    cruises = ['viking', 'royal caribbean', 'celebrity', 'carnival']

    provider_lower = provider_name.lower()

    if any(airline in provider_lower for airline in airlines):
        return 'airline'
    elif any(hotel in provider_lower for hotel in hotels):
        return 'hotel'
    elif any(cruise in provider_lower for cruise in cruises):
        return 'cruise'
    else:
        return 'unknown'

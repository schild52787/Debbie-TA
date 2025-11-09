"""Notification service for email and SMS alerts"""
from typing import List, Optional
from datetime import datetime
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from config.settings import settings
from app.services.gmail_service import gmail_service


class NotificationService:
    """Service for sending email and SMS notifications"""

    def __init__(self):
        # Initialize Twilio client
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            self.twilio_client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
        else:
            self.twilio_client = None

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """
        Send email notification

        Args:
            to: Recipient email address
            subject: Email subject
            body: Plain text email body
            html_body: Optional HTML email body

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Use Gmail service to send email
            success = gmail_service.send_email(to, subject, body)
            return success

        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    def send_sms(self, to: str, message: str) -> bool:
        """
        Send SMS notification via Twilio

        Args:
            to: Recipient phone number (E.164 format, e.g., +15551234567)
            message: SMS message text (max 1600 characters)

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.twilio_client:
            print("Twilio client not configured")
            return False

        try:
            # Ensure phone number is in E.164 format
            if not to.startswith('+'):
                to = f'+1{to}'

            message = self.twilio_client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=to
            )

            print(f"SMS sent successfully. SID: {message.sid}")
            return True

        except TwilioRestException as e:
            print(f"Twilio error: {e}")
            return False
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return False

    def send_deal_alert(
        self,
        deal_data: dict,
        via_email: bool = True,
        via_sms: bool = True
    ) -> dict:
        """
        Send deal alert via email and/or SMS

        Args:
            deal_data: Dictionary containing deal information
            via_email: Whether to send email notification
            via_sms: Whether to send SMS notification

        Returns:
            Dictionary with send results
        """
        results = {
            'email_sent': False,
            'sms_sent': False,
            'errors': []
        }

        # Prepare email content
        email_subject = f"Travel Deal Alert: {deal_data.get('title', 'New Deal')}"
        email_body = self._format_deal_email(deal_data)

        # Prepare SMS content (shorter)
        sms_body = self._format_deal_sms(deal_data)

        # Send email
        if via_email:
            try:
                results['email_sent'] = self.send_email(
                    to=settings.ALERT_EMAIL,
                    subject=email_subject,
                    body=email_body
                )
                if not results['email_sent']:
                    results['errors'].append("Failed to send email")
            except Exception as e:
                results['errors'].append(f"Email error: {e}")

        # Send SMS
        if via_sms:
            try:
                results['sms_sent'] = self.send_sms(
                    to=settings.ALERT_SMS,
                    message=sms_body
                )
                if not results['sms_sent']:
                    results['errors'].append("Failed to send SMS")
            except Exception as e:
                results['errors'].append(f"SMS error: {e}")

        return results

    def send_dispute_notification(
        self,
        dispute_data: dict,
        notification_type: str = "created"
    ) -> bool:
        """
        Send notification about dispute status

        Args:
            dispute_data: Dictionary containing dispute information
            notification_type: Type of notification (created, updated, resolved)

        Returns:
            True if sent successfully
        """
        subject = f"Dispute {notification_type.title()}: {dispute_data.get('provider_name', 'Unknown')}"
        body = self._format_dispute_email(dispute_data, notification_type)

        return self.send_email(
            to=settings.ALERT_EMAIL,
            subject=subject,
            body=body
        )

    def _format_deal_email(self, deal_data: dict) -> str:
        """Format deal data as email body"""
        title = deal_data.get('title', 'Untitled Deal')
        description = deal_data.get('description', '')
        price = deal_data.get('price')
        points = deal_data.get('points')
        origin = deal_data.get('origin_airport', 'MSP')
        destination = deal_data.get('destination_airport') or deal_data.get('destination_city', '')
        region = deal_data.get('destination_region', '')
        airline = deal_data.get('airline', '')
        travel_class = deal_data.get('travel_class', '')
        link = deal_data.get('link', '')

        email = f"""
Travel Deal Alert!
==================

{title}

Route: {origin} → {destination} ({region})
Airline: {airline}
Class: {travel_class.title() if travel_class else 'N/A'}

"""

        if price:
            email += f"Price: ${price:,.2f}\n"
        if points:
            email += f"Miles/Points: {points:,}\n"

        email += f"""

Description:
{description}

More details: {link}

---
This is an automated alert from Debbie's Travel Agent Assistant
"""

        return email

    def _format_deal_sms(self, deal_data: dict) -> str:
        """Format deal data as SMS (shorter)"""
        title = deal_data.get('title', 'New Deal')[:50]
        price = deal_data.get('price')
        points = deal_data.get('points')
        origin = deal_data.get('origin_airport', 'MSP')
        destination = deal_data.get('destination_airport') or deal_data.get('destination_city', '')

        sms = f"Travel Deal: {origin}→{destination}"

        if price:
            sms += f" ${price:,.0f}"
        elif points:
            sms += f" {points:,} pts"

        sms += f". {title[:80]}"

        return sms[:160]  # SMS length limit

    def _format_dispute_email(self, dispute_data: dict, notification_type: str) -> str:
        """Format dispute data as email body"""
        provider = dispute_data.get('provider_name', 'Unknown')
        dispute_type = dispute_data.get('dispute_type', 'Unknown')
        client_name = dispute_data.get('client_name', 'Unknown Client')
        issue_desc = dispute_data.get('issue_description', '')
        status = dispute_data.get('status', '')

        email = f"""
Dispute {notification_type.title()}
{'=' * 40}

Client: {client_name}
Provider: {provider}
Type: {dispute_type.replace('_', ' ').title()}
Status: {status.replace('_', ' ').title()}

Issue Description:
{issue_desc}

---
This is an automated notification from Debbie's Travel Agent Assistant
"""

        return email

    def send_daily_summary(self, deals: List[dict], disputes: List[dict]) -> bool:
        """
        Send daily summary of deals and disputes

        Args:
            deals: List of deals from today
            disputes: List of active disputes

        Returns:
            True if sent successfully
        """
        subject = f"Daily Summary - {datetime.now().strftime('%Y-%m-%d')}"

        body = f"""
Daily Travel Summary
====================

New Deals: {len(deals)}
Active Disputes: {len(disputes)}

"""

        if deals:
            body += "\nTop Deals:\n" + "-" * 40 + "\n"
            for deal in deals[:5]:
                title = deal.get('title', 'Untitled')
                price = deal.get('price')
                body += f"• {title}"
                if price:
                    body += f" - ${price:,.2f}"
                body += "\n"

        if disputes:
            body += "\n\nActive Disputes:\n" + "-" * 40 + "\n"
            for dispute in disputes:
                body += f"• {dispute.get('client_name')} - {dispute.get('provider_name')} ({dispute.get('status')})\n"

        body += "\n---\nDebbie's Travel Agent Assistant"

        return self.send_email(
            to=settings.ALERT_EMAIL,
            subject=subject,
            body=body
        )


# Create singleton instance
notification_service = NotificationService()

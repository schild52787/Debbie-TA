"""Gmail API integration for email parsing"""
import base64
import os
import re
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config.settings import settings

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.send']


class GmailService:
    """Service for interacting with Gmail API"""

    def __init__(self):
        self.service = None
        self.creds = None

    def authenticate(self):
        """Authenticate with Gmail API"""
        creds = None

        # Check if token file exists
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                # For production, use env variables
                if settings.GMAIL_CLIENT_ID and settings.GMAIL_CLIENT_SECRET:
                    # This would need a proper OAuth flow
                    # For now, we'll use the token file approach
                    pass

            # Save credentials for next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        self.creds = creds
        self.service = build('gmail', 'v1', credentials=creds)

    def get_messages(
        self,
        query: str = "",
        max_results: int = 10,
        label_ids: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Get messages from Gmail

        Args:
            query: Gmail search query (e.g., "from:delta.com subject:cancellation")
            max_results: Maximum number of messages to return
            label_ids: Filter by label IDs

        Returns:
            List of message dictionaries
        """
        if not self.service:
            self.authenticate()

        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results,
                labelIds=label_ids
            ).execute()

            messages = results.get('messages', [])

            # Fetch full message details
            detailed_messages = []
            for msg in messages:
                detailed = self.get_message(msg['id'])
                if detailed:
                    detailed_messages.append(detailed)

            return detailed_messages

        except HttpError as error:
            print(f'An error occurred: {error}')
            return []

    def get_message(self, message_id: str) -> Optional[Dict]:
        """Get a specific message by ID"""
        if not self.service:
            self.authenticate()

        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            return self._parse_message(message)

        except HttpError as error:
            print(f'An error occurred: {error}')
            return None

    def _parse_message(self, message: Dict) -> Dict:
        """Parse Gmail message into useful format"""
        headers = message['payload'].get('headers', [])

        # Extract key headers
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
        from_email = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
        to_email = next((h['value'] for h in headers if h['name'].lower() == 'to'), '')
        date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')

        # Get email body
        body = self._get_message_body(message['payload'])

        return {
            'id': message['id'],
            'thread_id': message['threadId'],
            'subject': subject,
            'from': from_email,
            'to': to_email,
            'date': date,
            'body': body,
            'snippet': message.get('snippet', ''),
            'label_ids': message.get('labelIds', []),
        }

    def _get_message_body(self, payload: Dict) -> str:
        """Extract message body from payload"""
        body = ""

        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
                elif part['mimeType'] == 'text/html' and not body:
                    data = part['body'].get('data', '')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
        else:
            data = payload['body'].get('data', '')
            if data:
                body = base64.urlsafe_b64decode(data).decode('utf-8')

        return body

    def search_dispute_emails(self, days_back: int = 30) -> List[Dict]:
        """
        Search for emails related to travel disputes

        Args:
            days_back: How many days back to search

        Returns:
            List of relevant email messages
        """
        # Keywords that indicate dispute-related emails
        keywords = [
            "cancellation", "cancelled", "delay", "delayed",
            "refund", "compensation", "lost luggage", "baggage",
            "overbook", "denied boarding", "complaint"
        ]

        # Airlines and travel providers
        providers = [
            "delta.com", "aa.com", "united.com", "marriott.com",
            "hyatt.com", "viking.com"
        ]

        # Build query
        after_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')

        queries = []
        for provider in providers:
            for keyword in keywords:
                queries.append(f"from:{provider} {keyword} after:{after_date}")

        all_messages = []
        for query in queries[:5]:  # Limit to avoid API quota issues
            messages = self.get_messages(query=query, max_results=5)
            all_messages.extend(messages)

        # Remove duplicates by message ID
        unique_messages = {msg['id']: msg for msg in all_messages}

        return list(unique_messages.values())

    def extract_dispute_info(self, email_body: str, subject: str) -> Dict:
        """
        Extract dispute-related information from email

        Args:
            email_body: Email body text
            subject: Email subject

        Returns:
            Dictionary with extracted information
        """
        info = {
            'flight_number': None,
            'confirmation_number': None,
            'date': None,
            'route': None,
            'issue_type': None,
        }

        # Extract flight number (e.g., DL1234, AA456)
        flight_match = re.search(r'\b([A-Z]{2}\s?\d{1,4})\b', email_body + subject)
        if flight_match:
            info['flight_number'] = flight_match.group(1).replace(' ', '')

        # Extract confirmation number (6-7 alphanumeric)
        conf_match = re.search(r'\b([A-Z0-9]{6,7})\b', email_body)
        if conf_match:
            info['confirmation_number'] = conf_match.group(1)

        # Extract route (e.g., MSP-CDG, MSP to Paris)
        route_match = re.search(
            r'\b([A-Z]{3})\s*(?:-|to)\s*([A-Z]{3})\b',
            email_body + subject
        )
        if route_match:
            info['route'] = f"{route_match.group(1)}-{route_match.group(2)}"

        # Determine issue type
        text_lower = (email_body + subject).lower()
        if 'cancel' in text_lower:
            info['issue_type'] = 'cancellation'
        elif 'delay' in text_lower:
            info['issue_type'] = 'delay'
        elif 'luggage' in text_lower or 'baggage' in text_lower:
            info['issue_type'] = 'lost_luggage'
        elif 'refund' in text_lower:
            info['issue_type'] = 'refund'

        return info

    def send_email(self, to: str, subject: str, body: str) -> bool:
        """
        Send an email via Gmail

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.service:
            self.authenticate()

        try:
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject

            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

            self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()

            return True

        except HttpError as error:
            print(f'An error occurred: {error}')
            return False


# Create singleton instance
gmail_service = GmailService()

"""Gmail service"""
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from typing import List, Optional
from datetime import datetime
from app.models.email import EmailAccount, EmailItem
from app.models.user import User
from app.services.email_service import EmailService
from app.utils.encryption import decrypt_token, encrypt_token
from app.config import settings
import structlog

logger = structlog.get_logger()


class GmailService(EmailService):
    """Gmail API service"""
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def _get_credentials(self, account: EmailAccount) -> Optional[Credentials]:
        """Get OAuth2 credentials from encrypted tokens"""
        try:
            access_token = decrypt_token(account.access_token_encrypted)
            refresh_token = decrypt_token(account.refresh_token_encrypted) if account.refresh_token_encrypted else None
            
            creds = Credentials(
                token=access_token,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.GMAIL_CLIENT_ID,
                client_secret=settings.GMAIL_CLIENT_SECRET
            )
            
            # Refresh if expired
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                # Update stored tokens
                account.access_token_encrypted = encrypt_token(creds.token)
                if creds.refresh_token:
                    account.refresh_token_encrypted = encrypt_token(creds.refresh_token)
            
            return creds
        except Exception as e:
            logger.error("Gmail credentials error", error=str(e))
            return None
    
    async def sync_emails(
        self,
        account: EmailAccount,
        user: User
    ) -> List[EmailItem]:
        """Sync emails from Gmail"""
        try:
            creds = self._get_credentials(account)
            if not creds:
                return []
            
            service = build('gmail', 'v1', credentials=creds)
            
            # Get messages - fetch recent emails (last 50)
            # Changed from only unread/important to recent emails
            results = service.users().messages().list(
                userId='me',
                maxResults=50
            ).execute()
            
            messages = results.get('messages', [])
            email_items = []
            
            for msg in messages:
                try:
                    message = service.users().messages().get(
                        userId='me',
                        id=msg['id']
                    ).execute()
                    
                    # Extract email data
                    headers = message['payload'].get('headers', [])
                    subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
                    sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
                    date_str = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                    
                    # Parse body
                    body_text = self._extract_body(message['payload'])
                    
                    # Parse date
                    from email.utils import parsedate_to_datetime
                    received_at = parsedate_to_datetime(date_str) if date_str else datetime.now()
                    
                    email_item = EmailItem(
                        email_account_id=account.id,
                        provider_message_id=msg['id'],
                        subject=subject,
                        sender_email=self._extract_email(sender),
                        sender_name=self._extract_name(sender),
                        body_text=body_text,
                        received_at=received_at,
                        is_read='UNREAD' not in message['labelIds'],
                        is_important='IMPORTANT' in message['labelIds']
                    )
                    
                    email_items.append(email_item)
                except Exception as e:
                    logger.warning("Error processing Gmail message", error=str(e))
                    continue
            
            return email_items
        except Exception as e:
            logger.error("Gmail sync error", error=str(e))
            return []
    
    def _extract_body(self, payload: dict) -> str:
        """Extract text body from message payload"""
        body = ""
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        import base64
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
        elif payload['mimeType'] == 'text/plain':
            if 'body' in payload and 'data' in payload['body']:
                import base64
                body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        
        return body
    
    def _extract_email(self, sender: str) -> str:
        """Extract email address from sender string"""
        import re
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', sender)
        return match.group(0) if match else sender
    
    def _extract_name(self, sender: str) -> str:
        """Extract name from sender string"""
        import re
        match = re.match(r'(.+?)\s*<', sender)
        return match.group(1).strip('"') if match else ""
    
    async def refresh_token(self, account: EmailAccount) -> bool:
        """Refresh Gmail access token"""
        try:
            creds = self._get_credentials(account)
            return creds is not None and not creds.expired
        except Exception:
            return False


# Global Gmail service instance
gmail_service = GmailService()

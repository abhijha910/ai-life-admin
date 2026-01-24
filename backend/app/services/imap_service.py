"""IMAP service for generic email providers"""
from imapclient import IMAPClient
from typing import List, Optional
from datetime import datetime
from email import message_from_bytes
from email.utils import parsedate_to_datetime
from app.models.email import EmailAccount, EmailItem
from app.models.user import User
from app.services.email_service import EmailService
from app.utils.encryption import decrypt_token
import structlog

logger = structlog.get_logger()


class IMAPService(EmailService):
    """IMAP service for generic email providers"""
    
    async def sync_emails(
        self,
        account: EmailAccount,
        user: User
    ) -> List[EmailItem]:
        """Sync emails via IMAP"""
        try:
            # Decrypt password (stored as access_token for IMAP)
            password = decrypt_token(account.access_token_encrypted)
            
            # Parse email address to get server
            email_parts = account.email_address.split('@')
            domain = email_parts[1] if len(email_parts) > 1 else ''
            
            # Common IMAP servers (in production, use a lookup service)
            imap_servers = {
                'gmail.com': 'imap.gmail.com',
                'outlook.com': 'outlook.office365.com',
                'hotmail.com': 'outlook.office365.com',
                'yahoo.com': 'imap.mail.yahoo.com',
            }
            
            server = imap_servers.get(domain.lower(), f'imap.{domain}')
            
            with IMAPClient(server, ssl=True) as client:
                client.login(account.email_address, password)
                client.select_folder('INBOX')
                
                # Search for unread or important messages
                messages = client.search(['UNSEEN', 'OR', 'FLAGGED'])
                
                email_items = []
                for msg_id, msg_data in client.fetch(messages[:50], ['RFC822']).items():
                    try:
                        email_msg = message_from_bytes(msg_data[b'RFC822'])
                        
                        subject = email_msg.get('Subject', '')
                        sender = email_msg.get('From', '')
                        date_str = email_msg.get('Date', '')
                        
                        # Parse body
                        body_text = self._extract_body(email_msg)
                        
                        # Parse date
                        received_at = parsedate_to_datetime(date_str) if date_str else datetime.now()
                        
                        email_item = EmailItem(
                            email_account_id=account.id,
                            provider_message_id=str(msg_id),
                            subject=subject,
                            sender_email=self._extract_email(sender),
                            sender_name=self._extract_name(sender),
                            body_text=body_text,
                            received_at=received_at,
                            is_read=False,  # We're only fetching unread
                            is_important='\\Flagged' in email_msg.get('Flags', [])
                        )
                        
                        email_items.append(email_item)
                    except Exception as e:
                        logger.warning("Error processing IMAP message", error=str(e))
                        continue
                
                return email_items
        except Exception as e:
            logger.error("IMAP sync error", error=str(e))
            return []
    
    def _extract_body(self, email_msg) -> str:
        """Extract text body from email message"""
        body = ""
        if email_msg.is_multipart():
            for part in email_msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    break
        else:
            if email_msg.get_content_type() == "text/plain":
                body = email_msg.get_payload(decode=True).decode('utf-8', errors='ignore')
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
        """IMAP doesn't use tokens, so this always returns True"""
        return True


# Global IMAP service instance
imap_service = IMAPService()

"""Outlook/Microsoft Graph service"""
from msal import ConfidentialClientApplication
from typing import List, Optional
from datetime import datetime
from app.models.email import EmailAccount, EmailItem
from app.models.user import User
from app.services.email_service import EmailService
from app.utils.encryption import decrypt_token, encrypt_token
from app.config import settings
import httpx
import structlog

logger = structlog.get_logger()


class OutlookService(EmailService):
    """Microsoft Graph API service for Outlook"""
    
    AUTHORITY = "https://login.microsoftonline.com/common"
    SCOPE = ["https://graph.microsoft.com/Mail.Read"]
    
    def _get_access_token(self, account: EmailAccount) -> Optional[str]:
        """Get access token from encrypted storage"""
        try:
            return decrypt_token(account.access_token_encrypted)
        except Exception:
            return None
    
    async def sync_emails(
        self,
        account: EmailAccount,
        user: User
    ) -> List[EmailItem]:
        """Sync emails from Outlook"""
        try:
            access_token = self._get_access_token(account)
            if not access_token:
                return []
            
            async with httpx.AsyncClient() as client:
                # Get messages
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                
                response = await client.get(
                    "https://graph.microsoft.com/v1.0/me/messages",
                    headers=headers,
                    params={
                        "$top": 50,
                        "$filter": "isRead eq false or flag/flagStatus eq 'flagged'",
                        "$orderby": "receivedDateTime desc"
                    }
                )
                
                if response.status_code != 200:
                    logger.warning("Outlook API error", status=response.status_code)
                    return []
                
                data = response.json()
                messages = data.get('value', [])
                email_items = []
                
                for msg in messages:
                    try:
                        email_item = EmailItem(
                            email_account_id=account.id,
                            provider_message_id=msg['id'],
                            subject=msg.get('subject', ''),
                            sender_email=msg.get('from', {}).get('emailAddress', {}).get('address', ''),
                            sender_name=msg.get('from', {}).get('emailAddress', {}).get('name', ''),
                            body_text=msg.get('bodyPreview', ''),
                            body_html=msg.get('body', {}).get('content', ''),
                            received_at=datetime.fromisoformat(
                                msg['receivedDateTime'].replace('Z', '+00:00')
                            ),
                            is_read=msg.get('isRead', False),
                            is_important=msg.get('flag', {}).get('flagStatus') == 'flagged'
                        )
                        email_items.append(email_item)
                    except Exception as e:
                        logger.warning("Error processing Outlook message", error=str(e))
                        continue
                
                return email_items
        except Exception as e:
            logger.error("Outlook sync error", error=str(e))
            return []
    
    async def refresh_token(self, account: EmailAccount) -> bool:
        """Refresh Outlook access token"""
        try:
            app = ConfidentialClientApplication(
                settings.OUTLOOK_CLIENT_ID,
                authority=self.AUTHORITY,
                client_credential=settings.OUTLOOK_CLIENT_SECRET
            )
            
            # Try to get token from cache or refresh
            refresh_token = decrypt_token(account.refresh_token_encrypted) if account.refresh_token_encrypted else None
            if refresh_token:
                result = app.acquire_token_by_refresh_token(refresh_token, scopes=self.SCOPE)
                if "access_token" in result:
                    account.access_token_encrypted = encrypt_token(result["access_token"])
                    if "refresh_token" in result:
                        account.refresh_token_encrypted = encrypt_token(result["refresh_token"])
                    return True
            
            return False
        except Exception as e:
            logger.error("Outlook token refresh error", error=str(e))
            return False


# Global Outlook service instance
outlook_service = OutlookService()

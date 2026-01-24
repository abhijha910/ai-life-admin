"""Email service base class"""
from typing import List, Optional
from app.models.email import EmailAccount, EmailItem
from app.models.user import User

class EmailService:
    """Base email service interface"""
    
    async def sync_emails(
        self,
        account: EmailAccount,
        user: User
    ) -> List[EmailItem]:
        """Sync emails from provider"""
        raise NotImplementedError
    
    async def refresh_token(self, account: EmailAccount) -> bool:
        """Refresh access token"""
        raise NotImplementedError

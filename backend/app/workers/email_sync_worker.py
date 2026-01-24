"""Email sync worker"""
from app.workers.celery_app import celery_app
from app.database import SessionLocal
from app.models.email import EmailAccount
from app.models.user import User
from app.services.gmail_service import gmail_service
from app.services.outlook_service import outlook_service
from app.services.imap_service import imap_service
from sqlalchemy import select
import uuid
from datetime import datetime

@celery_app.task(name="sync_email_account")
def sync_email_account(account_id: str):
    """Sync emails for a specific account"""
    db = SessionLocal()
    try:
        result = db.execute(
            select(EmailAccount).where(EmailAccount.id == uuid.UUID(account_id))
        )
        account = result.scalar_one_or_none()
        
        if not account or not account.sync_enabled:
            return {"status": "skipped", "reason": "Account not found or disabled"}
        
        # Get user
        result = db.execute(
            select(User).where(User.id == account.user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return {"status": "error", "reason": "User not found"}
        
        # Get appropriate service
        if account.provider == "gmail":
            service = gmail_service
        elif account.provider == "outlook":
            service = outlook_service
        else:
            service = imap_service
        
        # Sync emails (would need async wrapper in production)
        # For now, this is a placeholder
        account.last_sync_at = datetime.now()
        db.commit()
        
        return {"status": "success", "account_id": account_id}
    except Exception as e:
        return {"status": "error", "error": str(e)}
    finally:
        db.close()

@celery_app.task(name="sync_all_emails")
def sync_all_emails():
    """Sync all enabled email accounts"""
    db = SessionLocal()
    try:
        result = db.execute(
            select(EmailAccount).where(EmailAccount.sync_enabled == True)
        )
        accounts = result.scalars().all()
        
        for account in accounts:
            sync_email_account.delay(str(account.id))
        
        return {"status": "success", "accounts_synced": len(accounts)}
    finally:
        db.close()

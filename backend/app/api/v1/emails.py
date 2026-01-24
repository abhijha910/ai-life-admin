"""Email routes"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.email import EmailAccount, EmailItem
from app.schemas.email import EmailAccountCreate, EmailAccountResponse, EmailItemResponse, EmailListResponse, EmailSyncRequest
from app.services.gmail_service import gmail_service
from app.services.outlook_service import outlook_service
from app.services.imap_service import imap_service
from app.utils.encryption import encrypt_token
from app.ai_engine.task_generator import task_generator
from app.ai_engine.priority_scorer import priority_scorer
from app.ai_engine.nlp_extractor import nlp_extractor
import uuid
from datetime import datetime

router = APIRouter()


@router.post("/connect", response_model=EmailAccountResponse, status_code=status.HTTP_201_CREATED)
async def connect_email_account(
    account_data: EmailAccountCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Connect an email account"""
    # Encrypt tokens
    access_token_encrypted = encrypt_token(account_data.access_token) if account_data.access_token else None
    refresh_token_encrypted = encrypt_token(account_data.refresh_token) if account_data.refresh_token else None
    
    account = EmailAccount(
        id=uuid.uuid4(),
        user_id=current_user.id,
        provider=account_data.provider,
        email_address=account_data.email_address,
        access_token_encrypted=access_token_encrypted,
        refresh_token_encrypted=refresh_token_encrypted,
        sync_enabled=True
    )
    
    db.add(account)
    await db.commit()
    await db.refresh(account)
    
    return account


@router.get("/accounts", response_model=List[EmailAccountResponse])
async def list_email_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List connected email accounts"""
    result = await db.execute(
        select(EmailAccount).where(EmailAccount.user_id == current_user.id)
    )
    accounts = result.scalars().all()
    return accounts


@router.post("/sync")
async def sync_emails(
    sync_request: EmailSyncRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Sync emails from connected accounts"""
    if sync_request.account_id:
        result = await db.execute(
            select(EmailAccount).where(
                EmailAccount.id == uuid.UUID(sync_request.account_id),
                EmailAccount.user_id == current_user.id
            )
        )
        accounts = [result.scalar_one_or_none()]
    else:
        result = await db.execute(
            select(EmailAccount).where(
                EmailAccount.user_id == current_user.id,
                EmailAccount.sync_enabled == True
            )
        )
        accounts = result.scalars().all()
    
    synced_count = 0
    for account in accounts:
        if not account:
            continue
        
        # Get appropriate service
        if account.provider == "gmail":
            service = gmail_service
        elif account.provider == "outlook":
            service = outlook_service
        else:
            service = imap_service
        
        # Sync emails
        email_items = await service.sync_emails(account, current_user)
        
        # Process and store emails
        for email_item in email_items:
            # Check if email already exists
            existing = await db.execute(
                select(EmailItem).where(
                    EmailItem.provider_message_id == email_item.provider_message_id
                )
            )
            if existing.scalar_one_or_none():
                continue
            
            # AI processing
            if email_item.body_text:
                # Extract dates
                dates = nlp_extractor.extract_dates(email_item.body_text)
                email_item.ai_extracted_dates = {"dates": dates}
                
                # Calculate priority
                email_item.ai_priority_score = priority_scorer.calculate_email_priority(
                    email_item.body_text,
                    email_item.sender_email,
                    email_item.subject,
                    email_item.received_at
                )
                
                # Extract tasks
                tasks = await task_generator.extract_tasks(
                    email_item.body_text,
                    "email"
                )
                email_item.ai_extracted_tasks = {"tasks": tasks}
            
            db.add(email_item)
            synced_count += 1
        
        # Update last sync time
        account.last_sync_at = datetime.now()
        await db.commit()
    
    return {"synced_count": synced_count, "message": "Sync completed"}


@router.get("", response_model=EmailListResponse)
async def list_emails(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List emails"""
    offset = (page - 1) * page_size
    
    # Get user's email accounts
    accounts_result = await db.execute(
        select(EmailAccount.id).where(EmailAccount.user_id == current_user.id)
    )
    account_ids = [acc.id for acc in accounts_result.scalars().all()]
    
    if not account_ids:
        return EmailListResponse(emails=[], total=0, page=page, page_size=page_size)
    
    # Get emails
    result = await db.execute(
        select(EmailItem)
        .where(EmailItem.email_account_id.in_(account_ids))
        .order_by(EmailItem.received_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    emails = result.scalars().all()
    
    # Get total count
    count_result = await db.execute(
        select(EmailItem).where(EmailItem.email_account_id.in_(account_ids))
    )
    total = len(count_result.scalars().all())
    
    return EmailListResponse(
        emails=emails,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{email_id}", response_model=EmailItemResponse)
async def get_email(
    email_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get email details"""
    # Verify user owns the email account
    result = await db.execute(
        select(EmailItem)
        .join(EmailAccount)
        .where(
            EmailItem.id == uuid.UUID(email_id),
            EmailAccount.user_id == current_user.id
        )
    )
    email = result.scalar_one_or_none()
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    return email

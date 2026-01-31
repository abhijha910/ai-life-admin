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
import structlog

logger = structlog.get_logger()

router = APIRouter()


@router.get("/oauth/gmail/authorize")
async def gmail_oauth_authorize(
    current_user: User = Depends(get_current_user)
):
    """Get Gmail OAuth authorization URL"""
    from app.config import settings
    import secrets
    
    if not settings.GMAIL_CLIENT_ID or not settings.GMAIL_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Gmail OAuth not configured. Please set GMAIL_CLIENT_ID and GMAIL_CLIENT_SECRET in backend .env file or config.py"
        )
    
    # Generate state token for security
    state = secrets.token_urlsafe(32)
    
    # Store state in session/cache (simplified - in production use Redis)
    # Include provider and user_id in state: state:provider:user_id
    state_with_provider_user = f"{state}:gmail:{str(current_user.id)}"
    
    # Gmail OAuth URL
    # IMPORTANT: redirect_uri must match exactly what's configured in Google Cloud Console
    redirect_uri = settings.GMAIL_REDIRECT_URI or f"{settings.FRONTEND_URL}/emails/oauth/callback"
    scope = "https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/userinfo.email"
    
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.GMAIL_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope={scope}&"
        f"access_type=offline&"
        f"prompt=consent&"
        f"state={state_with_provider_user}"
    )
    
    return {"auth_url": auth_url, "state": state_with_provider_user}


@router.get("/oauth/outlook/authorize")
async def outlook_oauth_authorize(
    current_user: User = Depends(get_current_user)
):
    """Get Outlook OAuth authorization URL"""
    from app.config import settings
    import secrets
    
    if not settings.OUTLOOK_CLIENT_ID or not settings.OUTLOOK_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Outlook OAuth not configured. Please set OUTLOOK_CLIENT_ID and OUTLOOK_CLIENT_SECRET in backend .env file or config.py"
        )
    
    state = secrets.token_urlsafe(32)
    # Include provider and user_id in state: state:provider:user_id
    state_with_provider_user = f"{state}:outlook:{str(current_user.id)}"
    
    redirect_uri = settings.OUTLOOK_REDIRECT_URI or f"{settings.FRONTEND_URL}/emails/oauth/callback"
    scope = "https://graph.microsoft.com/Mail.Read offline_access"
    
    auth_url = (
        f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?"
        f"client_id={settings.OUTLOOK_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope={scope}&"
        f"state={state_with_provider_user}"
    )
    
    return {"auth_url": auth_url, "state": state_with_provider_user}


@router.get("/oauth/callback", response_model=EmailAccountResponse)
async def oauth_callback(
    code: str = Query(...),
    state: str = Query(...),
    provider: str = Query(None),  # Optional - will be extracted from state
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Handle OAuth callback and connect email account"""
    from app.config import settings
    import httpx
    
    # Verify state - format: state_token:provider:user_id
    if state.count(":") < 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state")
    
    parts = state.split(":", 2)
    if len(parts) < 3:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state format")
    
    state_token, state_provider, user_id = parts[0], parts[1], parts[2]
    
    # Use provider from state if not provided in query, otherwise verify they match
    if not provider:
        provider = state_provider
    elif provider != state_provider:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provider mismatch in state")
    
    if user_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="State mismatch")
    
    redirect_uri = (
        settings.GMAIL_REDIRECT_URI if provider == "gmail" 
        else settings.OUTLOOK_REDIRECT_URI
    ) or f"{settings.FRONTEND_URL}/emails/oauth/callback"
    
    # Check if account already exists (in case of duplicate callback)
    # We'll check this after getting the email address
    email_address = None
    
    if provider == "gmail":
        if not settings.GMAIL_CLIENT_ID or not settings.GMAIL_CLIENT_SECRET:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gmail OAuth not configured"
            )
        
        # Exchange code for tokens
        # IMPORTANT: redirect_uri must match exactly what was used in authorization URL
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.GMAIL_CLIENT_ID,
                    "client_secret": settings.GMAIL_CLIENT_SECRET,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            if response.status_code != 200:
                error_detail = response.text
                error_code = None
                try:
                    error_json = response.json()
                    error_code = error_json.get("error")
                    error_detail = error_json.get("error_description", error_json.get("error", error_detail))
                except:
                    pass
                
                # If code is invalid_grant (expired/already used), check if account already exists
                # This handles the case where callback is called twice
                if error_code == "invalid_grant":
                    # Try to get email from state or check existing accounts
                    # Since we can't get email without token, check all user's Gmail accounts
                    existing_accounts_result = await db.execute(
                        select(EmailAccount).where(
                            EmailAccount.user_id == current_user.id,
                            EmailAccount.provider == "gmail"
                        ).order_by(EmailAccount.created_at.desc())
                    )
                    existing_account = existing_accounts_result.scalars().first()
                    
                    if existing_account:
                        # Account already exists, return it instead of failing
                        await db.refresh(existing_account)
                        return EmailAccountResponse(
                            id=str(existing_account.id),
                            provider=existing_account.provider,
                            email_address=existing_account.email_address,
                            last_sync_at=existing_account.last_sync_at,
                            sync_enabled=existing_account.sync_enabled,
                            created_at=existing_account.created_at,
                        )
                    
                    # No existing account, code was used/expired - need fresh authorization
                    detail_msg = (
                        f"OAuth code expired or already used. Error: {error_detail}. "
                        f"This usually happens if you clicked 'Connect' multiple times. "
                        f"Please try connecting again with a fresh authorization."
                    )
                else:
                    detail_msg = (
                        f"Failed to exchange token: {error_detail}. "
                        f"Redirect URI used: {redirect_uri}. "
                        f"Make sure this EXACT URL is in Google Cloud Console → Credentials → Authorized redirect URIs"
                    )
                
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=detail_msg
                )
            token_data = response.json()
        
        # Get user email
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {token_data['access_token']}"},
            )
            if user_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to get user info: {user_response.text}"
                )
            user_info = user_response.json()
            email_address = user_info.get("email")
            
            if not email_address:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email address not found in user info. Make sure you granted email access."
                )
        
        # Check if account already exists for this user and email
        # Use first() instead of scalar_one_or_none() to handle duplicates
        existing_account_result = await db.execute(
            select(EmailAccount).where(
                EmailAccount.user_id == current_user.id,
                EmailAccount.email_address == email_address,
                EmailAccount.provider == "gmail"
            ).order_by(EmailAccount.created_at.desc())
        )
        existing_account = existing_account_result.scalars().first()
        
        if existing_account:
            # Update tokens for existing account
            try:
                access_token_encrypted = encrypt_token(token_data.get("access_token")) if token_data.get("access_token") else None
                refresh_token_encrypted = encrypt_token(token_data.get("refresh_token")) if token_data.get("refresh_token") else None
                
                existing_account.access_token_encrypted = access_token_encrypted
                existing_account.refresh_token_encrypted = refresh_token_encrypted
                existing_account.sync_enabled = True
                
                await db.commit()
                await db.refresh(existing_account)
                return EmailAccountResponse(
                    id=str(existing_account.id),
                    provider=existing_account.provider,
                    email_address=existing_account.email_address,
                    last_sync_at=existing_account.last_sync_at,
                    sync_enabled=existing_account.sync_enabled,
                    created_at=existing_account.created_at,
                )
            except Exception as e:
                await db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Database error occurred: {str(e)}"
                )
        
        # Create new account
        account_data = EmailAccountCreate(
            provider="gmail",
            email_address=email_address,
            access_token=token_data.get("access_token"),
            refresh_token=token_data.get("refresh_token"),
        )
        
    elif provider == "outlook":
        if not settings.OUTLOOK_CLIENT_ID or not settings.OUTLOOK_CLIENT_SECRET:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Outlook OAuth not configured"
            )
        
        # Exchange code for tokens
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://login.microsoftonline.com/common/oauth2/v2.0/token",
                data={
                    "code": code,
                    "client_id": settings.OUTLOOK_CLIENT_ID,
                    "client_secret": settings.OUTLOOK_CLIENT_SECRET,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to exchange token: {response.text}"
                )
            token_data = response.json()
        
        # Get user email
        async with httpx.AsyncClient() as client:
            user_response = await client.get(
                "https://graph.microsoft.com/v1.0/me",
                headers={"Authorization": f"Bearer {token_data['access_token']}"},
            )
            if user_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to get user info: {user_response.text}"
                )
            user_info = user_response.json()
            email_address = user_info.get("mail") or user_info.get("userPrincipalName")
            
            if not email_address:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email address not found in user info. Make sure you granted email access."
                )
        
        # Check if account already exists for this user and email
        # Use first() instead of scalar_one_or_none() to handle duplicates
        existing_account_result = await db.execute(
            select(EmailAccount).where(
                EmailAccount.user_id == current_user.id,
                EmailAccount.email_address == email_address,
                EmailAccount.provider == "outlook"
            ).order_by(EmailAccount.created_at.desc())
        )
        existing_account = existing_account_result.scalars().first()
        
        if existing_account:
            # Update tokens for existing account
            try:
                access_token_encrypted = encrypt_token(token_data.get("access_token")) if token_data.get("access_token") else None
                refresh_token_encrypted = encrypt_token(token_data.get("refresh_token")) if token_data.get("refresh_token") else None
                
                existing_account.access_token_encrypted = access_token_encrypted
                existing_account.refresh_token_encrypted = refresh_token_encrypted
                existing_account.sync_enabled = True
                
                await db.commit()
                await db.refresh(existing_account)
                return EmailAccountResponse(
                    id=str(existing_account.id),
                    provider=existing_account.provider,
                    email_address=existing_account.email_address,
                    last_sync_at=existing_account.last_sync_at,
                    sync_enabled=existing_account.sync_enabled,
                    created_at=existing_account.created_at,
                )
            except Exception as e:
                await db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Database error occurred: {str(e)}"
                )
        
        # Create new account
        account_data = EmailAccountCreate(
            provider="outlook",
            email_address=email_address,
            access_token=token_data.get("access_token"),
            refresh_token=token_data.get("refresh_token"),
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid provider"
        )
    
    # Create account using helper function (only if not existing)
    try:
        new_account = await _create_email_account(account_data, current_user, db)
        # Don't auto-sync here - let the frontend handle it after successful connection
        # This prevents OAuth callback from failing if sync has issues
        return EmailAccountResponse(
            id=str(new_account.id),
            provider=new_account.provider,
            email_address=new_account.email_address,
            last_sync_at=new_account.last_sync_at,
            sync_enabled=new_account.sync_enabled,
            created_at=new_account.created_at,
        )
    except Exception as e:
        # If account creation fails, it might be a duplicate
        # Try to find and update existing account
        existing_result = await db.execute(
            select(EmailAccount).where(
                EmailAccount.user_id == current_user.id,
                EmailAccount.email_address == account_data.email_address,
                EmailAccount.provider == account_data.provider
            ).order_by(EmailAccount.created_at.desc())
        )
        existing = existing_result.scalars().first()
        if existing:
            # Update existing account
            access_token_encrypted = encrypt_token(account_data.access_token) if account_data.access_token else None
            refresh_token_encrypted = encrypt_token(account_data.refresh_token) if account_data.refresh_token else None
            existing.access_token_encrypted = access_token_encrypted
            existing.refresh_token_encrypted = refresh_token_encrypted
            existing.sync_enabled = True
            await db.commit()
            await db.refresh(existing)
            return EmailAccountResponse(
                id=str(existing.id),
                provider=existing.provider,
                email_address=existing.email_address,
                last_sync_at=existing.last_sync_at,
                sync_enabled=existing.sync_enabled,
                created_at=existing.created_at,
            )
        else:
            # Re-raise the original error if no existing account found
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error occurred: {str(e)}"
            )


async def _create_email_account(
    account_data: EmailAccountCreate,
    current_user: User,
    db: AsyncSession
) -> EmailAccount:
    """Helper function to create email account"""
    # Check for existing account first to prevent duplicates
    existing_result = await db.execute(
        select(EmailAccount).where(
            EmailAccount.user_id == current_user.id,
            EmailAccount.email_address == account_data.email_address,
            EmailAccount.provider == account_data.provider
        )
    )
    existing = existing_result.scalar_one_or_none()
    
    if existing:
        # Update existing account with new tokens
        access_token_encrypted = encrypt_token(account_data.access_token) if account_data.access_token else None
        refresh_token_encrypted = encrypt_token(account_data.refresh_token) if account_data.refresh_token else None
        
        existing.access_token_encrypted = access_token_encrypted
        existing.refresh_token_encrypted = refresh_token_encrypted
        existing.sync_enabled = True
        
        await db.commit()
        await db.refresh(existing)
        return existing
    
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


@router.post("/connect", response_model=EmailAccountResponse, status_code=status.HTTP_201_CREATED)
async def connect_email_account(
    account_data: EmailAccountCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Connect an email account"""
    return await _create_email_account(account_data, current_user, db)


@router.get("/accounts", response_model=List[EmailAccountResponse])
async def list_email_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List connected email accounts (deduplicated by email_address and provider)"""
    result = await db.execute(
        select(EmailAccount).where(EmailAccount.user_id == current_user.id)
        .order_by(EmailAccount.created_at.desc())
    )
    accounts = result.scalars().all()
    
    # Deduplicate: keep only the most recent account for each email_address+provider combination
    seen = {}
    unique_accounts = []
    for account in accounts:
        key = (account.email_address.lower(), account.provider)
        if key not in seen:
            seen[key] = account
            unique_accounts.append(account)
    
    # Convert UUIDs to strings for response
    return [
        EmailAccountResponse(
            id=str(account.id),
            provider=account.provider,
            email_address=account.email_address,
            last_sync_at=account.last_sync_at,
            sync_enabled=account.sync_enabled,
            created_at=account.created_at,
        )
        for account in unique_accounts
    ]


@router.post("/accounts/cleanup")
async def cleanup_duplicate_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove duplicate email accounts, keeping only the most recent one for each email+provider"""
    
    # Get all accounts for user
    result = await db.execute(
        select(EmailAccount).where(EmailAccount.user_id == current_user.id)
        .order_by(EmailAccount.created_at.desc())
    )
    accounts = result.scalars().all()
    
    # Group by email_address+provider, keep only the most recent
    seen = {}
    to_delete = []
    for account in accounts:
        key = (account.email_address.lower(), account.provider)
        if key in seen:
            # This is a duplicate, mark for deletion
            to_delete.append(account.id)
        else:
            seen[key] = account
    
    # Delete duplicates
    deleted_count = 0
    if to_delete:
        for account_id in to_delete:
            result = await db.execute(
                select(EmailAccount).where(
                    EmailAccount.id == account_id,
                    EmailAccount.user_id == current_user.id
                )
            )
            account = result.scalar_one_or_none()
            if account:
                db.delete(account)
                deleted_count += 1
        
        await db.commit()
    
    return {"deleted_count": deleted_count, "message": f"Removed {deleted_count} duplicate account(s)"}


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
                
                # Calculate priority with enhanced factors
                email_item.ai_priority_score = priority_scorer.calculate_email_priority(
                    email_item.body_text or "",
                    email_item.received_at,
                    email_item.sender_email,
                    email_item.subject,
                    email_item.is_read,
                    email_item.is_important
                )
                
                # Extract tasks with context
                tasks = await task_generator.extract_tasks(
                    email_item.body_text,
                    "email",
                    context={
                        "sender_email": email_item.sender_email,
                        "sender_name": email_item.sender_name,
                        "subject": email_item.subject,
                        "received_at": email_item.received_at.isoformat() if email_item.received_at else None
                    }
                )
                email_item.ai_extracted_tasks = {"tasks": tasks}
            
            db.add(email_item)
            synced_count += 1
        
        # Update last sync time
        account.last_sync_at = datetime.now()
        await db.commit()

        # Level 4: Generate Action Suggestions after sync
        from app.services.action_service import action_engine
        from app.models.graph import ActionSuggestion
        
        # Get latest emails to analyze
        result = await db.execute(select(EmailItem).where(EmailItem.email_account_id == account.id).limit(10))
        latest_emails = result.scalars().all()
        
        suggestions = await action_engine.suggest_follow_ups(str(current_user.id), latest_emails)
        for s in suggestions:
            new_s = ActionSuggestion(
                user_id=current_user.id,
                type=s["type"],
                source_id=uuid.UUID(s["source_id"]),
                title=s["title"],
                description=s["description"],
                draft_content=s["draft_content"],
                action_label=s["action_label"]
            )
            db.add(new_s)
        await db.commit()
    
    return {"synced_count": synced_count, "message": "Sync completed and AI insights generated"}


@router.get("", response_model=EmailListResponse)
async def list_emails(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    unread_only: Optional[bool] = Query(None),
    important_only: Optional[bool] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List emails with search and filters"""
    from sqlalchemy import or_, func
    
    offset = (page - 1) * page_size
    
    # Get user's email accounts
    accounts_result = await db.execute(
        select(EmailAccount.id).where(EmailAccount.user_id == current_user.id)
    )
    # Since we're selecting only the ID, scalars() returns UUID objects directly
    account_ids = list(accounts_result.scalars().all())
    
    if not account_ids:
        return EmailListResponse(emails=[], total=0, page=page, page_size=page_size)
    
    # Build query with filters
    query = select(EmailItem).where(EmailItem.email_account_id.in_(account_ids))
    
    # Search filter (searches in subject, sender, and body)
    if search:
        search_pattern = f"%{search.lower()}%"
        # Use COALESCE to handle NULL values
        from sqlalchemy import case
        query = query.where(
            or_(
                func.lower(func.coalesce(EmailItem.subject, '')).like(search_pattern),
                func.lower(func.coalesce(EmailItem.sender_name, '')).like(search_pattern),
                func.lower(func.coalesce(EmailItem.sender_email, '')).like(search_pattern),
                func.lower(func.coalesce(EmailItem.body_text, '')).like(search_pattern),
                func.lower(func.coalesce(EmailItem.ai_summary, '')).like(search_pattern)
            )
        )
    
    # Unread filter
    if unread_only is not None:
        query = query.where(EmailItem.is_read == (not unread_only))
    
    # Important filter
    if important_only is not None and important_only:
        query = query.where(EmailItem.is_important == True)
    
    # Date range filters
    if date_from:
        query = query.where(EmailItem.received_at >= date_from)
    if date_to:
        query = query.where(EmailItem.received_at <= date_to)
    
    # Get total count (before pagination)
    count_query = select(func.count(EmailItem.id)).where(EmailItem.email_account_id.in_(account_ids))
    
    # Apply same filters to count query
    if search:
        search_pattern = f"%{search.lower()}%"
        count_query = count_query.where(
            or_(
                func.lower(func.coalesce(EmailItem.subject, '')).like(search_pattern),
                func.lower(func.coalesce(EmailItem.sender_name, '')).like(search_pattern),
                func.lower(func.coalesce(EmailItem.sender_email, '')).like(search_pattern),
                func.lower(func.coalesce(EmailItem.body_text, '')).like(search_pattern),
                func.lower(func.coalesce(EmailItem.ai_summary, '')).like(search_pattern)
            )
        )
    if unread_only is not None:
        count_query = count_query.where(EmailItem.is_read == (not unread_only))
    if important_only is not None and important_only:
        count_query = count_query.where(EmailItem.is_important == True)
    if date_from:
        count_query = count_query.where(EmailItem.received_at >= date_from)
    if date_to:
        count_query = count_query.where(EmailItem.received_at <= date_to)
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar_one() or 0
    
    # Get paginated emails
    result = await db.execute(
        query
        .order_by(EmailItem.received_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    emails = result.scalars().all()
    
    # Convert emails to response format (UUID to string)
    email_responses = [
        EmailItemResponse(
            id=str(email.id),
            subject=email.subject,
            sender_email=email.sender_email,
            sender_name=email.sender_name,
            body_text=email.body_text,
            received_at=email.received_at,
            is_read=email.is_read,
            is_important=email.is_important,
            ai_summary=email.ai_summary,
            ai_extracted_tasks=email.ai_extracted_tasks,
            ai_extracted_dates=email.ai_extracted_dates,
            ai_priority_score=email.ai_priority_score,
            created_at=email.created_at,
        )
        for email in emails
    ]
    
    return EmailListResponse(
        emails=email_responses,
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
    
    # Mark as read when viewing
    if not email.is_read:
        email.is_read = True
        await db.commit()
        await db.refresh(email)
    
    # Convert UUID to string for response
    return EmailItemResponse(
        id=str(email.id),
        subject=email.subject,
        sender_email=email.sender_email,
        sender_name=email.sender_name,
        body_text=email.body_text,
        received_at=email.received_at,
        is_read=email.is_read,
        is_important=email.is_important,
        ai_summary=email.ai_summary,
        ai_extracted_tasks=email.ai_extracted_tasks,
        ai_extracted_dates=email.ai_extracted_dates,
        ai_priority_score=email.ai_priority_score,
        created_at=email.created_at,
    )


@router.put("/{email_id}/read")
async def mark_email_read(
    email_id: str,
    read: bool = Query(True),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark email as read or unread"""
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
    
    email.is_read = read
    await db.commit()
    await db.refresh(email)
    
    return EmailItemResponse(
        id=str(email.id),
        subject=email.subject,
        sender_email=email.sender_email,
        sender_name=email.sender_name,
        body_text=email.body_text,
        received_at=email.received_at,
        is_read=email.is_read,
        is_important=email.is_important,
        ai_summary=email.ai_summary,
        ai_extracted_tasks=email.ai_extracted_tasks,
        ai_extracted_dates=email.ai_extracted_dates,
        ai_priority_score=email.ai_priority_score,
        created_at=email.created_at,
    )

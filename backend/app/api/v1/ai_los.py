"""AI-LOS Advanced Features Router"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.graph import ActionSuggestion, Goal
from sqlalchemy import select
import uuid

router = APIRouter()

@router.get("/suggestions", response_model=List[dict])
async def get_action_suggestions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get active AI action suggestions (Action Cards)"""
    result = await db.execute(
        select(ActionSuggestion).where(
            ActionSuggestion.user_id == current_user.id,
            ActionSuggestion.is_dismissed == False
        ).order_by(ActionSuggestion.created_at.desc())
    )
    suggestions = result.scalars().all()
    return [
        {
            "id": str(s.id),
            "type": s.type,
            "title": s.title,
            "description": s.description,
            "draft_content": s.draft_content,
            "action_label": s.action_label,
            "created_at": s.created_at
        }
        for s in suggestions
    ]

@router.post("/suggestions/{suggestion_id}/dismiss")
async def dismiss_suggestion(
    suggestion_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Dismiss an action suggestion"""
    result = await db.execute(
        select(ActionSuggestion).where(
            ActionSuggestion.id == uuid.UUID(suggestion_id),
            ActionSuggestion.user_id == current_user.id
        )
    )
    suggestion = result.scalar_one_or_none()
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    suggestion.is_dismissed = True
    await db.commit()
    return {"status": "success"}

@router.get("/goals", response_model=List[dict])
async def list_goals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user goals"""
    result = await db.execute(
        select(Goal).where(Goal.user_id == current_user.id)
    )
    goals = result.scalars().all()
    return [
        {
            "id": str(g.id),
            "title": g.title,
            "category": g.category,
            "status": g.status,
            "target_date": g.target_date
        }
        for g in goals
    ]

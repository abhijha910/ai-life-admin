"""Task service"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import Optional, List
from datetime import datetime, date
import uuid
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate
from app.ai_engine.priority_scorer import priority_scorer
import structlog

logger = structlog.get_logger()


class TaskService:
    """Task service"""
    
    async def create_task(
        self,
        db: AsyncSession,
        user: User,
        task_data: TaskCreate,
        source_type: Optional[str] = None,
        source_id: Optional[str] = None
    ) -> Task:
        """Create a new task"""
        try:
            # Calculate priority if due date provided
            priority = task_data.priority
            if task_data.due_date and priority == 0:
                priority = priority_scorer.calculate_priority(
                    task_data.due_date,
                    datetime.now(),
                    source_type
                )
            
            task = Task(
                id=uuid.uuid4(),
                user_id=user.id,
                title=task_data.title,
                description=task_data.description,
                consequences=task_data.consequences,
                source_type=source_type or "manual",
                source_id=uuid.UUID(source_id) if source_id else None,
                priority=priority,
                due_date=task_data.due_date,
                estimated_duration=task_data.estimated_duration,
                status="pending",
                ai_generated=task_data.ai_generated,
                is_approved=task_data.is_approved,
                dependency_id=uuid.UUID(task_data.dependency_id) if task_data.dependency_id else None,
                goal_id=uuid.UUID(task_data.goal_id) if task_data.goal_id else None,
                created_at=datetime.now()
            )
            
            db.add(task)
            await db.commit()
            await db.refresh(task)
            
            return task
        except Exception as e:
            logger.error("Task creation error", error=str(e))
            raise
    
    async def get_task(
        self,
        db: AsyncSession,
        task_id: str,
        user: User
    ) -> Optional[Task]:
        """Get task by ID"""
        result = await db.execute(
            select(Task).where(
                Task.id == uuid.UUID(task_id),
                Task.user_id == user.id
            )
        )
        return result.scalar_one_or_none()
    
    async def list_tasks(
        self,
        db: AsyncSession,
        user: User,
        status: Optional[str] = None,
        due_date: Optional[date] = None,
        is_approved: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[Task], int]:
        """List user's tasks"""
        offset = (page - 1) * page_size
        
        # Build query
        query = select(Task).where(Task.user_id == user.id)
        
        if status:
            query = query.where(Task.status == status)
        
        if due_date:
            query = query.where(Task.due_date <= due_date)
        
        if is_approved is not None:
            query = query.where(Task.is_approved == is_approved)
        
        # Get total count
        count_query = select(Task).where(Task.user_id == user.id)
        if status:
            count_query = count_query.where(Task.status == status)
        if due_date:
            count_query = count_query.where(Task.due_date <= due_date)
        if is_approved is not None:
            count_query = count_query.where(Task.is_approved == is_approved)
        
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())
        
        # Get paginated results
        query = query.order_by(Task.priority.desc(), Task.due_date.asc())
        query = query.offset(offset).limit(page_size)
        
        result = await db.execute(query)
        tasks = result.scalars().all()
        
        return tasks, total
    
    async def update_task(
        self,
        db: AsyncSession,
        task_id: str,
        user: User,
        task_data: TaskUpdate
    ) -> Optional[Task]:
        """Update task"""
        task = await self.get_task(db, task_id, user)
        if not task:
            return None
        
        # Update fields
        if task_data.title is not None:
            task.title = task_data.title
        if task_data.description is not None:
            task.description = task_data.description
        if task_data.consequences is not None:
            task.consequences = task_data.consequences
        if task_data.due_date is not None:
            task.due_date = task_data.due_date
            # Recalculate priority
            task.priority = priority_scorer.calculate_priority(
                task_data.due_date,
                task.created_at,
                task.source_type
            )
        if task_data.priority is not None:
            task.priority = task_data.priority
        if task_data.risk_level is not None:
            task.risk_level = task_data.risk_level
        if task_data.status is not None:
            task.status = task_data.status
            if task_data.status == "completed":
                task.completed_at = datetime.now()
        if task_data.estimated_duration is not None:
            task.estimated_duration = task_data.estimated_duration
        if task_data.dependency_id is not None:
            task.dependency_id = uuid.UUID(task_data.dependency_id) if task_data.dependency_id else None
        if task_data.goal_id is not None:
            task.goal_id = uuid.UUID(task_data.goal_id) if task_data.goal_id else None
        if task_data.is_approved is not None:
            task.is_approved = task_data.is_approved
        
        task.updated_at = datetime.now()
        await db.commit()
        await db.refresh(task)
        
        return task
    
    async def delete_task(
        self,
        db: AsyncSession,
        task_id: str,
        user: User
    ) -> bool:
        """Delete task"""
        task = await self.get_task(db, task_id, user)
        if task:
            await db.delete(task)
            await db.commit()
            return True
        return False
    
    async def complete_task(
        self,
        db: AsyncSession,
        task_id: str,
        user: User
    ) -> Optional[Task]:
        """Mark task as completed"""
        task = await self.get_task(db, task_id, user)
        if task:
            task.status = "completed"
            task.completed_at = datetime.now()
            task.updated_at = datetime.now()
            await db.commit()
            await db.refresh(task)
        return task

    async def resolve_ai_task_entities(
        self,
        db: AsyncSession,
        user: User,
        task_data: dict
    ) -> dict:
        """Resolve goal_category and institution_name to IDs"""
        from app.models.graph import Goal, Institution
        from sqlalchemy import select
        
        # 1. Resolve Goal
        goal_category = task_data.get("goal_category")
        if goal_category:
            result = await db.execute(
                select(Goal).where(
                    Goal.user_id == user.id,
                    Goal.category == goal_category
                )
            )
            goal = result.scalar_one_or_none()
            if not goal:
                # Create default goal for this category if not exists
                goal = Goal(
                    id=uuid.uuid4(),
                    user_id=user.id,
                    title=f"My {goal_category} Goals",
                    category=goal_category,
                    status="active"
                )
                db.add(goal)
                await db.flush()
            task_data["goal_id"] = str(goal.id)
            
        return task_data


# Global task service instance
task_service = TaskService()

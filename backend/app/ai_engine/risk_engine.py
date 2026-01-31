"""Risk Prediction Engine for deadline failure prediction"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.models.task import Task
from app.ai_engine.habit_predictor import habit_predictor
import structlog

logger = structlog.get_logger()

class RiskEngine:
    """Analyze and predict risks of task failure"""

    def calculate_task_risk(
        self,
        task: Task,
        completion_patterns: Dict[str, Any]
    ) -> int:
        """Calculate risk level (0-100) for a single task"""
        if task.status == "completed":
            return 0
        
        risk_score = 0
        now = datetime.now(task.due_date.tzinfo) if task.due_date and task.due_date.tzinfo else datetime.now()

        # 1. Deadline Proximity Risk
        if task.due_date:
            time_left = (task.due_date - now).total_seconds() / 3600  # hours
            
            if time_left < 0:
                risk_score += 90  # Already overdue
            elif time_left < 2:
                risk_score += 80  # Extremely urgent
            elif time_left < 8:
                risk_score += 60
            elif time_left < 24:
                risk_score += 40
            elif time_left < 48:
                risk_score += 20

        # 2. Habit-based Risk (Time Reality)
        # If user typically completes tasks in peak hours, and we are past that
        peak_hour = completion_patterns.get("peak_hour", 10)
        if now.hour > peak_hour and task.due_date and task.due_date.date() == now.date():
            risk_score += 15

        # 3. Completion Probability Risk
        # Convert Task model to dict for habit_predictor
        task_dict = {
            "priority": task.priority,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "source_type": task.source_type
        }
        probability = habit_predictor.predict_completion_probability(task_dict, completion_patterns)
        # Lower probability = higher risk
        risk_score += int((1.0 - probability) * 30)

        # 4. Dependency Risk
        if task.dependency_id:
            risk_score += 20  # Risk increased if it depends on something else

        # 5. Complexity Risk
        duration = task.estimated_duration or 60
        if duration > 120:  # Tasks longer than 2 hours are riskier
            risk_score += 10

        return max(0, min(100, risk_score))

    def detect_overload(
        self,
        tasks: List[Task],
        target_date: datetime
    ) -> Dict[str, Any]:
        """Detect if the user has too many tasks for a given day"""
        day_tasks = [t for t in tasks if t.due_date and t.due_date.date() == target_date.date()]
        total_duration = sum(t.estimated_duration or 60 for t in day_tasks)
        
        # Assume 8-hour workday (480 minutes)
        capacity = 480 
        load_percentage = (total_duration / capacity) * 100
        
        is_overloaded = load_percentage > 90
        
        return {
            "is_overloaded": is_overloaded,
            "load_percentage": load_percentage,
            "total_duration": total_duration,
            "task_count": len(day_tasks)
        }

risk_engine = RiskEngine()

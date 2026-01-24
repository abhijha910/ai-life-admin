"""Daily plan generator"""
from typing import List, Dict, Any, Optional
from datetime import date, datetime, time, timedelta
from app.ai_engine.llm_client import llm_client
from app.ai_engine.priority_scorer import priority_scorer
import json
import structlog

logger = structlog.get_logger()


class PlanGenerator:
    """Generate daily action plans"""
    
    async def generate_plan(
        self,
        tasks: List[Dict[str, Any]],
        target_date: date,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate daily plan for a specific date"""
        try:
            # Filter tasks for the target date
            relevant_tasks = self._filter_tasks_for_date(tasks, target_date)
            
            # Sort by priority
            sorted_tasks = sorted(
                relevant_tasks,
                key=lambda t: t.get("priority", 50),
                reverse=True
            )
            
            # Generate schedule
            scheduled_tasks = self._schedule_tasks(
                sorted_tasks,
                target_date,
                user_preferences
            )
            
            # Generate AI recommendations
            recommendations = await self._generate_recommendations(
                scheduled_tasks,
                user_preferences
            )
            
            # Calculate statistics
            total_duration = sum(
                t.get("estimated_duration", 60) for t in scheduled_tasks
            )
            priority_breakdown = self._calculate_priority_breakdown(scheduled_tasks)
            
            return {
                "date": target_date.isoformat(),
                "tasks": scheduled_tasks,
                "total_duration": total_duration,
                "priority_breakdown": priority_breakdown,
                "ai_recommendations": recommendations,
                "generated_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error("Plan generation error", error=str(e))
            return self._fallback_plan(tasks, target_date)
    
    def _filter_tasks_for_date(
        self,
        tasks: List[Dict[str, Any]],
        target_date: date
    ) -> List[Dict[str, Any]]:
        """Filter tasks relevant to target date"""
        relevant = []
        
        for task in tasks:
            due_date = task.get("due_date")
            status = task.get("status", "pending")
            
            # Include if:
            # - Due on target date
            # - Overdue
            # - No due date and status is pending
            if status in ["pending", "in_progress"]:
                if due_date:
                    if isinstance(due_date, str):
                        due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    if isinstance(due_date, datetime):
                        due_date = due_date.date()
                    
                    if due_date <= target_date:
                        relevant.append(task)
                else:
                    relevant.append(task)
        
        return relevant
    
    def _schedule_tasks(
        self,
        tasks: List[Dict[str, Any]],
        target_date: date,
        user_preferences: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Schedule tasks throughout the day"""
        start_time = time(9, 0)  # Default 9 AM
        if user_preferences and "daily_plan_time" in user_preferences:
            start_time = user_preferences["daily_plan_time"]
        
        current_time = datetime.combine(target_date, start_time)
        scheduled = []
        
        for task in tasks:
            duration = task.get("estimated_duration", 60)  # Default 1 hour
            
            scheduled_task = {
                "task_id": task.get("id"),
                "title": task.get("title"),
                "priority": task.get("priority", 50),
                "estimated_duration": duration,
                "scheduled_time": current_time.isoformat(),
                "source": task.get("source_type", "manual")
            }
            
            scheduled.append(scheduled_task)
            
            # Move to next time slot
            current_time += timedelta(minutes=duration + 15)  # 15 min buffer
        
        return scheduled
    
    async def _generate_recommendations(
        self,
        scheduled_tasks: List[Dict[str, Any]],
        user_preferences: Optional[Dict[str, Any]]
    ) -> Optional[str]:
        """Generate AI recommendations for the day"""
        try:
            if not scheduled_tasks:
                return "No tasks scheduled for today. Enjoy your free day!"
            
            task_summary = "\n".join([
                f"- {t['title']} (Priority: {t['priority']}, Duration: {t['estimated_duration']} min)"
                for t in scheduled_tasks[:10]
            ])
            
            prompt = f"""Based on these scheduled tasks for today, provide 2-3 brief recommendations:
            
{task_summary}

Provide practical, actionable recommendations. Keep it under 100 words."""
            
            response = await llm_client.generate(prompt=prompt)
            return response.strip() if response else None
        except Exception as e:
            logger.warning("Recommendation generation error", error=str(e))
            return None
    
    def _calculate_priority_breakdown(
        self,
        tasks: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Calculate priority breakdown"""
        breakdown = {"high": 0, "medium": 0, "low": 0}
        
        for task in tasks:
            priority = task.get("priority", 50)
            if priority >= 70:
                breakdown["high"] += 1
            elif priority >= 40:
                breakdown["medium"] += 1
            else:
                breakdown["low"] += 1
        
        return breakdown
    
    def _fallback_plan(
        self,
        tasks: List[Dict[str, Any]],
        target_date: date
    ) -> Dict[str, Any]:
        """Fallback plan generation"""
        relevant = self._filter_tasks_for_date(tasks, target_date)
        scheduled = self._schedule_tasks(relevant, target_date, None)
        
        return {
            "date": target_date.isoformat(),
            "tasks": scheduled,
            "total_duration": sum(t.get("estimated_duration", 60) for t in scheduled),
            "priority_breakdown": self._calculate_priority_breakdown(scheduled),
            "ai_recommendations": None,
            "generated_at": datetime.now().isoformat()
        }


# Global plan generator instance
plan_generator = PlanGenerator()

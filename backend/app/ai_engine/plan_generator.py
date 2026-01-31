"""Daily plan generator"""
from typing import List, Dict, Any, Optional
from datetime import date, datetime, time, timedelta
from app.ai_engine.llm_client import llm_client
from app.ai_engine.priority_scorer import priority_scorer
from app.ai_engine.risk_engine import risk_engine
from app.ai_engine.habit_predictor import habit_predictor
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
            
            # Generate scheduled tasks list for risk analysis
            scheduled_task_models = [] # We need Task models here for RiskEngine, but we have dicts. 
            # For simplicity in this iteration, let's just use the dicts and adapt RiskEngine if needed, 
            # or better, calculate risk during task filtering.
            
            # Calculate statistics
            overload_info = self._check_burnout(scheduled_tasks, target_date)
            
            # Generate AI recommendations
            recommendations = await self._generate_recommendations(
                scheduled_tasks,
                user_preferences
            )
            
            total_duration = sum(
                t.get("estimated_duration", 60) for t in scheduled_tasks
            )
            priority_breakdown = self._calculate_priority_breakdown(scheduled_tasks)
            
            return {
                "date": target_date.isoformat(),
                "tasks": scheduled_tasks,
                "total_duration": total_duration,
                "priority_breakdown": priority_breakdown,
                "overload_info": overload_info,
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
            # Level 7: Approval layer - Only include approved tasks in the plan
            if not task.get("is_approved", True):
                continue

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
        """Schedule tasks throughout the day with Time Reality adjustment"""
        start_time = time(9, 0)  # Default 9 AM
        if user_preferences and "daily_plan_time" in user_preferences:
            start_time = user_preferences["daily_plan_time"]
        
        # Time Reality Adjustment: If user takes longer than estimated
        # This could be a learned factor from HabitPredictor
        time_reality_factor = user_preferences.get("time_reality_factor", 1.0) if user_preferences else 1.2 # Default 20% buffer
        
        current_time = datetime.combine(target_date, start_time)
        scheduled = []
        
        for task in tasks:
            base_duration = task.get("estimated_duration", 60)
            duration = int(base_duration * time_reality_factor)
            
            # Calculate dynamic risk if not set
            risk_level = task.get("risk_level", 0)
            if risk_level == 0 and task.get("due_date"):
                # Simple real-time risk calculation for dashboard
                from app.ai_engine.habit_predictor import habit_predictor
                patterns = habit_predictor.analyze_patterns([]) # Get patterns
                
                # Proximity risk
                due = datetime.fromisoformat(task["due_date"].replace('Z', '+00:00'))
                now = datetime.now(due.tzinfo)
                hours_left = (due - now).total_seconds() / 3600
                if hours_left < 24: risk_level = 75
                elif hours_left < 48: risk_level = 45
                else: risk_level = 15

            scheduled_task = {
                "task_id": task.get("id"),
                "title": task.get("title"),
                "priority": task.get("priority", 50),
                "risk_level": risk_level,
                "consequences": task.get("consequences") or "Missing this might impact your daily goals.",
                "estimated_duration": duration,
                "original_duration": base_duration,
                "scheduled_time": current_time.isoformat(),
                "source": task.get("source_type", "manual")
            }
            
            scheduled.append(scheduled_task)
            
            # Move to next time slot with buffer
            buffer_minutes = 15 if duration < 60 else 30
            current_time += timedelta(minutes=duration + buffer_minutes)
        
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

    def _check_burnout(self, scheduled_tasks: List[Dict[str, Any]], target_date: date) -> Dict[str, Any]:
        """Check for cognitive overload and burnout risk"""
        total_minutes = sum(t.get("estimated_duration", 60) for t in scheduled_tasks)
        # Assuming 8 hours of productive time (480 minutes)
        capacity = 480
        load = (total_minutes / capacity) * 100
        
        # Regret Prevention logic: Check for high-priority goal tasks being snoozed
        regret_warnings = []
        for task in scheduled_tasks:
            # If a task is linked to a goal and has been postponed multiple times
            # (Note: we'd need a 'snooze_count' in Task model for full implementation)
            if task.get("priority", 50) > 80 and task.get("source") == "manual":
                regret_warnings.append(f"Regret Warning: You've skipped '{task['title']}' multiple times. This is a high-priority personal goal.")

        return {
            "load_percentage": round(load, 1),
            "is_overloaded": load > 90,
            "burnout_risk": "high" if load > 110 else "medium" if load > 85 else "low",
            "recommendation": "Consider moving some tasks to tomorrow to avoid burnout." if load > 90 else "Load looks manageable.",
            "regret_warnings": regret_warnings
        }
    
    def _fallback_plan(
        self,
        tasks: List[Dict[str, Any]],
        target_date: date
    ) -> Dict[str, Any]:
        """Fallback plan generation with new fields support"""
        relevant = self._filter_tasks_for_date(tasks, target_date)
        scheduled = self._schedule_tasks(relevant, target_date, None)
        
        # Calculate overload info even in fallback
        overload_info = self._check_burnout(scheduled, target_date)
        
        return {
            "date": target_date.isoformat(),
            "tasks": scheduled,
            "total_duration": sum(t.get("estimated_duration", 60) for t in scheduled),
            "priority_breakdown": self._calculate_priority_breakdown(scheduled),
            "overload_info": overload_info,
            "ai_recommendations": "AI recommendations are temporarily unavailable, but your plan is ready.",
            "generated_at": datetime.now().isoformat()
        }


# Global plan generator instance
plan_generator = PlanGenerator()

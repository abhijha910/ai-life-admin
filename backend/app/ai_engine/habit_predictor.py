"""Habit pattern predictor"""
from typing import List, Dict, Any, Optional
from datetime import datetime, time
from collections import defaultdict
import structlog

logger = structlog.get_logger()


class HabitPredictor:
    """Predict user habits and optimal task scheduling"""
    
    def analyze_patterns(
        self,
        completed_tasks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze task completion patterns"""
        if not completed_tasks:
            return {}
        
        # Group by hour of completion
        hour_completions = defaultdict(int)
        day_completions = defaultdict(int)
        category_completions = defaultdict(int)
        
        for task in completed_tasks:
            completed_at = task.get("completed_at")
            if completed_at:
                if isinstance(completed_at, str):
                    completed_at = datetime.fromisoformat(completed_at.replace('Z', '+00:00'))
                
                hour = completed_at.hour
                day = completed_at.strftime("%A")
                
                hour_completions[hour] += 1
                day_completions[day] += 1
                
                category = task.get("source_type", "manual")
                category_completions[category] += 1
        
        # Find peak hours
        peak_hour = max(hour_completions.items(), key=lambda x: x[1])[0] if hour_completions else 10
        peak_day = max(day_completions.items(), key=lambda x: x[1])[0] if day_completions else "Monday"
        
        return {
            "peak_hour": peak_hour,
            "peak_day": peak_day,
            "hour_distribution": dict(hour_completions),
            "day_distribution": dict(day_completions),
            "category_distribution": dict(category_completions)
        }
    
    def predict_optimal_time(
        self,
        task: Dict[str, Any],
        patterns: Dict[str, Any]
    ) -> Optional[time]:
        """Predict optimal time for a task based on patterns"""
        if not patterns:
            return time(10, 0)  # Default 10 AM
        
        peak_hour = patterns.get("peak_hour", 10)
        return time(peak_hour, 0)
    
    def predict_completion_probability(
        self,
        task: Dict[str, Any],
        patterns: Dict[str, Any]
    ) -> float:
        """Predict probability of task completion"""
        base_probability = 0.5
        
        # Factors that increase completion probability
        if task.get("priority", 50) >= 70:
            base_probability += 0.2
        
        if task.get("due_date"):
            base_probability += 0.1
        
        # Check if similar tasks were completed in the past
        category = task.get("source_type", "manual")
        category_dist = patterns.get("category_distribution", {})
        if category in category_dist and category_dist[category] > 5:
            base_probability += 0.1
        
        return min(1.0, base_probability)


# Global habit predictor instance
habit_predictor = HabitPredictor()

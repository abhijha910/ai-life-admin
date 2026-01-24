"""AI task generator"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.ai_engine.llm_client import llm_client
from app.ai_engine.nlp_extractor import nlp_extractor
from app.ai_engine.extractors import date_extractor
import json
import structlog

logger = structlog.get_logger()


class TaskGenerator:
    """Generate tasks from text using AI"""
    
    async def extract_tasks(
        self,
        text: str,
        source_type: str = "email",
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Extract tasks from text"""
        try:
            # First, use NLP to find potential action items
            action_items = nlp_extractor.extract_action_items(text)
            
            # Use LLM to refine and extract structured tasks
            system_prompt = """You are a task extraction system. Extract actionable tasks from the given text.
            Return a JSON array of tasks, each with: title, description (optional), due_date (ISO format or null), priority (0-100), estimated_duration (minutes or null).
            Only extract clear, actionable tasks. Ignore vague or completed items."""
            
            user_prompt = f"""Extract tasks from this {source_type}:
            
{text[:3000]}

Return JSON array of tasks: [{{"title": "...", "description": "...", "due_date": "...", "priority": 0-100, "estimated_duration": minutes}}]"""
            
            response = await llm_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                format="json"
            )
            
            try:
                tasks = json.loads(response)
                if not isinstance(tasks, list):
                    tasks = [tasks]
                
                # Validate and clean tasks
                validated_tasks = []
                for task in tasks:
                    if isinstance(task, dict) and "title" in task:
                        validated_task = {
                            "title": task.get("title", "").strip(),
                            "description": task.get("description", "").strip() or None,
                            "due_date": self._parse_due_date(task.get("due_date")),
                            "priority": self._validate_priority(task.get("priority", 50)),
                            "estimated_duration": task.get("estimated_duration"),
                            "ai_generated": True
                        }
                        if validated_task["title"]:
                            validated_tasks.append(validated_task)
                
                return validated_tasks
            except json.JSONDecodeError:
                logger.warning("Failed to parse LLM task response, using NLP fallback")
                return self._fallback_extract_tasks(text)
                
        except Exception as e:
            logger.error("Task extraction error", error=str(e))
            return self._fallback_extract_tasks(text)
    
    def _fallback_extract_tasks(self, text: str) -> List[Dict[str, Any]]:
        """Fallback task extraction using NLP"""
        action_items = nlp_extractor.extract_action_items(text)
        dates = date_extractor.extract_dates(text)
        
        tasks = []
        for item in action_items[:5]:  # Limit to 5 tasks
            # Find associated date if any
            due_date = None
            if dates:
                # Use first date found
                due_date = dates[0].get("parsed")
            
            tasks.append({
                "title": item[:200],  # Truncate
                "description": None,
                "due_date": due_date,
                "priority": 50,
                "estimated_duration": None,
                "ai_generated": True
            })
        
        return tasks
    
    def _parse_due_date(self, date_str: Optional[str]) -> Optional[str]:
        """Parse due date string to ISO format"""
        if not date_str:
            return None
        
        try:
            from dateutil import parser
            dt = parser.parse(date_str)
            return dt.isoformat()
        except Exception:
            return None
    
    def _validate_priority(self, priority: Any) -> int:
        """Validate and normalize priority (0-100)"""
        try:
            priority = int(priority)
            return max(0, min(100, priority))
        except (ValueError, TypeError):
            return 50


# Global task generator instance
task_generator = TaskGenerator()

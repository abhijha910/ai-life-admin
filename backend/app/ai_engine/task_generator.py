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
        """Extract tasks from text with improved prompts and accuracy"""
        try:
            # First, use NLP to find potential action items and dates
            action_items = nlp_extractor.extract_action_items(text)
            dates = date_extractor.extract_dates(text)
            
            # Check if LLM is available
            llm_available = await llm_client.check_connection()
            
            if not llm_available:
                logger.warning("LLM not available, using NLP fallback")
                return self._fallback_extract_tasks(text)
            
            # Enhanced system prompt with better instructions
            system_prompt = """You are an expert task extraction assistant. Your job is to identify actionable tasks from text.

CRITICAL RULES:
1. Only extract tasks that are ACTIONABLE (something someone needs to DO)
2. Ignore completed tasks, past events, or vague statements
3. Extract clear, specific tasks with actionable verbs (review, submit, call, schedule, etc.)
4. If a due date is mentioned, extract it in ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
5. Identify the CONSEQUENCES if the task is not completed (e.g., penalty, missed opportunity, late fee, etc.)
6. Confidence: Provide a confidence score (0-1) for how certain you are about this task.
7. Priority: 0-100 scale where:
   - 80-100: Urgent/High priority (deadlines within 24h, marked urgent)
   - 60-79: Important (deadlines within 3 days, action required)
   - 40-59: Normal (deadlines within a week)
   - 20-39: Low (deadlines beyond a week)
   - 0-19: Very low (no deadline, optional)
8. Estimated duration should be in minutes
9. Identify the GOAL this task contributes to (e.g., 'Health', 'Career', 'Finance', 'Personal', etc.)
10. Identify any INSTITUTION involved (e.g., 'Bank of America', 'Employer Name', 'IRS', etc.)
11. Return ONLY valid JSON array, no additional text

Return format: [{"title": "Task title", "description": "Optional details", "consequences": "What happens if missed", "confidence_score": 0-1, "due_date": "YYYY-MM-DD or null", "priority": 0-100, "estimated_duration": minutes or null, "goal_category": "Health/Career/etc", "institution_name": "Name of institution or null"}]"""
            
            # Enhanced user prompt with context
            context_info = ""
            if context:
                if context.get("sender_email"):
                    context_info += f"\nSender: {context.get('sender_email')}\n"
                if context.get("subject"):
                    context_info += f"Subject: {context.get('subject')}\n"
                if dates:
                    context_info += f"Dates found in text: {[d.get('text', '') for d in dates[:3]]}\n"
            
            user_prompt = f"""Extract actionable tasks from this {source_type}:
{context_info}
---
Text:
{text[:4000]}

Analyze the text and extract all actionable tasks. Return a JSON array of tasks."""
            
            response = await llm_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                format="json",
                temperature=0.3  # Lower temperature for more consistent task extraction
            )
            
            try:
                # Clean response - remove markdown code blocks if present
                cleaned_response = response.strip()
                if cleaned_response.startswith("```json"):
                    cleaned_response = cleaned_response[7:]
                if cleaned_response.startswith("```"):
                    cleaned_response = cleaned_response[3:]
                if cleaned_response.endswith("```"):
                    cleaned_response = cleaned_response[:-3]
                cleaned_response = cleaned_response.strip()
                
                tasks = json.loads(cleaned_response)
                if not isinstance(tasks, list):
                    tasks = [tasks]
                
                # Validate and clean tasks with improved logic
                validated_tasks = []
                for task in tasks:
                    if isinstance(task, dict) and "title" in task:
                        title = task.get("title", "").strip()
                        
                        # Skip if title is too short or seems invalid
                        if len(title) < 3:
                            continue
                        
                        # Skip if it looks like a completed task
                        if any(word in title.lower() for word in ["completed", "done", "finished", "sent", "received"]):
                            continue
                        
                        validated_task = {
                            "title": title,
                            "description": self._clean_description(task.get("description", "").strip()),
                            "consequences": task.get("consequences", "").strip(),
                            "confidence_score": self._validate_confidence(task.get("confidence_score", 1.0)),
                            "due_date": self._parse_due_date(task.get("due_date"), dates),
                            "priority": self._validate_priority(task.get("priority", 50)),
                            "estimated_duration": self._validate_duration(task.get("estimated_duration")),
                            "goal_category": task.get("goal_category"),
                            "institution_name": task.get("institution_name"),
                            "ai_generated": True,
                            "is_approved": False  # New tasks need approval
                        }
                        
                        if validated_task["title"]:
                            validated_tasks.append(validated_task)
                
                # Remove duplicates based on title similarity
                validated_tasks = self._deduplicate_tasks(validated_tasks)
                
                logger.info(f"Extracted {len(validated_tasks)} tasks from {source_type}")
                return validated_tasks
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse LLM task response: {e}, using NLP fallback")
                logger.debug(f"LLM response was: {response[:500]}")
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
    
    def _parse_due_date(self, date_str: Optional[str], extracted_dates: Optional[List[Dict[str, Any]]] = None) -> Optional[str]:
        """Parse due date string to ISO format with improved parsing"""
        if not date_str:
            # Try to use extracted dates if available
            if extracted_dates and len(extracted_dates) > 0:
                parsed_date = extracted_dates[0].get("parsed")
                if parsed_date:
                    return parsed_date.isoformat() if hasattr(parsed_date, 'isoformat') else str(parsed_date)
            return None
        
        try:
            from dateutil import parser
            # Try parsing the date string
            dt = parser.parse(date_str)
            # Ensure it's in the future (for due dates)
            now = datetime.now()
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=now.tzinfo)
            return dt.isoformat()
        except Exception as e:
            logger.debug(f"Failed to parse date '{date_str}': {e}")
            # Fallback to extracted dates
            if extracted_dates and len(extracted_dates) > 0:
                parsed_date = extracted_dates[0].get("parsed")
                if parsed_date:
                    return parsed_date.isoformat() if hasattr(parsed_date, 'isoformat') else str(parsed_date)
            return None
    
    def _clean_description(self, description: str) -> Optional[str]:
        """Clean and validate description"""
        if not description:
            return None
        desc = description.strip()
        if len(desc) < 5:  # Too short to be useful
            return None
        if len(desc) > 1000:  # Truncate very long descriptions
            return desc[:1000] + "..."
        return desc
    
    def _validate_duration(self, duration: Any) -> Optional[int]:
        """Validate estimated duration in minutes"""
        if duration is None:
            return None
        try:
            duration = int(duration)
            if duration < 1:
                return None
            if duration > 1440:  # More than 24 hours
                return 1440
            return duration
        except (ValueError, TypeError):
            return None
    
    def _deduplicate_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate or very similar tasks"""
        if len(tasks) <= 1:
            return tasks
        
        unique_tasks = []
        seen_titles = set()
        
        for task in tasks:
            title_lower = task["title"].lower().strip()
            # Simple deduplication - check for exact matches
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_tasks.append(task)
            else:
                # Check for very similar titles (fuzzy match)
                is_duplicate = False
                for seen_title in seen_titles:
                    # Simple similarity check
                    if self._titles_similar(title_lower, seen_title):
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    seen_titles.add(title_lower)
                    unique_tasks.append(task)
        
        return unique_tasks
    
    def _titles_similar(self, title1: str, title2: str, threshold: float = 0.8) -> bool:
        """Check if two task titles are similar"""
        # Simple word-based similarity
        words1 = set(title1.split())
        words2 = set(title2.split())
        
        if not words1 or not words2:
            return False
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        similarity = len(intersection) / len(union) if union else 0
        return similarity >= threshold
    
    def _validate_priority(self, priority: Any) -> int:
        """Validate and normalize priority (0-100)"""
        try:
            priority = int(priority)
            return max(0, min(100, priority))
        except (ValueError, TypeError):
            return 50

    def _validate_confidence(self, confidence: Any) -> float:
        """Validate and normalize confidence score (0.0-1.0)"""
        try:
            confidence = float(confidence)
            return max(0.0, min(1.0, confidence))
        except (ValueError, TypeError):
            return 1.0


# Global task generator instance
task_generator = TaskGenerator()

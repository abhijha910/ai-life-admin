"""Action Engine for smart follow-ups and automated suggestions"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.models.task import Task
from app.models.email import EmailItem
from app.ai_engine.llm_client import llm_client
import structlog

logger = structlog.get_logger()

class ActionEngine:
    """Take responsibility for digital life by suggesting and acting"""

    async def suggest_follow_ups(self, user_id: str, emails: List[EmailItem]) -> List[Dict[str, Any]]:
        """Detect stalled email threads and suggest follow-up drafts"""
        suggestions = []
        now = datetime.now()
        
        for email in emails:
            # Check if email is from the user (sent) and has no reply for > 3 days
            if email.is_sent and not email.has_reply:
                time_since_sent = (now - email.received_at).days
                if time_since_sent >= 3:
                    draft = await self._generate_follow_up_draft(email)
                    suggestions.append({
                        "type": "follow_up",
                        "source_id": str(email.id),
                        "title": f"Follow up with {email.recipient}",
                        "description": f"No response received for {time_since_sent} days.",
                        "draft_content": draft,
                        "action_label": "Send Follow-up"
                    })
        
        return suggestions

    async def _generate_follow_up_draft(self, email: EmailItem) -> str:
        """Use LLM to generate a polite follow-up draft"""
        prompt = f"""Generate a polite, professional follow-up email for this thread:
Recipient: {email.recipient}
Subject: {email.subject}
Original message: {email.content[:500]}

The follow-up should be concise and mention that we are checking in on the status of the previous email."""
        
        response = await llm_client.generate(prompt=prompt)
        return response.strip()

    def detect_stalled_tasks(self, tasks: List[Task]) -> List[Dict[str, Any]]:
        """Identify tasks that have been in 'in_progress' for too long"""
        suggestions = []
        now = datetime.now()
        
        for task in tasks:
            if task.status == "in_progress" and task.updated_at:
                days_stalled = (now - task.updated_at.replace(tzinfo=None)).days
                if days_stalled >= 5:
                    suggestions.append({
                        "type": "stalled_task",
                        "task_id": str(task.id),
                        "title": f"Task stalled: {task.title}",
                        "description": f"This task has been in progress for {days_stalled} days without updates.",
                        "action_label": "Update Status"
                    })
        
        return suggestions

action_engine = ActionEngine()

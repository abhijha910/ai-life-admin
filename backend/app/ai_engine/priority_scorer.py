"""Priority scoring algorithm"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()


class PriorityScorer:
    """Calculate priority scores for tasks"""
    
    def calculate_priority(
        self,
        due_date: Optional[datetime],
        created_at: datetime,
        source_type: Optional[str] = None,
        user_feedback: Optional[Dict[str, Any]] = None
    ) -> int:
        """Calculate priority score (0-100)"""
        score = 50  # Base score
        
        # Urgency factor (based on due date)
        if due_date:
            now = datetime.now(due_date.tzinfo) if due_date.tzinfo else datetime.now()
            time_until_due = (due_date - now).total_seconds() / 3600  # hours
            
            if time_until_due < 0:
                score += 30  # Overdue
            elif time_until_due < 24:
                score += 25  # Due today
            elif time_until_due < 72:
                score += 15  # Due in 3 days
            elif time_until_due < 168:
                score += 5  # Due in a week
            else:
                score -= 10  # Far in future
        
        # Source type factor
        if source_type == "email":
            score += 5  # Emails are slightly more important
        elif source_type == "document":
            score += 3
        
        # Age factor (older tasks get slightly higher priority)
        age_days = (datetime.now() - created_at.replace(tzinfo=None)).days
        if age_days > 7:
            score += 5
        
        # User feedback factor
        if user_feedback:
            if user_feedback.get("important"):
                score += 20
            if user_feedback.get("starred"):
                score += 15
        
        # Normalize to 0-100
        return max(0, min(100, int(score)))
    
    def calculate_email_priority(
        self,
        email_text: str,
        received_at: datetime,
        sender: Optional[str] = None,
        subject: Optional[str] = None
    ) -> int:
        """Calculate priority for email"""
        score = 50
        
        # Check for urgent keywords
        urgent_keywords = ["urgent", "asap", "immediately", "deadline", "important", "action required"]
        text_lower = (email_text + " " + (subject or "")).lower()
        
        urgent_count = sum(1 for keyword in urgent_keywords if keyword in text_lower)
        score += urgent_count * 5
        
        # Sender importance (could be enhanced with user's contact list)
        important_domains = ["@company.com", "@work.com"]  # Example
        if sender and any(domain in sender.lower() for domain in important_domains):
            score += 10
        
        # Recency (recent emails slightly higher priority)
        hours_old = (datetime.now() - received_at.replace(tzinfo=None)).total_seconds() / 3600
        if hours_old < 1:
            score += 5
        
        return max(0, min(100, int(score)))


# Global priority scorer instance
priority_scorer = PriorityScorer()

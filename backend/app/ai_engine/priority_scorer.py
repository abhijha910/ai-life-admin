"""Priority scoring algorithm with enhanced factors"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import structlog
import re

logger = structlog.get_logger()


class PriorityScorer:
    """Calculate priority scores for tasks with multiple factors"""
    
    def calculate_priority(
        self,
        due_date: Optional[datetime],
        created_at: datetime,
        source_type: Optional[str] = None,
        user_feedback: Optional[Dict[str, Any]] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        sender: Optional[str] = None
    ) -> int:
        """Calculate priority score (0-100) with enhanced factors"""
        score = 50  # Base score
        
        # 1. Urgency factor (based on due date) - Enhanced
        if due_date:
            now = datetime.now(due_date.tzinfo) if due_date.tzinfo else datetime.now()
            time_until_due = (due_date - now).total_seconds() / 3600  # hours
            
            if time_until_due < 0:
                score += 35  # Overdue - very urgent
                # More overdue = higher priority
                days_overdue = abs(time_until_due) / 24
                score += min(int(days_overdue * 2), 15)  # Cap at +15
            elif time_until_due < 6:
                score += 30  # Due within 6 hours - very urgent
            elif time_until_due < 24:
                score += 25  # Due today
            elif time_until_due < 48:
                score += 20  # Due tomorrow
            elif time_until_due < 72:
                score += 15  # Due in 3 days
            elif time_until_due < 168:
                score += 5  # Due in a week
            else:
                score -= 10  # Far in future
        
        # 2. Source type factor - Enhanced
        if source_type == "email":
            score += 8  # Emails are more important
        elif source_type == "document":
            score += 5
        elif source_type == "calendar":
            score += 10  # Calendar events are important
        
        # 3. Keyword analysis - NEW
        text = f"{title or ''} {description or ''}".lower()
        urgent_keywords = {
            "urgent": 15, "asap": 20, "immediately": 15, "critical": 15,
            "deadline": 10, "important": 8, "action required": 12,
            "review by": 8, "submit by": 10, "respond by": 8
        }
        
        for keyword, weight in urgent_keywords.items():
            if keyword in text:
                score += weight
                break  # Only count once
        
        # 4. Sender importance - Enhanced
        if sender:
            # Check for important domains
            important_domains = ["@company.com", "@work.com", "@manager", "@boss"]
            if any(domain in sender.lower() for domain in important_domains):
                score += 12
            
            # Check for VIP senders (could be from user settings)
            # For now, check for common patterns
            if any(word in sender.lower() for word in ["ceo", "director", "manager", "lead"]):
                score += 8
        
        # 5. Age factor - Enhanced
        age_days = (datetime.now() - created_at.replace(tzinfo=None)).days
        if age_days > 14:
            score += 10  # Very old tasks need attention
        elif age_days > 7:
            score += 5
        
        # 6. User feedback factor - Enhanced
        if user_feedback:
            if user_feedback.get("important"):
                score += 25  # User marked as important
            if user_feedback.get("starred"):
                score += 20  # User starred
            if user_feedback.get("pinned"):
                score += 15
            if user_feedback.get("priority_override"):
                # User manually set priority
                try:
                    override = int(user_feedback.get("priority_override"))
                    score = override  # Override with user's priority
                except (ValueError, TypeError):
                    pass
        
        # 7. Task complexity - NEW (based on description length and keywords)
        if description:
            desc_length = len(description)
            if desc_length > 500:
                score += 3  # Complex tasks might be more important
            if any(word in description.lower() for word in ["meeting", "call", "presentation"]):
                score += 5  # Communication tasks are important
        
        # 8. Time-based patterns - NEW (could be enhanced with ML)
        current_hour = datetime.now().hour
        # Tasks created during work hours might be more urgent
        if 9 <= current_hour <= 17:
            score += 2
        
        # Normalize to 0-100
        return max(0, min(100, int(score)))
    
    def calculate_email_priority(
        self,
        email_text: str,
        received_at: datetime,
        sender: Optional[str] = None,
        subject: Optional[str] = None,
        is_read: bool = False,
        is_important: bool = False
    ) -> int:
        """Calculate priority for email with enhanced factors"""
        score = 50
        
        # 1. Check for urgent keywords - Enhanced
        urgent_keywords = {
            "urgent": 15, "asap": 20, "immediately": 15, "critical": 15,
            "deadline": 12, "important": 10, "action required": 12,
            "fyi": -5, "no action needed": -10, "for your information": -5
        }
        
        text_lower = (email_text + " " + (subject or "")).lower()
        for keyword, weight in urgent_keywords.items():
            if keyword in text_lower:
                score += weight
                break  # Only count strongest match
        
        # 2. Subject line analysis - NEW
        if subject:
            subject_lower = subject.lower()
            # Check for action verbs
            action_verbs = ["review", "approve", "sign", "submit", "respond", "reply", "call"]
            if any(verb in subject_lower for verb in action_verbs):
                score += 8
            
            # Check for question marks (might need response)
            if "?" in subject:
                score += 5
        
        # 3. Sender importance - Enhanced
        if sender:
            # Important domains
            important_domains = ["@company.com", "@work.com", "@manager", "@boss", "@hr"]
            if any(domain in sender.lower() for domain in important_domains):
                score += 12
            
            # VIP senders
            if any(word in sender.lower() for word in ["ceo", "director", "manager", "lead", "hr", "finance"]):
                score += 10
            
            # Check if sender is user themselves (sent emails)
            if "sent" in sender.lower() or "from: me" in sender.lower():
                score -= 5
        
        # 4. Recency - Enhanced
        hours_old = (datetime.now() - received_at.replace(tzinfo=None)).total_seconds() / 3600
        if hours_old < 1:
            score += 10  # Very recent
        elif hours_old < 6:
            score += 5
        elif hours_old > 168:  # Older than a week
            score -= 5
        
        # 5. Read status - NEW
        if is_read:
            score -= 5  # Read emails slightly lower priority
        else:
            score += 8  # Unread emails higher priority
        
        # 6. Important flag - NEW
        if is_important:
            score += 20
        
        # 7. Email length - NEW (longer emails might be more important)
        if len(email_text) > 1000:
            score += 3
        
        # 8. Check for attachments - NEW (could indicate importance)
        if "attachment" in text_lower or "attached" in text_lower:
            score += 5
        
        # 9. Check for meeting requests - NEW
        if any(word in text_lower for word in ["meeting", "calendar", "schedule", "appointment"]):
            score += 8
        
        # 10. Check for follow-up indicators - NEW
        if any(word in text_lower for word in ["follow up", "reminder", "second request", "still waiting"]):
            score += 12
        
        return max(0, min(100, int(score)))


# Global priority scorer instance
priority_scorer = PriorityScorer()

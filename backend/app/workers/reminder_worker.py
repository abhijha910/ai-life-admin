"""Reminder worker"""
from app.workers.celery_app import celery_app
from app.database import SessionLocal
from app.models.reminder import Reminder
from app.services.notification_service import notification_service
from sqlalchemy import select, and_
from datetime import datetime

@celery_app.task(name="check_and_send_reminders")
def check_and_send_reminders():
    """Check for due reminders and send notifications"""
    db = SessionLocal()
    try:
        now = datetime.now()
        
        result = db.execute(
            select(Reminder).where(
                and_(
                    Reminder.trigger_at <= now,
                    Reminder.is_sent == False
                )
            )
        )
        reminders = result.scalars().all()
        
        sent_count = 0
        for reminder in reminders:
            # Create notification
            notification_service.create_notification(
                db,
                reminder.user,
                "reminder",
                reminder.title,
                reminder.message
            )
            
            reminder.is_sent = True
            reminder.sent_at = now
            sent_count += 1
        
        db.commit()
        return {"status": "success", "reminders_sent": sent_count}
    except Exception as e:
        return {"status": "error", "error": str(e)}
    finally:
        db.close()

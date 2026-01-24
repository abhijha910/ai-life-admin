"""AI processing worker"""
from app.workers.celery_app import celery_app

@celery_app.task(name="process_email_with_ai")
def process_email_with_ai(email_id: str):
    """Process email with AI for task extraction"""
    # Placeholder for AI processing
    return {"status": "success", "email_id": email_id}

@celery_app.task(name="generate_daily_plan")
def generate_daily_plan(user_id: str, target_date: str):
    """Generate daily plan for user"""
    # Placeholder for plan generation
    return {"status": "success", "user_id": user_id, "date": target_date}

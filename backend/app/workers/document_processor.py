"""Document processing worker"""
from app.workers.celery_app import celery_app
from app.database import SessionLocal
from app.models.document import Document
from sqlalchemy import select
from datetime import datetime
import uuid

@celery_app.task(name="process_document")
def process_document(document_id: str):
    """Process a document with OCR and AI"""
    db = SessionLocal()
    try:
        result = db.execute(
            select(Document).where(Document.id == uuid.UUID(document_id))
        )
        document = result.scalar_one_or_none()
        
        if not document:
            return {"status": "error", "reason": "Document not found"}
        
        # Process document (would call document_service.process_document)
        # This is a placeholder - actual processing would happen here
        document.processed_at = datetime.now()
        db.commit()
        
        return {"status": "success", "document_id": document_id}
    except Exception as e:
        return {"status": "error", "error": str(e)}
    finally:
        db.close()

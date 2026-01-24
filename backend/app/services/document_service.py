"""Document service"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from datetime import datetime
import uuid
import os
from app.models.document import Document
from app.models.user import User
from app.utils.s3_client import upload_file, generate_presigned_url, delete_file
from app.ai_engine.ocr_pipeline import ocr_pipeline
from app.ai_engine.classifier import document_classifier
import structlog

logger = structlog.get_logger()


class DocumentService:
    """Document service"""
    
    async def upload_document(
        self,
        db: AsyncSession,
        user: User,
        file_content: bytes,
        file_name: str,
        mime_type: str
    ) -> Document:
        """Upload and process document"""
        try:
            # Generate S3 key
            file_type = os.path.splitext(file_name)[1][1:].lower()
            s3_key = f"users/{user.id}/{uuid.uuid4()}/{file_name}"
            
            # Upload to S3
            if not upload_file(file_content, s3_key, mime_type):
                raise ValueError("Failed to upload file to S3")
            
            # Create document record
            document = Document(
                id=uuid.uuid4(),
                user_id=user.id,
                file_name=file_name,
                file_type=file_type,
                file_size=len(file_content),
                s3_key=s3_key,
                mime_type=mime_type
            )
            
            db.add(document)
            await db.commit()
            await db.refresh(document)
            
            # Trigger async processing (would be done by worker in production)
            # For now, process synchronously
            await self.process_document(db, document, file_content)
            
            return document
        except Exception as e:
            logger.error("Document upload error", error=str(e))
            raise
    
    async def process_document(
        self,
        db: AsyncSession,
        document: Document,
        file_content: Optional[bytes] = None
    ) -> Document:
        """Process document with OCR and AI"""
        try:
            # Get file content if not provided
            if file_content is None:
                # In production, download from S3
                # For now, assume file_content is available
                pass
            
            # Extract text with OCR
            ocr_text, success = ocr_pipeline.extract_text(
                file_content,
                document.file_type,
                document.mime_type or ""
            )
            
            if success:
                document.ocr_text = ocr_text
                
                # Classify document
                classification = await document_classifier.classify(
                    ocr_text,
                    document.file_name
                )
                document.ai_classification = classification.get("category")
                
                # Extract structured data (could use AI here)
                document.ai_extracted_data = {
                    "classification_confidence": classification.get("confidence", 0.5)
                }
            
            document.processed_at = datetime.now()
            await db.commit()
            await db.refresh(document)
            
            return document
        except Exception as e:
            logger.error("Document processing error", error=str(e))
            raise
    
    async def get_document(
        self,
        db: AsyncSession,
        document_id: str,
        user: User
    ) -> Optional[Document]:
        """Get document by ID"""
        result = await db.execute(
            select(Document).where(
                Document.id == uuid.UUID(document_id),
                Document.user_id == user.id
            )
        )
        document = result.scalar_one_or_none()
        
        if document:
            # Generate presigned URL
            document.presigned_url = generate_presigned_url(document.s3_key)
        
        return document
    
    async def list_documents(
        self,
        db: AsyncSession,
        user: User,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[Document], int]:
        """List user's documents"""
        offset = (page - 1) * page_size
        
        # Get total count
        count_result = await db.execute(
            select(Document).where(Document.user_id == user.id)
        )
        total = len(count_result.scalars().all())
        
        # Get paginated results
        result = await db.execute(
            select(Document)
            .where(Document.user_id == user.id)
            .order_by(Document.uploaded_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        documents = result.scalars().all()
        
        # Generate presigned URLs
        for doc in documents:
            doc.presigned_url = generate_presigned_url(doc.s3_key)
        
        return documents, total
    
    async def delete_document(
        self,
        db: AsyncSession,
        document_id: str,
        user: User
    ) -> bool:
        """Delete document"""
        result = await db.execute(
            select(Document).where(
                Document.id == uuid.UUID(document_id),
                Document.user_id == user.id
            )
        )
        document = result.scalar_one_or_none()
        
        if document:
            # Delete from S3
            delete_file(document.s3_key)
            
            # Delete from database
            await db.delete(document)
            await db.commit()
            return True
        
        return False


# Global document service instance
document_service = DocumentService()

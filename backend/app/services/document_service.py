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
            file_type = os.path.splitext(file_name)[1][1:].lower() if '.' in file_name else 'unknown'
            s3_key = f"users/{user.id}/{uuid.uuid4()}/{file_name}"
            
            # Try to upload to S3, but don't fail if S3 is not configured
            s3_uploaded = False
            if upload_file(file_content, s3_key, mime_type):
                s3_uploaded = True
                logger.info("File uploaded to S3", s3_key=s3_key)
            else:
                # S3 not configured or upload failed - use local storage as fallback
                logger.warning("S3 upload failed or not configured, using local storage fallback")
                # Create local storage directory if it doesn't exist
                local_storage_dir = os.path.join(os.getcwd(), "uploads", "documents", str(user.id))
                os.makedirs(local_storage_dir, exist_ok=True)
                
                # Save file locally
                local_file_path = os.path.join(local_storage_dir, f"{uuid.uuid4()}_{file_name}")
                with open(local_file_path, 'wb') as f:
                    f.write(file_content)
                
                # Update s3_key to local path for reference
                s3_key = f"local:{local_file_path}"
            
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
            try:
                await self.process_document(db, document, file_content)
            except Exception as process_error:
                # Don't fail upload if processing fails
                logger.warning("Document processing failed", error=str(process_error), document_id=str(document.id))
            
            return document
        except Exception as e:
            logger.error("Document upload error", error=str(e), exc_info=True)
            raise ValueError(f"Failed to upload document: {str(e)}")
    
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
            # Generate presigned URL or local file URL
            if document.s3_key.startswith("local:"):
                # URL encode the filename for proper handling
                from urllib.parse import quote
                encoded_filename = quote(document.file_name, safe='')
                document.presigned_url = f"/api/v1/documents/file/{encoded_filename}"
            else:
                document.presigned_url = generate_presigned_url(document.s3_key)
        
        return document
    
    async def list_documents(
        self,
        db: AsyncSession,
        user: User,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None
    ) -> tuple[List[Document], int]:
        """List user's documents"""
        from sqlalchemy import or_, func
        
        offset = (page - 1) * page_size
        
        # Build base query
        base_query = select(Document).where(Document.user_id == user.id)
        
        # Add search filter
        if search:
            search_pattern = f"%{search.lower()}%"
            base_query = base_query.where(
                or_(
                    func.lower(func.coalesce(Document.file_name, '')).like(search_pattern),
                    func.lower(func.coalesce(Document.ai_summary, '')).like(search_pattern),
                    func.lower(func.coalesce(Document.ai_classification, '')).like(search_pattern),
                    func.lower(func.coalesce(Document.ocr_text, '')).like(search_pattern)
                )
            )
        
        # Get total count
        count_query = select(func.count(Document.id)).where(Document.user_id == user.id)
        if search:
            search_pattern = f"%{search.lower()}%"
            count_query = count_query.where(
                or_(
                    func.lower(func.coalesce(Document.file_name, '')).like(search_pattern),
                    func.lower(func.coalesce(Document.ai_summary, '')).like(search_pattern),
                    func.lower(func.coalesce(Document.ai_classification, '')).like(search_pattern),
                    func.lower(func.coalesce(Document.ocr_text, '')).like(search_pattern)
                )
            )
        total_result = await db.execute(count_query)
        total = total_result.scalar_one() or 0
        
        # Get paginated results
        result = await db.execute(
            base_query
            .order_by(Document.uploaded_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        documents = result.scalars().all()
        
        # Generate presigned URLs or local file URLs
        from urllib.parse import quote
        for doc in documents:
            if doc.s3_key.startswith("local:"):
                # For local files, generate a download URL with URL encoding
                encoded_filename = quote(doc.file_name, safe='')
                doc.presigned_url = f"/api/v1/documents/file/{encoded_filename}"
            else:
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

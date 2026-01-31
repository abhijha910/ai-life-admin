"""Document routes"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.document import DocumentUploadResponse, DocumentResponse, DocumentListResponse
from app.services.document_service import document_service
from app.services.task_service import task_service
from app.schemas.task import TaskCreate
from app.ai_engine.task_generator import task_generator
from datetime import datetime

router = APIRouter()


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload a document"""
    import os
    import structlog
    
    logger = structlog.get_logger()
    
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File name is required"
            )
        
        file_content = await file.read()
        
        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if len(file_content) > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum allowed size of {max_size / 1024 / 1024}MB"
            )
        
        # Validate file type
        allowed_extensions = ['.pdf', '.doc', '.docx', '.txt', '.jpg', '.jpeg', '.png', '.gif', '.webp']
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        document = await document_service.upload_document(
            db,
            current_user,
            file_content,
            file.filename,
            file.content_type or "application/octet-stream"
        )
        
        # Automatically process document and extract tasks after upload
        try:
            # Process document (OCR + classification)
            document = await document_service.process_document(db, document, file_content)
            
            # Extract tasks from document if OCR text available
            if document.ocr_text:
                tasks = await task_generator.extract_tasks(
                    document.ocr_text,
                    "document",
                    context={
                        "document_id": str(document.id),
                        "file_name": document.file_name,
                        "file_type": document.file_type,
                        "classification": document.ai_classification
                    }
                )
                
                # Create tasks automatically
                for task_data in tasks:
                    try:
                        # Resolve entities (Goal, etc.)
                        resolved_data = await task_service.resolve_ai_task_entities(db, current_user, task_data)
                        
                        task_create = TaskCreate(
                            title=resolved_data["title"],
                            description=resolved_data.get("description"),
                            consequences=resolved_data.get("consequences"),
                            due_date=datetime.fromisoformat(resolved_data["due_date"]) if resolved_data.get("due_date") else None,
                            priority=resolved_data.get("priority", 50),
                            estimated_duration=resolved_data.get("estimated_duration"),
                            goal_id=resolved_data.get("goal_id"),
                            is_approved=False,  # AI tasks need approval (Level 7)
                            ai_generated=True
                        )
                        await task_service.create_task(
                            db,
                            current_user,
                            task_create,
                            source_type="document",
                            source_id=str(document.id)
                        )
                    except Exception as task_error:
                        logger.warning(f"Failed to create task from document: {task_error}")
                        continue
        except Exception as process_error:
            # Don't fail upload if processing fails
            logger.warning(f"Document processing failed after upload: {process_error}")
        
        # Convert to response format
        return DocumentUploadResponse(
            id=str(document.id),
            file_name=document.file_name,
            file_type=document.file_type,
            file_size=document.file_size,
            uploaded_at=document.uploaded_at,
            processed_at=document.processed_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Document upload error", error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to upload document: {str(e)}"
        )


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's documents"""
    documents, total = await document_service.list_documents(
        db,
        current_user,
        page,
        page_size,
        search
    )
    
    # Convert to response format - explicitly convert UUIDs to strings
    document_responses = []
    for doc in documents:
        # Get presigned URL if available
        presigned_url = getattr(doc, 'presigned_url', None)
        if not presigned_url:
            # Generate URL if not already set
            if doc.s3_key.startswith("local:"):
                presigned_url = f"/api/v1/documents/file/{doc.file_name}"
            else:
                from app.utils.s3_client import generate_presigned_url
                presigned_url = generate_presigned_url(doc.s3_key)
        
        document_responses.append(
            DocumentResponse(
                id=str(doc.id),  # Convert UUID to string
                file_name=doc.file_name,
                file_type=doc.file_type,
                file_size=doc.file_size,
                mime_type=doc.mime_type,
                ocr_text=doc.ocr_text,
                ai_summary=doc.ai_summary,
                ai_classification=doc.ai_classification,
                ai_extracted_data=doc.ai_extracted_data,
                uploaded_at=doc.uploaded_at,
                processed_at=doc.processed_at,
                presigned_url=presigned_url
            )
        )
    
    return DocumentListResponse(
        documents=document_responses,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get document details"""
    document = await document_service.get_document(db, document_id, current_user)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Get presigned URL if available
    presigned_url = getattr(document, 'presigned_url', None)
    if not presigned_url:
        if document.s3_key.startswith("local:"):
            presigned_url = f"/api/v1/documents/file/{document.file_name}"
        else:
            from app.utils.s3_client import generate_presigned_url
            presigned_url = generate_presigned_url(document.s3_key)
    
    # Convert to response format - explicitly convert UUID to string
    return DocumentResponse(
        id=str(document.id),  # Convert UUID to string
        file_name=document.file_name,
        file_type=document.file_type,
        file_size=document.file_size,
        mime_type=document.mime_type,
        ocr_text=document.ocr_text,
        ai_summary=document.ai_summary,
        ai_classification=document.ai_classification,
        ai_extracted_data=document.ai_extracted_data,
        uploaded_at=document.uploaded_at,
        processed_at=document.processed_at,
        presigned_url=presigned_url
    )


@router.post("/{document_id}/process")
async def process_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Trigger document processing"""
    document = await document_service.get_document(db, document_id, current_user)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Process document (in production, this would be async via worker)
    document = await document_service.process_document(db, document)
    
    # Extract tasks from document if OCR text available
    if document.ocr_text:
        tasks = await task_generator.extract_tasks(
            document.ocr_text,
            "document",
            context={
                "document_id": str(document.id),
                "file_name": document.file_name,
                "file_type": document.file_type,
                "classification": document.ai_classification
            }
        )
        
        # Create tasks
        for task_data in tasks:
            # Resolve entities (Goal, etc.)
            resolved_data = await task_service.resolve_ai_task_entities(db, current_user, task_data)
            
            task_create = TaskCreate(
                title=resolved_data["title"],
                description=resolved_data.get("description"),
                consequences=resolved_data.get("consequences"),
                due_date=datetime.fromisoformat(resolved_data["due_date"]) if resolved_data.get("due_date") else None,
                priority=resolved_data.get("priority", 50),
                estimated_duration=resolved_data.get("estimated_duration"),
                goal_id=resolved_data.get("goal_id"),
                is_approved=False,
                ai_generated=True
            )
            await task_service.create_task(
                db,
                current_user,
                task_create,
                source_type="document",
                source_id=str(document.id)
            )
    
    return {"message": "Document processed successfully", "document": document}


@router.get("/file/{filename}")
async def serve_local_file(
    filename: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Serve local file (fallback when S3 is not configured)"""
    from fastapi.responses import FileResponse, StreamingResponse
    import os
    from pathlib import Path
    import urllib.parse
    
    # Decode URL-encoded filename
    filename = urllib.parse.unquote(filename)
    
    # Find document by filename
    from app.models.document import Document
    from sqlalchemy import select
    import uuid
    
    # Search for document with this filename
    result = await db.execute(
        select(Document).where(
            Document.user_id == current_user.id,
            Document.file_name == filename
        ).order_by(Document.uploaded_at.desc())
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Check if it's a local file
    if document.s3_key.startswith("local:"):
        local_path = document.s3_key.replace("local:", "")
        if os.path.exists(local_path):
            # Determine media type
            media_type = document.mime_type or "application/octet-stream"
            
            # For PDFs and images, return as FileResponse for inline viewing
            if media_type in ["application/pdf", "image/jpeg", "image/png", "image/gif", "image/webp"]:
                return FileResponse(
                    local_path,
                    media_type=media_type,
                    filename=document.file_name,
                    headers={
                        "Content-Disposition": f'inline; filename="{document.file_name}"'
                    }
                )
            else:
                # For other files, force download
                return FileResponse(
                    local_path,
                    media_type=media_type,
                    filename=document.file_name,
                    headers={
                        "Content-Disposition": f'attachment; filename="{document.file_name}"'
                    }
                )
    
    # If it's an S3 file, redirect to presigned URL or return error
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="File not found on local storage"
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete document"""
    success = await document_service.delete_document(db, document_id, current_user)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

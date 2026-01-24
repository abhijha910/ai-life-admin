"""Document routes"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
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
    try:
        file_content = await file.read()
        document = await document_service.upload_document(
            db,
            current_user,
            file_content,
            file.filename,
            file.content_type or "application/octet-stream"
        )
        return document
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's documents"""
    documents, total = await document_service.list_documents(
        db,
        current_user,
        page,
        page_size
    )
    
    return DocumentListResponse(
        documents=documents,
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
    
    return document


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
            {"document_id": str(document.id)}
        )
        
        # Create tasks
        for task_data in tasks:
            task_create = TaskCreate(
                title=task_data["title"],
                description=task_data.get("description"),
                due_date=datetime.fromisoformat(task_data["due_date"]) if task_data.get("due_date") else None,
                priority=task_data.get("priority", 50),
                estimated_duration=task_data.get("estimated_duration")
            )
            await task_service.create_task(
                db,
                current_user,
                task_create,
                source_type="document",
                source_id=str(document.id)
            )
    
    return {"message": "Document processed successfully", "document": document}


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

"""Document API routes."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db, Document
from app.models.schemas import DocumentResponse, ExportRequest

router = APIRouter()


@router.get("", response_model=list[DocumentResponse])
async def list_documents(
    doc_type: str = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List all documents."""
    query = select(Document).order_by(Document.created_at.desc())
    
    if doc_type:
        query = query.where(Document.doc_type == doc_type)
    
    result = await db.execute(query.offset(offset).limit(limit))
    documents = result.scalars().all()
    
    return [
        DocumentResponse(
            id=doc.id,
            title=doc.title,
            doc_type=doc.doc_type,
            content=doc.content,
            format=doc.format,
            created_at=doc.created_at,
            metadata=doc.metadata_ or {},
        )
        for doc in documents
    ]


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific document."""
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentResponse(
        id=document.id,
        title=document.title,
        doc_type=document.doc_type,
        content=document.content,
        format=document.format,
        created_at=document.created_at,
        metadata=document.metadata_ or {},
    )


@router.post("/{document_id}/export")
async def export_document(
    document_id: str,
    data: ExportRequest,
    db: AsyncSession = Depends(get_db),
):
    """Export document to specified format."""
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # TODO: Implement actual export via DocumentService
    if data.format == "markdown":
        return Response(
            content=document.content,
            media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename={document.title}.md"},
        )
    elif data.format == "html":
        import markdown
        html_content = markdown.markdown(document.content)
        return Response(
            content=html_content,
            media_type="text/html",
            headers={"Content-Disposition": f"attachment; filename={document.title}.html"},
        )
    else:
        raise HTTPException(
            status_code=501,
            detail=f"Export to {data.format} not yet implemented",
        )

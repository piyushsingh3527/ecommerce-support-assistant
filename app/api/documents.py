from uuid import uuid4
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.db.models.document import KnowledgeDocument
from app.db.models.document_chunk import DocumentChunk
from app.db.models.user import User
from app.db.session import get_db
from app.services.document_loader import read_document
from app.services.chunking import chunk_text
from app.services.embedding import create_embedding


router = APIRouter(prefix="/documents", tags=["Knowledge Documents"])

STORAGE_DIR = Path("data/storage")
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    description: str | None = None,
    current_user: User = Depends(require_role("admin", "support")),
    db: Session = Depends(get_db),
):
    original_filename = Path(file.filename or "").name
    extension = Path(original_filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Allowed: PDF, DOCX, TXT, Markdown",
        )

    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    stored_filename = f"{uuid4().hex}{extension}"
    file_path = STORAGE_DIR / stored_filename

    with file_path.open("wb") as buffer:
        buffer.write(file.file.read())

    document_type = extension.lstrip(".")

    content = read_document(str(file_path))
    chunks = chunk_text(content)

    document = KnowledgeDocument(
        filename=original_filename,
        stored_filename=stored_filename,
        document_type=document_type,
        status="uploaded",
        description=description,
        content=content,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    for chunk in chunks:
        embedding = create_embedding(chunk)

        db_chunk = DocumentChunk(
            document_id=document.id,
            chunk_text=chunk,
            embedding=embedding,
        )

        db.add(db_chunk)

    db.commit()

    document.status = "indexed"
    db.commit()

    return {
        "message": "Document uploaded successfully",
        "document_id": document.id,
        "filename": document.filename,
        "document_type": document.document_type,
        "status": document.status,
    }


@router.get("/")
def get_documents(
    current_user: User = Depends(require_role("admin", "support")),
    db: Session = Depends(get_db),
):
    documents = (
        db.query(KnowledgeDocument)
        .order_by(KnowledgeDocument.id.desc())
        .all()
    )

    return documents


@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    document = (
        db.query(KnowledgeDocument)
        .filter(KnowledgeDocument.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    # Delete the stored file from the storage folder
    file_path = STORAGE_DIR / document.stored_filename

    if file_path.exists():
        file_path.unlink()

    # Delete document chunks first
    db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document.id
    ).delete()

    # Delete the document
    db.delete(document)
    db.commit()

    return {
        "message": "Document deleted successfully",
        "document_id": document_id,
    }


@router.post("/{document_id}/reindex")
def reindex_document(
    document_id: int,
    current_user: User = Depends(require_role("admin", "support")),
    db: Session = Depends(get_db),
):
    document = (
        db.query(KnowledgeDocument)
        .filter(KnowledgeDocument.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    # Read the document again from storage
    file_path = STORAGE_DIR / document.stored_filename

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Stored document file not found",
        )

    content = read_document(str(file_path))

    if not content.strip():
        raise HTTPException(
            status_code=400,
            detail="Document contains no readable text",
        )

    # Remove old chunks and embeddings
    db.query(DocumentChunk).filter(
        DocumentChunk.document_id == document.id
    ).delete()

    # Create new chunks and embeddings
    chunks = chunk_text(content)

    for chunk in chunks:
        embedding = create_embedding(chunk)

        db_chunk = DocumentChunk(
            document_id=document.id,
            chunk_text=chunk,
            embedding=embedding,
        )

        db.add(db_chunk)

    # Update document content and status
    document.content = content
    document.status = "indexed"

    db.commit()

    return {
        "message": "Document re-indexed successfully",
        "document_id": document.id,
        "filename": document.filename,
        "status": document.status,
        "chunks": len(chunks),
    }
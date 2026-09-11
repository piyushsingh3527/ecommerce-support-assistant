from sqlalchemy.orm import Session

from app.db.models.document_chunk import DocumentChunk
from app.db.models.document import KnowledgeDocument
from app.services.embedding import create_embedding


def search_similar_chunks(
    db: Session,
    query: str,
    limit: int = 3,
    max_distance: float = 0.5,
):
    query_embedding = create_embedding(query)

    results = (
        db.query(
            DocumentChunk,
            KnowledgeDocument.filename,
            DocumentChunk.embedding.cosine_distance(query_embedding).label("distance"),
        )
        .join(
            KnowledgeDocument,
            KnowledgeDocument.id == DocumentChunk.document_id,
        )
        .filter(DocumentChunk.embedding.is_not(None))
        .filter(
            DocumentChunk.embedding.cosine_distance(query_embedding) <= max_distance
        )
        .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
        .limit(limit)
        .all()
    )

    return [
        {
            "document_id": chunk.document_id,
            "source": filename,
            "content": chunk.chunk_text,
            "distance": float(distance),
        }
        for chunk, filename, distance in results
    ]
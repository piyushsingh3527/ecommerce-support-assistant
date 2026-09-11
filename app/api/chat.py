from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.db.models.user import User
from app.services.rag_service import answer_question

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/")
def chat(
    question: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    answer = answer_question(db, question, current_user)

    return {
        "question": question,
        "answer": answer,
    }
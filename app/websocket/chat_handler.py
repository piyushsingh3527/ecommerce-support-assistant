from fastapi import WebSocket
from app.db.session import SessionLocal
from app.services.rag_service import answer_question
from app.db.models.user import User
from app.core.config import settings
import jwt


async def websocket_chat(websocket: WebSocket):

    db = SessionLocal()

    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=1008)
        db.close()
        return

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )

        user_id = payload.get("sub")

        if not user_id:
            await websocket.close(code=1008)
            db.close()
            return

        current_user = (
            db.query(User)
            .filter(User.id == int(user_id))
            .first()
        )

        if not current_user:
            await websocket.close(code=1008)
            db.close()
            return

    except (jwt.InvalidTokenError, ValueError):
        await websocket.close(code=1008)
        db.close()
        return

    await websocket.accept()

    await websocket.send_text(
        "Connected to E-Commerce Support Assistant."
    )

    try:
        while True:
            question = await websocket.receive_text()

            answer = answer_question(
                db,
                question,
                current_user
            )

            await websocket.send_text(answer)

    finally:
        db.close()
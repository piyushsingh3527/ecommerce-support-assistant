import logging

from fastapi import Depends, FastAPI
from fastapi import WebSocket
from app.websocket.chat_handler import websocket_chat
from app.api.auth import router as auth_router
from app.api.categories import router as categories_router
from app.api.customers import router as customers_router
from app.api.products import router as products_router
from app.api.orders import router as orders_router
from app.api.tickets import router as tickets_router
from app.api.documents import router as documents_router
from app.api.chat import router as chat_router
from app.api.deps import get_current_user
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.models.user import User
from fastapi.staticfiles import StaticFiles


setup_logging()

logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(products_router)
app.include_router(customers_router)
app.include_router(orders_router)
app.include_router(tickets_router)
app.include_router(documents_router)
app.include_router(chat_router)

@app.get("/health")
def health_check():
    logger.info("Health check requested")
    return {"status": "ok"}


@app.get("/me")
def get_my_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
    }


@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_chat(websocket)
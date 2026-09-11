import re
from sqlalchemy.orm import Session

from app.services.retriever import search_similar_chunks
from app.services.prompt_builder import build_context
from app.llm.groq_provider import generate_answer
from app.services.order_service import get_order_for_user
from app.db.models.order_item import OrderItem
from app.db.models.product import Product


def extract_order_id(question: str):
    match = re.search(r"order\s+#?(\d+)", question.lower())

    if match:
        return int(match.group(1))

    return None


def answer_question(db: Session, question: str, current_user) -> str:
    order_id = extract_order_id(question)

    order_keywords = [
        "status",
        "total",
        "item",
        "items",
        "product",
        "quantity",
    ]

    is_order_question = any(
        keyword in question.lower()
        for keyword in order_keywords
    )

    if order_id and is_order_question:
        order = get_order_for_user(db, order_id, current_user)

        if not order:
            return "I could not find this order or you do not have permission to access it."

        items = (
            db.query(OrderItem, Product)
            .join(Product, Product.id == OrderItem.product_id)
            .filter(OrderItem.order_id == order.id)
            .all()
        )

        item_lines = []

        for item, product in items:
            item_lines.append(
                f"- {product.name} × {item.quantity}"
            )

        return (
            f"Order {order.id} information:\n"
            f"Status: {order.status}\n"
            f"Total: ₹{order.total}\n"
            f"Items:\n"
            + "\n".join(item_lines)
            + "\nSource: Order Database"
        )

    results = search_similar_chunks(db, question, limit=3)

    if not results:
        return "I could not find this information in the knowledge base."

    context = build_context(results)

    return generate_answer(question, context)
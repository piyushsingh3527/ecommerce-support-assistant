from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.db.models.customer import Customer
from app.db.models.order import Order
from app.db.models.order_access import OrderAccess
from app.db.models.order_item import OrderItem
from app.db.models.product import Product
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.order import OrderCreate, OrderStatusUpdate
from app.services.order_service import get_order_for_user


router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@router.post("/")
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Find the customer profile belonging to the logged-in user.
    customer = (
        db.query(Customer)
        .filter(Customer.user_id == current_user.id)
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer profile not found",
        )

    total = Decimal("0")

    # Create the order first.
    order = Order(
        customer_id=customer.id,
        status="pending",
        shipping_address=order_data.shipping_address,
        total=0,
    )

    db.add(order)
    db.flush()

    # Validate products, calculate total, and reduce stock.
    for item in order_data.items:
        product = (
            db.query(Product)
            .filter(Product.id == item.product_id)
            .first()
        )

        if not product:
            raise HTTPException(
                status_code=404,
                detail=f"Product {item.product_id} not found",
            )

        if product.stock < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for product {product.id}",
            )

        unit_price = Decimal(str(product.price))
        line_total = unit_price * item.quantity

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item.quantity,
            unit_price=unit_price,
            line_total=line_total,
        )

        db.add(order_item)

        product.stock -= item.quantity
        total += line_total

    # Store the server-calculated total.
    order.total = total

    db.commit()
    db.refresh(order)

    return {
        "id": order.id,
        "customer_id": order.customer_id,
        "total": order.total,
        "status": order.status,
        "shipping_address": order.shipping_address,
    }


@router.put("/{order_id}/status")
def update_order_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_role("admin", "support")
    ),
):
    # Check whether this admin/support user is allowed to access the order.
    order = get_order_for_user(
        db,
        order_id,
        current_user,
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail=(
                "Order not found or you do not have permission "
                "to access this order"
            ),
        )

    # Only these status changes are allowed.
    allowed_transitions = {
        "pending": ["confirmed"],
        "confirmed": ["shipped"],
        "shipped": ["delivered"],
        "delivered": [],
    }

    if status_data.status not in allowed_transitions.get(
        order.status,
        [],
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                f"Cannot change order status from "
                f"{order.status} to {status_data.status}"
            ),
        )

    order.status = status_data.status

    db.commit()
    db.refresh(order)

    return {
        "id": order.id,
        "status": order.status,
    }


@router.get("/")
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Customer -> only their own orders.
    if current_user.role == "customer":
        customer = (
            db.query(Customer)
            .filter(Customer.user_id == current_user.id)
            .first()
        )

        if not customer:
            raise HTTPException(
                status_code=404,
                detail="Customer profile not found",
            )

        orders = (
            db.query(Order)
            .filter(Order.customer_id == customer.id)
            .order_by(Order.created_at.desc())
            .all()
        )

    # Admin -> all orders.
    elif current_user.role == "admin":
        orders = (
            db.query(Order)
            .order_by(Order.created_at.desc())
            .all()
        )

    # Support -> only orders assigned through OrderAccess.
    elif current_user.role == "support":
        orders = (
            db.query(Order)
            .join(
                OrderAccess,
                OrderAccess.order_id == Order.id,
            )
            .filter(
                OrderAccess.support_user_id == current_user.id
            )
            .order_by(Order.created_at.desc())
            .all()
        )

    else:
        raise HTTPException(
            status_code=403,
            detail="You do not have permission to access orders",
        )

    result = []

    for order in orders:
        items = (
            db.query(OrderItem)
            .filter(OrderItem.order_id == order.id)
            .all()
        )

        result.append(
            {
                "id": order.id,
                "customer_id": order.customer_id,
                "total": order.total,
                "status": order.status,
                "shipping_address": order.shipping_address,
                "created_at": order.created_at,
                "items": [
                    {
                        "id": item.id,
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "unit_price": item.unit_price,
                        "line_total": item.line_total,
                    }
                    for item in items
                ],
            }
        )

    return result


@router.get("/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Customer -> own order only.
    # Support -> assigned orders only.
    # Admin -> any order.
    order = get_order_for_user(
        db,
        order_id,
        current_user,
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail=(
                "Order not found or you do not have permission "
                "to access this order"
            ),
        )

    items = (
        db.query(OrderItem)
        .filter(OrderItem.order_id == order.id)
        .all()
    )

    return {
        "id": order.id,
        "customer_id": order.customer_id,
        "total": order.total,
        "status": order.status,
        "shipping_address": order.shipping_address,
        "created_at": order.created_at,
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "line_total": item.line_total,
            }
            for item in items
        ],
    }


@router.delete("/{order_id}")
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Only a customer can delete their own order.
    customer = (
        db.query(Customer)
        .filter(Customer.user_id == current_user.id)
        .first()
    )

    if not customer:
        raise HTTPException(
            status_code=404,
            detail="Customer profile not found",
        )

    order = (
        db.query(Order)
        .filter(
            Order.id == order_id,
            Order.customer_id == customer.id,
        )
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    # Only pending orders can be deleted.
    if order.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending orders can be deleted",
        )

    items = (
        db.query(OrderItem)
        .filter(OrderItem.order_id == order.id)
        .all()
    )

    # Restore the stock for every product.
    for item in items:
        product = (
            db.query(Product)
            .filter(Product.id == item.product_id)
            .first()
        )

        if product:
            product.stock += item.quantity

    # Delete order items first.
    for item in items:
        db.delete(item)

    db.flush()

    # Then delete the order.
    db.delete(order)
    db.commit()

    return {
        "message": "Order deleted successfully",
    }
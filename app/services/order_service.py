from sqlalchemy.orm import Session

from app.db.models.customer import Customer
from app.db.models.order import Order
from app.db.models.order_access import OrderAccess


def get_order_for_user(db: Session, order_id: int, current_user):
    # Admin can access any order
    if current_user.role == "admin":
        return (
            db.query(Order)
            .filter(Order.id == order_id)
            .first()
        )

    # Support staff can access only permitted orders
    if current_user.role == "support":
        access = (
            db.query(OrderAccess)
            .filter(
                OrderAccess.order_id == order_id,
                OrderAccess.support_user_id == current_user.id,
            )
            .first()
        )

        if not access:
            return None

        return (
            db.query(Order)
            .filter(Order.id == order_id)
            .first()
        )

    # Customer can access only their own orders
    customer = (
        db.query(Customer)
        .filter(Customer.user_id == current_user.id)
        .first()
    )

    if not customer:
        return None

    return (
        db.query(Order)
        .filter(
            Order.id == order_id,
            Order.customer_id == customer.id,
        )
        .first()
    )
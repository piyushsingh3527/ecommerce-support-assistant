from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class OrderAccess(Base):
    __tablename__ = "order_access"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"),
        nullable=False,
    )

    support_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
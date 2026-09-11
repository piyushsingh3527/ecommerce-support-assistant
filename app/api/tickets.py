from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_role
from app.db.models.customer import Customer
from app.db.models.ticket import SupportTicket
from app.db.models.order import Order
from app.db.models.user import User
from app.db.session import get_db
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketStatusUpdate

router = APIRouter(prefix="/tickets", tags=["Support Tickets"])


@router.post("/")
def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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

    if ticket_data.order_id is not None:
        order = (
            db.query(Order)
            .filter(
                Order.id == ticket_data.order_id,
                Order.customer_id == customer.id,
            )
            .first()
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found",
            )

    ticket = SupportTicket(
        customer_id=customer.id,
        order_id=ticket_data.order_id,
        subject=ticket_data.subject,
        details=ticket_data.details,
        status="open",
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    return ticket


@router.get("/")
def get_my_tickets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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

    tickets = (
        db.query(SupportTicket)
        .filter(SupportTicket.customer_id == customer.id)
        .all()
    )

    return tickets


@router.get("/{ticket_id}")
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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

    ticket = (
        db.query(SupportTicket)
        .filter(
            SupportTicket.id == ticket_id,
            SupportTicket.customer_id == customer.id,
        )
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return ticket


@router.put("/{ticket_id}")
def update_ticket(
    ticket_id: int,
    ticket_data: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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

    ticket = (
        db.query(SupportTicket)
        .filter(
            SupportTicket.id == ticket_id,
            SupportTicket.customer_id == customer.id,
        )
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    if ticket_data.subject is not None:
        ticket.subject = ticket_data.subject

    if ticket_data.details is not None:
        ticket.details = ticket_data.details

    db.commit()
    db.refresh(ticket)

    return ticket


@router.delete("/{ticket_id}")
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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

    ticket = (
        db.query(SupportTicket)
        .filter(
            SupportTicket.id == ticket_id,
            SupportTicket.customer_id == customer.id,
        )
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    if ticket.status != "open":
        raise HTTPException(
            status_code=400,
            detail="Only open tickets can be deleted",
        )

    db.delete(ticket)
    db.commit()

    return {"message": "Ticket deleted successfully"}


@router.patch("/{ticket_id}/status")
def update_ticket_status(
    ticket_id: int,
    status_data: TicketStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin", "support")),
):
    ticket = (
        db.query(SupportTicket)
        .filter(SupportTicket.id == ticket_id)
        .first()
    )

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    allowed_transitions = {
        "open": ["in_progress"],
        "in_progress": ["resolved"],
        "resolved": [],
    }

    if status_data.status not in allowed_transitions:
        raise HTTPException(
            status_code=400,
            detail="Invalid ticket status",
        )

    if status_data.status not in allowed_transitions[ticket.status]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot change ticket status from {ticket.status} to {status_data.status}",
        )

    ticket.status = status_data.status

    db.commit()
    db.refresh(ticket)

    return ticket
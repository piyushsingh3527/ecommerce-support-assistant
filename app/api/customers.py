from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.models.customer import Customer
from app.db.session import get_db
from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
)


router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
)


@router.post("/", response_model=CustomerResponse)
def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    existing_customer = (
        db.query(Customer)
        .filter(Customer.user_id == current_user.id)
        .first()
    )

    if existing_customer:
        raise HTTPException(
            status_code=400,
            detail="Customer profile already exists",
        )

    customer = Customer(
        user_id=current_user.id,
        phone=customer_data.phone,
        address=customer_data.address,
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return customer


@router.get("/", response_model=CustomerResponse)
def get_my_customer_profile(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
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

    return customer


@router.put("/", response_model=CustomerResponse)
def update_my_customer_profile(
    customer_data: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
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

    customer.phone = customer_data.phone
    customer.address = customer_data.address

    db.commit()
    db.refresh(customer)

    return customer


@router.delete("/")
def delete_my_customer_profile(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
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

    db.delete(customer)
    db.commit()

    return {"message": "Customer profile deleted successfully"}
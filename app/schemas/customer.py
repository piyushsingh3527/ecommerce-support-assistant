from pydantic import BaseModel, ConfigDict


class CustomerCreate(BaseModel):
    phone: str | None = None
    address: dict | None = None


class CustomerUpdate(BaseModel):
    phone: str | None = None
    address: dict | None = None


class CustomerResponse(BaseModel):
    id: int
    user_id: int
    phone: str | None = None
    address: dict | None = None

    model_config = ConfigDict(from_attributes=True)
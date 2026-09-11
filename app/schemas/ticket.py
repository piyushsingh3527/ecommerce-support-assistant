from pydantic import BaseModel, ConfigDict


class TicketCreate(BaseModel):
    order_id: int | None = None
    subject: str
    details: str


class TicketUpdate(BaseModel):
    subject: str | None = None
    details: str | None = None


class TicketStatusUpdate(BaseModel):
    status: str


class TicketResponse(BaseModel):
    id: int
    customer_id: int
    order_id: int | None
    subject: str
    details: str
    status: str

    model_config = ConfigDict(from_attributes=True)
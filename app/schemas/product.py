from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    category_id: int
    sku: str
    name: str
    price: Decimal = Field(gt=0)
    stock: int = Field(ge=0)
    specifications: dict


class ProductUpdate(BaseModel):
    category_id: int
    sku: str
    name: str
    price: Decimal = Field(gt=0)
    stock: int = Field(ge=0)
    specifications: dict


class ProductResponse(BaseModel):
    id: int
    category_id: int
    sku: str
    name: str
    price: Decimal
    stock: int
    specifications: dict

    model_config = ConfigDict(from_attributes=True)
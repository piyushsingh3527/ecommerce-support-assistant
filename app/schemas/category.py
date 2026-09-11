from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    name: str
    slug: str
    description: str | None = None


class CategoryUpdate(BaseModel):
    name: str
    slug: str
    description: str | None = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)
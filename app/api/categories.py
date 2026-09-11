from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import require_role
from app.db.models.category import Category
from app.db.session import get_db
from app.schemas.category import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)


router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
)


@router.post(
    "/",
    response_model=CategoryResponse,
)
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin")),
):
    existing_category = (
        db.query(Category)
        .filter(
            (Category.name == category_data.name)
            | (Category.slug == category_data.slug)
        )
        .first()
    )

    if existing_category:
        raise HTTPException(
            status_code=400,
            detail="Category name or slug already exists",
        )

    category = Category(
        name=category_data.name,
        slug=category_data.slug,
        description=category_data.description,
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


@router.get(
    "/",
    response_model=list[CategoryResponse],
)
def get_categories(
    db: Session = Depends(get_db),
):
    categories = db.query(Category).all()

    return categories


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
):
    category = (
        db.query(Category)
        .filter(Category.id == category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    return category


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin")),
):
    category = (
        db.query(Category)
        .filter(Category.id == category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    existing_category = (
        db.query(Category)
        .filter(
            (
                (Category.name == category_data.name)
                | (Category.slug == category_data.slug)
            )
            & (Category.id != category_id)
        )
        .first()
    )

    if existing_category:
        raise HTTPException(
            status_code=400,
            detail="Category name or slug already exists",
        )

    category.name = category_data.name
    category.slug = category_data.slug
    category.description = category_data.description

    db.commit()
    db.refresh(category)

    return category


@router.delete(
    "/{category_id}",
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_role("admin")),
):
    category = (
        db.query(Category)
        .filter(Category.id == category_id)
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    db.delete(category)
    db.commit()

    return {
        "message": "Category deleted successfully",
    }
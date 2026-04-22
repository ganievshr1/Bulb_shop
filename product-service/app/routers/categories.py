from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas

router = APIRouter(tags=["Categories"])


@router.get("/categories", response_model=List[schemas.CategoryResponse])
async def get_categories(db: Session = Depends(get_db)):
    categories = db.query(models.Category).filter(models.Category.is_active == True).all()
    return categories


@router.get("/categories/{category_id}", response_model=schemas.CategoryResponse)
async def get_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(
        models.Category.id == category_id,
        models.Category.is_active == True
    ).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.post("/categories", status_code=status.HTTP_201_CREATED, response_model=schemas.CategoryResponse)
async def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    db_category = models.Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.put("/categories/{category_id}", response_model=schemas.CategoryResponse)
async def update_category(category_id: int, category_update: schemas.CategoryUpdate, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    update_data = category_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)

    db.commit()
    db.refresh(category)
    return category


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = db.query(models.Category).filter(models.Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    category.is_active = False
    db.commit()
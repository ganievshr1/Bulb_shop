from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.exceptions import CategoryNotFoundError


class CategoryService:
    """Сервис для работы с категориями"""

    @staticmethod
    def get_category(db: Session, category_id: int, active_only: bool = True) -> models.Category:
        """Получить категорию по ID"""
        query = db.query(models.Category).filter(models.Category.id == category_id)
        if active_only:
            query = query.filter(models.Category.is_active == True)

        category = query.first()
        if not category:
            raise CategoryNotFoundError(f"Category {category_id} not found")
        return category

    @staticmethod
    def get_all_categories(db: Session, active_only: bool = True) -> List[models.Category]:
        """Получить все категории"""
        query = db.query(models.Category)
        if active_only:
            query = query.filter(models.Category.is_active == True)
        return query.all()

    @staticmethod
    def create_category(db: Session, category_data: schemas.CategoryCreate) -> models.Category:
        """Создать новую категорию"""
        db_category = models.Category(**category_data.model_dump())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category

    @staticmethod
    def update_category(
            db: Session,
            category_id: int,
            category_data: schemas.CategoryUpdate
    ) -> models.Category:
        """Обновить категорию"""
        category = CategoryService.get_category(db, category_id, active_only=False)

        update_data = category_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(category, key, value)

        db.commit()
        db.refresh(category)
        return category

    @staticmethod
    def delete_category(db: Session, category_id: int) -> bool:
        """Мягкое удаление категории"""
        category = CategoryService.get_category(db, category_id, active_only=False)
        category.is_active = False
        db.commit()
        return True
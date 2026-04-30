from sqlalchemy.orm import Session
from decimal import Decimal
from typing import Optional, List, Tuple
from app import models, schemas
from app.exceptions import ProductNotFoundError, InsufficientStockError


class ProductService:
    """Сервис для работы с товарами"""

    @staticmethod
    def get_product(db: Session, product_id: int, active_only: bool = True) -> models.Product:
        """Получить товар по ID"""
        query = db.query(models.Product).filter(models.Product.id == product_id)
        if active_only:
            query = query.filter(models.Product.is_active == True)

        product = query.first()
        if not product:
            raise ProductNotFoundError(f"Product {product_id} not found")
        return product

    @staticmethod
    def get_products(
            db: Session,
            page: int = 1,
            limit: int = 20,
            category_id: Optional[int] = None,
            min_price: Optional[Decimal] = None,
            max_price: Optional[Decimal] = None,
            socket_type: Optional[str] = None
    ) -> Tuple[List[models.Product], int]:
        """Получить список товаров с фильтрацией и пагинацией"""
        query = db.query(models.Product).filter(models.Product.is_active == True)

        if category_id:
            query = query.filter(models.Product.category_id == category_id)
        if min_price:
            query = query.filter(models.Product.price >= min_price)
        if max_price:
            query = query.filter(models.Product.price <= max_price)
        if socket_type:
            query = query.filter(models.Product.socket_type == socket_type)

        total = query.count()
        offset = (page - 1) * limit
        products = query.offset(offset).limit(limit).all()

        return products, total

    @staticmethod
    def check_stock(db: Session, product_id: int, quantity: int) -> bool:
        """Проверить наличие товара на складе"""
        product = ProductService.get_product(db, product_id)
        return product.stock >= quantity

    @staticmethod
    def reserve_stock(db: Session, product_id: int, quantity: int) -> bool:
        """Зарезервировать товар (уменьшить остаток)"""
        product = ProductService.get_product(db, product_id)

        if product.stock < quantity:
            raise InsufficientStockError(
                f"Insufficient stock for product {product.name}. "
                f"Available: {product.stock}, Required: {quantity}"
            )

        product.stock -= quantity
        db.commit()
        db.refresh(product)
        return True

    @staticmethod
    def release_stock(db: Session, product_id: int, quantity: int) -> bool:
        """Вернуть товар на склад (при отмене заказа)"""
        product = ProductService.get_product(db, product_id, active_only=False)
        product.stock += quantity
        db.commit()
        db.refresh(product)
        return True

    @staticmethod
    def create_product(db: Session, product_data: schemas.ProductCreate) -> models.Product:
        """Создать новый товар"""
        db_product = models.Product(**product_data.model_dump())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product

    @staticmethod
    def update_product(
            db: Session,
            product_id: int,
            product_data: schemas.ProductUpdate
    ) -> models.Product:
        """Обновить товар"""
        product = ProductService.get_product(db, product_id, active_only=False)

        update_data = product_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(product, key, value)

        db.commit()
        db.refresh(product)
        return product

    @staticmethod
    def delete_product(db: Session, product_id: int) -> bool:
        """Мягкое удаление товара"""
        product = ProductService.get_product(db, product_id, active_only=False)
        product.is_active = False
        db.commit()
        return True

    @staticmethod
    def search_products(
            db: Session,
            query_str: str,
            page: int = 1,
            limit: int = 20
    ) -> Tuple[List[models.Product], int]:
        """Поиск товаров по названию и описанию"""
        query = db.query(models.Product).filter(
            models.Product.is_active == True,
            (models.Product.name.ilike(f"%{query_str}%")) |
            (models.Product.description.ilike(f"%{query_str}%"))
        )

        total = query.count()
        offset = (page - 1) * limit
        products = query.offset(offset).limit(limit).all()

        return products, total
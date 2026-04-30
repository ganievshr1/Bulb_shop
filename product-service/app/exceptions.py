class ProductNotFoundError(Exception):
    """Товар не найден"""
    pass

class InsufficientStockError(Exception):
    """Недостаточно товара на складе"""
    pass

class CategoryNotFoundError(Exception):
    """Категория не найдена"""
    pass

class InvalidProductDataError(Exception):
    """Невалидные данные товара"""
    pass
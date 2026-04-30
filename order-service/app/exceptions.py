class OrderNotFoundError(Exception):
    """Заказ не найден"""
    pass

class InvalidOrderStatusError(Exception):
    """Недопустимый статус заказа"""
    pass

class ProductServiceError(Exception):
    """Ошибка при обращении к Product Service"""
    pass
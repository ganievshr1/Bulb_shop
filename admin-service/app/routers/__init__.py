from .auth import router as auth_router
from .products import router as products_router
from .orders import router as orders_router
from .logs import router as logs_router
from .profile import router as profile_router

__all__ = ['auth_router', 'products_router', 'orders_router', 'logs_router', 'profile_router']

# app/routers/__init__.py
"""
Routers package - Router-Paket - Pacote de roteadores
"""
from .contracts import router as contracts_router
from .users import router as users_router
from .auth import router as auth_router

__all__ = ["contracts_router", "users_router", "auth_router"]
# End of file
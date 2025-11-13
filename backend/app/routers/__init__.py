# app/routers/__init__.py
"""
Routers package - Router-Paket - Pacote de roteadores
"""
from .contracts import router as contracts_router
from .users import router as users_router
from .auth import router as auth_router
from .alerts import router as alerts_router
from .rent_steps import router as rent_steps_router

__all__ = ["contracts_router", "users_router", "auth_router", "alerts_router", "rent_steps_router"]
# End of file
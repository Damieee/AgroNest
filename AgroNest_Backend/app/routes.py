from fastapi.routing import APIRouter

from .api.auth.views import router as auth_router
from .api.payments.views import router as payments_router
from .api.wallet.views import router as wallet_router
from .api.user_module.views import router as user_module_router



api_router_v1 = APIRouter()

api_router_v1.include_router(auth_router, prefix="/auth", tags=["Auth"])

api_router_v1.include_router(
    auth_router,
    prefix="/auth",
    tags=["Auth"],
)

api_router_v1.include_router(
    wallet_router,
    prefix="/wallet",
    tags=["Wallet"],
)

api_router_v1.include_router(
    payments_router,
    prefix="/payment",
    tags=["Payments"],
)

api_router_v1.include_router(
    user_module_router,
    prefix="/user",
    tags=["User"],
)
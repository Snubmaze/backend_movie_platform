from fastapi import APIRouter
from app.subscription_service.subscriptions.routers import router as subscriptions_router
from app.subscription_service.payments.routers import router as payments_router


router = APIRouter(
    tags=["Subscription"]
    )


router.include_router(payments_router)
router.include_router(subscriptions_router)

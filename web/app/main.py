from fastapi import FastAPI
from app.content_service.routers import router as movies_router
from app.auth_service.router import router as auth_router


app = FastAPI(title="Content Service")

app.include_router(movies_router)
app.include_router(auth_router)
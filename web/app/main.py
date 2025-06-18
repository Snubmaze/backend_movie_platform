from fastapi import FastAPI
from app.content_service.routers import router as movies_router


app = FastAPI(title="Content Service")

app.include_router(movies_router)

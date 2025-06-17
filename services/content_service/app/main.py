from fastapi import FastAPI
from .routers.movies import router as movies_router


app = FastAPI(title="Content Service")

app.include_router(movies_router, prefix="/movies", tags=["movies"])

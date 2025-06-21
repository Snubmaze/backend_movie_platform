from fastapi import FastAPI
from app.content_service.routers import router as content_router
from app.auth_service.router import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from app.review_service.routers import router as reviews_router
app = FastAPI(
    title="Movie Backend Service", 
    swagger_ui_parameters={"requestCredentials": "include"}
)

app.include_router(content_router)
app.include_router(auth_router)
app.include_router(reviews_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


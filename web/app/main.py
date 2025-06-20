from fastapi import FastAPI
from app.content_service.routers import router as movies_router
from app.auth_service.router import router as auth_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Content Service", 
    swagger_ui_parameters={"requestCredentials": "include"}
)

app.include_router(movies_router)
app.include_router(auth_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


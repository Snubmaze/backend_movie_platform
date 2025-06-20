from fastapi import APIRouter
from app.content_service.genres.routers import router as genres_router
from app.content_service.movies.routers import router as movies_router
from app.content_service.actors.routers import router as actors_router
from app.content_service.directors.routers import router as directors_router
from app.content_service.countries.routers import router as countries_router

router = APIRouter(
    tags=["Content"]
    )


router.include_router(movies_router)
router.include_router(genres_router)
router.include_router(actors_router)
router.include_router(directors_router)
router.include_router(countries_router)
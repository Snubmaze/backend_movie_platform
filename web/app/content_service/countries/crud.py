from typing import List
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.content_service.countries.schemas import CountryCreate, CountryRead


async def get_all_countries(session: AsyncSession) -> List[CountryRead]:
    result = await session.execute(
        text("SELECT country_id, name FROM countries ORDER BY name")
    )
    rows = result.fetchall()
    return [CountryRead(**row._mapping) for row in rows]


async def create_country(session: AsyncSession, country: CountryCreate) -> CountryRead:
    dup = await session.execute(
        text("SELECT 1 FROM countries WHERE name = :name"),
        {"name": country.name}
    )
    if dup.scalar_one_or_none():
        raise HTTPException(400, "Country already exists")

    result = await session.execute(
        text("""
            INSERT INTO countries (name)
            VALUES (:name)
            RETURNING country_id, name
        """),
        {"name": country.name}
    )
    await session.commit()
    row = result.first()
    return CountryRead(**row._mapping)


async def delete_country(session: AsyncSession, country_id: int) -> dict:
    exists = await session.execute(
        text("SELECT 1 FROM countries WHERE country_id = :cid"),
        {"cid": country_id}
    )
    if not exists.scalar_one_or_none():
        raise HTTPException(404, "Country not found")

    await session.execute(
        text("DELETE FROM movie_countries WHERE country_id = :cid"),
        {"cid": country_id}
    )

    await session.execute(
        text("DELETE FROM countries WHERE country_id = :cid"),
        {"cid": country_id}
    )
    await session.commit()
    return {"status": 200, "detail": f"Country {country_id} successfully deleted"}


async def add_movie_country(
    session: AsyncSession,
    movie_id: int,
    country_id: int
) -> dict:
    await session.execute(
        text(
            "INSERT INTO movie_countries(movie_id, country_id) "
            "VALUES(:movie_id, :country_id) "
            "ON CONFLICT DO NOTHING"
        ),
        {"movie_id": movie_id, "country_id": country_id}
    )
    return {"status": 200, "detail": f"Country {country_id} assigned to movie {movie_id}"}


async def remove_movie_country(
    session: AsyncSession,
    movie_id: int,
    country_id: int
) -> dict:
    await session.execute(
        text(
            "DELETE FROM movie_countries "
            "WHERE movie_id = :movie_id AND country_id = :country_id"
        ),
        {"movie_id": movie_id, "country_id": country_id}
    )
    return {"status": 200, "detail": f"Country {country_id} unassigned from movie {movie_id}"}

from typing import List
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.content_service.movies.schemas import MovieSummary


async def search_movies_by_title(
    session: AsyncSession,
    query: str
) -> List[MovieSummary]:
    sql = text("""
        SELECT
          movie_id,
          title,
          release_year,
          avg_rating,
          poster_url
        FROM movies
        WHERE
           title ILIKE :prefix
        OR title ILIKE :word_prefix
        ORDER BY title
        LIMIT 50
    """)
    # начало всей строки
    prefix = f"{query}%"
    # начало любого слова (после пробела)
    word_prefix = f"% {query}%"
    result = await session.execute(sql, {
        "prefix": prefix,
        "word_prefix": word_prefix
    })
    rows = result.mappings().all()
    return [MovieSummary(**row) for row in rows]
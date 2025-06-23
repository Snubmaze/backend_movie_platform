from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.recommendation.schemas import MovieRead

async def get_recommendations(
    session: AsyncSession,
    user_id: int,
    limit: int = 20
) -> List[MovieRead]:
    """
    Возвращает рекомендованные фильмы для пользователя, сортируя по сумме очков предпочтений и avg_rating.
    """
    query = text("""
        SELECT m.movie_id, m.title, m.description, m.release_year, m.duration_min,
               m.avg_rating, m.poster_url, m.trailer_url, m.subscription_required, m.favorites_count
          FROM movies m
          LEFT JOIN movie_genres mg ON mg.movie_id = m.movie_id
          LEFT JOIN user_genre_pref ugp ON ugp.genre_id = mg.genre_id AND ugp.user_id = :user_id
          LEFT JOIN movie_actors ma ON ma.movie_id = m.movie_id
          LEFT JOIN user_actor_pref uap ON uap.actor_id = ma.actor_id AND uap.user_id = :user_id
          LEFT JOIN movie_directors md ON md.movie_id = m.movie_id
          LEFT JOIN user_director_pref udp ON udp.director_id = md.director_id AND udp.user_id = :user_id
         GROUP BY m.movie_id
         ORDER BY 
           COALESCE(SUM(ugp.score), 0) + COALESCE(SUM(uap.score), 0) + COALESCE(SUM(udp.score), 0) DESC,
           m.avg_rating DESC
         LIMIT :limit
    """)

    result = await session.execute(query, {"user_id": user_id, "limit": limit})
    rows = result.fetchall()

    return [MovieRead(**row._mapping) for row in rows]

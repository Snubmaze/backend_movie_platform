-- Для быстрого поиска фильмов по названию (ILIKE '%…%'):
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX IF NOT EXISTS idx_movies_title_trgm
  ON movies
  USING gin (title gin_trgm_ops);

-- Для быстрого поиска пользователя по username:
CREATE INDEX IF NOT EXISTS idx_users_username
  ON users (username);

-- Для агрегации и чтения всех отзывов/рейтингов по фильму:
CREATE INDEX IF NOT EXISTS idx_reviews_movie_id
  ON reviews (movie_id);
CREATE INDEX IF NOT EXISTS idx_ratings_movie_id
  ON ratings (movie_id);

-- Для агрегации и чтения всех отзывов/рейтингов по пользователю:
CREATE INDEX IF NOT EXISTS idx_reviews_user_id
  ON reviews (user_id);
CREATE INDEX IF NOT EXISTS idx_ratings_user_id
  ON ratings (user_id);

-- Для подсчёта и выборки избранного по фильму:
CREATE INDEX IF NOT EXISTS idx_favorites_movie_id
  ON favorites (movie_id);

-- Для связи «пользователь → подписки» и быстрого поиска по user_id:
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id
  ON subscriptions (user_id);

-- Для связи «подписка → платежи» и фильтрации по subscription_id:
CREATE INDEX IF NOT EXISTS idx_payments_subscription_id
  ON payments (subscription_id);
CREATE INDEX IF NOT EXISTS idx_payments_user_id
  ON payments (user_id);

-- Для быстрого поиска связанных сущностей по второму столбцу composite PK:
CREATE INDEX IF NOT EXISTS idx_movie_actors_actor_id
  ON movie_actors (actor_id);
CREATE INDEX IF NOT EXISTS idx_movie_directors_director_id
  ON movie_directors (director_id);
CREATE INDEX IF NOT EXISTS idx_movie_countries_country_id
  ON movie_countries (country_id);

-- Для ускорения фильтрации по жанру:
CREATE INDEX IF NOT EXISTS idx_movie_genres_genre_id
  ON movie_genres (genre_id);

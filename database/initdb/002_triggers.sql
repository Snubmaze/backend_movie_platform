-- =============================================================================
-- 002_triggers.sql
-- Триггер для автоматического пересчёта avg_rating в таблице movies
-- =============================================================================

-- 1) Функция, пересчитывающая средний рейтинг для конкретного фильма
CREATE OR REPLACE FUNCTION update_movie_avg_rating() RETURNS TRIGGER AS $$
DECLARE
  mid BIGINT;
BEGIN
  -- Определяем movie_id: после DELETE берём OLD, иначе — NEW
  IF (TG_OP = 'DELETE') THEN
    mid := OLD.movie_id;
  ELSE
    mid := NEW.movie_id;
  END IF;

  -- Пересчитываем средний рейтинг (округляем до 2 знаков) или ставим 0, если отзывов нет
  UPDATE movies
     SET avg_rating = COALESCE((
         SELECT ROUND(AVG(rating)::numeric, 2)
           FROM reviews
          WHERE movie_id = mid
       ), 0)
   WHERE movie_id = mid;

  RETURN NULL;  -- для AFTER-триггера возвращаем NULL
END;
$$ LANGUAGE plpgsql;


-- 2) Сам триггер: срабатывает после вставки, обновления или удаления в reviews
DROP TRIGGER IF EXISTS trg_reviews_avg ON reviews;
CREATE TRIGGER trg_reviews_avg
  AFTER INSERT OR UPDATE OR DELETE
    ON reviews
  FOR EACH ROW
  EXECUTE FUNCTION update_movie_avg_rating();

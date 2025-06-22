-- 1) Подключаем cron, если ещё не подключено
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- =============================================================================
-- 1. Функция и триггер для пересчёта avg_rating
-- =============================================================================

CREATE OR REPLACE FUNCTION update_movie_avg_rating() RETURNS TRIGGER AS $$
DECLARE
  mid BIGINT;
BEGIN
  IF TG_OP = 'DELETE' THEN
    mid := OLD.movie_id;
  ELSE
    mid := NEW.movie_id;
  END IF;

  UPDATE movies
     SET avg_rating = COALESCE(
           (SELECT ROUND(AVG(rating)::numeric, 2)
              FROM reviews
             WHERE movie_id = mid),
           0
         )
   WHERE movie_id = mid;

  RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_reviews_avg ON reviews;
CREATE TRIGGER trg_reviews_avg
  AFTER INSERT OR UPDATE OR DELETE
    ON reviews
  FOR EACH ROW
  EXECUTE FUNCTION update_movie_avg_rating();


-- =============================================================================
-- 2. Функция и триггер для активации подписки при оплате
-- =============================================================================

CREATE OR REPLACE FUNCTION activate_subscription_on_payment() RETURNS TRIGGER AS $$
BEGIN
  IF NEW.subscription_id IS NOT NULL
     AND NEW.status = 'completed'
  THEN
    UPDATE subscriptions
       SET status = 'active'
     WHERE subscription_id = NEW.subscription_id;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_activate_sub_on_pay ON payments;
CREATE TRIGGER trg_activate_sub_on_pay
  AFTER INSERT OR UPDATE OF status
    ON payments
  FOR EACH ROW
  EXECUTE FUNCTION activate_subscription_on_payment();


-- =============================================================================
-- 3. Функция-утилита для ежедневного истечения подписок + расписание cron
-- =============================================================================

CREATE OR REPLACE FUNCTION expire_subscriptions() RETURNS VOID AS $$
BEGIN
  UPDATE subscriptions
     SET status = 'expired'
   WHERE end_date < CURRENT_DATE
     AND status = 'active';
END;
$$ LANGUAGE plpgsql;

SELECT cron.schedule(
  'daily_expire_subs',      -- имя задачи
  '0 0 * * *',              -- каждый день в полночь
  $$ SELECT expire_subscriptions(); $$
);


-- =============================================================================
-- Триггер и функция для автоматического поддержания favorites_count в movies
-- =============================================================================

-- 1) Функция, инкрементирующая или декрементирующая счётчик избранного
CREATE OR REPLACE FUNCTION update_movie_favorites_count() RETURNS TRIGGER AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    UPDATE movies
       SET favorites_count = favorites_count + 1
     WHERE movie_id = NEW.movie_id;
  ELSIF TG_OP = 'DELETE' THEN
    UPDATE movies
       SET favorites_count = GREATEST(favorites_count - 1, 0)
     WHERE movie_id = OLD.movie_id;
  END IF;
  RETURN NULL;  -- для AFTER-триггера
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_fav_count ON favorites;
CREATE TRIGGER trg_fav_count
  AFTER INSERT OR DELETE
    ON favorites
  FOR EACH ROW
  EXECUTE FUNCTION update_movie_favorites_count();


-- =============================================================================
--  Триггер: Ежедневная выручка по подпискам
-- =============================================================================

CREATE OR REPLACE FUNCTION update_subscription_sales() RETURNS TRIGGER AS $$
BEGIN
  -- Если вставили новый платёж, сразу в статусе completed,
  -- или обновили существующий платёж до completed
  IF (TG_OP = 'INSERT' AND NEW.status = 'completed')
     OR (TG_OP = 'UPDATE'
         AND NEW.status = 'completed'
         AND OLD.status IS DISTINCT FROM 'completed')
  THEN
    INSERT INTO subscription_sales(sale_date, total_amount)
      VALUES (CURRENT_DATE, NEW.amount)
    ON CONFLICT (sale_date)
      DO UPDATE
        SET total_amount = subscription_sales.total_amount + NEW.amount;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_update_sales ON payments;
CREATE TRIGGER trg_update_sales
  AFTER INSERT OR UPDATE OF status
    ON payments
  FOR EACH ROW
  EXECUTE FUNCTION update_subscription_sales();



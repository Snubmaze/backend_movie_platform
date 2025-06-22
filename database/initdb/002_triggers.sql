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

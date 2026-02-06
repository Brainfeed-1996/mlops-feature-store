CREATE TABLE IF NOT EXISTS user_features (
  user_id BIGINT NOT NULL,
  event_ts TIMESTAMPTZ NOT NULL,
  country TEXT,
  age INTEGER,
  purchases_7d DOUBLE PRECISION,
  PRIMARY KEY (user_id, event_ts)
);

CREATE INDEX IF NOT EXISTS idx_user_features_user_ts ON user_features (user_id, event_ts DESC);

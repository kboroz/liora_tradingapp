-- LIORA TradingApp — PostgreSQL + TimescaleDB Schema

CREATE EXTENSION IF NOT EXISTS timescaledb;

-- ─── Raw OHLCV Table ──────────────────────────────────────
CREATE TABLE IF NOT EXISTS raw_ohlcv (
    id          BIGSERIAL,
    symbol      VARCHAR(20)   NOT NULL,
    open_time   TIMESTAMPTZ   NOT NULL,
    open        NUMERIC(20,8) NOT NULL,
    high        NUMERIC(20,8) NOT NULL,
    low         NUMERIC(20,8) NOT NULL,
    close       NUMERIC(20,8) NOT NULL,
    volume      NUMERIC(30,8) NOT NULL,
    num_trades  INTEGER       NOT NULL,
    created_at  TIMESTAMPTZ   DEFAULT NOW(),
    PRIMARY KEY (id, open_time)
);

SELECT create_hypertable('raw_ohlcv', 'open_time', if_not_exists => TRUE);

CREATE UNIQUE INDEX IF NOT EXISTS idx_raw_ohlcv_symbol_time
    ON raw_ohlcv (symbol, open_time DESC);

-- ─── Features Table ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS features (
    id              BIGSERIAL,
    symbol          VARCHAR(20)   NOT NULL,
    open_time       TIMESTAMPTZ   NOT NULL,
    close           NUMERIC(20,8),
    returns         NUMERIC(20,8),
    log_returns     NUMERIC(20,8),
    volatility_24h  NUMERIC(20,8),
    rsi_14          NUMERIC(10,4),
    macd            NUMERIC(20,8),
    macd_signal     NUMERIC(20,8),
    bb_upper        NUMERIC(20,8),
    bb_lower        NUMERIC(20,8),
    volume_zscore   NUMERIC(10,4),
    garch_vol       NUMERIC(20,8),
    created_at      TIMESTAMPTZ   DEFAULT NOW(),
    PRIMARY KEY (id, open_time)
);

SELECT create_hypertable('features', 'open_time', if_not_exists => TRUE);

CREATE UNIQUE INDEX IF NOT EXISTS idx_features_symbol_time
    ON features (symbol, open_time DESC);

-- ─── Predictions Table ────────────────────────────────────
CREATE TABLE IF NOT EXISTS predictions (
    id              BIGSERIAL,
    symbol          VARCHAR(20)   NOT NULL,
    predicted_at    TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    horizon_hours   INTEGER       NOT NULL,
    predicted_price NUMERIC(20,8) NOT NULL,
    confidence      NUMERIC(5,4),
    model_version   VARCHAR(50),
    PRIMARY KEY (id, predicted_at)
);

SELECT create_hypertable('predictions', 'predicted_at', if_not_exists => TRUE);

-- ─── Correlations Table ───────────────────────────────────
CREATE TABLE IF NOT EXISTS correlations (
    id           BIGSERIAL      PRIMARY KEY,
    calculated_at TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    symbol_a     VARCHAR(20)   NOT NULL,
    symbol_b     VARCHAR(20)   NOT NULL,
    window_hours INTEGER       NOT NULL,
    correlation  NUMERIC(10,6) NOT NULL
);

-- ─── Model Registry Table ─────────────────────────────────
CREATE TABLE IF NOT EXISTS model_registry (
    id           BIGSERIAL PRIMARY KEY,
    model_name   VARCHAR(100) NOT NULL,
    version      VARCHAR(50)  NOT NULL,
    symbol       VARCHAR(20)  NOT NULL,
    mlflow_run   VARCHAR(100),
    mae          NUMERIC(20,8),
    rmse         NUMERIC(20,8),
    trained_at   TIMESTAMPTZ  DEFAULT NOW(),
    is_active    BOOLEAN      DEFAULT FALSE
);

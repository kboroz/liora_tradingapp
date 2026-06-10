-- Enable TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Assets/Instruments
CREATE TABLE IF NOT EXISTS assets (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100),
    asset_type VARCHAR(20),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- OHLCV price data (hypertable)
CREATE TABLE IF NOT EXISTS ohlcv (
    time TIMESTAMPTZ NOT NULL,
    asset_id INTEGER REFERENCES assets(id),
    open DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    close DOUBLE PRECISION,
    volume DOUBLE PRECISION
);
SELECT create_hypertable('ohlcv', 'time', if_not_exists => TRUE);

-- Trades
CREATE TABLE IF NOT EXISTS trades (
    id SERIAL PRIMARY KEY,
    asset_id INTEGER REFERENCES assets(id),
    side VARCHAR(10) NOT NULL,
    quantity DOUBLE PRECISION NOT NULL,
    price DOUBLE PRECISION NOT NULL,
    executed_at TIMESTAMPTZ DEFAULT NOW(),
    strategy VARCHAR(50),
    pnl DOUBLE PRECISION
);

-- Portfolio snapshots (hypertable)
CREATE TABLE IF NOT EXISTS portfolio_snapshots (
    time TIMESTAMPTZ NOT NULL,
    total_value DOUBLE PRECISION,
    cash DOUBLE PRECISION,
    invested DOUBLE PRECISION
);
SELECT create_hypertable('portfolio_snapshots', 'time', if_not_exists => TRUE);

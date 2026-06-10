from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # ─── App ──────────────────────────────────────────────
    APP_NAME:    str = "LIORA TradingApp"
    APP_VERSION: str = "1.0.0"
    DEBUG:       bool = False

    # ─── PostgreSQL ───────────────────────────────────────
    POSTGRES_HOST:     str = "localhost"
    POSTGRES_PORT:     int = 5432
    POSTGRES_USER:     str = "liora_user"
    POSTGRES_PASSWORD: str = "liora_password_123"
    POSTGRES_DB:       str = "liora_db"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # ─── Redis ────────────────────────────────────────────
    REDIS_HOST:     str = "localhost"
    REDIS_PORT:     int = 6379
    REDIS_PASSWORD: str = "redis_password_123"

    # ─── Kafka ────────────────────────────────────────────
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_OHLCV:       str = "liora.ohlcv"
    KAFKA_TOPIC_FEATURES:    str = "liora.features"
    KAFKA_TOPIC_PREDICTIONS: str = "liora.predictions"

    # ─── Binance ──────────────────────────────────────────
    BINANCE_API_KEY:    str = ""
    BINANCE_API_SECRET: str = ""
    BINANCE_BASE_URL:   str = "https://api.binance.com"
    BINANCE_WS_URL:     str = "wss://stream.binance.com:9443"

    # ─── MLflow ───────────────────────────────────────────
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"

    # ─── Grafana ──────────────────────────────────────────
    GRAFANA_PASSWORD: str = "admin123"

    class Config:
        env_file      = ".env"
        case_sensitive = True


settings = Settings()

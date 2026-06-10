from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Binance
    BINANCE_API_KEY:    str = ""
    BINANCE_API_SECRET: str = ""

    # PostgreSQL
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

    # Redis
    REDIS_HOST:     str = "localhost"
    REDIS_PORT:     int = 6379
    REDIS_PASSWORD: str = "redis_password_123"

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_RAW:         str = "crypto.raw.ohlcv"
    KAFKA_TOPIC_FEATURES:    str = "crypto.features"
    KAFKA_TOPIC_PREDICTIONS: str = "crypto.predictions"
    KAFKA_GROUP_ID:          str = "liora-streaming-consumer"

    # MLflow
    MLFLOW_TRACKING_URI:    str = "http://localhost:5000"
    MLFLOW_EXPERIMENT_NAME: str = "liora_lstm_crypto"

    # Grafana
    GRAFANA_PASSWORD: str = "admin123"

    # Snowflake
    SNOWFLAKE_ACCOUNT:   str = ""
    SNOWFLAKE_USER:      str = ""
    SNOWFLAKE_PASSWORD:  str = ""
    SNOWFLAKE_DATABASE:  str = "LIORA_DW"
    SNOWFLAKE_SCHEMA:    str = "CRYPTO"
    SNOWFLAKE_WAREHOUSE: str = "COMPUTE_WH"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

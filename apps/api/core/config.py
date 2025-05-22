from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, PostgresDsn, RedisDsn, SecretStr

class Settings(BaseSettings):
    """Application settings."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # API Configuration
    API_VERSION: str = "v1"
    ENVIRONMENT: str = "development"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:3000"]  # Web UI
    DEBUG: bool = False

    # Security
    CLERK_SECRET_KEY: SecretStr
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    DATABASE_URL: PostgresDsn
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: RedisDsn
    REDIS_POOL_SIZE: int = 10

    # Google Cloud
    GOOGLE_CLOUD_PROJECT: str
    GOOGLE_APPLICATION_CREDENTIALS: str
    GOOGLE_PUBSUB_TOPIC_PREFIX: str = "alpha-me"

    # OpenAI
    OPENAI_API_KEY: SecretStr
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    EMBEDDING_MODEL: str = "BAAI/bge-base-en"

    # OAuth Providers
    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: SecretStr
    TWITTER_API_KEY: str
    TWITTER_API_SECRET: SecretStr

    # AI Pipeline
    NARRATIVE_CLUSTER_MIN_SIZE: int = 3
    NARRATIVE_CLUSTER_MIN_SAMPLES: int = 2
    NARRATIVE_SIMILARITY_THRESHOLD: float = 0.75
    NARRATIVE_MAX_QUESTIONS: int = 3

    # Newsletter
    NEWSLETTER_STORAGE_BUCKET: str = "alpha-me-newsletters"
    NEWSLETTER_BASE_URL: str = "https://alpha.me/u"

    # Matchmaking
    MATCH_BATCH_SIZE: int = 100
    MATCH_MIN_SCORE: float = 0.6
    MATCH_MAX_RECOMMENDATIONS: int = 5

    # Observability
    OTEL_EXPORTER_OTLP_ENDPOINT: str | None = None
    OTEL_SERVICE_NAME: str = "alpha-me-api"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"

settings = Settings() 
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "WHISPER_"}

    database_url: str = "postgresql+asyncpg://whisper:whisper_dev_password@localhost:5432/whisper"
    redis_url: str = "redis://localhost:6379"
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "whisper"
    minio_secret_key: str = "whisper_dev_password"
    minio_bucket: str = "whisper-files"
    minio_secure: bool = False
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 24
    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings. Default values are for local development."""

    POSTGRES_USER: str = "area_verde"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = "area_verde"
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    RUN_MIGRATIONS: bool = False
    LOG_LEVEL: str = "INFO"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Databricks settings
    DATABRICKS_HOST: str
    DATABRICKS_TOKEN: str
    GENIE_SPACE_ID: str

    # Deployment settings
    BASE_URL: str = "http://localhost:8000"

    # Auth0 settings
    AUTH0_DOMAIN: str
    AUTH0_CLIENT_ID: str
    AUTH0_CLIENT_SECRET: str


    # Security
    APP_SECRET_KEY: str = "super-secret-default"

    # Microsoft Bot Framework
    MicrosoftAppId: Optional[str] = ""
    MicrosoftAppPassword: Optional[str] = ""

    # Load from .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8", 
        extra="ignore"
    )

# Global settings instance
settings = Settings()


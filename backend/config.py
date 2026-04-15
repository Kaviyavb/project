from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Databricks settings
    DATABRICKS_HOST: str
    DATABRICKS_TOKEN: str
    GENIE_SPACE_ID: str

    # Microsoft Bot Framework
    MicrosoftAppId: Optional[str] = ""
    MicrosoftAppPassword: Optional[str] = ""

    # Load from .env file (looks in current dir, then parent)
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8", 
        extra="ignore"
    )

# Global settings instance
settings = Settings()

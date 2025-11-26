from pydantic_settings import BaseSettings
from typing import Literal

class Settings(BaseSettings):
    ENVIRONMENT: Literal["development", "production"] = "development"
    DATABASE_URL: str

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"

    }

settings = Settings()  # ← будет читать .env автоматически
import os
from pathlib import Path

from pydantic_settings import BaseSettings

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    app_name: str = "OpenGauss知识智能体"
    app_version: str = "1.0.0"
    debug: bool = True

    database_url: str = "postgresql+asyncpg://postgres@localhost:5432/opengauss_agent"

    modelarts_api_key: str = ""
    modelarts_base_url: str = ""
    modelarts_model: str = ""

    docx_dir: str = ""

    jwt_secret_key: str = "opengauss-agent-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
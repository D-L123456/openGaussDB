from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "OpenGauss知识智能体"
    app_version: str = "1.0.0"
    debug: bool = True

    database_url: str = "sqlite+aiosqlite:///./opengauss_agent.db"

    modelarts_api_key: str = ""
    modelarts_base_url: str = ""
    modelarts_model: str = ""

    chroma_persist_dir: str = "./chroma_data"
    chroma_collection_name: str = "opengauss_knowledge"

    embedding_model: str = "BAAI/bge-small-zh-v1.5"
    chunk_size: int = 500
    chunk_overlap: int = 100

    docx_dir: str = ""

    jwt_secret_key: str = "opengauss-agent-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
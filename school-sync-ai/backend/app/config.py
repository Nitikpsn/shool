from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    ai_api_key: str = ""
    database_url: str = "mysql+aiomysql://root:password@localhost:3306/school_sync"
    upload_dir: str = "../uploads"
    report_dir: str = "../reports"

    class Config:
        env_file = "../.env"


settings = Settings()
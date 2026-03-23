from pydantic_settings import BaseSettings
import os
import dotenv
dotenv.load_dotenv()
class Settings(BaseSettings):
    # PostgreSQL (por defecto)
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    ALTERNATE_DATABASE_URL: str = os.getenv("ALTERNATE_DATABASE_URL")
    # MySQL (por defecto)
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    DEBUG: bool = os.getenv("DEBUG")

    class Config:
        env_file = ".env"


settings = Settings()
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+mysqlconnector://root:password@localhost:3306/recidron"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    DEBUG: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
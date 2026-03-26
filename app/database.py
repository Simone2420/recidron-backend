from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

database_url = settings.ALTERNATE_DATABASE_URL or settings.DATABASE_URL
if not database_url:
    raise RuntimeError("No database URL configured. Set ALTERNATE_DATABASE_URL or DATABASE_URL in .env")

engine = create_engine(database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
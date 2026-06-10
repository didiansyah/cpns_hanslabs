import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root@localhost/cpns")
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "1800")),
    pool_size=int(os.getenv("DB_POOL_SIZE", "8")),
    max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "4")),
    pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "10")),
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from app.config.app_config import getAppConfig

Base = declarative_base()
config = getAppConfig()
db_url:Optional[str] = (
    config.db_dev
    if config.app_env == "development"
    else config.db_url
)
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

import json
from uuid import UUID
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import DATABASE_URL

def uuid_serializer(obj):
    if isinstance(obj, UUID):
        return str(obj)
    raise TypeError

engine = create_engine(DATABASE_URL, json_serializer=uuid_serializer)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

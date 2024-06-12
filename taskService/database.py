from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URI = os.environ.get("DATABASE_URI")

engine = create_engine(DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session():
    return SessionLocal()
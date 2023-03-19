"""Create SQLAlchemy engine and session objects."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config
# from sqlalchemy.ext.asyncio import create_async_engine

# Create database engine
engine = create_engine(Config.DATABASE_URL)
# engine_async = create_async_engine(os.getenv("DATABASE_URL"), echo=True)

# Create database session
Session = sessionmaker(bind=engine)
session = Session()

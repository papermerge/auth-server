from sqlalchemy.orm import sessionmaker
from .engine import engine

SessionLocal = sessionmaker(engine)


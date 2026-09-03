import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
URL=os.getenv("DATABASE_URL","sqlite:///./foodpulse.db")
engine=create_engine(URL, pool_pre_ping=True)
SessionLocal=sessionmaker(bind=engine,autocommit=False,autoflush=False)
class Base(DeclarativeBase): pass
def db():
    s=SessionLocal()
    try: yield s
    finally: s.close()
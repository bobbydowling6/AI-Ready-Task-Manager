from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
class Base(DeclarativeBase):
    pass


def initialize_db():
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    if "tasks" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("tasks")}
    if "password" not in columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN password VARCHAR(100) NOT NULL DEFAULT ''"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

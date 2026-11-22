"""
Database connection, SQLAlchemy engine and session factory
"""
# SQLAlchemy engine, declarative ORM base and session factory
from pymysql.constants import CLIENT  # MySQL FOUND_ROWS client flag for matched-row counts
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Read database connection settings
from core.config import settings

# Check and recycle pooled connections with pool_pre_ping and pool_recycle to handle MySQL disconnects
engine = create_engine(
    settings.database_url,  # Connection string assembled from .env settings
    pool_pre_ping=True,  # Test connections before use and replace stale ones
    pool_recycle=3600,  # Recycle connections after 3,600 seconds
    pool_size=8,  # Number of persistent connections in the pool
    max_overflow=8,  # Extra temporary connections allowed during peak usage
    echo=False,  # Disable console SQL logging
    # Count matched rows like JDBC so an UPDATE that keeps the existing value still reports success
    connect_args={"client_flag": CLIENT.FOUND_ROWS},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)  # Session factory with explicit flush and commit. Objects remain accessible after commit.


class Base(DeclarativeBase):
    """Base class for ORM entities"""
    pass


def get_db():
    """FastAPI dependency that opens one session per request and closes it afterward"""
    db = SessionLocal()  # Create a dedicated session for the request
    try:
        yield db  # Yield the session to the route handler
    finally:
        db.close()  # Close the session and release its connection after the request, including on failure

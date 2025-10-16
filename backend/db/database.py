import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=10,  # Maximum number of connections in the pool
    max_overflow=20,  # Maximum overflow connections
    echo=False  # Set to True to log all SQL statements (useful for debugging)
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for declarative models
Base = declarative_base()

# Dependency to get database session
def get_db():
    """
    Dependency function to get database session.
    Use this in FastAPI route dependencies.
    
    Example:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Function to initialize database (create all tables)
def init_db():
    """
    Initialize database by creating all tables.
    Call this function when the application starts.
    """
    # Import models here to ensure they are registered with Base
    from users import models  # noqa: F401
    from events import models as calendar_models  # noqa: F401
    Base.metadata.create_all(bind=engine)


# Function to close database connections
def close_db():
    """
    Close database connections.
    Call this function when the application shuts down.
    """
    engine.dispose()

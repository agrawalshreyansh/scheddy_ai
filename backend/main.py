from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from db.database import get_db, init_db, close_db
from db.qdrant_client import init_qdrant, close_qdrant, get_qdrant_client
from contextlib import asynccontextmanager
from users.router import router as users_router
from users.preference_router import router as preferences_router
from events.router import router as calendar_router
from chat.router import router as chat_router
from config import CORSConfig


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    init_qdrant()
    print("Qdrant initialized successfully")
    yield
    # Shutdown
    close_db()
    close_qdrant()
    print("Qdrant connections closed")

app = FastAPI(lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORSConfig.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(users_router)
app.include_router(preferences_router)
app.include_router(calendar_router)
app.include_router(chat_router)

@app.get("/")
def read_root():
    return {"message": "Hello from shrage"}


@app.get("/db-test")
def test_database(db: Session = Depends(get_db)):
    """Test endpoint to verify database connection"""
    try:
        # Test the database connection
        db.execute(text("SELECT 1"))
        return {"status": "success", "message": "Database connection is working"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/qdrant-test")
def test_qdrant():
    """Test endpoint to verify Qdrant connection"""
    try:
        client = get_qdrant_client()
        collections = client.get_collections()
        return {
            "status": "success",
            "message": "Qdrant connection is working",
            "collections_count": len(collections.collections),
            "collections": [col.name for col in collections.collections]
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    import uvicorn
    import os
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))


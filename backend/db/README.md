# Database Module

This module contains database configuration and utilities for both PostgreSQL (via SQLAlchemy) and Qdrant vector database.

## Files

### `database.py`
PostgreSQL database configuration using SQLAlchemy.

**Key Functions:**
- `get_db()`: Dependency to get database session
- `init_db()`: Initialize database and create tables
- `close_db()`: Close database connections

### `qdrant_client.py`
Qdrant vector database client and utilities.

**Key Functions:**
- `get_qdrant_client()`: Get Qdrant client instance
- `init_qdrant()`: Initialize Qdrant connection
- `close_qdrant()`: Close Qdrant connections
- `create_collection()`: Create a new vector collection
- `upsert_points()`: Insert or update vectors
- `search_vectors()`: Search for similar vectors
- `delete_points()`: Delete vectors by ID
- `get_collection_info()`: Get collection metadata

## Documentation

- **[QDRANT_QUICKSTART.md](../QDRANT_QUICKSTART.md)**: Quick 5-minute setup guide
- **[QDRANT_SETUP.md](QDRANT_SETUP.md)**: Comprehensive setup and configuration guide
- **[QDRANT_EXAMPLES.md](QDRANT_EXAMPLES.md)**: Code examples and use cases

## Quick Start

### PostgreSQL
```python
from db.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends

@app.get("/items")
def get_items(db: Session = Depends(get_db)):
    return db.query(Item).all()
```

### Qdrant
```python
from db.qdrant_client import create_collection, search_vectors
from qdrant_client.models import Distance

# Create collection
create_collection("my_collection", vector_size=384, distance=Distance.COSINE)

# Search
results = search_vectors(
    collection_name="my_collection",
    query_vector=[0.1, 0.2, ...],
    limit=5
)
```

## Environment Variables

```env
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/scheddy

# Qdrant (Local)
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Qdrant (Cloud)
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-api-key
```

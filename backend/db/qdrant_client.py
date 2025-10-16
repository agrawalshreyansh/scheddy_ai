"""
Qdrant Vector Database Client Setup
This module provides configuration and utility functions for Qdrant vector database.
"""

import os
from typing import Optional, List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchRequest,
)
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Qdrant configuration
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))

# Global client instance
_qdrant_client: Optional[QdrantClient] = None


def get_qdrant_client() -> QdrantClient:
    """
    Get or create Qdrant client instance.
    
    Returns:
        QdrantClient: Initialized Qdrant client
        
    Example:
        client = get_qdrant_client()
        collections = client.get_collections()
    """
    global _qdrant_client
    
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
        )
    return _qdrant_client


def init_qdrant():
    """
    Initialize Qdrant client and verify connection.
    Call this function when the application starts.
    """
    try:
        client = get_qdrant_client()
        # Test connection by getting collections
        collections = client.get_collections()
        print(f"Qdrant initialized successfully. Collections: {len(collections.collections)}")
        return True
    except Exception as e:
        print(f"Failed to initialize Qdrant: {str(e)}")
        return False


def close_qdrant():
    """
    Close Qdrant client connections.
    Call this function when the application shuts down.
    """
    global _qdrant_client
    if _qdrant_client is not None:
        _qdrant_client.close()
        _qdrant_client = None
        print("Qdrant connections closed")


def create_collection(
    collection_name: str,
    vector_size: int,
    distance: Distance = Distance.COSINE,
    on_disk_payload: bool = False,
) -> bool:
    """
    Create a new collection in Qdrant.
    
    Args:
        collection_name: Name of the collection to create
        vector_size: Dimension of the vectors (e.g., 384 for all-MiniLM-L6-v2, 768 for BERT, 1536 for OpenAI)
        distance: Distance metric (COSINE, EUCLID, DOT)
        on_disk_payload: Whether to store payload on disk (useful for large datasets)
        
    Returns:
        bool: True if successful, False otherwise
        
    Example:
        create_collection("events_embeddings", vector_size=384, distance=Distance.COSINE)
    """
    try:
        client = get_qdrant_client()
        
        # Check if collection already exists
        collections = client.get_collections().collections
        if any(col.name == collection_name for col in collections):
            print(f"Collection '{collection_name}' already exists")
            return True
        
        # Create collection
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=distance,
                on_disk=on_disk_payload,
            ),
        )
        print(f"Collection '{collection_name}' created successfully")
        return True
    except Exception as e:
        print(f"Failed to create collection '{collection_name}': {str(e)}")
        return False


def upsert_points(
    collection_name: str,
    points: List[PointStruct],
) -> bool:
    """
    Insert or update points in a collection.
    
    Args:
        collection_name: Name of the collection
        points: List of PointStruct objects to upsert
        
    Returns:
        bool: True if successful, False otherwise
        
    Example:
        points = [
            PointStruct(
                id=1,
                vector=[0.1, 0.2, 0.3, ...],
                payload={"text": "Example text", "user_id": 123}
            )
        ]
        upsert_points("events_embeddings", points)
    """
    try:
        client = get_qdrant_client()
        client.upsert(
            collection_name=collection_name,
            points=points,
        )
        print(f"Upserted {len(points)} points to '{collection_name}'")
        return True
    except Exception as e:
        print(f"Failed to upsert points to '{collection_name}': {str(e)}")
        return False


def search_vectors(
    collection_name: str,
    query_vector: List[float],
    limit: int = 10,
    score_threshold: Optional[float] = None,
    filter_conditions: Optional[Filter] = None,
) -> List[Any]:
    """
    Search for similar vectors in a collection.
    
    Args:
        collection_name: Name of the collection to search
        query_vector: Vector to search for
        limit: Maximum number of results to return
        score_threshold: Minimum similarity score (0-1 for cosine)
        filter_conditions: Optional filter conditions
        
    Returns:
        List of search results
        
    Example:
        results = search_vectors(
            "events_embeddings",
            query_vector=[0.1, 0.2, 0.3, ...],
            limit=5,
            score_threshold=0.7
        )
    """
    try:
        client = get_qdrant_client()
        results = client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=limit,
            score_threshold=score_threshold,
            query_filter=filter_conditions,
        )
        return results
    except Exception as e:
        print(f"Failed to search in '{collection_name}': {str(e)}")
        return []


def delete_points(
    collection_name: str,
    points_ids: List[int],
) -> bool:
    """
    Delete points from a collection by IDs.
    
    Args:
        collection_name: Name of the collection
        points_ids: List of point IDs to delete
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        client = get_qdrant_client()
        client.delete(
            collection_name=collection_name,
            points_selector=points_ids,
        )
        print(f"Deleted {len(points_ids)} points from '{collection_name}'")
        return True
    except Exception as e:
        print(f"Failed to delete points from '{collection_name}': {str(e)}")
        return False


def delete_collection(collection_name: str) -> bool:
    """
    Delete a collection.
    
    Args:
        collection_name: Name of the collection to delete
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        client = get_qdrant_client()
        client.delete_collection(collection_name=collection_name)
        print(f"Collection '{collection_name}' deleted successfully")
        return True
    except Exception as e:
        print(f"Failed to delete collection '{collection_name}': {str(e)}")
        return False


def get_collection_info(collection_name: str) -> Optional[Dict[str, Any]]:
    """
    Get information about a collection.
    
    Args:
        collection_name: Name of the collection
        
    Returns:
        Dictionary with collection info or None if failed
    """
    try:
        client = get_qdrant_client()
        info = client.get_collection(collection_name=collection_name)
        return info.dict()
    except Exception as e:
        print(f"Failed to get info for collection '{collection_name}': {str(e)}")
        return None

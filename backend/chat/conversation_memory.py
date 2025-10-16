"""
Conversation Memory Service using Qdrant for Semantic Search
Stores chat history, embeddings, and provides context-aware retrieval
"""
import os
import json
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
from uuid import UUID
import requests
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from sqlalchemy.orm import Session

from db.qdrant_client import get_qdrant_client
from events.controllers import get_events_by_date_range


class ConversationMemory:
    """
    Manages conversation history and context using Qdrant vector database.
    
    Features:
    - Store all user/assistant messages with embeddings
    - Semantic search over past conversations
    - Find similar tasks scheduled before
    - Detect recurring patterns
    - Multi-turn conversation tracking
    """
    
    COLLECTION_NAME = "conversations"
    TASKS_COLLECTION_NAME = "scheduled_tasks"
    EMBEDDING_DIM = 384  # Using all-MiniLM-L6-v2 model
    
    def __init__(self):
        self.client = get_qdrant_client()
        self._ensure_collections_exist()
    
    def _ensure_collections_exist(self):
        """Create Qdrant collections if they don't exist"""
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            # Create conversations collection
            if self.COLLECTION_NAME not in collection_names:
                self.client.create_collection(
                    collection_name=self.COLLECTION_NAME,
                    vectors_config=VectorParams(
                        size=self.EMBEDDING_DIM,
                        distance=Distance.COSINE
                    )
                )
            
            # Create tasks collection
            if self.TASKS_COLLECTION_NAME not in collection_names:
                self.client.create_collection(
                    collection_name=self.TASKS_COLLECTION_NAME,
                    vectors_config=VectorParams(
                        size=self.EMBEDDING_DIM,
                        distance=Distance.COSINE
                    )
                )
        except Exception as e:
            print(f"Error ensuring collections exist: {e}")
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get text embedding using HuggingFace API (free).
        Using all-MiniLM-L6-v2 model for sentence embeddings.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            # Using HuggingFace Inference API (free)
            API_URL = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
            headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY', '')}"}
            
            response = requests.post(
                API_URL,
                headers=headers,
                json={"inputs": text, "options": {"wait_for_model": True}}
            )
            
            if response.status_code == 200:
                # Response is a list of embeddings, take the first one
                embedding = response.json()
                if isinstance(embedding, list) and len(embedding) > 0:
                    # Handle nested list structure
                    if isinstance(embedding[0], list):
                        return embedding[0]
                    return embedding
            
            # Fallback: return zero vector if API fails
            print(f"Embedding API failed: {response.status_code}")
            return [0.0] * self.EMBEDDING_DIM
            
        except Exception as e:
            print(f"Error getting embedding: {e}")
            # Return zero vector as fallback
            return [0.0] * self.EMBEDDING_DIM
    
    def store_message(
        self,
        user_id: UUID,
        role: str,
        content: str,
        intent_data: Optional[Dict] = None,
        conversation_id: Optional[str] = None
    ) -> str:
        """
        Store a conversation message in Qdrant.
        
        Args:
            user_id: User UUID
            role: 'user' or 'assistant'
            content: Message content
            intent_data: Parsed intent from LLM (for user messages)
            conversation_id: ID to track multi-turn conversations
            
        Returns:
            Point ID in Qdrant
        """
        try:
            # Generate embedding
            embedding = self.get_embedding(content)
            
            # Create unique point ID
            point_id = f"{user_id}_{datetime.utcnow().timestamp()}"
            
            # Prepare payload
            payload = {
                "user_id": str(user_id),
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat(),
                "conversation_id": conversation_id or point_id,
            }
            
            if intent_data:
                payload["intent_data"] = json.dumps(intent_data)
            
            # Store in Qdrant
            self.client.upsert(
                collection_name=self.COLLECTION_NAME,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload=payload
                    )
                ]
            )
            
            return point_id
            
        except Exception as e:
            print(f"Error storing message: {e}")
            return ""
    
    def store_scheduled_task(
        self,
        user_id: UUID,
        event_id: UUID,
        title: str,
        description: Optional[str],
        category: str,
        priority: int,
        start_time: datetime,
        duration_minutes: int
    ):
        """
        Store scheduled task in Qdrant for similarity search.
        
        Args:
            user_id: User UUID
            event_id: Event UUID
            title: Task title
            description: Task description
            category: Task category
            priority: Priority number
            start_time: Scheduled start time
            duration_minutes: Task duration
        """
        try:
            # Create searchable text
            text = f"{title}. {description or ''}"
            embedding = self.get_embedding(text)
            
            # Point ID based on event
            point_id = f"task_{event_id}"
            
            payload = {
                "user_id": str(user_id),
                "event_id": str(event_id),
                "title": title,
                "description": description or "",
                "category": category,
                "priority": priority,
                "start_time": start_time.isoformat(),
                "duration_minutes": duration_minutes,
                "created_at": datetime.utcnow().isoformat()
            }
            
            self.client.upsert(
                collection_name=self.TASKS_COLLECTION_NAME,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=embedding,
                        payload=payload
                    )
                ]
            )
            
        except Exception as e:
            print(f"Error storing task: {e}")
    
    def search_similar_conversations(
        self,
        user_id: UUID,
        query: str,
        limit: int = 5,
        days_back: int = 30
    ) -> List[Dict]:
        """
        Find similar past conversations using semantic search.
        
        Args:
            user_id: User UUID
            query: Current user query
            limit: Max results to return
            days_back: Only search conversations from last N days
            
        Returns:
            List of similar conversation snippets
        """
        try:
            query_embedding = self.get_embedding(query)
            cutoff_date = (datetime.utcnow() - timedelta(days=days_back)).isoformat()
            
            results = self.client.search(
                collection_name=self.COLLECTION_NAME,
                query_vector=query_embedding,
                query_filter=Filter(
                    must=[
                        FieldCondition(
                            key="user_id",
                            match=MatchValue(value=str(user_id))
                        )
                    ]
                ),
                limit=limit
            )
            
            conversations = []
            for result in results:
                payload = result.payload
                # Filter by date
                if payload.get("timestamp", "") >= cutoff_date:
                    conversations.append({
                        "role": payload.get("role"),
                        "content": payload.get("content"),
                        "timestamp": payload.get("timestamp"),
                        "score": result.score,
                        "intent_data": json.loads(payload.get("intent_data", "{}")) if payload.get("intent_data") else None
                    })
            
            return conversations
            
        except Exception as e:
            print(f"Error searching conversations: {e}")
            return []
    
    def search_similar_tasks(
        self,
        user_id: UUID,
        query: str,
        limit: int = 5
    ) -> List[Dict]:
        """
        Find similar tasks scheduled in the past.
        
        Args:
            user_id: User UUID
            query: Task description to search
            limit: Max results
            
        Returns:
            List of similar past tasks
        """
        try:
            query_embedding = self.get_embedding(query)
            
            results = self.client.search(
                collection_name=self.TASKS_COLLECTION_NAME,
                query_vector=query_embedding,
                query_filter=Filter(
                    must=[
                        FieldCondition(
                            key="user_id",
                            match=MatchValue(value=str(user_id))
                        )
                    ]
                ),
                limit=limit
            )
            
            tasks = []
            for result in results:
                payload = result.payload
                tasks.append({
                    "title": payload.get("title"),
                    "description": payload.get("description"),
                    "category": payload.get("category"),
                    "priority": payload.get("priority"),
                    "duration_minutes": payload.get("duration_minutes"),
                    "start_time": payload.get("start_time"),
                    "similarity_score": result.score
                })
            
            return tasks
            
        except Exception as e:
            print(f"Error searching tasks: {e}")
            return []
    
    def detect_recurring_pattern(
        self,
        user_id: UUID,
        task_title: str,
        category: str
    ) -> Optional[Dict]:
        """
        Detect if this is a recurring task pattern.
        
        Args:
            user_id: User UUID
            task_title: Title to check
            category: Task category
            
        Returns:
            Pattern info if detected, None otherwise
        """
        try:
            # Search for similar tasks
            similar_tasks = self.search_similar_tasks(user_id, task_title, limit=10)
            
            # Filter high-similarity tasks (>0.8 score)
            recurring = [t for t in similar_tasks if t['similarity_score'] > 0.8]
            
            if len(recurring) >= 2:
                # Calculate average duration
                avg_duration = sum(t['duration_minutes'] for t in recurring) / len(recurring)
                
                # Most common priority
                priorities = [t['priority'] for t in recurring]
                most_common_priority = max(set(priorities), key=priorities.count)
                
                return {
                    "is_recurring": True,
                    "occurrences": len(recurring),
                    "suggested_duration_minutes": int(avg_duration),
                    "suggested_priority": most_common_priority,
                    "last_scheduled": recurring[0]['start_time']
                }
            
            return None
            
        except Exception as e:
            print(f"Error detecting pattern: {e}")
            return None
    
    def get_conversation_context(
        self,
        user_id: UUID,
        current_query: str,
        db: Session
    ) -> str:
        """
        Build rich context for LLM including:
        - Similar past conversations
        - Similar scheduled tasks
        - Recurring patterns
        - Recent schedule
        
        Args:
            user_id: User UUID
            current_query: Current user message
            db: Database session
            
        Returns:
            Formatted context string for LLM
        """
        context_parts = []
        
        # 1. Find similar conversations
        similar_convos = self.search_similar_conversations(user_id, current_query, limit=3)
        if similar_convos:
            context_parts.append("## Similar Past Conversations:")
            for conv in similar_convos[:2]:  # Top 2
                context_parts.append(
                    f"- {conv['role']}: {conv['content'][:100]}... "
                    f"(similarity: {conv['score']:.2f})"
                )
        
        # 2. Find similar tasks
        similar_tasks = self.search_similar_tasks(user_id, current_query, limit=3)
        if similar_tasks:
            context_parts.append("\n## Similar Previously Scheduled Tasks:")
            for task in similar_tasks[:2]:  # Top 2
                context_parts.append(
                    f"- '{task['title']}' ({task['category']}) - "
                    f"{task['duration_minutes']}min, priority: {task['priority']}"
                )
        
        # 3. Check for recurring pattern
        # Extract potential task title from query
        words = current_query.lower().split()
        if any(word in words for word in ['gym', 'workout', 'meeting', 'standup', 'learning']):
            pattern = self.detect_recurring_pattern(user_id, current_query, "general")
            if pattern and pattern['is_recurring']:
                context_parts.append(
                    f"\n## ⚠️ Recurring Pattern Detected:\n"
                    f"This task appears {pattern['occurrences']} times before. "
                    f"Suggested: {pattern['suggested_duration_minutes']}min duration."
                )
        
        # 4. Recent schedule (next 7 days)
        try:
            today = datetime.now().date()
            week_end = today + timedelta(days=7)
            recent_events = get_events_by_date_range(
                db, user_id, today, week_end
            )
            if recent_events:
                context_parts.append(f"\n## Upcoming Schedule (Next 7 Days): {len(recent_events)} events")
        except Exception as e:
            print(f"Error fetching recent events: {e}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def get_recent_conversation(
        self,
        user_id: UUID,
        conversation_id: str,
        limit: int = 5
    ) -> List[Dict]:
        """
        Get recent messages in a multi-turn conversation.
        
        Args:
            user_id: User UUID
            conversation_id: Conversation ID
            limit: Max messages to retrieve
            
        Returns:
            List of messages in chronological order
        """
        try:
            # Search with filter for conversation_id
            results = self.client.scroll(
                collection_name=self.COLLECTION_NAME,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="user_id",
                            match=MatchValue(value=str(user_id))
                        ),
                        FieldCondition(
                            key="conversation_id",
                            match=MatchValue(value=conversation_id)
                        )
                    ]
                ),
                limit=limit
            )
            
            messages = []
            for point in results[0]:  # results is tuple (points, next_offset)
                payload = point.payload
                messages.append({
                    "role": payload.get("role"),
                    "content": payload.get("content"),
                    "timestamp": payload.get("timestamp")
                })
            
            # Sort by timestamp
            messages.sort(key=lambda x: x['timestamp'])
            
            return messages
            
        except Exception as e:
            print(f"Error getting recent conversation: {e}")
            return []

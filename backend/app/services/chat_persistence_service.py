"""
Chat persistence service for managing chat sessions and messages in MongoDB.
Provides CRUD operations with pagination support.
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.models.schemas import (
    ChatSession,
    ChatSessionCreate,
    ChatSessionResponse,
    ChatSessionListResponse,
    ChatMessage,
    ChatMessageCreate,
    ChatMessageResponse,
    MessageListResponse,
    MessageSource
)

logger = logging.getLogger(__name__)


class ChatPersistenceService:
    """
    Service for persisting chat sessions and messages to MongoDB.
    """
    
    def __init__(self, database: AsyncIOMotorDatabase):
        """
        Initialize chat persistence service.
        
        Args:
            database: Motor database instance
        """
        self.db = database
        self.sessions_collection = database.chat_sessions
        self.messages_collection = database.chat_messages
    
    # ========================================================================
    # Session Operations
    # ========================================================================
    
    async def create_session(
        self,
        user_id: Optional[str] = None,
        project_id: str = "default",
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatSessionResponse:
        """
        Create a new chat session.
        
        Args:
            user_id: User identifier
            project_id: Project identifier
            title: Session title (will be auto-generated if None)
            metadata: Additional metadata
            
        Returns:
            ChatSessionResponse: Created session
        """
        session_create = ChatSessionCreate(
            user_id=user_id,
            project_id=project_id,
            title=title,
            metadata=metadata or {}
        )
        
        session = ChatSession(
            user_id=session_create.user_id,
            project_id=session_create.project_id,
            title=session_create.title or "New Conversation",
            metadata=session_create.metadata
        )
        
        # Convert to dict for MongoDB
        session_dict = session.model_dump(by_alias=True)
        
        # Insert into database
        await self.sessions_collection.insert_one(session_dict)
        
        logger.info(f"Created session {session.id} for user {user_id}")
        
        return ChatSessionResponse(
            session_id=session.id,
            user_id=session.user_id,
            project_id=session.project_id,
            title=session.title,
            message_count=0,
            created_at=session.created_at,
            updated_at=session.updated_at
        )
    
    async def get_session(self, session_id: str) -> Optional[ChatSessionResponse]:
        """
        Get a session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            ChatSessionResponse: Session if found, None otherwise
        """
        session_doc = await self.sessions_collection.find_one({"_id": session_id})
        
        if not session_doc:
            return None
        
        return ChatSessionResponse(
            session_id=session_doc["_id"],
            user_id=session_doc.get("user_id"),
            project_id=session_doc.get("project_id", "default"),
            title=session_doc.get("title", "Untitled"),
            message_count=session_doc.get("message_count", 0),
            created_at=session_doc.get("created_at"),
            updated_at=session_doc.get("updated_at")
        )
    
    async def list_sessions(
        self,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> ChatSessionListResponse:
        """
        List sessions with optional filtering and pagination.
        
        Args:
            user_id: Filter by user ID
            project_id: Filter by project ID
            page: Page number (1-indexed)
            page_size: Number of sessions per page
            
        Returns:
            ChatSessionListResponse: Paginated session list
        """
        # Build filter query
        query = {}
        if user_id:
            query["user_id"] = user_id
        if project_id:
            query["project_id"] = project_id
        
        # Get total count
        total_count = await self.sessions_collection.count_documents(query)
        
        # Calculate pagination
        skip = (page - 1) * page_size
        
        # Query sessions sorted by updated_at (most recent first)
        cursor = self.sessions_collection.find(query).sort("updated_at", -1).skip(skip).limit(page_size)
        
        sessions = []
        async for doc in cursor:
            sessions.append(ChatSessionResponse(
                session_id=doc["_id"],
                user_id=doc.get("user_id"),
                project_id=doc.get("project_id", "default"),
                title=doc.get("title", "Untitled"),
                message_count=doc.get("message_count", 0),
                created_at=doc.get("created_at"),
                updated_at=doc.get("updated_at")
            ))
        
        has_more = (skip + page_size) < total_count
        
        return ChatSessionListResponse(
            sessions=sessions,
            total_count=total_count,
            page=page,
            page_size=page_size,
            has_more=has_more
        )
    
    async def update_session_title(self, session_id: str, title: str) -> bool:
        """
        Update session title.
        
        Args:
            session_id: Session identifier
            title: New title
            
        Returns:
            bool: True if updated, False if session not found
        """
        result = await self.sessions_collection.update_one(
            {"_id": session_id},
            {
                "$set": {
                    "title": title,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return result.modified_count > 0
    
    async def update_session_activity(self, session_id: str) -> bool:
        """
        Update session's updated_at timestamp and increment message count.
        
        Args:
            session_id: Session identifier
            
        Returns:
            bool: True if updated, False if session not found
        """
        result = await self.sessions_collection.update_one(
            {"_id": session_id},
            {
                "$set": {"updated_at": datetime.utcnow()},
                "$inc": {"message_count": 1}
            }
        )
        
        return result.modified_count > 0
    
    async def delete_session(self, session_id: str, cascade: bool = True) -> bool:
        """
        Delete a session and optionally cascade delete its messages.
        
        Args:
            session_id: Session identifier
            cascade: If True, also delete all messages in the session
            
        Returns:
            bool: True if deleted, False if session not found
        """
        # Delete messages if cascade
        if cascade:
            delete_result = await self.messages_collection.delete_many({"session_id": session_id})
            logger.info(f"Deleted {delete_result.deleted_count} messages for session {session_id}")
        
        # Delete session
        result = await self.sessions_collection.delete_one({"_id": session_id})
        
        if result.deleted_count > 0:
            logger.info(f"Deleted session {session_id}")
            return True
        
        return False
    
    # ========================================================================
    # Message Operations
    # ========================================================================
    
    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        sources: Optional[List[Dict[str, Any]]] = None,
        routing_info: Optional[Dict[str, Any]] = None,
        safety_info: Optional[Dict[str, Any]] = None,
        tokens: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatMessageResponse:
        """
        Add a message to a session.
        
        Args:
            session_id: Session identifier
            role: Message role ('user' or 'assistant')
            content: Message content
            sources: Retrieved sources for this message
            routing_info: RAG routing metadata
            safety_info: Safety analysis metadata
            tokens: Token count
            metadata: Additional metadata
            
        Returns:
            ChatMessageResponse: Created message
        """
        # Convert sources dict to MessageSource objects if provided
        source_objects = None
        if sources:
            source_objects = [MessageSource(**src) if isinstance(src, dict) else src for src in sources]
        
        message_create = ChatMessageCreate(
            session_id=session_id,
            role=role,
            content=content,
            sources=source_objects,
            routing_info=routing_info,
            safety_info=safety_info,
            tokens=tokens,
            metadata=metadata or {}
        )
        
        message = ChatMessage(
            session_id=message_create.session_id,
            role=message_create.role,
            content=message_create.content,
            sources=message_create.sources,
            routing_info=message_create.routing_info,
            safety_info=message_create.safety_info,
            tokens=message_create.tokens,
            metadata=message_create.metadata
        )
        
        # Convert to dict for MongoDB
        message_dict = message.model_dump(by_alias=True)
        
        # Insert into database
        await self.messages_collection.insert_one(message_dict)
        
        # Update session activity
        await self.update_session_activity(session_id)
        
        logger.info(f"Added {role} message to session {session_id}")
        
        return ChatMessageResponse(
            id=message.id,
            session_id=message.session_id,
            role=message.role,
            content=message.content,
            sources=message.sources,
            routing_info=message.routing_info,
            safety_info=message.safety_info,
            tokens=message.tokens,
            created_at=message.created_at
        )
    
    async def get_messages(
        self,
        session_id: str,
        page: int = 1,
        page_size: int = 50,
        ascending: bool = True
    ) -> MessageListResponse:
        """
        Get messages for a session with pagination.
        
        Args:
            session_id: Session identifier
            page: Page number (1-indexed)
            page_size: Number of messages per page
            ascending: If True, sort by created_at ascending (oldest first)
                      If False, sort descending (newest first)
            
        Returns:
            MessageListResponse: Paginated message list
        """
        # Build query
        query = {"session_id": session_id}
        
        # Get total count
        total_count = await self.messages_collection.count_documents(query)
        
        # Calculate pagination
        skip = (page - 1) * page_size
        
        # Sort direction
        sort_direction = 1 if ascending else -1
        
        # Query messages
        cursor = self.messages_collection.find(query).sort("created_at", sort_direction).skip(skip).limit(page_size)
        
        messages = []
        async for doc in cursor:
            # Convert sources back to MessageSource objects
            sources = None
            if doc.get("sources"):
                sources = [MessageSource(**src) for src in doc["sources"]]
            
            messages.append(ChatMessageResponse(
                id=doc["_id"],
                session_id=doc["session_id"],
                role=doc["role"],
                content=doc["content"],
                sources=sources,
                routing_info=doc.get("routing_info"),
                safety_info=doc.get("safety_info"),
                tokens=doc.get("tokens"),
                created_at=doc["created_at"]
            ))
        
        has_more = (skip + page_size) < total_count
        
        return MessageListResponse(
            messages=messages,
            total_count=total_count,
            page=page,
            page_size=page_size,
            has_more=has_more
        )
    
    async def get_recent_messages(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[ChatMessageResponse]:
        """
        Get the most recent messages for a session.
        
        Args:
            session_id: Session identifier
            limit: Maximum number of messages to return
            
        Returns:
            List[ChatMessageResponse]: List of recent messages (oldest to newest)
        """
        query = {"session_id": session_id}
        
        # Get most recent messages in descending order
        cursor = self.messages_collection.find(query).sort("created_at", -1).limit(limit)
        
        messages = []
        async for doc in cursor:
            sources = None
            if doc.get("sources"):
                sources = [MessageSource(**src) for src in doc["sources"]]
            
            messages.append(ChatMessageResponse(
                id=doc["_id"],
                session_id=doc["session_id"],
                role=doc["role"],
                content=doc["content"],
                sources=sources,
                routing_info=doc.get("routing_info"),
                safety_info=doc.get("safety_info"),
                tokens=doc.get("tokens"),
                created_at=doc["created_at"]
            ))
        
        # Reverse to get chronological order (oldest to newest)
        messages.reverse()
        
        return messages
    
    async def delete_messages(self, session_id: str) -> int:
        """
        Delete all messages for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            int: Number of messages deleted
        """
        result = await self.messages_collection.delete_many({"session_id": session_id})
        logger.info(f"Deleted {result.deleted_count} messages for session {session_id}")
        return result.deleted_count
    
    # ========================================================================
    # Statistics and Health
    # ========================================================================
    
    async def get_session_stats(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dict: Session statistics or None if session not found
        """
        session = await self.get_session(session_id)
        if not session:
            return None
        
        # Count messages by role
        user_messages = await self.messages_collection.count_documents({
            "session_id": session_id,
            "role": "user"
        })
        
        assistant_messages = await self.messages_collection.count_documents({
            "session_id": session_id,
            "role": "assistant"
        })
        
        # Calculate total tokens (if available)
        pipeline = [
            {"$match": {"session_id": session_id, "tokens": {"$exists": True}}},
            {"$group": {"_id": None, "total_tokens": {"$sum": "$tokens"}}}
        ]
        
        token_result = await self.messages_collection.aggregate(pipeline).to_list(1)
        total_tokens = token_result[0]["total_tokens"] if token_result else 0
        
        return {
            "session_id": session_id,
            "title": session.title,
            "total_messages": session.message_count,
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "total_tokens": total_tokens,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat()
        }
    
    async def get_global_stats(self) -> Dict[str, Any]:
        """
        Get global statistics across all sessions and messages.
        
        Returns:
            Dict: Global statistics
        """
        total_sessions = await self.sessions_collection.count_documents({})
        total_messages = await self.messages_collection.count_documents({})
        
        # Count unique users
        unique_users = await self.sessions_collection.distinct("user_id")
        
        # Count unique projects
        unique_projects = await self.sessions_collection.distinct("project_id")
        
        return {
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "unique_users": len([u for u in unique_users if u]),
            "unique_projects": len([p for p in unique_projects if p]),
        }


# Global service instance
_chat_persistence_service: Optional[ChatPersistenceService] = None


def get_chat_persistence_service() -> ChatPersistenceService:
    """
    Get the global chat persistence service instance.
    
    Returns:
        ChatPersistenceService: Service instance
        
    Raises:
        RuntimeError: If service not initialized
    """
    global _chat_persistence_service
    if _chat_persistence_service is None:
        raise RuntimeError("Chat persistence service not initialized")
    return _chat_persistence_service


def initialize_chat_persistence_service(database: AsyncIOMotorDatabase) -> ChatPersistenceService:
    """
    Initialize the global chat persistence service.
    
    Args:
        database: Motor database instance
        
    Returns:
        ChatPersistenceService: Initialized service
    """
    global _chat_persistence_service
    _chat_persistence_service = ChatPersistenceService(database)
    return _chat_persistence_service

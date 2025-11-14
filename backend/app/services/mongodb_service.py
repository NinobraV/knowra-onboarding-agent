"""
MongoDB service for managing database connections and operations.
Uses Motor for async MongoDB operations compatible with FastAPI.
"""
import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure

logger = logging.getLogger(__name__)


class MongoDBService:
    """
    MongoDB service for managing async database connections.
    """
    
    def __init__(
        self,
        mongodb_url: str,
        db_name: str,
        max_pool_size: int = 10,
        min_pool_size: int = 1,
        timeout_ms: int = 5000
    ):
        """
        Initialize MongoDB service.
        
        Args:
            mongodb_url: MongoDB connection URL
            db_name: Database name
            max_pool_size: Maximum connection pool size
            min_pool_size: Minimum connection pool size
            timeout_ms: Server selection timeout in milliseconds
        """
        self.mongodb_url = mongodb_url
        self.db_name = db_name
        self.max_pool_size = max_pool_size
        self.min_pool_size = min_pool_size
        self.timeout_ms = timeout_ms
        
        self._client: Optional[AsyncIOMotorClient] = None
        self._db: Optional[AsyncIOMotorDatabase] = None
        self._connected = False
    
    async def connect(self) -> None:
        """
        Connect to MongoDB and initialize database.
        
        Raises:
            ConnectionFailure: If connection fails
        """
        if self._connected:
            logger.info("MongoDB already connected")
            return
        
        try:
            logger.info(f"Connecting to MongoDB at {self.mongodb_url}")
            
            self._client = AsyncIOMotorClient(
                self.mongodb_url,
                maxPoolSize=self.max_pool_size,
                minPoolSize=self.min_pool_size,
                serverSelectionTimeoutMS=self.timeout_ms
            )
            
            # Test connection
            await self._client.admin.command('ping')
            
            self._db = self._client[self.db_name]
            self._connected = True
            
            logger.info(f"Successfully connected to MongoDB database: {self.db_name}")
            
            # Create indexes
            await self._create_indexes()
            
        except (ServerSelectionTimeoutError, ConnectionFailure) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise ConnectionFailure(f"Could not connect to MongoDB: {e}")
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            raise
    
    async def disconnect(self) -> None:
        """
        Disconnect from MongoDB.
        """
        if self._client:
            self._client.close()
            self._connected = False
            logger.info("Disconnected from MongoDB")
    
    async def _create_indexes(self) -> None:
        """
        Create necessary indexes for optimal query performance.
        """
        try:
            # Sessions collection indexes
            sessions_collection = self._db.chat_sessions
            
            # Index on user_id for filtering user's sessions
            await sessions_collection.create_index("user_id")
            
            # Index on project_id for filtering by project
            await sessions_collection.create_index("project_id")
            
            # Compound index on user_id + project_id for combined filtering
            await sessions_collection.create_index([
                ("user_id", 1),
                ("project_id", 1)
            ])
            
            # Index on updated_at for sorting by recent activity (descending)
            await sessions_collection.create_index([("updated_at", -1)])
            
            # Index on created_at for sorting by creation time
            await sessions_collection.create_index([("created_at", -1)])
            
            logger.info("Created indexes on chat_sessions collection")
            
            # Messages collection indexes
            messages_collection = self._db.chat_messages
            
            # Compound index on session_id + created_at for chronological message retrieval
            # This is the most important index for pagination queries
            await messages_collection.create_index([
                ("session_id", 1),
                ("created_at", 1)
            ])
            
            # Index on session_id alone for counting and filtering
            await messages_collection.create_index("session_id")
            
            # Index on created_at for general time-based queries
            await messages_collection.create_index([("created_at", -1)])
            
            # Optional: Index on role for filtering by user/assistant messages
            await messages_collection.create_index("role")
            
            logger.info("Created indexes on chat_messages collection")
            
            # Optional: TTL index for automatic message expiration (e.g., after 90 days)
            # Uncomment if you want automatic cleanup of old messages
            # await messages_collection.create_index(
            #     "created_at",
            #     expireAfterSeconds=90 * 24 * 60 * 60  # 90 days
            # )
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            # Don't raise - indexes are optional for functionality
    
    @property
    def database(self) -> AsyncIOMotorDatabase:
        """
        Get the database instance.
        
        Returns:
            AsyncIOMotorDatabase: Motor database instance
            
        Raises:
            RuntimeError: If not connected to database
        """
        if not self._connected or self._db is None:
            raise RuntimeError("Not connected to MongoDB. Call connect() first.")
        return self._db
    
    @property
    def is_connected(self) -> bool:
        """
        Check if connected to MongoDB.
        
        Returns:
            bool: True if connected
        """
        return self._connected
    
    async def health_check(self) -> dict:
        """
        Perform a health check on the MongoDB connection.
        
        Returns:
            dict: Health check results
        """
        try:
            if not self._connected:
                return {
                    "status": "disconnected",
                    "database": self.db_name,
                    "error": "Not connected to MongoDB"
                }
            
            # Ping the database
            await self._client.admin.command('ping')
            
            # Get database stats
            stats = await self._db.command('dbStats')
            
            return {
                "status": "connected",
                "database": self.db_name,
                "collections": stats.get('collections', 0),
                "dataSize": stats.get('dataSize', 0),
                "indexSize": stats.get('indexSize', 0)
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "error",
                "database": self.db_name,
                "error": str(e)
            }


# Global MongoDB service instance
_mongodb_service: Optional[MongoDBService] = None


def get_mongodb_service() -> MongoDBService:
    """
    Get the global MongoDB service instance.
    
    Returns:
        MongoDBService: MongoDB service instance
        
    Raises:
        RuntimeError: If service not initialized
    """
    global _mongodb_service
    if _mongodb_service is None:
        raise RuntimeError("MongoDB service not initialized. Call initialize_mongodb() first.")
    return _mongodb_service


def initialize_mongodb(
    mongodb_url: str,
    db_name: str,
    max_pool_size: int = 10,
    min_pool_size: int = 1,
    timeout_ms: int = 5000
) -> MongoDBService:
    """
    Initialize the global MongoDB service instance.
    
    Args:
        mongodb_url: MongoDB connection URL
        db_name: Database name
        max_pool_size: Maximum connection pool size
        min_pool_size: Minimum connection pool size
        timeout_ms: Server selection timeout
        
    Returns:
        MongoDBService: Initialized MongoDB service
    """
    global _mongodb_service
    _mongodb_service = MongoDBService(
        mongodb_url=mongodb_url,
        db_name=db_name,
        max_pool_size=max_pool_size,
        min_pool_size=min_pool_size,
        timeout_ms=timeout_ms
    )
    return _mongodb_service

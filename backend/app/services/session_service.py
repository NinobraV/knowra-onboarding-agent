"""
session_service.py

Session management service for handling user sessions and project scoping.
Provides session creation, tracking, and cleanup functionality.
"""

import uuid
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger("session_service")


class SessionStatus(Enum):
    """Session status types."""
    ACTIVE = "active"
    IDLE = "idle"
    EXPIRED = "expired"
    TERMINATED = "terminated"


@dataclass
class SessionInfo:
    """Session information container."""
    session_id: str
    user_id: Optional[str]
    project_id: Optional[str]
    session_name: Optional[str]
    status: SessionStatus
    created_at: datetime
    last_activity: datetime
    expires_at: Optional[datetime]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        for field in ['created_at', 'last_activity', 'expires_at']:
            if data[field]:
                data[field] = data[field].isoformat() if isinstance(data[field], datetime) else data[field]
        data['status'] = data['status'].value if hasattr(data['status'], 'value') else str(data['status'])
        return data


class SessionStore:
    """Session storage backend."""
    
    def __init__(self, redis_url: Optional[str] = None, prefix: str = "session:"):
        """Initialize session store."""
        self.prefix = prefix
        self.enabled = False
        self._client = None
        
        if redis_url and REDIS_AVAILABLE:
            try:
                self._client = redis.from_url(redis_url, decode_responses=True)
                # Test connection
                self._client.ping()
                self.enabled = True
                logger.info("Redis session store initialized")
            except Exception as e:
                logger.warning(f"Redis session store init failed: {e}. Using in-memory store.")
                
        # Fallback in-memory store
        self._memory_sessions: Dict[str, SessionInfo] = {}
        
    def _key(self, session_id: str) -> str:
        """Generate Redis key for session."""
        return f"{self.prefix}{session_id}"
    
    def store_session(self, session: SessionInfo) -> None:
        """Store session information."""
        if self.enabled:
            try:
                import json
                data = session.to_dict()
                self._client.setex(
                    self._key(session.session_id),
                    int(timedelta(days=7).total_seconds()),  # 7 day expiration
                    json.dumps(data)
                )
            except Exception as e:
                logger.error(f"Failed to store session in Redis: {e}")
                self._memory_sessions[session.session_id] = session
        else:
            self._memory_sessions[session.session_id] = session
    
    def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """Get session by ID."""
        if self.enabled:
            try:
                import json
                data = self._client.get(self._key(session_id))
                if data:
                    session_data = json.loads(data)
                    return self._dict_to_session(session_data)
            except Exception as e:
                logger.error(f"Failed to get session from Redis: {e}")
        
        return self._memory_sessions.get(session_id)
    
    def list_sessions(
        self, 
        user_id: Optional[str] = None, 
        project_id: Optional[str] = None,
        status: Optional[SessionStatus] = None,
        limit: int = 50
    ) -> List[SessionInfo]:
        """List sessions with optional filters."""
        sessions = []
        
        if self.enabled:
            try:
                pattern = f"{self.prefix}*"
                keys = list(self._client.scan_iter(match=pattern))
                
                for key in keys[:limit]:  # Basic limit
                    try:
                        import json
                        data = self._client.get(key)
                        if data:
                            session_data = json.loads(data)
                            session = self._dict_to_session(session_data)
                            if self._matches_filters(session, user_id, project_id, status):
                                sessions.append(session)
                    except Exception:
                        continue
                        
            except Exception as e:
                logger.error(f"Failed to list sessions from Redis: {e}")
        
        # Also check memory store
        for session in list(self._memory_sessions.values())[:limit]:
            if self._matches_filters(session, user_id, project_id, status):
                sessions.append(session)
        
        # Sort by last_activity (most recent first)
        sessions.sort(key=lambda s: s.last_activity, reverse=True)
        return sessions[:limit]
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session."""
        deleted = False
        
        if self.enabled:
            try:
                result = self._client.delete(self._key(session_id))
                deleted = bool(result)
            except Exception as e:
                logger.error(f"Failed to delete session from Redis: {e}")
        
        if session_id in self._memory_sessions:
            del self._memory_sessions[session_id]
            deleted = True
            
        return deleted
    
    def update_activity(self, session_id: str) -> None:
        """Update last activity timestamp for session."""
        session = self.get_session(session_id)
        if session:
            session.last_activity = datetime.utcnow()
            session.status = SessionStatus.ACTIVE
            self.store_session(session)
    
    def _dict_to_session(self, data: Dict[str, Any]) -> SessionInfo:
        """Convert dictionary to SessionInfo."""
        # Convert ISO strings back to datetime objects
        for field in ['created_at', 'last_activity', 'expires_at']:
            if data.get(field):
                try:
                    data[field] = datetime.fromisoformat(data[field].replace('Z', '+00:00'))
                except Exception:
                    data[field] = datetime.utcnow()
        
        # Convert status string to enum
        if isinstance(data.get('status'), str):
            try:
                data['status'] = SessionStatus(data['status'])
            except ValueError:
                data['status'] = SessionStatus.ACTIVE
        
        return SessionInfo(**data)
    
    def _matches_filters(
        self, 
        session: SessionInfo, 
        user_id: Optional[str], 
        project_id: Optional[str], 
        status: Optional[SessionStatus]
    ) -> bool:
        """Check if session matches filters."""
        if user_id and session.user_id != user_id:
            return False
        if project_id and session.project_id != project_id:
            return False
        if status and session.status != status:
            return False
        return True


class SessionService:
    """
    Session management service for conversation continuity and project scoping.
    """
    
    def __init__(
        self, 
        redis_url: Optional[str] = None,
        default_session_ttl: timedelta = timedelta(days=7),
        cleanup_interval: timedelta = timedelta(hours=1)
    ):
        """
        Initialize session service.
        
        Args:
            redis_url: Optional Redis URL for persistent session storage
            default_session_ttl: Default time-to-live for sessions
            cleanup_interval: How often to run cleanup of expired sessions
        """
        self.session_store = SessionStore(redis_url)
        self.default_session_ttl = default_session_ttl
        self.cleanup_interval = cleanup_interval
        self._last_cleanup = datetime.utcnow()
        
    def create_session(
        self,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        session_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SessionInfo:
        """
        Create a new session.
        
        Args:
            user_id: Optional user identifier
            project_id: Optional project identifier
            session_name: Optional human-readable session name
            metadata: Optional additional session metadata
            
        Returns:
            SessionInfo: Created session information
        """
        session_id = f"session-{uuid.uuid4()}"
        now = datetime.utcnow()
        expires_at = now + self.default_session_ttl
        
        session = SessionInfo(
            session_id=session_id,
            user_id=user_id,
            project_id=project_id,
            session_name=session_name or f"Session {now.strftime('%Y-%m-%d %H:%M')}",
            status=SessionStatus.ACTIVE,
            created_at=now,
            last_activity=now,
            expires_at=expires_at,
            metadata=metadata or {}
        )
        
        self.session_store.store_session(session)
        logger.info(f"Created session {session_id} for user {user_id}, project {project_id}")
        
        return session
    
    def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """
        Get session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            SessionInfo: Session information if found
        """
        session = self.session_store.get_session(session_id)
        if session:
            # Check if session is expired
            if self._is_session_expired(session):
                session.status = SessionStatus.EXPIRED
                self.session_store.store_session(session)
                return session  # Return expired session for cleanup
            
        return session
    
    def get_or_create_session(
        self,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        session_name: Optional[str] = None
    ) -> SessionInfo:
        """
        Get existing session or create new one if not found.
        
        Args:
            session_id: Optional existing session ID
            user_id: Optional user identifier
            project_id: Optional project identifier  
            session_name: Optional session name
            
        Returns:
            SessionInfo: Existing or newly created session
        """
        if session_id:
            session = self.get_session(session_id)
            if session and session.status != SessionStatus.EXPIRED:
                # Update activity and return existing session
                self.update_session_activity(session_id)
                return session
        
        # Create new session
        return self.create_session(
            user_id=user_id,
            project_id=project_id,
            session_name=session_name
        )
    
    def list_sessions(
        self,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        status: Optional[SessionStatus] = None,
        limit: int = 50
    ) -> List[SessionInfo]:
        """
        List sessions with optional filters.
        
        Args:
            user_id: Filter by user ID
            project_id: Filter by project ID
            status: Filter by session status
            limit: Maximum number of sessions to return
            
        Returns:
            List[SessionInfo]: Filtered list of sessions
        """
        return self.session_store.list_sessions(user_id, project_id, status, limit)
    
    def update_session_activity(self, session_id: str) -> bool:
        """
        Update session activity timestamp.
        
        Args:
            session_id: Session identifier
            
        Returns:
            bool: True if session was updated
        """
        session = self.session_store.get_session(session_id)
        if session and not self._is_session_expired(session):
            self.session_store.update_activity(session_id)
            return True
        return False
    
    def terminate_session(self, session_id: str) -> bool:
        """
        Terminate a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            bool: True if session was terminated
        """
        session = self.session_store.get_session(session_id)
        if session:
            session.status = SessionStatus.TERMINATED
            session.last_activity = datetime.utcnow()
            self.session_store.store_session(session)
            logger.info(f"Terminated session {session_id}")
            return True
        return False
    
    def delete_session(self, session_id: str) -> bool:
        """
        Permanently delete a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            bool: True if session was deleted
        """
        deleted = self.session_store.delete_session(session_id)
        if deleted:
            logger.info(f"Deleted session {session_id}")
        return deleted
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions.
        
        Returns:
            int: Number of sessions cleaned up
        """
        now = datetime.utcnow()
        if now - self._last_cleanup < self.cleanup_interval:
            return 0  # Skip cleanup if not enough time has passed
        
        sessions = self.list_sessions(limit=1000)  # Get more for cleanup
        cleaned_count = 0
        
        for session in sessions:
            if self._is_session_expired(session):
                # Mark as expired but don't delete immediately
                if session.status != SessionStatus.EXPIRED:
                    session.status = SessionStatus.EXPIRED
                    self.session_store.store_session(session)
                
                # Delete sessions that have been expired for more than 24 hours
                if session.expires_at and (now - session.expires_at) > timedelta(days=1):
                    self.delete_session(session.session_id)
                    cleaned_count += 1
        
        self._last_cleanup = now
        if cleaned_count > 0:
            logger.info(f"Cleaned up {cleaned_count} expired sessions")
        
        return cleaned_count
    
    def _is_session_expired(self, session: SessionInfo) -> bool:
        """Check if session is expired."""
        if not session.expires_at:
            return False
        return datetime.utcnow() > session.expires_at
    
    def generate_session_id(self, prefix: str = "session") -> str:
        """Generate a unique session ID."""
        return f"{prefix}-{uuid.uuid4()}"
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        all_sessions = self.list_sessions(limit=1000)
        
        stats = {
            "total_sessions": len(all_sessions),
            "active_sessions": len([s for s in all_sessions if s.status == SessionStatus.ACTIVE]),
            "idle_sessions": len([s for s in all_sessions if s.status == SessionStatus.IDLE]),
            "expired_sessions": len([s for s in all_sessions if s.status == SessionStatus.EXPIRED]),
            "terminated_sessions": len([s for s in all_sessions if s.status == SessionStatus.TERMINATED]),
            "projects": len(set(s.project_id for s in all_sessions if s.project_id)),
            "users": len(set(s.user_id for s in all_sessions if s.user_id))
        }
        
        return stats
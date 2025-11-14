"""
enhanced_memory_service.py

Enhanced memory management system that provides:
- ConversationSummaryBuffer for token optimization
- Dynamic window sizing based on content
- Fact-based long-term storage
- Session and project-scoped memory
- Cleanup and garbage collection
"""

import logging
import time
from typing import Dict, List, Optional, Any, Callable, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

# Import our fact extractor
try:
    from .fact_extractor_service import FactExtractorService, FactType, ImportanceLevel
    FACT_EXTRACTOR_AVAILABLE = False
    FactExtractorType = FactExtractorService
except ImportError:
    FactExtractorService = None
    FactType = None
    ImportanceLevel = None
    FACT_EXTRACTOR_AVAILABLE = False
    FactExtractorType = type(None)

# Import session service
try:
    from ..session_service import SessionService, SessionInfo
    SESSION_SERVICE_AVAILABLE = True
except ImportError:
    SESSION_SERVICE_AVAILABLE = False

logger = logging.getLogger("enhanced_memory_service")


class MemoryType(Enum):
    """Types of memory storage."""
    SHORT_TERM = "short_term"      # Recent conversation messages
    LONG_TERM = "long_term"        # Extracted facts and summarized conversations
    SUMMARY = "summary"            # Conversation summaries
    FACT = "fact"                  # Structured facts


class MemoryPriority(Enum):
    """Memory retention priorities."""
    CRITICAL = "critical"          # Must retain
    HIGH = "high"                 # Important to retain
    MEDIUM = "medium"             # Normal retention
    LOW = "low"                   # May be garbage collected
    DISPOSABLE = "disposable"     # Can be deleted anytime


@dataclass
class MemoryEntry:
    """Enhanced memory entry with metadata."""
    id: str
    content: str
    memory_type: MemoryType
    priority: MemoryPriority
    created_at: datetime
    last_accessed: datetime
    session_id: str
    project_id: Optional[str]
    metadata: Dict[str, Any]
    expires_at: Optional[datetime] = None
    access_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'content': self.content,
            'memory_type': self.memory_type.value,
            'priority': self.priority.value,
            'created_at': self.created_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat(),
            'session_id': self.session_id,
            'project_id': self.project_id,
            'metadata': self.metadata,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'access_count': self.access_count
        }


class ConversationSummaryBuffer:
    """
    Buffer that maintains recent messages and creates summaries when window is exceeded.
    """
    
    def __init__(
        self,
        max_messages: int = 12,
        summary_threshold: int = 8,
        summarizer: Optional[Callable[[List[Dict]], str]] = None
    ):
        """
        Initialize conversation summary buffer.
        
        Args:
            max_messages: Maximum number of messages to keep in buffer
            summary_threshold: When to trigger summarization
            summarizer: Function to create summaries from message lists
        """
        self.max_messages = max_messages
        self.summary_threshold = summary_threshold
        self.summarizer = summarizer or self._default_summarizer
        self.messages: List[Dict[str, Any]] = []
        self.summaries: List[str] = []
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None) -> None:
        """Add a message to the buffer."""
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.utcnow().isoformat(),
            'metadata': metadata or {}
        }
        
        self.messages.append(message)
        
        # Trigger summarization if threshold exceeded
        if len(self.messages) > self.summary_threshold:
            self._maybe_summarize()
    
    def get_context(self, include_summaries: bool = True) -> List[Dict[str, Any]]:
        """Get current context (summaries + recent messages)."""
        context = []
        
        if include_summaries:
            for summary in self.summaries:
                context.append({
                    'role': 'system',
                    'content': f"Previous conversation summary: {summary}",
                    'metadata': {'type': 'summary'}
                })
        
        context.extend(self.messages)
        return context
    
    def _maybe_summarize(self) -> None:
        """Summarize older messages if buffer is full."""
        if len(self.messages) > self.max_messages:
            # Take messages to summarize (leave recent ones)
            to_summarize = self.messages[:-self.summary_threshold]
            self.messages = self.messages[-self.summary_threshold:]
            
            if to_summarize:
                summary = self.summarizer(to_summarize)
                if summary:
                    self.summaries.append(summary)
                    # Keep only recent summaries
                    if len(self.summaries) > 3:
                        self.summaries = self.summaries[-3:]
    
    def _default_summarizer(self, messages: List[Dict[str, Any]]) -> str:
        """Default message summarization."""
        if not messages:
            return ""
        
        # Simple summarization - extract key points
        user_messages = [msg for msg in messages if msg.get('role') == 'user']
        assistant_messages = [msg for msg in messages if msg.get('role') == 'assistant']
        
        summary_parts = []
        
        if user_messages:
            topics = []
            for msg in user_messages:
                content = msg.get('content', '')
                # Extract potential topics (very basic)
                if any(word in content.lower() for word in ['what', 'how', 'explain']):
                    topics.append(content[:50] + "..." if len(content) > 50 else content)
            
            if topics:
                summary_parts.append(f"User asked about: {'; '.join(topics[:3])}")
        
        if assistant_messages:
            summary_parts.append(f"Assistant provided {len(assistant_messages)} responses")
        
        return ". ".join(summary_parts) if summary_parts else "General conversation"
    
    def clear(self) -> None:
        """Clear all messages and summaries."""
        self.messages.clear()
        self.summaries.clear()


class EnhancedMemoryStore:
    """
    Enhanced memory store with multiple storage backends and intelligent management.
    """
    
    def __init__(
        self,
        vector_store_service: Optional[Any] = None,
        fact_extractor: Optional[Any] = None,
        redis_url: Optional[str] = None,
        namespace_prefix: str = "enhanced_memory:"
    ):
        """
        Initialize enhanced memory store.
        
        Args:
            vector_store_service: Vector store for semantic memory search
            fact_extractor: Fact extraction service
            redis_url: Optional Redis URL for persistence
            namespace_prefix: Prefix for memory namespaces
        """
        self.vector_store_service = vector_store_service
        self.fact_extractor = fact_extractor
        self.namespace_prefix = namespace_prefix
        
        # In-memory storage for different memory types
        self.short_term_memory: Dict[str, List[MemoryEntry]] = {}  # session_id -> entries
        self.long_term_memory: Dict[str, List[MemoryEntry]] = {}   # session_id -> entries
        self.fact_memory: Dict[str, List[Dict]] = {}               # session_id -> facts
        
        # Summary buffers per session
        self.conversation_buffers: Dict[str, ConversationSummaryBuffer] = {}
        
        # Configuration
        self.max_short_term_entries = 50
        self.max_long_term_entries = 200
        self.fact_retention_days = 30
        
    def add_conversation_turn(
        self,
        session_id: str,
        user_message: str,
        assistant_response: str,
        project_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a complete conversation turn (user + assistant).
        
        Args:
            session_id: Session identifier
            user_message: User's message
            assistant_response: Assistant's response
            project_id: Optional project identifier
            metadata: Additional metadata
        """
        metadata = metadata or {}
        now = datetime.utcnow()
        
        # Get or create conversation buffer for session
        if session_id not in self.conversation_buffers:
            summarizer = self._create_smart_summarizer()
            self.conversation_buffers[session_id] = ConversationSummaryBuffer(
                max_messages=12,
                summary_threshold=8,
                summarizer=summarizer
            )
        
        buffer = self.conversation_buffers[session_id]
        
        # Add messages to conversation buffer
        buffer.add_message('user', user_message, metadata.get('user_metadata'))
        buffer.add_message('assistant', assistant_response, metadata.get('assistant_metadata'))
        
        # Store in short-term memory
        self._add_short_term_memory(
            session_id, user_message, 'user', project_id, metadata
        )
        self._add_short_term_memory(
            session_id, assistant_response, 'assistant', project_id, metadata
        )
        
        # Extract and store facts
        if self.fact_extractor:
            self._extract_and_store_facts(
                session_id, user_message, project_id, metadata
            )
            
        # Store important information in long-term memory
        self._maybe_promote_to_long_term(session_id, user_message, assistant_response, project_id)
        
        # Trigger cleanup if needed
        self._maybe_cleanup_session_memory(session_id)
    
    def get_relevant_context(
        self,
        session_id: str,
        query: str,
        max_entries: int = 10,
        include_facts: bool = True,
        include_summaries: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get relevant context for a query.
        
        Args:
            session_id: Session identifier
            query: Query to find relevant context for
            max_entries: Maximum number of context entries
            include_facts: Whether to include extracted facts
            include_summaries: Whether to include conversation summaries
            
        Returns:
            List of relevant context entries
        """
        context = []
        
        # Get conversation buffer context
        if session_id in self.conversation_buffers and include_summaries:
            buffer_context = self.conversation_buffers[session_id].get_context()
            context.extend(buffer_context)
        
        # Get recent short-term memory
        short_term = self.short_term_memory.get(session_id, [])
        for entry in reversed(short_term[-5:]):  # Last 5 entries
            context.append({
                'role': 'memory',
                'content': entry.content,
                'metadata': {
                    'type': 'short_term',
                    'created_at': entry.created_at.isoformat(),
                    **entry.metadata
                }
            })
        
        # Get relevant long-term memory (semantic search if available)
        if self.vector_store_service:
            try:
                # Search in memory namespace
                memory_namespace = f"memory_{session_id}"
                relevant_memories = self.vector_store_service.semantic_search(
                    query, k=3, namespace=memory_namespace
                )
                
                for memory in relevant_memories:
                    context.append({
                        'role': 'memory',
                        'content': memory.page_content,
                        'metadata': {
                            'type': 'long_term_semantic',
                            'score': getattr(memory, 'score', 0.0),
                            **memory.metadata
                        }
                    })
            except Exception as e:
                logger.debug(f"Semantic memory search failed: {e}")
        
        # Get relevant facts
        if include_facts and session_id in self.fact_memory:
            facts = self.fact_memory[session_id]
            # Get high-importance facts that might be relevant
            relevant_facts = [
                fact for fact in facts 
                if fact.get('importance') in ['critical', 'high'] and
                self._is_fact_relevant(fact, query)
            ]
            
            for fact in relevant_facts[:3]:  # Top 3 facts
                context.append({
                    'role': 'fact',
                    'content': fact.get('content', ''),
                    'metadata': {
                        'type': 'extracted_fact',
                        'fact_type': fact.get('fact_type'),
                        'confidence': fact.get('confidence', 0.0),
                        **fact.get('metadata', {})
                    }
                })
        
        # Limit total context size
        if len(context) > max_entries:
            # Prioritize: facts > summaries > recent memory > older memory
            prioritized = []
            
            # Add facts first
            prioritized.extend([c for c in context if c.get('role') == 'fact'])
            
            # Add summaries
            prioritized.extend([c for c in context if c.get('metadata', {}).get('type') == 'summary'])
            
            # Add remaining entries up to limit
            remaining = [c for c in context if c not in prioritized]
            prioritized.extend(remaining[:max_entries - len(prioritized)])
            
            context = prioritized[:max_entries]
        
        return context
    
    def _add_short_term_memory(
        self,
        session_id: str,
        content: str,
        role: str,
        project_id: Optional[str],
        metadata: Dict[str, Any]
    ) -> None:
        """Add entry to short-term memory."""
        if session_id not in self.short_term_memory:
            self.short_term_memory[session_id] = []
        
        entry = MemoryEntry(
            id=f"st_{session_id}_{int(time.time())}_{len(self.short_term_memory[session_id])}",
            content=content,
            memory_type=MemoryType.SHORT_TERM,
            priority=MemoryPriority.MEDIUM,
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
            session_id=session_id,
            project_id=project_id,
            metadata={
                'role': role,
                **metadata
            }
        )
        
        self.short_term_memory[session_id].append(entry)
        
        # Keep only recent entries
        if len(self.short_term_memory[session_id]) > self.max_short_term_entries:
            self.short_term_memory[session_id] = self.short_term_memory[session_id][-self.max_short_term_entries:]
    
    def _should_extract_facts(self, message: str, metadata: Dict[str, Any]) -> bool:
        """
        Determine if a message warrants fact extraction.
        Separates fact-extraction worthy queries from normal conversational queries.
        
        Args:
            message: Message text
            metadata: Message metadata
            
        Returns:
            True if facts should be extracted, False otherwise
        """
        # Skip fact extraction for very short messages (likely simple questions)
        if len(message.split()) < 5:
            return False
        
        # Skip for simple question queries that don't contain factual information
        simple_question_patterns = [
            r'^\s*(?:what|how|why|when|where|who|can|could|would|should|is|are|do|does)\s+',
            r'^\s*(?:tell me|show me|explain|describe)\s+(?:about|how|what)',
            r'^\s*(?:help|assist|guide)',
        ]
        
        import re
        message_lower = message.lower().strip()
        for pattern in simple_question_patterns:
            if re.match(pattern, message_lower):
                # These are information-seeking queries, not fact-stating messages
                return False
        
        # Extract facts from messages that contain structured information
        fact_indicator_patterns = [
            # Configuration/credentials
            r'\b(?:password|api[_\s-]?key|token|secret|credential)\b',
            r'\b(?:config|configuration|setting|environment)\s+(?:is|in|at|=)',
            
            # File/location references
            r'\b(?:file|folder|directory|path)\s+(?:is|in|at|located)',
            r'\b\w+\.\w+\s+(?:is|in|at|contains)',
            
            # Process/procedural information
            r'\b(?:step|process|procedure|workflow)\s+\d+',
            r'\b(?:first|then|next|finally|after that)\s+\w+',
            
            # System/technical information
            r'\b(?:server|database|endpoint|url|host)\s+(?:is|at)',
            r'\b(?:runs?|deploy|install|configure)\s+(?:on|at|in)',
            
            # Declarative statements
            r'\b(?:the|this|that)\s+\w+\s+(?:is|are|contains?|stores?|uses?)',
            r'\bwe\s+(?:use|store|keep|maintain)',
        ]
        
        for pattern in fact_indicator_patterns:
            if re.search(pattern, message_lower):
                return True
        
        # Extract facts from longer, detailed responses (likely containing instructions)
        if len(message.split()) > 30:
            return True
        
        # Check metadata for fact-extraction hints
        if metadata.get('force_fact_extraction', False):
            return True
        
        # Default to not extracting for typical conversational queries
        return False
    
    def _extract_and_store_facts(
        self,
        session_id: str,
        message: str,
        project_id: Optional[str],
        metadata: Dict[str, Any]
    ) -> None:
        """
        Extract and store facts from message (only for fact-worthy messages).
        This separates fact extraction queries from normal conversational queries.
        """
        if not self.fact_extractor:
            return
        
        # Check if this message warrants fact extraction
        if not self._should_extract_facts(message, metadata):
            logger.debug(f"Skipping fact extraction for simple query: {message[:50]}...")
            return
        
        try:
            logger.debug(f"Extracting facts from message: {message[:50]}...")
            facts = self.fact_extractor.extract_facts(
                message, session_id, project_id, context=metadata
            )
            
            if facts:
                if session_id not in self.fact_memory:
                    self.fact_memory[session_id] = []
                
                for fact in facts:
                    fact_dict = self.fact_extractor.serialize_fact(fact)
                    self.fact_memory[session_id].append(fact_dict)
                    
                logger.info(f"Extracted {len(facts)} facts from message for session {session_id}")
            else:
                logger.debug(f"No facts extracted from message")
        except Exception as e:
            logger.error(f"Fact extraction failed: {e}")
    
    def _maybe_promote_to_long_term(
        self,
        session_id: str,
        user_message: str,
        assistant_response: str,
        project_id: Optional[str]
    ) -> None:
        """Promote important information to long-term memory."""
        # Simple heuristics for promotion
        promotion_keywords = [
            'important', 'remember', 'key', 'critical', 'deadline',
            'password', 'config', 'server', 'database', 'api'
        ]
        
        messages_to_promote = []
        
        # Check user message
        if any(keyword in user_message.lower() for keyword in promotion_keywords):
            messages_to_promote.append((user_message, 'user', MemoryPriority.HIGH))
        
        # Check assistant response
        if any(keyword in assistant_response.lower() for keyword in promotion_keywords):
            messages_to_promote.append((assistant_response, 'assistant', MemoryPriority.HIGH))
        
        # Long responses might be important
        if len(assistant_response) > 500:
            messages_to_promote.append((assistant_response, 'assistant', MemoryPriority.MEDIUM))
        
        # Store in long-term memory
        for content, role, priority in messages_to_promote:
            self._add_long_term_memory(session_id, content, role, project_id, priority)
    
    def _add_long_term_memory(
        self,
        session_id: str,
        content: str,
        role: str,
        project_id: Optional[str],
        priority: MemoryPriority
    ) -> None:
        """Add entry to long-term memory."""
        if session_id not in self.long_term_memory:
            self.long_term_memory[session_id] = []
        
        entry = MemoryEntry(
            id=f"lt_{session_id}_{int(time.time())}_{len(self.long_term_memory[session_id])}",
            content=content,
            memory_type=MemoryType.LONG_TERM,
            priority=priority,
            created_at=datetime.utcnow(),
            last_accessed=datetime.utcnow(),
            session_id=session_id,
            project_id=project_id,
            metadata={'role': role}
        )
        
        self.long_term_memory[session_id].append(entry)
        
        # Store in vector store if available
        if self.vector_store_service:
            try:
                memory_namespace = f"memory_{session_id}"
                memory_item = {
                    'id': entry.id,
                    'text': content,
                    'metadata': {
                        'memory_type': 'long_term',
                        'role': role,
                        'priority': priority.value,
                        'created_at': entry.created_at.isoformat(),
                        'session_id': session_id,
                        'project_id': project_id
                    }
                }
                
                self.vector_store_service.upsert_embeddings([memory_item], namespace=memory_namespace)
                
            except Exception as e:
                logger.error(f"Failed to store in vector memory: {e}")
    
    def _maybe_cleanup_session_memory(self, session_id: str) -> None:
        """Clean up session memory if it gets too large."""
        # Clean up long-term memory
        if session_id in self.long_term_memory:
            entries = self.long_term_memory[session_id]
            if len(entries) > self.max_long_term_entries:
                # Sort by priority and last_accessed, keep high-priority recent ones
                entries.sort(key=lambda e: (e.priority.value, e.last_accessed), reverse=True)
                self.long_term_memory[session_id] = entries[:self.max_long_term_entries]
        
        # Clean up old facts
        if session_id in self.fact_memory:
            facts = self.fact_memory[session_id]
            cutoff_date = datetime.utcnow() - timedelta(days=self.fact_retention_days)
            
            self.fact_memory[session_id] = [
                fact for fact in facts
                if datetime.fromisoformat(str(fact.get('extracted_at', datetime.utcnow().isoformat()))) > cutoff_date or
                fact.get('importance') in ['critical', 'high']
            ]
    
    def _create_smart_summarizer(self) -> Callable[[List[Dict]], str]:
        """Create a smart summarizer function."""
        def smart_summarizer(messages: List[Dict[str, Any]]) -> str:
            if not messages:
                return ""
            
            # Extract key information
            topics = set()
            actions = set()
            
            for msg in messages:
                content = msg.get('content', '').lower()
                
                # Extract topics (simple keyword extraction)
                if any(word in content for word in ['what is', 'explain', 'about']):
                    # Try to extract the topic
                    for word in content.split():
                        if len(word) > 4 and word.isalpha():
                            topics.add(word)
                
                # Extract actions
                if any(word in content for word in ['how to', 'configure', 'setup', 'install']):
                    actions.add('configuration/setup discussed')
                
                if any(word in content for word in ['error', 'problem', 'issue', 'fix']):
                    actions.add('troubleshooting discussed')
            
            summary_parts = []
            if topics:
                summary_parts.append(f"Discussed: {', '.join(list(topics)[:3])}")
            if actions:
                summary_parts.append(f"Actions: {', '.join(actions)}")
            
            return '. '.join(summary_parts) if summary_parts else f"Conversation with {len(messages)} messages"
        
        return smart_summarizer
    
    def _is_fact_relevant(self, fact: Dict[str, Any], query: str) -> bool:
        """Check if a fact is relevant to the query."""
        query_lower = query.lower()
        fact_content = fact.get('content', '').lower()
        
        # Simple relevance check
        query_words = set(query_lower.split())
        fact_words = set(fact_content.split())
        
        # Check for word overlap
        overlap = len(query_words.intersection(fact_words))
        return overlap > 0
    
    def clear_session_memory(self, session_id: str) -> None:
        """Clear all memory for a session."""
        # Clear in-memory storage
        self.short_term_memory.pop(session_id, None)
        self.long_term_memory.pop(session_id, None)
        self.fact_memory.pop(session_id, None)
        self.conversation_buffers.pop(session_id, None)
        
        # Clear vector store memory
        if self.vector_store_service:
            try:
                memory_namespace = f"memory_{session_id}"
                self.vector_store_service.delete_namespace(memory_namespace)
            except Exception as e:
                logger.error(f"Failed to clear vector memory: {e}")
        
        logger.info(f"Cleared all memory for session {session_id}")
    
    def get_memory_stats(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get memory statistics."""
        if session_id:
            # Session-specific stats
            stats = {
                'session_id': session_id,
                'short_term_entries': len(self.short_term_memory.get(session_id, [])),
                'long_term_entries': len(self.long_term_memory.get(session_id, [])),
                'facts_stored': len(self.fact_memory.get(session_id, [])),
                'has_conversation_buffer': session_id in self.conversation_buffers,
                'buffer_messages': len(self.conversation_buffers[session_id].messages) if session_id in self.conversation_buffers else 0,
                'buffer_summaries': len(self.conversation_buffers[session_id].summaries) if session_id in self.conversation_buffers else 0
            }
        else:
            # Global stats
            stats = {
                'total_sessions': len(set(list(self.short_term_memory.keys()) + list(self.long_term_memory.keys()) + list(self.fact_memory.keys()))),
                'total_short_term_entries': sum(len(entries) for entries in self.short_term_memory.values()),
                'total_long_term_entries': sum(len(entries) for entries in self.long_term_memory.values()),
                'total_facts': sum(len(facts) for facts in self.fact_memory.values()),
                'active_buffers': len(self.conversation_buffers),
                'fact_extractor_enabled': self.fact_extractor is not None,
                'vector_store_enabled': self.vector_store_service is not None
            }
        
        return stats


class EnhancedMemoryService:
    """
    Enhanced memory service that orchestrates all memory components.
    """
    
    def __init__(
        self,
        vector_store_service: Optional[Any] = None,
        fact_extractor: Optional[Any] = None,
        session_service: Optional[Any] = None,
        redis_url: Optional[str] = None
    ):
        """
        Initialize enhanced memory service.
        
        Args:
            vector_store_service: Vector store for semantic memory
            fact_extractor: Fact extraction service
            session_service: Session management service
            redis_url: Optional Redis URL for persistence
        """
        self.memory_store = EnhancedMemoryStore(
            vector_store_service=vector_store_service,
            fact_extractor=fact_extractor,
            redis_url=redis_url
        )
        self.session_service = session_service
        
    def process_conversation_turn(
        self,
        session_id: str,
        user_message: str,
        assistant_response: str,
        project_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Process a complete conversation turn.
        Automatically determines if fact extraction should occur.
        """
        # Update session activity if session service is available
        if self.session_service:
            self.session_service.update_session_activity(session_id)
        
        # Add to memory store (will automatically determine if facts should be extracted)
        self.memory_store.add_conversation_turn(
            session_id=session_id,
            user_message=user_message,
            assistant_response=assistant_response,
            project_id=project_id,
            metadata=metadata or {}
        )
    
    def extract_facts_explicitly(
        self,
        session_id: str,
        message: str,
        project_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Explicitly extract facts from a message, bypassing normal query filtering.
        Use this when you know the message contains structured facts.
        
        Args:
            session_id: Session identifier
            message: Message to extract facts from
            project_id: Optional project identifier
            metadata: Additional metadata
            
        Returns:
            List of extracted facts
        """
        metadata = metadata or {}
        metadata['force_fact_extraction'] = True
        
        # Call the extraction method directly
        self.memory_store._extract_and_store_facts(
            session_id=session_id,
            message=message,
            project_id=project_id,
            metadata=metadata
        )
        
        # Return the extracted facts
        return self.memory_store.fact_memory.get(session_id, [])
    
    def get_context_for_query(
        self,
        session_id: str,
        query: str,
        max_context: int = 10
    ) -> List[Dict[str, Any]]:
        """Get relevant context for a query."""
        return self.memory_store.get_relevant_context(
            session_id=session_id,
            query=query,
            max_entries=max_context
        )
    
    def clear_session(self, session_id: str) -> None:
        """Clear all memory for a session."""
        self.memory_store.clear_session_memory(session_id)
    
    def get_stats(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get memory statistics."""
        return self.memory_store.get_memory_stats(session_id)
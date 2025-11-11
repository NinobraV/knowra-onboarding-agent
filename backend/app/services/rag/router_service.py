"""
router_service.py

Intelligent routing service that combines:
- Heuristic routing (keyword co-reference detection)
- Semantic similarity scoring
- Context-aware decision making

Routing decisions determine whether to:
- Use knowledge base only
- Use conversation memory only  
- Use both KB + memory
- Apply special handling
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple, Callable
from enum import Enum
from dataclasses import dataclass

# Optional semantic similarity
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger("router_service")


class RouteDecision(Enum):
    """Routing decision types."""
    KNOWLEDGE_BASE_ONLY = "kb_only"
    MEMORY_ONLY = "memory_only" 
    KNOWLEDGE_AND_MEMORY = "kb_and_memory"
    SENSITIVE_HANDLING = "sensitive"
    DEFAULT = "default"


@dataclass
class RoutingContext:
    """Context information for routing decisions."""
    query: str
    session_id: str
    project_id: Optional[str] = None
    conversation_length: int = 0
    has_recent_context: bool = False
    detected_entities: List[str] = None
    confidence_score: float = 0.0
    reasoning: str = ""


@dataclass
class RoutingResult:
    """Result of routing decision."""
    decision: RouteDecision
    confidence: float
    reasoning: str
    context: RoutingContext
    metadata: Dict[str, Any] = None


class RouterService:
    """
    Intelligent routing service with heuristic and semantic analysis.
    """
    
    def __init__(
        self,
        retriever: Optional[Callable[[str, int], List[Any]]] = None,
        memory_getter: Optional[Callable[[str], List[Dict]]] = None
    ):
        """
        Initialize router service.
        
        Args:
            retriever: Function to retrieve documents from knowledge base
            memory_getter: Function to get conversation memory for session
        """
        self.retriever = retriever
        self.memory_getter = memory_getter
        
        # Heuristic patterns for different routing decisions
        self.kb_patterns = [
            r'\b(what is|explain|define|documentation|guide|how to|tutorial)\b',
            r'\b(architecture|system|design|specification|requirements)\b',
            r'\b(API|endpoint|reference|interface)\b',
            r'\b(onboarding|process|procedure|steps)\b',
        ]
        
        self.memory_patterns = [
            r'\b(we discussed|earlier|before|previously|you said|remember)\b',
            r'\b(continue|follow up|next step|then what)\b',
            r'\b(clarify|explain that|more about that)\b',
        ]
        
        self.sensitive_patterns = [
            r'\b(password|key|secret|token|credential)\b',
            r'\b(database|server|production|env|config)\b',
            r'\b(login|access|permission|auth)\b',
            r'\b(private|confidential|internal)\b',
        ]
        
        # Co-reference patterns
        self.coref_patterns = [
            r'\b(this|that|it|they|them|these|those)\b',
            r'\b(here|there)\b',
            r'\b(same|similar|like that)\b',
        ]
        
        # Initialize TF-IDF for semantic similarity (if available)
        self.tfidf_vectorizer = None
        if SKLEARN_AVAILABLE:
            try:
                self.tfidf_vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=(1, 2)
                )
            except Exception as e:
                logger.warning(f"Failed to initialize TF-IDF vectorizer: {e}")
    
    def route_query(
        self, 
        query: str, 
        session_id: str, 
        project_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> RoutingResult:
        """
        Route a query based on heuristic and semantic analysis.
        
        Args:
            query: User query to route
            session_id: Session identifier
            project_id: Optional project identifier
            context: Additional context information
            
        Returns:
            RoutingResult: Routing decision with reasoning
        """
        context = context or {}
        
        # Build routing context
        routing_context = RoutingContext(
            query=query,
            session_id=session_id,
            project_id=project_id,
            conversation_length=context.get('conversation_length', 0),
            has_recent_context=context.get('has_recent_context', False),
            detected_entities=self._extract_entities(query)
        )
        
        # Step 1: Check for sensitive content first
        if self._is_sensitive_query(query):
            return RoutingResult(
                decision=RouteDecision.SENSITIVE_HANDLING,
                confidence=0.9,
                reasoning="Query contains sensitive patterns requiring special handling",
                context=routing_context,
                metadata={"sensitive_patterns": self._match_patterns(query, self.sensitive_patterns)}
            )
        
        # Step 2: Heuristic routing
        heuristic_score = self._heuristic_routing_score(query, routing_context)
        
        # Step 3: Semantic routing (if available)
        semantic_score = self._semantic_routing_score(query, routing_context)
        
        # Step 4: Combine scores and make decision
        final_decision, confidence, reasoning = self._make_routing_decision(
            query, routing_context, heuristic_score, semantic_score
        )
        
        routing_context.confidence_score = confidence
        routing_context.reasoning = reasoning
        
        return RoutingResult(
            decision=final_decision,
            confidence=confidence,
            reasoning=reasoning,
            context=routing_context,
            metadata={
                "heuristic_score": heuristic_score,
                "semantic_score": semantic_score
            }
        )
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract potential entities from text (simple pattern-based)."""
        entities = []
        
        # Extract potential file paths
        file_patterns = r'\b[\w\-\.]+\.(md|py|js|json|env|txt|log)\b'
        entities.extend(re.findall(file_patterns, text, re.IGNORECASE))
        
        # Extract potential URLs
        url_patterns = r'https?://[^\s]+'
        entities.extend(re.findall(url_patterns, text, re.IGNORECASE))
        
        # Extract potential API endpoints
        api_patterns = r'/api/[\w\-/]+'
        entities.extend(re.findall(api_patterns, text))
        
        return list(set(entities))
    
    def _is_sensitive_query(self, query: str) -> bool:
        """Check if query contains sensitive patterns."""
        return len(self._match_patterns(query, self.sensitive_patterns)) > 0
    
    def _match_patterns(self, text: str, patterns: List[str]) -> List[str]:
        """Match text against list of regex patterns."""
        matches = []
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matches.append(pattern)
        return matches
    
    def _heuristic_routing_score(self, query: str, context: RoutingContext) -> Dict[str, float]:
        """Calculate heuristic routing scores."""
        scores = {
            'kb_score': 0.0,
            'memory_score': 0.0,
            'combined_score': 0.0
        }
        
        # Knowledge base indicators
        kb_matches = self._match_patterns(query, self.kb_patterns)
        scores['kb_score'] = min(len(kb_matches) * 0.3, 1.0)
        
        # Memory/conversation indicators
        memory_matches = self._match_patterns(query, self.memory_patterns)
        scores['memory_score'] = min(len(memory_matches) * 0.4, 1.0)
        
        # Co-reference detection (suggests need for memory)
        coref_matches = self._match_patterns(query, self.coref_patterns)
        if coref_matches and context.has_recent_context:
            scores['memory_score'] += 0.3
        
        # Short queries with co-reference likely need memory
        if len(query.split()) <= 5 and coref_matches:
            scores['memory_score'] += 0.2
        
        # Questions about specific processes likely need both
        if any(word in query.lower() for word in ['how', 'what', 'explain']) and \
           any(word in query.lower() for word in ['process', 'workflow', 'procedure']):
            scores['combined_score'] = 0.7
        
        # Normalize scores
        for key in scores:
            scores[key] = min(scores[key], 1.0)
        
        return scores
    
    def _semantic_routing_score(self, query: str, context: RoutingContext) -> Dict[str, float]:
        """Calculate semantic similarity scores."""
        scores = {
            'kb_similarity': 0.0,
            'memory_similarity': 0.0
        }
        
        if not SKLEARN_AVAILABLE or not self.tfidf_vectorizer:
            return scores
        
        try:
            # Get recent memory for comparison
            if self.memory_getter and context.session_id:
                recent_memory = self.memory_getter(context.session_id)
                if recent_memory:
                    memory_text = " ".join([msg.get('content', '') for msg in recent_memory[-3:]])
                    
                    # Calculate similarity between query and recent memory
                    corpus = [query, memory_text]
                    tfidf_matrix = self.tfidf_vectorizer.fit_transform(corpus)
                    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                    scores['memory_similarity'] = float(similarity)
            
            # For KB similarity, we'd need to sample some KB content
            # This is a simplified version - in practice you might want to
            # compare against KB document summaries or topics
            
        except Exception as e:
            logger.debug(f"Semantic scoring failed: {e}")
        
        return scores
    
    def _make_routing_decision(
        self, 
        query: str, 
        context: RoutingContext, 
        heuristic_score: Dict[str, float], 
        semantic_score: Dict[str, float]
    ) -> Tuple[RouteDecision, float, str]:
        """Make final routing decision based on all scores."""
        
        # Weight the scores
        kb_score = (heuristic_score['kb_score'] * 0.7) + (semantic_score['kb_similarity'] * 0.3)
        memory_score = (heuristic_score['memory_score'] * 0.6) + (semantic_score['memory_similarity'] * 0.4)
        combined_score = heuristic_score['combined_score']
        
        # Decision thresholds
        KB_THRESHOLD = 0.6
        MEMORY_THRESHOLD = 0.5
        COMBINED_THRESHOLD = 0.4
        
        # Make decision
        if combined_score > COMBINED_THRESHOLD:
            return (
                RouteDecision.KNOWLEDGE_AND_MEMORY,
                combined_score,
                f"Query benefits from both KB and memory (combined_score: {combined_score:.2f})"
            )
        elif kb_score > KB_THRESHOLD and memory_score < MEMORY_THRESHOLD:
            return (
                RouteDecision.KNOWLEDGE_BASE_ONLY,
                kb_score,
                f"Query is KB-focused (kb_score: {kb_score:.2f})"
            )
        elif memory_score > MEMORY_THRESHOLD and kb_score < KB_THRESHOLD:
            return (
                RouteDecision.MEMORY_ONLY,
                memory_score,
                f"Query requires conversation context (memory_score: {memory_score:.2f})"
            )
        elif kb_score > 0.3 or memory_score > 0.3:
            return (
                RouteDecision.KNOWLEDGE_AND_MEMORY,
                max(kb_score, memory_score),
                f"Moderate confidence, using both sources (kb: {kb_score:.2f}, memory: {memory_score:.2f})"
            )
        else:
            return (
                RouteDecision.DEFAULT,
                0.5,
                "No strong routing signals detected, using default behavior"
            )
    
    def get_routing_stats(self, session_id: str, limit: int = 50) -> Dict[str, Any]:
        """Get routing statistics for debugging and optimization."""
        # This would track routing decisions over time
        # For now, return a placeholder
        return {
            "session_id": session_id,
            "total_queries": 0,
            "routing_distribution": {
                "kb_only": 0,
                "memory_only": 0, 
                "kb_and_memory": 0,
                "sensitive": 0,
                "default": 0
            },
            "average_confidence": 0.0
        }
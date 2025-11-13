"""
router_service.py

Intelligent routing service that combines:
- Enhanced heuristic routing (keyword and pattern matching)
- Semantic similarity scoring with embeddings
- Context-aware decision making with confidence thresholds
- Multi-intent query detection and routing

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
from dataclasses import dataclass, field

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
    metadata: Dict[str, Any] = field(default_factory=dict)
    sub_queries: List[str] = field(default_factory=list)  # For multi-intent queries


class RouterService:
    """
    Enhanced intelligent routing service with:
    - Improved heuristic pattern matching
    - Semantic similarity using embeddings
    - Confidence-based fallback routing
    - Multi-intent query detection and handling
    """
    
    # Confidence thresholds for routing decisions
    HIGH_CONFIDENCE_THRESHOLD = 0.75
    MEDIUM_CONFIDENCE_THRESHOLD = 0.50
    LOW_CONFIDENCE_THRESHOLD = 0.30
    
    def __init__(
        self,
        retriever: Optional[Callable[[str, int], List[Any]]] = None,
        memory_getter: Optional[Callable[[str], List[Dict]]] = None,
        confidence_threshold: float = 0.50,
        enable_multi_intent: bool = True
    ):
        """
        Initialize router service.
        
        Args:
            retriever: Function to retrieve documents from knowledge base
            memory_getter: Function to get conversation memory for session
            confidence_threshold: Minimum confidence for routing decisions (default: 0.50)
            enable_multi_intent: Enable multi-intent query detection (default: True)
        """
        self.retriever = retriever
        self.memory_getter = memory_getter
        self.confidence_threshold = confidence_threshold
        self.enable_multi_intent = enable_multi_intent
        
        # Enhanced heuristic patterns for different routing decisions
        self.kb_patterns = [
            # Documentation queries
            r'\b(what is|explain|define|documentation|docs|guide|manual)\b',
            r'\b(how to|how do I|how can I|tutorial|example)\b',
            r'\b(where can I find|show me|give me)\b',
            
            # Technical queries
            r'\b(architecture|system|design|specification|requirements|SRS)\b',
            r'\b(API|endpoint|reference|interface|REST|HTTP)\b',
            r'\b(function|class|method|module|component)\b',
            
            # Process queries
            r'\b(onboarding|deployment|setup|installation|configuration)\b',
            r'\b(process|procedure|workflow|steps|guideline)\b',
            r'\b(best practice|standard|convention|policy)\b',
            
            # Security & compliance
            r'\b(security|authentication|authorization|compliance|GDPR)\b',
            r'\b(test|testing|QA|quality assurance|validation)\b',
        ]
        
        self.memory_patterns = [
            # Co-reference patterns
            r'\b(we discussed|earlier|before|previously|last time)\b',
            r'\b(you said|you mentioned|you told me|you explained)\b',
            r'\b(remember|recall|as I mentioned|as we talked)\b',
            
            # Continuation patterns
            r'\b(continue|follow up|next step|then what|what next)\b',
            r'\b(more about|tell me more|elaborate|expand on)\b',
            r'\b(clarify|explain that|what did you mean)\b',
            
            # Context-dependent pronouns
            r'\b(this|that|it|they|them|these|those|the same)\b',
            r'\b(here|there|above|below)\b',
        ]
        
        self.sensitive_patterns = [
            # Credentials and secrets
            r'\b(password|passwd|pwd|secret|key|token|credential)\b',
            r'\b(API[_\s]?key|access[_\s]?key|private[_\s]?key)\b',
            
            # Infrastructure
            r'\b(database|db|server|host|production|prod|staging)\b',
            r'\b(environment|env|config|configuration|.env)\b',
            
            # Access control
            r'\b(login|sign[_\s]?in|access|permission|auth|authorization)\b',
            r'\b(admin|administrator|root|sudo)\b',
            
            # Confidential
            r'\b(private|confidential|internal|proprietary|classified)\b',
            r'\b(NDA|non[_\s]?disclosure|trade[_\s]?secret)\b',
        ]
        
        # Multi-intent query separators
        self.query_separators = [
            r'\s+and\s+',
            r'\s+also\s+',
            r'\s+plus\s+',
            r'[;,]\s+',
            r'\s+then\s+',
        ]
        
        # Initialize TF-IDF for semantic similarity (if available)
        self.tfidf_vectorizer = None
        if SKLEARN_AVAILABLE:
            try:
                self.tfidf_vectorizer = TfidfVectorizer(
                    max_features=1000,
                    stop_words='english',
                    ngram_range=(1, 2),
                    min_df=1
                )
                logger.info("TF-IDF vectorizer initialized for semantic routing")
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
        Route a query based on enhanced heuristic and semantic analysis.
        Supports multi-intent query detection and confidence-based fallback.
        
        Args:
            query: User query to route
            session_id: Session identifier
            project_id: Optional project identifier
            context: Additional context information
            
        Returns:
            RoutingResult: Routing decision with reasoning and sub-queries
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
        
        # Step 1: Check for multi-intent queries
        sub_queries = []
        if self.enable_multi_intent:
            sub_queries = self._detect_multi_intent(query)
            if len(sub_queries) > 1:
                logger.info(f"Multi-intent query detected: {len(sub_queries)} sub-queries")
        
        # Step 2: Check for sensitive content first (high priority)
        if self._is_sensitive_query(query):
            return RoutingResult(
                decision=RouteDecision.SENSITIVE_HANDLING,
                confidence=0.95,
                reasoning="Query contains sensitive patterns requiring special handling",
                context=routing_context,
                metadata={"sensitive_patterns": self._match_patterns(query, self.sensitive_patterns)},
                sub_queries=sub_queries
            )
        
        # Step 3: Heuristic routing with enhanced patterns
        heuristic_score = self._heuristic_routing_score(query, routing_context)
        
        # Step 4: Semantic routing with embeddings (if available)
        semantic_score = self._semantic_routing_score(query, routing_context)
        
        # Step 5: Combine scores and make decision with confidence threshold
        final_decision, confidence, reasoning = self._make_routing_decision(
            query, routing_context, heuristic_score, semantic_score
        )
        
        # Step 6: Apply confidence-based fallback
        if confidence < self.confidence_threshold:
            logger.debug(f"Confidence {confidence:.2f} below threshold {self.confidence_threshold:.2f}, using fallback")
            final_decision = RouteDecision.KNOWLEDGE_AND_MEMORY
            reasoning = f"Low confidence ({confidence:.2f}), using combined approach for safety"
            confidence = self.confidence_threshold
        
        routing_context.confidence_score = confidence
        routing_context.reasoning = reasoning
        
        return RoutingResult(
            decision=final_decision,
            confidence=confidence,
            reasoning=reasoning,
            context=routing_context,
            metadata={
                "heuristic_score": heuristic_score,
                "semantic_score": semantic_score,
                "confidence_threshold": self.confidence_threshold,
                "multi_intent_enabled": self.enable_multi_intent
            },
            sub_queries=sub_queries
        )
    
    def _detect_multi_intent(self, query: str) -> List[str]:
        """
        Detect if query contains multiple intents and split into sub-queries.
        
        Args:
            query: User query
            
        Returns:
            List of sub-queries (single item if no multi-intent detected)
        """
        # If query is very short, it's unlikely to be multi-intent
        if len(query.split()) < 5:
            return [query]
        
        # Try to split by common separators
        for separator_pattern in self.query_separators:
            parts = re.split(separator_pattern, query, flags=re.IGNORECASE)
            if len(parts) > 1:
                # Filter out very short fragments
                sub_queries = [p.strip() for p in parts if len(p.strip().split()) >= 3]
                if len(sub_queries) > 1:
                    logger.debug(f"Split query into {len(sub_queries)} sub-queries using pattern: {separator_pattern}")
                    return sub_queries
        
        # Check for question chains (e.g., "What is X? How does it work?")
        question_pattern = r'[.!?]\s+'
        parts = re.split(question_pattern, query)
        if len(parts) > 1:
            sub_queries = [p.strip() for p in parts if len(p.strip().split()) >= 3]
            if len(sub_queries) > 1:
                logger.debug(f"Split query into {len(sub_queries)} question-based sub-queries")
                return sub_queries
        
        # No multi-intent detected
        return [query]
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract potential entities from text (enhanced pattern-based)."""
        entities = []
        
        # Extract file paths and names
        file_patterns = r'\b[\w\-\.]+\.(md|py|js|jsx|ts|tsx|json|env|txt|log|yml|yaml|xml|html|css|sh|bat)\b'
        entities.extend(re.findall(file_patterns, text, re.IGNORECASE))
        
        # Extract URLs
        url_patterns = r'https?://[^\s<>"\']+'
        entities.extend(re.findall(url_patterns, text, re.IGNORECASE))
        
        # Extract API endpoints
        api_patterns = r'/api/[\w\-/]+'
        entities.extend(re.findall(api_patterns, text))
        
        # Extract package/module names (e.g., react, fastapi, numpy)
        package_patterns = r'\b(?:npm|pip|yarn)\s+(?:install\s+)?(\w+(?:[_\-]\w+)*)\b'
        entities.extend(re.findall(package_patterns, text, re.IGNORECASE))
        
        # Extract technical terms (camelCase, PascalCase, snake_case)
        tech_patterns = r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b|\b\w+_\w+\b'
        entities.extend(re.findall(tech_patterns, text))
        
        # Extract version numbers
        version_patterns = r'\bv?\d+\.\d+(?:\.\d+)?(?:\-[a-z0-9]+)?\b'
        entities.extend(re.findall(version_patterns, text, re.IGNORECASE))
        
        return list(set(entities))  # Remove duplicates
    
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
        """Calculate enhanced heuristic routing scores."""
        scores = {
            'kb_score': 0.0,
            'memory_score': 0.0,
            'combined_score': 0.0
        }
        
        query_lower = query.lower()
        query_words = query.split()
        
        # Knowledge base indicators (stronger weighting)
        kb_matches = self._match_patterns(query, self.kb_patterns)
        scores['kb_score'] = min(len(kb_matches) * 0.25, 1.0)
        
        # Boost KB score for technical entities
        if context.detected_entities:
            scores['kb_score'] += min(len(context.detected_entities) * 0.15, 0.4)
        
        # Boost KB score for question words
        question_words = ['what', 'how', 'why', 'where', 'when', 'which', 'who']
        if any(word in query_lower for word in question_words):
            scores['kb_score'] += 0.2
        
        # Memory/conversation indicators
        memory_matches = self._match_patterns(query, self.memory_patterns)
        scores['memory_score'] = min(len(memory_matches) * 0.35, 1.0)
        
        # Strong boost for co-reference with recent context
        coref_pattern = r'\b(this|that|it|they|them|these|those|the same)\b'
        if re.search(coref_pattern, query_lower) and context.has_recent_context:
            scores['memory_score'] += 0.4
        
        # Short queries with co-reference strongly suggest memory need
        if len(query_words) <= 6 and scores['memory_score'] > 0:
            scores['memory_score'] = min(scores['memory_score'] + 0.3, 1.0)
        
        # Continuation phrases strongly indicate memory need
        continuation_phrases = ['tell me more', 'elaborate', 'continue', 'go on', 'what else']
        if any(phrase in query_lower for phrase in continuation_phrases):
            scores['memory_score'] = min(scores['memory_score'] + 0.35, 1.0)
        
        # Combined approach indicators
        # Complex questions about specific topics benefit from both sources
        if scores['kb_score'] > 0.3 and scores['memory_score'] > 0.2:
            scores['combined_score'] = 0.7
        
        # Long, detailed questions often need both context and knowledge
        if len(query_words) > 15:
            scores['combined_score'] = max(scores['combined_score'], 0.5)
        
        # Process/workflow questions benefit from both
        process_keywords = ['process', 'workflow', 'procedure', 'step', 'how do i', 'guide me']
        if any(keyword in query_lower for keyword in process_keywords):
            scores['combined_score'] = max(scores['combined_score'], 0.6)
        
        # Normalize all scores
        for key in scores:
            scores[key] = min(scores[key], 1.0)
        
        logger.debug(f"Heuristic scores - KB: {scores['kb_score']:.2f}, Memory: {scores['memory_score']:.2f}, Combined: {scores['combined_score']:.2f}")
        
        return scores
    
    def _semantic_routing_score(self, query: str, context: RoutingContext) -> Dict[str, float]:
        """Calculate semantic similarity scores using embeddings."""
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
                
                if recent_memory and len(recent_memory) > 0:
                    # Extract content from recent messages
                    memory_texts = [msg.get('content', '') for msg in recent_memory[-5:]]
                    memory_text = " ".join([t for t in memory_texts if t])
                    
                    if memory_text:
                        # Calculate similarity between query and recent memory
                        corpus = [query, memory_text]
                        try:
                            tfidf_matrix = self.tfidf_vectorizer.fit_transform(corpus)
                            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                            scores['memory_similarity'] = float(similarity)
                            logger.debug(f"Memory similarity: {similarity:.2f}")
                        except Exception as e:
                            logger.debug(f"TF-IDF similarity calculation failed: {e}")
            
            # For KB similarity, sample some documents if retriever is available
            if self.retriever:
                try:
                    kb_docs = self.retriever(query, 3)
                    if kb_docs:
                        kb_texts = [getattr(doc, 'page_content', str(doc)) for doc in kb_docs]
                        kb_text = " ".join(kb_texts[:100])  # Limit to prevent memory issues
                        
                        if kb_text:
                            corpus = [query, kb_text]
                            try:
                                tfidf_matrix = self.tfidf_vectorizer.fit_transform(corpus)
                                similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                                scores['kb_similarity'] = float(similarity)
                                logger.debug(f"KB similarity: {similarity:.2f}")
                            except Exception as e:
                                logger.debug(f"KB similarity calculation failed: {e}")
                except Exception as e:
                    logger.debug(f"KB retrieval for similarity failed: {e}")
            
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
        """
        Make final routing decision based on all scores with confidence thresholds.
        Uses weighted combination of heuristic and semantic signals.
        """
        
        # Weight the scores (heuristic weighted higher as it's more reliable)
        kb_score = (heuristic_score['kb_score'] * 0.7) + (semantic_score.get('kb_similarity', 0) * 0.3)
        memory_score = (heuristic_score['memory_score'] * 0.65) + (semantic_score.get('memory_similarity', 0) * 0.35)
        combined_score = heuristic_score['combined_score']
        
        # Boost combined score if both individual scores are moderate
        if kb_score > 0.35 and memory_score > 0.35:
            combined_score = max(combined_score, (kb_score + memory_score) / 2)
        
        logger.debug(f"Weighted scores - KB: {kb_score:.2f}, Memory: {memory_score:.2f}, Combined: {combined_score:.2f}")
        
        # Decision thresholds (configurable)
        KB_HIGH_THRESHOLD = self.HIGH_CONFIDENCE_THRESHOLD  # 0.75
        KB_MEDIUM_THRESHOLD = self.MEDIUM_CONFIDENCE_THRESHOLD  # 0.50
        MEMORY_HIGH_THRESHOLD = self.HIGH_CONFIDENCE_THRESHOLD
        MEMORY_MEDIUM_THRESHOLD = self.MEDIUM_CONFIDENCE_THRESHOLD
        COMBINED_THRESHOLD = self.LOW_CONFIDENCE_THRESHOLD  # 0.30
        
        # Make decision based on thresholds
        decisions = []
        
        # High confidence KB route
        if kb_score >= KB_HIGH_THRESHOLD and memory_score < MEMORY_MEDIUM_THRESHOLD:
            decisions.append((
                RouteDecision.KNOWLEDGE_BASE_ONLY,
                kb_score,
                f"High confidence KB query (score: {kb_score:.2f})"
            ))
        
        # High confidence memory route
        if memory_score >= MEMORY_HIGH_THRESHOLD and kb_score < KB_MEDIUM_THRESHOLD:
            decisions.append((
                RouteDecision.MEMORY_ONLY,
                memory_score,
                f"High confidence memory query (score: {memory_score:.2f})"
            ))
        
        # Strong combined signal
        if combined_score >= COMBINED_THRESHOLD:
            decisions.append((
                RouteDecision.KNOWLEDGE_AND_MEMORY,
                combined_score,
                f"Combined approach beneficial (score: {combined_score:.2f})"
            ))
        
        # Medium confidence KB with some memory
        if kb_score >= KB_MEDIUM_THRESHOLD and memory_score >= COMBINED_THRESHOLD:
            decisions.append((
                RouteDecision.KNOWLEDGE_AND_MEMORY,
                (kb_score + memory_score) / 2,
                f"Both sources relevant (KB: {kb_score:.2f}, Memory: {memory_score:.2f})"
            ))
        
        # Medium confidence KB only
        if kb_score >= KB_MEDIUM_THRESHOLD and memory_score < COMBINED_THRESHOLD:
            decisions.append((
                RouteDecision.KNOWLEDGE_BASE_ONLY,
                kb_score,
                f"KB-focused query (score: {kb_score:.2f})"
            ))
        
        # Medium confidence memory only
        if memory_score >= MEMORY_MEDIUM_THRESHOLD and kb_score < COMBINED_THRESHOLD:
            decisions.append((
                RouteDecision.MEMORY_ONLY,
                memory_score,
                f"Context-dependent query (score: {memory_score:.2f})"
            ))
        
        # Select the decision with highest confidence
        if decisions:
            # Sort by confidence and take the highest
            decisions.sort(key=lambda x: x[1], reverse=True)
            return decisions[0]
        
        # Fallback: use combined approach with low confidence
        fallback_confidence = max(kb_score, memory_score, 0.4)
        return (
            RouteDecision.DEFAULT,
            fallback_confidence,
            f"No strong routing signals, using default behavior (KB: {kb_score:.2f}, Memory: {memory_score:.2f})"
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
"""
memory_cleanup_service.py

Periodic memory cleanup and maintenance service.
Provides garbage collection, deduplication, and value-based filtering.
"""

import logging
import time
from typing import Dict, List, Optional, Any, Callable, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import asyncio
import threading

logger = logging.getLogger("memory_cleanup_service")


class CleanupAction(Enum):
    """Types of cleanup actions."""
    DELETE = "delete"
    ARCHIVE = "archive"
    COMPRESS = "compress"
    MERGE = "merge"
    KEEP = "keep"


class CleanupReason(Enum):
    """Reasons for cleanup actions."""
    EXPIRED = "expired"
    LOW_VALUE = "low_value"
    DUPLICATE = "duplicate"
    OVER_QUOTA = "over_quota"
    CORRUPTED = "corrupted"
    MERGED = "merged"


@dataclass
class CleanupRule:
    """Rule for memory cleanup."""
    name: str
    condition: Callable[[Any], bool]
    action: CleanupAction
    reason: CleanupReason
    priority: int  # Lower number = higher priority
    description: str


@dataclass
class CleanupResult:
    """Result of cleanup operation."""
    total_items_processed: int
    items_deleted: int
    items_archived: int
    items_compressed: int
    items_merged: int
    bytes_freed: int
    execution_time: float
    errors: List[str]
    details: Dict[str, Any]


class ValueBasedFilter:
    """
    Filter for determining memory value based on various criteria.
    """
    
    def __init__(self):
        """Initialize value-based filter."""
        # Value tags that indicate important content
        self.value_tags = {
            'deadline': 10,
            'credential': 9,
            'url': 8,
            'configuration': 7,
            'api_endpoint': 7,
            'file_reference': 6,
            'error_solution': 8,
            'process_step': 6,
            'system_component': 5,
            'business_rule': 6
        }
        
        # Keywords that boost value
        self.high_value_keywords = {
            'important': 3,
            'critical': 5,
            'urgent': 4,
            'must': 3,
            'required': 3,
            'production': 4,
            'security': 4,
            'password': 5,
            'secret': 5,
            'key': 4
        }
        
        # Keywords that reduce value
        self.low_value_keywords = {
            'test': -2,
            'example': -2,
            'demo': -2,
            'hello': -3,
            'thanks': -2,
            'ok': -3,
            'yes': -2,
            'no': -2
        }
        
        # Minimum content length for retention
        self.min_content_length = 10
        
    def calculate_value_score(self, item: Dict[str, Any]) -> float:
        """
        Calculate value score for a memory item.
        
        Args:
            item: Memory item to score
            
        Returns:
            float: Value score (higher = more valuable)
        """
        score = 0.0
        content = str(item.get('content', '')).lower()
        
        # Base score from content length
        content_length = len(content)
        if content_length < self.min_content_length:
            score -= 5
        else:
            score += min(content_length / 100, 3)  # Cap at 3 points
        
        # Check for value tags
        tags = item.get('tags', [])
        for tag in tags:
            if tag.lower() in self.value_tags:
                score += self.value_tags[tag.lower()]
        
        # Check content for high-value keywords
        for keyword, value in self.high_value_keywords.items():
            if keyword in content:
                score += value
        
        # Check content for low-value keywords
        for keyword, value in self.low_value_keywords.items():
            if keyword in content:
                score += value  # These are negative values
        
        # Boost score based on metadata
        metadata = item.get('metadata', {})
        
        # Fact type boost
        fact_type = metadata.get('fact_type')
        if fact_type in ['credential_location', 'deadline', 'api_endpoint']:
            score += 5
        elif fact_type in ['error_solution', 'configuration']:
            score += 3
        
        # Importance boost
        importance = metadata.get('importance', '').lower()
        if importance == 'critical':
            score += 8
        elif importance == 'high':
            score += 5
        elif importance == 'medium':
            score += 2
        elif importance == 'low':
            score -= 1
        elif importance == 'temporary':
            score -= 3
        
        # Recency factor
        created_at = metadata.get('created_at')
        if created_at:
            try:
                created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                age_days = (datetime.utcnow() - created_date).days
                
                if age_days < 1:
                    score += 2  # Recent boost
                elif age_days < 7:
                    score += 1
                elif age_days > 30:
                    score -= 2  # Age penalty
                elif age_days > 90:
                    score -= 5
                    
            except Exception:
                pass
        
        # Access frequency boost
        access_count = metadata.get('access_count', 0)
        if access_count > 5:
            score += min(access_count / 5, 3)
        
        return score
    
    def should_retain(self, item: Dict[str, Any], threshold: float = 2.0) -> bool:
        """
        Determine if item should be retained based on value.
        
        Args:
            item: Memory item to evaluate
            threshold: Minimum value score for retention
            
        Returns:
            bool: True if item should be retained
        """
        score = self.calculate_value_score(item)
        return score >= threshold


class DuplicationDetector:
    """
    Detector for duplicate or similar memory items.
    """
    
    def __init__(self, similarity_threshold: float = 0.8):
        """
        Initialize duplication detector.
        
        Args:
            similarity_threshold: Threshold for considering items duplicates
        """
        self.similarity_threshold = similarity_threshold
    
    def find_duplicates(self, items: List[Dict[str, Any]]) -> List[List[int]]:
        """
        Find groups of duplicate items.
        
        Args:
            items: List of memory items
            
        Returns:
            List of lists, each containing indices of duplicate items
        """
        duplicate_groups = []
        processed = set()
        
        for i, item1 in enumerate(items):
            if i in processed:
                continue
                
            group = [i]
            processed.add(i)
            
            for j, item2 in enumerate(items[i+1:], i+1):
                if j in processed:
                    continue
                    
                if self._are_similar(item1, item2):
                    group.append(j)
                    processed.add(j)
            
            if len(group) > 1:
                duplicate_groups.append(group)
        
        return duplicate_groups
    
    def _are_similar(self, item1: Dict[str, Any], item2: Dict[str, Any]) -> bool:
        """Check if two items are similar enough to be duplicates."""
        content1 = str(item1.get('content', '')).lower().strip()
        content2 = str(item2.get('content', '')).lower().strip()
        
        # Exact match
        if content1 == content2:
            return True
        
        # Similar content (simple Jaccard similarity)
        if len(content1) < 10 or len(content2) < 10:
            return False
        
        words1 = set(content1.split())
        words2 = set(content2.split())
        
        if not words1 or not words2:
            return False
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        similarity = intersection / union if union > 0 else 0
        return similarity >= self.similarity_threshold
    
    def select_best_from_group(self, items: List[Dict[str, Any]], group_indices: List[int], value_filter: ValueBasedFilter) -> int:
        """
        Select the best item from a group of duplicates.
        
        Args:
            items: All items
            group_indices: Indices of duplicate items
            value_filter: Value filter for scoring
            
        Returns:
            Index of the best item to keep
        """
        best_index = group_indices[0]
        best_score = value_filter.calculate_value_score(items[best_index])
        
        for index in group_indices[1:]:
            score = value_filter.calculate_value_score(items[index])
            if score > best_score:
                best_score = score
                best_index = index
        
        return best_index


class MemoryCleanupService:
    """
    Service for periodic memory cleanup and maintenance.
    """
    
    def __init__(
        self,
        enhanced_memory_service: Any,
        session_service: Optional[Any] = None,
        cleanup_interval: timedelta = timedelta(hours=6),
        max_memory_per_session: int = 1000,
        value_threshold: float = 2.0
    ):
        """
        Initialize memory cleanup service.
        
        Args:
            enhanced_memory_service: Enhanced memory service to clean
            session_service: Optional session service
            cleanup_interval: How often to run cleanup
            max_memory_per_session: Maximum memory items per session
            value_threshold: Minimum value score for retention
        """
        self.enhanced_memory_service = enhanced_memory_service
        self.session_service = session_service
        self.cleanup_interval = cleanup_interval
        self.max_memory_per_session = max_memory_per_session
        self.value_threshold = value_threshold
        
        # Components
        self.value_filter = ValueBasedFilter()
        self.duplication_detector = DuplicationDetector()
        
        # Cleanup rules
        self.cleanup_rules = self._create_default_cleanup_rules()
        
        # State
        self._last_cleanup = datetime.utcnow()
        self._cleanup_running = False
        self._cleanup_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
    
    def _create_default_cleanup_rules(self) -> List[CleanupRule]:
        """Create default cleanup rules."""
        rules = [
            # Rule 1: Delete expired items
            CleanupRule(
                name="delete_expired",
                condition=lambda item: self._is_expired(item),
                action=CleanupAction.DELETE,
                reason=CleanupReason.EXPIRED,
                priority=1,
                description="Delete items past their expiration date"
            ),
            
            # Rule 2: Delete very low value items
            CleanupRule(
                name="delete_low_value",
                condition=lambda item: self.value_filter.calculate_value_score(item) < -2,
                action=CleanupAction.DELETE,
                reason=CleanupReason.LOW_VALUE,
                priority=2,
                description="Delete items with very low value scores"
            ),
            
            # Rule 3: Archive old low-medium value items
            CleanupRule(
                name="archive_old_low_value",
                condition=lambda item: (
                    self._is_old(item, days=30) and 
                    self.value_filter.calculate_value_score(item) < 3
                ),
                action=CleanupAction.ARCHIVE,
                reason=CleanupReason.LOW_VALUE,
                priority=3,
                description="Archive old items with low-medium value"
            ),
            
            # Rule 4: Compress old items
            CleanupRule(
                name="compress_old",
                condition=lambda item: self._is_old(item, days=60),
                action=CleanupAction.COMPRESS,
                reason=CleanupReason.EXPIRED,
                priority=4,
                description="Compress very old items"
            ),
        ]
        
        return rules
    
    def start_background_cleanup(self) -> None:
        """Start background cleanup process."""
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            logger.warning("Cleanup thread already running")
            return
        
        self._stop_event.clear()
        self._cleanup_thread = threading.Thread(target=self._background_cleanup_loop)
        self._cleanup_thread.daemon = True
        self._cleanup_thread.start()
        logger.info("Started background memory cleanup service")
    
    def stop_background_cleanup(self) -> None:
        """Stop background cleanup process."""
        self._stop_event.set()
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=30)
        logger.info("Stopped background memory cleanup service")
    
    def _background_cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while not self._stop_event.is_set():
            try:
                if datetime.utcnow() - self._last_cleanup >= self.cleanup_interval:
                    logger.info("Starting scheduled memory cleanup")
                    result = self.cleanup_all_sessions()
                    logger.info(f"Cleanup completed: {result.items_deleted} deleted, {result.items_archived} archived")
                
                # Sleep for 5 minutes between checks
                self._stop_event.wait(300)
                
            except Exception as e:
                logger.error(f"Background cleanup error: {e}")
                self._stop_event.wait(600)  # Wait 10 minutes on error
    
    def cleanup_all_sessions(self) -> CleanupResult:
        """
        Clean up memory for all sessions.
        
        Returns:
            CleanupResult: Summary of cleanup operations
        """
        if self._cleanup_running:
            logger.warning("Cleanup already in progress")
            return CleanupResult(
                total_items_processed=0,
                items_deleted=0,
                items_archived=0,
                items_compressed=0,
                items_merged=0,
                bytes_freed=0,
                execution_time=0,
                errors=["Cleanup already in progress"],
                details={}
            )
        
        self._cleanup_running = True
        start_time = time.time()
        
        try:
            # Get all sessions from memory store
            memory_store = self.enhanced_memory_service.memory_store
            all_sessions = set()
            
            # Collect session IDs
            all_sessions.update(memory_store.short_term_memory.keys())
            all_sessions.update(memory_store.long_term_memory.keys())
            all_sessions.update(memory_store.fact_memory.keys())
            
            total_result = CleanupResult(
                total_items_processed=0,
                items_deleted=0,
                items_archived=0,
                items_compressed=0,
                items_merged=0,
                bytes_freed=0,
                execution_time=0,
                errors=[],
                details={}
            )
            
            # Clean each session
            for session_id in all_sessions:
                try:
                    result = self.cleanup_session(session_id)
                    
                    # Aggregate results
                    total_result.total_items_processed += result.total_items_processed
                    total_result.items_deleted += result.items_deleted
                    total_result.items_archived += result.items_archived
                    total_result.items_compressed += result.items_compressed
                    total_result.items_merged += result.items_merged
                    total_result.bytes_freed += result.bytes_freed
                    total_result.errors.extend(result.errors)
                    
                except Exception as e:
                    error_msg = f"Failed to clean session {session_id}: {e}"
                    total_result.errors.append(error_msg)
                    logger.error(error_msg)
            
            # Update cleanup timestamp
            self._last_cleanup = datetime.utcnow()
            total_result.execution_time = time.time() - start_time
            
            return total_result
            
        finally:
            self._cleanup_running = False
    
    def cleanup_session(self, session_id: str) -> CleanupResult:
        """
        Clean up memory for a specific session.
        
        Args:
            session_id: Session to clean up
            
        Returns:
            CleanupResult: Summary of cleanup operations
        """
        start_time = time.time()
        result = CleanupResult(
            total_items_processed=0,
            items_deleted=0,
            items_archived=0,
            items_compressed=0,
            items_merged=0,
            bytes_freed=0,
            execution_time=0,
            errors=[],
            details={'session_id': session_id}
        )
        
        try:
            memory_store = self.enhanced_memory_service.memory_store
            
            # Clean short-term memory
            if session_id in memory_store.short_term_memory:
                st_result = self._cleanup_memory_list(
                    memory_store.short_term_memory[session_id],
                    f"short_term_{session_id}"
                )
                result = self._merge_results(result, st_result)
            
            # Clean long-term memory
            if session_id in memory_store.long_term_memory:
                lt_result = self._cleanup_memory_list(
                    memory_store.long_term_memory[session_id],
                    f"long_term_{session_id}"
                )
                result = self._merge_results(result, lt_result)
            
            # Clean fact memory
            if session_id in memory_store.fact_memory:
                fact_result = self._cleanup_fact_list(
                    memory_store.fact_memory[session_id],
                    f"facts_{session_id}"
                )
                result = self._merge_results(result, fact_result)
            
            # Check if session has exceeded quota
            self._enforce_session_quota(session_id)
            
            result.execution_time = time.time() - start_time
            
        except Exception as e:
            result.errors.append(f"Session cleanup failed: {e}")
            logger.error(f"Session {session_id} cleanup failed: {e}")
        
        return result
    
    def _cleanup_memory_list(self, memory_list: List[Any], context: str) -> CleanupResult:
        """Clean up a list of memory entries."""
        result = CleanupResult(
            total_items_processed=len(memory_list),
            items_deleted=0,
            items_archived=0,
            items_compressed=0,
            items_merged=0,
            bytes_freed=0,
            execution_time=0,
            errors=[],
            details={'context': context}
        )
        
        if not memory_list:
            return result
        
        # Convert memory entries to dicts for processing
        items = []
        for entry in memory_list:
            if hasattr(entry, 'to_dict'):
                items.append(entry.to_dict())
            elif hasattr(entry, '__dict__'):
                items.append(entry.__dict__)
            else:
                items.append({'content': str(entry), 'metadata': {}})
        
        # Find duplicates
        duplicate_groups = self.duplication_detector.find_duplicates(items)
        
        # Merge duplicates
        items_to_remove = set()
        for group in duplicate_groups:
            if len(group) > 1:
                best_index = self.duplication_detector.select_best_from_group(
                    items, group, self.value_filter
                )
                # Mark others for removal
                for idx in group:
                    if idx != best_index:
                        items_to_remove.add(idx)
                        result.items_merged += 1
        
        # Apply cleanup rules
        for i, item in enumerate(items):
            if i in items_to_remove:
                continue
                
            for rule in sorted(self.cleanup_rules, key=lambda r: r.priority):
                try:
                    if rule.condition(item):
                        if rule.action == CleanupAction.DELETE:
                            items_to_remove.add(i)
                            result.items_deleted += 1
                        elif rule.action == CleanupAction.ARCHIVE:
                            # Mark as archived in metadata
                            item['metadata'] = item.get('metadata', {})
                            item['metadata']['archived'] = True
                            item['metadata']['archived_at'] = datetime.utcnow().isoformat()
                            result.items_archived += 1
                        elif rule.action == CleanupAction.COMPRESS:
                            # Compress content
                            content = item.get('content', '')
                            if len(content) > 200:
                                item['content'] = content[:100] + "...[compressed]..." + content[-50:]
                                result.items_compressed += 1
                        break  # Apply first matching rule only
                except Exception as e:
                    result.errors.append(f"Rule {rule.name} failed: {e}")
        
        # Remove items marked for deletion
        if items_to_remove:
            # Calculate bytes freed (rough estimate)
            for idx in items_to_remove:
                content_size = len(str(items[idx].get('content', '')))
                result.bytes_freed += content_size
            
            # Remove from original list (in reverse order to maintain indices)
            for idx in sorted(items_to_remove, reverse=True):
                if idx < len(memory_list):
                    del memory_list[idx]
        
        return result
    
    def _cleanup_fact_list(self, fact_list: List[Dict[str, Any]], context: str) -> CleanupResult:
        """Clean up a list of facts."""
        result = CleanupResult(
            total_items_processed=len(fact_list),
            items_deleted=0,
            items_archived=0,
            items_compressed=0,
            items_merged=0,
            bytes_freed=0,
            execution_time=0,
            errors=[],
            details={'context': context}
        )
        
        if not fact_list:
            return result
        
        # Find duplicate facts
        duplicate_groups = self.duplication_detector.find_duplicates(fact_list)
        
        # Merge duplicates
        items_to_remove = set()
        for group in duplicate_groups:
            if len(group) > 1:
                best_index = self.duplication_detector.select_best_from_group(
                    fact_list, group, self.value_filter
                )
                for idx in group:
                    if idx != best_index:
                        items_to_remove.add(idx)
                        result.items_merged += 1
        
        # Apply value filtering to facts
        for i, fact in enumerate(fact_list):
            if i in items_to_remove:
                continue
            
            # Check value score
            value_score = self.value_filter.calculate_value_score(fact)
            if value_score < self.value_threshold:
                # Check if it's a critical fact type that should be kept
                fact_type = fact.get('fact_type', '').lower()
                importance = fact.get('importance', '').lower()
                
                if fact_type in ['credential_location', 'deadline'] or importance == 'critical':
                    # Keep critical facts even with low scores
                    continue
                else:
                    items_to_remove.add(i)
                    result.items_deleted += 1
        
        # Remove items
        if items_to_remove:
            for idx in sorted(items_to_remove, reverse=True):
                if idx < len(fact_list):
                    content_size = len(str(fact_list[idx].get('content', '')))
                    result.bytes_freed += content_size
                    del fact_list[idx]
        
        return result
    
    def _enforce_session_quota(self, session_id: str) -> None:
        """Enforce memory quota for a session."""
        memory_store = self.enhanced_memory_service.memory_store
        
        # Count total items
        total_items = 0
        total_items += len(memory_store.short_term_memory.get(session_id, []))
        total_items += len(memory_store.long_term_memory.get(session_id, []))
        total_items += len(memory_store.fact_memory.get(session_id, []))
        
        if total_items > self.max_memory_per_session:
            excess = total_items - self.max_memory_per_session
            logger.info(f"Session {session_id} over quota by {excess} items, cleaning up")
            
            # Remove oldest, lowest-value short-term memories first
            if session_id in memory_store.short_term_memory:
                st_memories = memory_store.short_term_memory[session_id]
                if len(st_memories) > excess:
                    # Sort by value and age, remove lowest-value oldest items
                    st_with_scores = [
                        (i, entry, self.value_filter.calculate_value_score(entry.to_dict() if hasattr(entry, 'to_dict') else {'content': str(entry)}))
                        for i, entry in enumerate(st_memories)
                    ]
                    st_with_scores.sort(key=lambda x: (x[2], x[1].created_at if hasattr(x[1], 'created_at') else datetime.min))
                    
                    # Remove lowest value items
                    to_remove = min(excess, len(st_with_scores) // 2)
                    indices_to_remove = [x[0] for x in st_with_scores[:to_remove]]
                    
                    for idx in sorted(indices_to_remove, reverse=True):
                        del st_memories[idx]
    
    def _merge_results(self, result1: CleanupResult, result2: CleanupResult) -> CleanupResult:
        """Merge two cleanup results."""
        return CleanupResult(
            total_items_processed=result1.total_items_processed + result2.total_items_processed,
            items_deleted=result1.items_deleted + result2.items_deleted,
            items_archived=result1.items_archived + result2.items_archived,
            items_compressed=result1.items_compressed + result2.items_compressed,
            items_merged=result1.items_merged + result2.items_merged,
            bytes_freed=result1.bytes_freed + result2.bytes_freed,
            execution_time=max(result1.execution_time, result2.execution_time),
            errors=result1.errors + result2.errors,
            details={**result1.details, **result2.details}
        )
    
    def _is_expired(self, item: Dict[str, Any]) -> bool:
        """Check if item is expired."""
        expires_at = item.get('expires_at')
        if not expires_at:
            return False
        
        try:
            expiry_date = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            return datetime.utcnow() > expiry_date
        except Exception:
            return False
    
    def _is_old(self, item: Dict[str, Any], days: int) -> bool:
        """Check if item is older than specified days."""
        created_at = item.get('created_at') or item.get('metadata', {}).get('created_at')
        if not created_at:
            return False
        
        try:
            created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            age = datetime.utcnow() - created_date
            return age > timedelta(days=days)
        except Exception:
            return False
    
    def get_cleanup_stats(self) -> Dict[str, Any]:
        """Get cleanup statistics."""
        return {
            'last_cleanup': self._last_cleanup.isoformat(),
            'cleanup_interval_hours': self.cleanup_interval.total_seconds() / 3600,
            'cleanup_running': self._cleanup_running,
            'background_service_active': self._cleanup_thread is not None and self._cleanup_thread.is_alive(),
            'max_memory_per_session': self.max_memory_per_session,
            'value_threshold': self.value_threshold,
            'cleanup_rules': len(self.cleanup_rules),
            'next_cleanup_estimated': (self._last_cleanup + self.cleanup_interval).isoformat()
        }
"""
safety_service.py

Safety and moderation service that provides:
- Lightweight LLM classifier for sensitive data detection
- Few-shot prompting for context-aware classification
- Content sanitization and isolation
- Privacy-preserving query processing
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple, Callable
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger("safety_service")


class SafetyLevel(Enum):
    """Safety classification levels."""
    SAFE = "safe"
    POTENTIALLY_SENSITIVE = "potentially_sensitive"
    SENSITIVE = "sensitive"
    BLOCKED = "blocked"


class ContentType(Enum):
    """Types of potentially sensitive content."""
    CREDENTIAL = "credential"
    PERSONAL_INFO = "personal_info"
    SYSTEM_INFO = "system_info"
    BUSINESS_SECRET = "business_secret"
    UNKNOWN = "unknown"


@dataclass
class SafetyResult:
    """Result of safety analysis."""
    level: SafetyLevel
    content_types: List[ContentType]
    confidence: float
    reasoning: str
    suggested_action: str
    sanitized_content: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass  
class SensitivePattern:
    """Definition of a sensitive content pattern."""
    name: str
    pattern: str
    content_type: ContentType
    severity: float
    description: str


class SafetyService:
    """
    Safety service for content moderation and sensitive data detection.
    """
    
    def __init__(
        self,
        llm_classifier: Optional[Callable[[str], str]] = None,
        enable_llm_classification: bool = True
    ):
        """
        Initialize safety service.
        
        Args:
            llm_classifier: Optional LLM function for advanced classification
            enable_llm_classification: Whether to use LLM for classification
        """
        self.llm_classifier = llm_classifier
        self.enable_llm_classification = enable_llm_classification
        
        # Define sensitive patterns with different severity levels
        self.sensitive_patterns = [
            # High severity - credentials and secrets
            SensitivePattern(
                name="api_keys",
                pattern=r'\b(api[_\s-]?key|secret[_\s-]?key|access[_\s-]?token)\b.*?[\w\-]{15,}',
                content_type=ContentType.CREDENTIAL,
                severity=0.9,
                description="API keys or access tokens"
            ),
            SensitivePattern(
                name="passwords",
                pattern=r'\b(password|passwd|pwd)\s*[:=]\s*["\']?[\w\@\!\#\$\%\^\&\*]{8,}["\']?',
                content_type=ContentType.CREDENTIAL,
                severity=0.95,
                description="Passwords or password-like strings"
            ),
            SensitivePattern(
                name="database_urls",
                pattern=r'\b(database[_\s-]?url|db[_\s-]?url|connection[_\s-]?string)\s*[:=]\s*["\']?[^\s"\']+["\']?',
                content_type=ContentType.SYSTEM_INFO,
                severity=0.8,
                description="Database connection strings"
            ),
            
            # Medium severity - system information
            SensitivePattern(
                name="server_addresses",
                pattern=r'\b(?:server|host)\s*[:=]\s*["\']?(?:\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|[\w\-\.]+\.[\w]+)["\']?',
                content_type=ContentType.SYSTEM_INFO,
                severity=0.7,
                description="Server addresses or hostnames"
            ),
            SensitivePattern(
                name="file_paths",
                pattern=r'\b(?:path|file)\s*[:=]\s*["\']?(?:[/\\][\w\-\.\\\/]+|[A-Z]:[\\\/][\w\-\.\\\/]+)["\']?',
                content_type=ContentType.SYSTEM_INFO,
                severity=0.5,
                description="System file paths"
            ),
            
            # Lower severity - potentially sensitive business info
            SensitivePattern(
                name="business_metrics",
                pattern=r'\b(?:revenue|profit|cost|budget|salary)\s*[:=]\s*["\']?\$?[\d,]+\.?\d*["\']?',
                content_type=ContentType.BUSINESS_SECRET,
                severity=0.6,
                description="Business financial information"
            ),
            SensitivePattern(
                name="personal_emails",
                pattern=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                content_type=ContentType.PERSONAL_INFO,
                severity=0.4,
                description="Email addresses"
            ),
        ]
        
        # Contextual keywords that increase sensitivity
        self.sensitivity_amplifiers = [
            "production", "prod", "live", "confidential", "private", "internal",
            "secret", "classified", "restricted", "do not share", "proprietary"
        ]
        
        # Safe context indicators
        self.safe_indicators = [
            "example", "demo", "test", "sample", "placeholder", "mock",
            "documentation", "tutorial", "guide", "public"
        ]
    
    def analyze_content(self, content: str, context: Optional[Dict[str, Any]] = None) -> SafetyResult:
        """
        Analyze content for safety and sensitivity.
        
        Args:
            content: Text content to analyze
            context: Additional context for analysis
            
        Returns:
            SafetyResult: Safety analysis result
        """
        context = context or {}
        
        # Step 1: Pattern-based detection
        pattern_results = self._detect_sensitive_patterns(content)
        
        # Step 2: Context analysis
        context_score = self._analyze_context(content, context)
        
        # Step 3: LLM classification (if enabled)
        llm_result = None
        if self.enable_llm_classification and self.llm_classifier:
            llm_result = self._llm_classify(content, context)
        
        # Step 4: Combine results and make final decision
        final_result = self._combine_results(content, pattern_results, context_score, llm_result)
        
        return final_result
    
    def _detect_sensitive_patterns(self, content: str) -> Dict[str, Any]:
        """Detect sensitive patterns in content."""
        matches = []
        max_severity = 0.0
        content_types = set()
        
        for pattern_def in self.sensitive_patterns:
            pattern_matches = re.finditer(pattern_def.pattern, content, re.IGNORECASE)
            for match in pattern_matches:
                matches.append({
                    "pattern_name": pattern_def.name,
                    "match": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "severity": pattern_def.severity,
                    "content_type": pattern_def.content_type,
                    "description": pattern_def.description
                })
                max_severity = max(max_severity, pattern_def.severity)
                content_types.add(pattern_def.content_type)
        
        return {
            "matches": matches,
            "max_severity": max_severity,
            "content_types": list(content_types),
            "match_count": len(matches)
        }
    
    def _analyze_context(self, content: str, context: Dict[str, Any]) -> float:
        """Analyze contextual factors that affect sensitivity."""
        context_score = 0.0
        
        # Check for sensitivity amplifiers
        for amplifier in self.sensitivity_amplifiers:
            if amplifier.lower() in content.lower():
                context_score += 0.1
        
        # Check for safe indicators (reduces sensitivity)
        for indicator in self.safe_indicators:
            if indicator.lower() in content.lower():
                context_score -= 0.1
        
        # Context from session (if available)
        session_context = context.get('session_context', {})
        if session_context.get('is_development_environment'):
            context_score -= 0.2
        if session_context.get('is_production_environment'):
            context_score += 0.3
        
        return max(0.0, min(1.0, context_score))
    
    def _llm_classify(self, content: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Use LLM for advanced content classification."""
        if not self.llm_classifier:
            return None
        
        try:
            # Few-shot prompt for classification
            prompt = self._build_classification_prompt(content, context)
            response = self.llm_classifier(prompt)
            
            # Parse LLM response
            return self._parse_llm_response(response)
            
        except Exception as e:
            logger.warning(f"LLM classification failed: {e}")
            return None
    
    def _build_classification_prompt(self, content: str, context: Dict[str, Any]) -> str:
        """Build few-shot classification prompt."""
        prompt = """
Classify the following content for sensitivity. Consider whether it contains:
- Credentials (passwords, API keys, tokens)
- Personal information (emails, names, IDs)
- System information (servers, databases, file paths)
- Business secrets (financial data, proprietary info)

Examples:
Input: "The API key is sk-123456789abcdef for our OpenAI integration"
Output: SENSITIVE - Contains API key credential

Input: "To configure the system, set the database_url in your .env file"
Output: POTENTIALLY_SENSITIVE - References system configuration 

Input: "What is the onboarding process for new employees?"
Output: SAFE - General business process question

Input: "How do I use the API endpoints documented in the guide?"
Output: SAFE - Documentation reference

Now classify this content:
Input: "{content}"
Output:"""
        
        return prompt.format(content=content[:500])  # Limit length
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM classification response."""
        response = response.strip().upper()
        
        if "SENSITIVE" in response:
            level = SafetyLevel.SENSITIVE
            confidence = 0.8
        elif "POTENTIALLY_SENSITIVE" in response:
            level = SafetyLevel.POTENTIALLY_SENSITIVE
            confidence = 0.6
        elif "SAFE" in response:
            level = SafetyLevel.SAFE
            confidence = 0.7
        else:
            level = SafetyLevel.POTENTIALLY_SENSITIVE
            confidence = 0.3
        
        return {
            "level": level,
            "confidence": confidence,
            "reasoning": response[:200]  # Truncate reasoning
        }
    
    def _combine_results(
        self, 
        content: str, 
        pattern_results: Dict[str, Any], 
        context_score: float, 
        llm_result: Optional[Dict[str, Any]]
    ) -> SafetyResult:
        """Combine all analysis results into final safety decision."""
        
        # Start with pattern-based assessment
        base_severity = pattern_results["max_severity"]
        content_types = [ContentType(ct.value) for ct in pattern_results["content_types"]]
        
        # Adjust based on context
        adjusted_severity = min(1.0, base_severity + context_score)
        
        # Factor in LLM result if available
        final_confidence = 0.7  # Base confidence
        if llm_result:
            llm_severity_map = {
                SafetyLevel.SAFE: 0.0,
                SafetyLevel.POTENTIALLY_SENSITIVE: 0.4,
                SafetyLevel.SENSITIVE: 0.8,
                SafetyLevel.BLOCKED: 1.0
            }
            llm_severity = llm_severity_map.get(llm_result["level"], 0.4)
            
            # Weight pattern-based (70%) and LLM-based (30%) results
            adjusted_severity = (adjusted_severity * 0.7) + (llm_severity * 0.3)
            final_confidence = (final_confidence * 0.6) + (llm_result["confidence"] * 0.4)
        
        # Determine final safety level
        if adjusted_severity >= 0.8:
            safety_level = SafetyLevel.SENSITIVE
            suggested_action = "isolate_and_sanitize"
        elif adjusted_severity >= 0.5:
            safety_level = SafetyLevel.POTENTIALLY_SENSITIVE
            suggested_action = "review_and_process"
        elif adjusted_severity >= 0.2:
            safety_level = SafetyLevel.SAFE
            suggested_action = "process_normally"
        else:
            safety_level = SafetyLevel.SAFE
            suggested_action = "process_normally"
        
        # Generate reasoning
        reasoning_parts = []
        if pattern_results["match_count"] > 0:
            reasoning_parts.append(f"Found {pattern_results['match_count']} sensitive patterns")
        if context_score > 0.1:
            reasoning_parts.append(f"Contextual sensitivity score: {context_score:.2f}")
        if llm_result:
            reasoning_parts.append(f"LLM classification: {llm_result['level'].value}")
        
        reasoning = "; ".join(reasoning_parts) if reasoning_parts else "No significant sensitivity indicators"
        
        # Sanitize content if needed
        sanitized_content = None
        if safety_level in [SafetyLevel.SENSITIVE, SafetyLevel.POTENTIALLY_SENSITIVE]:
            sanitized_content = self._sanitize_content(content, pattern_results["matches"])
        
        return SafetyResult(
            level=safety_level,
            content_types=content_types or [ContentType.UNKNOWN],
            confidence=final_confidence,
            reasoning=reasoning,
            suggested_action=suggested_action,
            sanitized_content=sanitized_content,
            metadata={
                "pattern_matches": pattern_results["matches"],
                "context_score": context_score,
                "adjusted_severity": adjusted_severity,
                "llm_result": llm_result
            }
        )
    
    def _sanitize_content(self, content: str, matches: List[Dict[str, Any]]) -> str:
        """Sanitize content by replacing sensitive patterns."""
        sanitized = content
        
        # Sort matches by position (reverse order to maintain indices)
        sorted_matches = sorted(matches, key=lambda x: x["start"], reverse=True)
        
        for match in sorted_matches:
            start, end = match["start"], match["end"]
            content_type = match["content_type"]
            
            # Choose replacement based on content type
            if content_type == ContentType.CREDENTIAL:
                replacement = "[REDACTED_CREDENTIAL]"
            elif content_type == ContentType.PERSONAL_INFO:
                replacement = "[REDACTED_PERSONAL_INFO]"
            elif content_type == ContentType.SYSTEM_INFO:
                replacement = "[REDACTED_SYSTEM_INFO]"
            elif content_type == ContentType.BUSINESS_SECRET:
                replacement = "[REDACTED_BUSINESS_INFO]"
            else:
                replacement = "[REDACTED]"
            
            sanitized = sanitized[:start] + replacement + sanitized[end:]
        
        return sanitized
    
    def create_safe_processing_context(self, content: str, safety_result: SafetyResult) -> Dict[str, Any]:
        """Create a safe processing context based on safety analysis."""
        context = {
            "original_content": content,
            "safety_level": safety_result.level.value,
            "processing_mode": "normal"
        }
        
        if safety_result.level == SafetyLevel.SENSITIVE:
            context.update({
                "processing_mode": "isolated",
                "content_to_process": safety_result.sanitized_content,
                "require_manual_review": True,
                "log_interaction": True
            })
        elif safety_result.level == SafetyLevel.POTENTIALLY_SENSITIVE:
            context.update({
                "processing_mode": "cautious",
                "content_to_process": safety_result.sanitized_content or content,
                "require_manual_review": False,
                "log_interaction": True
            })
        else:
            context.update({
                "content_to_process": content,
                "require_manual_review": False,
                "log_interaction": False
            })
        
        return context
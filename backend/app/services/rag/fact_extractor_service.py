"""
fact_extractor_service.py

Fact extraction pipeline for long-term memory storage.
Converts conversation messages into structured facts using Pydantic schemas.

Example:
Message: "API Key ở server A, file .env"
→ Extracted fact: { resource: "server A", path: ".env", type: "credential_location" }
"""

import re
import json
import logging
from typing import List, Dict, Any, Optional, Union, Callable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict

try:
    from pydantic import BaseModel, Field, validator
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    BaseModel = object

logger = logging.getLogger("fact_extractor_service")


class FactType(Enum):
    """Types of extractable facts."""
    CREDENTIAL_LOCATION = "credential_location"
    API_ENDPOINT = "api_endpoint"
    FILE_REFERENCE = "file_reference"
    PROCESS_STEP = "process_step"
    CONFIGURATION = "configuration"
    DEADLINE = "deadline"
    PERSON_ROLE = "person_role"
    BUSINESS_RULE = "business_rule"
    SYSTEM_COMPONENT = "system_component"
    ERROR_SOLUTION = "error_solution"
    URL_REFERENCE = "url_reference"
    ENVIRONMENT_INFO = "environment_info"
    UNKNOWN = "unknown"


class ImportanceLevel(Enum):
    """Importance levels for fact retention."""
    CRITICAL = "critical"    # Must retain, high value
    HIGH = "high"           # Important information
    MEDIUM = "medium"       # Useful context
    LOW = "low"            # Nice to have
    TEMPORARY = "temporary" # Short-term relevance only


# Pydantic schemas for structured fact extraction
if PYDANTIC_AVAILABLE:
    class BaseFact(BaseModel):
        """Base fact schema."""
        fact_type: FactType
        content: str
        importance: ImportanceLevel = ImportanceLevel.MEDIUM
        extracted_at: datetime = Field(default_factory=datetime.utcnow)
        session_id: str
        project_id: Optional[str] = None
        confidence: float = Field(0.5, ge=0.0, le=1.0)
        source_message: str = ""
        tags: List[str] = Field(default_factory=list)
        metadata: Dict[str, Any] = Field(default_factory=dict)
        
        class Config:
            use_enum_values = True

    class CredentialLocationFact(BaseFact):
        """Fact about credential storage locations."""
        fact_type: FactType = FactType.CREDENTIAL_LOCATION
        resource: str = Field(..., description="Server, service, or system name")
        path: str = Field(..., description="File path or location")
        credential_type: str = Field("", description="Type of credential (API key, password, etc.)")
        
    class APIEndpointFact(BaseFact):
        """Fact about API endpoints."""
        fact_type: FactType = FactType.API_ENDPOINT
        endpoint_url: str = Field(..., description="API endpoint URL or path")
        method: str = Field("", description="HTTP method")
        purpose: str = Field("", description="What the endpoint does")
        
    class FileReferenceFact(BaseFact):
        """Fact about file references."""
        fact_type: FactType = FactType.FILE_REFERENCE
        file_path: str = Field(..., description="File path or name")
        file_type: str = Field("", description="File type or extension")
        purpose: str = Field("", description="What the file is used for")
        
    class ProcessStepFact(BaseFact):
        """Fact about process or workflow steps."""
        fact_type: FactType = FactType.PROCESS_STEP
        process_name: str = Field(..., description="Name of the process")
        step_number: Optional[int] = Field(None, description="Step number if sequential")
        step_description: str = Field(..., description="What this step involves")
        dependencies: List[str] = Field(default_factory=list, description="Prerequisites")
        
    class ConfigurationFact(BaseFact):
        """Fact about system or application configuration."""
        fact_type: FactType = FactType.CONFIGURATION
        config_key: str = Field(..., description="Configuration parameter name")
        config_value: str = Field("", description="Configuration value (if safe)")
        config_location: str = Field("", description="Where configuration is stored")
        
    class DeadlineFact(BaseFact):
        """Fact about deadlines or time-sensitive information."""
        fact_type: FactType = FactType.DEADLINE
        deadline_date: Optional[datetime] = Field(None, description="Deadline date/time")
        task_description: str = Field(..., description="What needs to be done")
        urgency: str = Field("medium", description="Urgency level")
        
    class PersonRoleFact(BaseFact):
        """Fact about people and their roles."""
        fact_type: FactType = FactType.PERSON_ROLE
        person_name: str = Field(..., description="Person's name or identifier")
        role: str = Field(..., description="Their role or responsibility")
        contact_info: str = Field("", description="Contact information if provided")
        
    class BusinessRuleFact(BaseFact):
        """Fact about business rules or policies."""
        fact_type: FactType = FactType.BUSINESS_RULE
        rule_description: str = Field(..., description="Description of the rule")
        scope: str = Field("", description="Where/when the rule applies")
        exceptions: List[str] = Field(default_factory=list, description="Exceptions to the rule")
        
    class SystemComponentFact(BaseFact):
        """Fact about system components or architecture."""
        fact_type: FactType = FactType.SYSTEM_COMPONENT
        component_name: str = Field(..., description="Name of the component")
        component_type: str = Field("", description="Type of component (service, database, etc.)")
        purpose: str = Field("", description="What the component does")
        dependencies: List[str] = Field(default_factory=list, description="Component dependencies")
        
    class ErrorSolutionFact(BaseFact):
        """Fact about error solutions or troubleshooting."""
        fact_type: FactType = FactType.ERROR_SOLUTION
        error_description: str = Field(..., description="Description of the error")
        solution: str = Field(..., description="How to solve the error")
        error_code: str = Field("", description="Error code if applicable")
        
    class URLReferenceFact(BaseFact):
        """Fact about URL references."""
        fact_type: FactType = FactType.URL_REFERENCE
        url: str = Field(..., description="The URL")
        purpose: str = Field("", description="What the URL is for")
        access_method: str = Field("", description="How to access (if special requirements)")
        
    class EnvironmentInfoFact(BaseFact):
        """Fact about environment information."""
        fact_type: FactType = FactType.ENVIRONMENT_INFO
        environment_name: str = Field(..., description="Environment name (dev, staging, prod)")
        info_type: str = Field(..., description="Type of information")
        details: str = Field(..., description="Environmental details")

else:
    # Fallback dataclass versions if Pydantic not available
    @dataclass
    class BaseFact:
        fact_type: FactType
        content: str
        importance: ImportanceLevel
        extracted_at: datetime
        session_id: str
        project_id: Optional[str] = None
        confidence: float = 0.5
        source_message: str = ""
        tags: List[str] = None
        metadata: Dict[str, Any] = None


class FactExtractorService:
    """
    Service for extracting structured facts from conversation messages.
    """
    
    def __init__(
        self,
        llm_extractor: Optional[Callable[[str], str]] = None,
        enable_llm_extraction: bool = True,
        min_confidence_threshold: float = 0.3
    ):
        """
        Initialize fact extractor service.
        
        Args:
            llm_extractor: Optional LLM function for advanced fact extraction
            enable_llm_extraction: Whether to use LLM for extraction
            min_confidence_threshold: Minimum confidence to retain facts
        """
        self.llm_extractor = llm_extractor
        self.enable_llm_extraction = enable_llm_extraction
        self.min_confidence_threshold = min_confidence_threshold
        
        # Pattern-based extractors
        self.extraction_patterns = {
            FactType.CREDENTIAL_LOCATION: [
                {
                    "pattern": r"\b(?:api[_\s-]?key|password|token|secret)\s+(?:in|at|from|on)\s+([^,\.\s]+)(?:\s*,\s*(?:file|path)?\s*([^\s,\.]+))?",
                    "extractor": self._extract_credential_location
                },
                {
                    "pattern": r"\b([^,\s]+)\s*[,:]?\s*file\s+([^\s,\.]+\.env|[^\s,\.]*config[^\s,\.]*)",
                    "extractor": self._extract_credential_location
                }
            ],
            FactType.API_ENDPOINT: [
                {
                    "pattern": r"\b(/?api/[^\s]+)",
                    "extractor": self._extract_api_endpoint
                },
                {
                    "pattern": r"\b(https?://[^\s]+/api[^\s]*)",
                    "extractor": self._extract_api_endpoint
                }
            ],
            FactType.FILE_REFERENCE: [
                {
                    "pattern": r"\b([^\s]+\.[a-zA-Z]{2,4})\b",
                    "extractor": self._extract_file_reference
                },
                {
                    "pattern": r"\b(?:file|script|document|config)\s+([^\s,\.]+)",
                    "extractor": self._extract_file_reference
                }
            ],
            FactType.DEADLINE: [
                {
                    "pattern": r"\b(?:deadline|due|by)\s+([^,\.]+)(?:for|to)\s+([^,\.]+)",
                    "extractor": self._extract_deadline
                },
                {
                    "pattern": r"\b(?:complete|finish|done)\s+([^,\.]+)\s+(?:by|before)\s+([^,\.]+)",
                    "extractor": self._extract_deadline
                }
            ],
            FactType.CONFIGURATION: [
                {
                    "pattern": r"\b([A-Z_][A-Z0-9_]*)\s*[:=]\s*([^\s,\.]+)",
                    "extractor": self._extract_configuration
                },
                {
                    "pattern": r"\bset\s+([^\s]+)\s+(?:to|=)\s+([^\s,\.]+)",
                    "extractor": self._extract_configuration
                }
            ],
            FactType.URL_REFERENCE: [
                {
                    "pattern": r"\b(https?://[^\s]+)",
                    "extractor": self._extract_url_reference
                }
            ]
        }
        
        # Importance keywords
        self.importance_keywords = {
            ImportanceLevel.CRITICAL: ["critical", "urgent", "important", "must", "required", "production"],
            ImportanceLevel.HIGH: ["should", "need", "deadline", "key", "main"],
            ImportanceLevel.MEDIUM: ["helpful", "useful", "good", "recommend"],
            ImportanceLevel.LOW: ["optional", "nice", "consider", "maybe"],
            ImportanceLevel.TEMPORARY: ["temp", "temporary", "quick", "test"]
        }
    
    def extract_facts(
        self, 
        message: str, 
        session_id: str, 
        project_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Union[BaseFact, Dict[str, Any]]]:
        """
        Extract facts from a conversation message.
        
        Args:
            message: Message text to extract facts from
            session_id: Session identifier
            project_id: Optional project identifier
            context: Additional context for extraction
            
        Returns:
            List of extracted facts
        """
        context = context or {}
        facts = []
        
        # Step 1: Pattern-based extraction
        pattern_facts = self._extract_pattern_facts(message, session_id, project_id, context)
        facts.extend(pattern_facts)
        
        # Step 2: LLM-based extraction (if enabled)
        if self.enable_llm_extraction and self.llm_extractor:
            llm_facts = self._extract_llm_facts(message, session_id, project_id, context)
            facts.extend(llm_facts)
        
        # Step 3: Filter by confidence threshold
        filtered_facts = [f for f in facts if self._get_fact_confidence(f) >= self.min_confidence_threshold]
        
        # Step 4: Deduplicate and normalize
        normalized_facts = self._normalize_facts(filtered_facts)
        
        return normalized_facts
    
    def _extract_pattern_facts(
        self, 
        message: str, 
        session_id: str, 
        project_id: Optional[str], 
        context: Dict[str, Any]
    ) -> List[Union[BaseFact, Dict[str, Any]]]:
        """Extract facts using pattern matching."""
        facts = []
        
        for fact_type, patterns in self.extraction_patterns.items():
            for pattern_config in patterns:
                pattern = pattern_config["pattern"]
                extractor = pattern_config["extractor"]
                
                matches = re.finditer(pattern, message, re.IGNORECASE)
                for match in matches:
                    try:
                        fact = extractor(match, message, session_id, project_id, context)
                        if fact:
                            facts.append(fact)
                    except Exception as e:
                        logger.warning(f"Pattern extraction failed for {fact_type}: {e}")
        
        return facts
    
    def _extract_llm_facts(
        self, 
        message: str, 
        session_id: str, 
        project_id: Optional[str], 
        context: Dict[str, Any]
    ) -> List[Union[BaseFact, Dict[str, Any]]]:
        """Extract facts using LLM."""
        if not self.llm_extractor:
            return []
        
        try:
            prompt = self._build_extraction_prompt(message, context)
            response = self.llm_extractor(prompt)
            
            # Log the raw response for debugging
            logger.debug(f"LLM fact extraction response: {response[:500]}...")
            
            if not response or not response.strip():
                logger.debug("LLM returned empty response for fact extraction")
                return []
                
            return self._parse_llm_extraction_response(response, message, session_id, project_id)
        except Exception as e:
            logger.warning(f"LLM fact extraction failed: {e}")
            # Log more details about the error for debugging
            if hasattr(e, '__class__'):
                logger.debug(f"Exception type: {e.__class__.__name__}")
            return []
    
    def _build_extraction_prompt(self, message: str, context: Dict[str, Any]) -> str:
        """Build prompt for LLM fact extraction."""
        prompt = """
Extract structured facts from the following conversation message. You must respond with a valid JSON array only.

IMPORTANT: Your response must be ONLY a JSON array, starting with [ and ending with ]. Do not include any other text.

Each fact should have these exact fields:
- fact_type: one of [credential_location, api_endpoint, file_reference, process_step, configuration, deadline, person_role, business_rule, system_component, error_solution, url_reference, environment_info]
- content: brief description of the fact
- importance: one of [critical, high, medium, low, temporary]
- confidence: number between 0.0 and 1.0
- extracted_details: object with relevant fields for the fact type

Examples:

Message: "The API key is stored in server A, file .env"
Response: [{{"fact_type": "credential_location", "content": "API key location", "importance": "high", "confidence": 0.9, "extracted_details": {{"resource": "server A", "path": ".env", "credential_type": "API key"}}}}]

Message: "To deploy, first run npm install, then npm run build"
Response: [{{"fact_type": "process_step", "content": "Deployment process step 1", "importance": "medium", "confidence": 0.8, "extracted_details": {{"process_name": "deployment", "step_number": 1, "step_description": "run npm install"}}}}, {{"fact_type": "process_step", "content": "Deployment process step 2", "importance": "medium", "confidence": 0.8, "extracted_details": {{"process_name": "deployment", "step_number": 2, "step_description": "run npm run build"}}}}]

Message: "How are you today?"
Response: []

Message: "{message}"
Response:"""
        
        return prompt.format(message=message[:500])  # Limit message length
    
    def _parse_llm_extraction_response(
        self, 
        response: str, 
        message: str, 
        session_id: str, 
        project_id: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Parse LLM extraction response."""
        try:
            # Clean response and try multiple JSON extraction patterns
            cleaned_response = response.strip()
            
            # Handle case where LLM returns just a quoted string
            if cleaned_response.startswith('"') and cleaned_response.endswith('"') and cleaned_response.count('"') == 2:
                logger.debug(f"LLM returned quoted string instead of JSON: {cleaned_response}")
                return []
            
            # Pattern 1: Look for JSON array
            json_match = re.search(r'\[.*\]', cleaned_response, re.DOTALL)
            if json_match:
                try:
                    facts_data = json.loads(json_match.group())
                except json.JSONDecodeError as e:
                    logger.debug(f"JSON decode error for array pattern: {e}")
                    # Try to fix common JSON issues
                    json_text = json_match.group()
                    json_text = re.sub(r',\s*}', '}', json_text)  # Remove trailing commas
                    json_text = re.sub(r',\s*]', ']', json_text)  # Remove trailing commas
                    json_text = re.sub(r'([^"])"([^":])', r'\1"\2', json_text)  # Fix unescaped quotes
                    try:
                        facts_data = json.loads(json_text)
                    except json.JSONDecodeError as final_e:
                        logger.warning(f"Could not parse JSON even after cleanup: {json_text[:200]}... Error: {final_e}")
                        return []
                
                # Process facts
                facts = []
                for fact_data in facts_data:
                    if isinstance(fact_data, dict):
                        fact = self._create_fact_from_llm_data(fact_data, message, session_id, project_id)
                        if fact:
                            facts.append(fact)
                
                return facts
            
            # Pattern 2: Look for individual JSON objects
            json_objects = re.findall(r'\{[^{}]*\}', cleaned_response)
            if json_objects:
                facts = []
                for json_str in json_objects:
                    try:
                        fact_data = json.loads(json_str)
                        if isinstance(fact_data, dict) and 'fact_type' in fact_data:
                            fact = self._create_fact_from_llm_data(fact_data, message, session_id, project_id)
                            if fact:
                                facts.append(fact)
                    except json.JSONDecodeError:
                        continue
                return facts
            
            # Pattern 3: Check if response indicates no facts
            no_facts_indicators = ['no facts', 'no structured facts', 'none found', 'empty', '[]']
            if any(indicator in cleaned_response.lower() for indicator in no_facts_indicators):
                logger.debug(f"LLM indicated no facts found: {cleaned_response}")
                return []
            
            logger.debug(f"No valid JSON found in response: {cleaned_response[:200]}...")
            
        except Exception as e:
            logger.warning(f"Failed to parse LLM extraction response: {e}")
        
        return []
    
    def _create_fact_from_llm_data(
        self, 
        fact_data: Dict[str, Any], 
        message: str, 
        session_id: str, 
        project_id: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """Create a fact object from LLM-extracted data."""
        try:
            fact_type_str = fact_data.get("fact_type", "unknown")
            try:
                fact_type = FactType(fact_type_str)
            except ValueError:
                logger.debug(f"Unknown fact type: {fact_type_str}, skipping fact")
                return None
            
            importance_str = fact_data.get("importance", "medium") 
            try:
                importance = ImportanceLevel(importance_str)
            except ValueError:
                logger.debug(f"Unknown importance level: {importance_str}, defaulting to medium")
                importance = ImportanceLevel.MEDIUM
            
            # Validate required fields
            content = fact_data.get("content", "").strip()
            if not content:
                logger.debug("Fact missing content, skipping")
                return None
            
            base_fact = {
                "fact_type": fact_type,
                "content": content,
                "importance": importance,
                "extracted_at": datetime.utcnow(),
                "session_id": session_id,
                "project_id": project_id,
                "confidence": max(0.0, min(1.0, float(fact_data.get("confidence", 0.5)))),  # Clamp between 0-1
                "source_message": message,
                "tags": [],
                "metadata": fact_data.get("extracted_details", {}) if isinstance(fact_data.get("extracted_details"), dict) else {}
            }
            
            return base_fact
            
        except Exception as e:
            logger.warning(f"Failed to create fact from LLM data: {e}")
            return None
    
    # Pattern extractor methods
    def _extract_credential_location(self, match, message, session_id, project_id, context):
        """Extract credential location fact."""
        groups = match.groups()
        
        if len(groups) >= 2 and groups[1]:
            resource = groups[0]
            path = groups[1]
        else:
            # Try to infer from the single match
            text = groups[0] if groups else match.group()
            parts = text.split()
            resource = parts[0] if parts else "unknown"
            path = parts[1] if len(parts) > 1 else ""
        
        importance = self._determine_importance(message)
        
        if PYDANTIC_AVAILABLE:
            return CredentialLocationFact(
                content=f"Credential location: {resource} -> {path}",
                importance=importance,
                session_id=session_id,
                project_id=project_id,
                confidence=0.8,
                source_message=message,
                resource=resource,
                path=path,
                credential_type="unknown"
            )
        else:
            return {
                "fact_type": FactType.CREDENTIAL_LOCATION,
                "content": f"Credential location: {resource} -> {path}",
                "importance": importance,
                "extracted_at": datetime.utcnow(),
                "session_id": session_id,
                "project_id": project_id,
                "confidence": 0.8,
                "source_message": message,
                "resource": resource,
                "path": path,
                "credential_type": "unknown"
            }
    
    def _extract_api_endpoint(self, match, message, session_id, project_id, context):
        """Extract API endpoint fact."""
        endpoint = match.group(1) if match.groups() else match.group()
        importance = self._determine_importance(message)
        
        if PYDANTIC_AVAILABLE:
            return APIEndpointFact(
                content=f"API endpoint: {endpoint}",
                importance=importance,
                session_id=session_id,
                project_id=project_id,
                confidence=0.9,
                source_message=message,
                endpoint_url=endpoint,
                method="",
                purpose=""
            )
        else:
            return {
                "fact_type": FactType.API_ENDPOINT,
                "content": f"API endpoint: {endpoint}",
                "importance": importance,
                "extracted_at": datetime.utcnow(),
                "session_id": session_id,
                "project_id": project_id,
                "confidence": 0.9,
                "source_message": message,
                "endpoint_url": endpoint,
                "method": "",
                "purpose": ""
            }
    
    def _extract_file_reference(self, match, message, session_id, project_id, context):
        """Extract file reference fact."""
        file_path = match.group(1) if match.groups() else match.group()
        importance = self._determine_importance(message)
        
        # Determine file type
        file_type = ""
        if "." in file_path:
            file_type = file_path.split(".")[-1]
        
        if PYDANTIC_AVAILABLE:
            return FileReferenceFact(
                content=f"File reference: {file_path}",
                importance=importance,
                session_id=session_id,
                project_id=project_id,
                confidence=0.7,
                source_message=message,
                file_path=file_path,
                file_type=file_type,
                purpose=""
            )
        else:
            return {
                "fact_type": FactType.FILE_REFERENCE,
                "content": f"File reference: {file_path}",
                "importance": importance,
                "extracted_at": datetime.utcnow(),
                "session_id": session_id,
                "project_id": project_id,
                "confidence": 0.7,
                "source_message": message,
                "file_path": file_path,
                "file_type": file_type,
                "purpose": ""
            }
    
    def _extract_deadline(self, match, message, session_id, project_id, context):
        """Extract deadline fact."""
        groups = match.groups()
        if len(groups) >= 2:
            task = groups[1]
            deadline_text = groups[0]
        else:
            task = match.group()
            deadline_text = ""
        
        importance = ImportanceLevel.HIGH  # Deadlines are usually important
        
        if PYDANTIC_AVAILABLE:
            return DeadlineFact(
                content=f"Deadline: {task} by {deadline_text}",
                importance=importance,
                session_id=session_id,
                project_id=project_id,
                confidence=0.8,
                source_message=message,
                deadline_date=None,  # Would need date parsing
                task_description=task,
                urgency="medium"
            )
        else:
            return {
                "fact_type": FactType.DEADLINE,
                "content": f"Deadline: {task} by {deadline_text}",
                "importance": importance,
                "extracted_at": datetime.utcnow(),
                "session_id": session_id,
                "project_id": project_id,
                "confidence": 0.8,
                "source_message": message,
                "deadline_date": None,
                "task_description": task,
                "urgency": "medium"
            }
    
    def _extract_configuration(self, match, message, session_id, project_id, context):
        """Extract configuration fact."""
        groups = match.groups()
        config_key = groups[0] if groups else ""
        config_value = groups[1] if len(groups) > 1 else ""
        
        importance = self._determine_importance(message)
        
        if PYDANTIC_AVAILABLE:
            return ConfigurationFact(
                content=f"Configuration: {config_key} = {config_value}",
                importance=importance,
                session_id=session_id,
                project_id=project_id,
                confidence=0.7,
                source_message=message,
                config_key=config_key,
                config_value=config_value,
                config_location=""
            )
        else:
            return {
                "fact_type": FactType.CONFIGURATION,
                "content": f"Configuration: {config_key} = {config_value}",
                "importance": importance,
                "extracted_at": datetime.utcnow(),
                "session_id": session_id,
                "project_id": project_id,
                "confidence": 0.7,
                "source_message": message,
                "config_key": config_key,
                "config_value": config_value,
                "config_location": ""
            }
    
    def _extract_url_reference(self, match, message, session_id, project_id, context):
        """Extract URL reference fact."""
        url = match.group(1) if match.groups() else match.group()
        importance = self._determine_importance(message)
        
        if PYDANTIC_AVAILABLE:
            return URLReferenceFact(
                content=f"URL reference: {url}",
                importance=importance,
                session_id=session_id,
                project_id=project_id,
                confidence=0.9,
                source_message=message,
                url=url,
                purpose="",
                access_method=""
            )
        else:
            return {
                "fact_type": FactType.URL_REFERENCE,
                "content": f"URL reference: {url}",
                "importance": importance,
                "extracted_at": datetime.utcnow(),
                "session_id": session_id,
                "project_id": project_id,
                "confidence": 0.9,
                "source_message": message,
                "url": url,
                "purpose": "",
                "access_method": ""
            }
    
    def _determine_importance(self, message: str) -> ImportanceLevel:
        """Determine importance level based on message content."""
        message_lower = message.lower()
        
        for importance, keywords in self.importance_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return importance
        
        return ImportanceLevel.MEDIUM
    
    def _get_fact_confidence(self, fact: Union[BaseFact, Dict[str, Any]]) -> float:
        """Get confidence score from fact."""
        if hasattr(fact, 'confidence'):
            return fact.confidence
        elif isinstance(fact, dict):
            return fact.get('confidence', 0.5)
        return 0.5
    
    def _normalize_facts(self, facts: List[Union[BaseFact, Dict[str, Any]]]) -> List[Union[BaseFact, Dict[str, Any]]]:
        """Normalize and deduplicate facts."""
        # Simple deduplication based on content similarity
        seen_contents = set()
        normalized = []
        
        for fact in facts:
            content = getattr(fact, 'content', fact.get('content', '')) if hasattr(fact, 'content') or isinstance(fact, dict) else str(fact)
            
            # Simple content similarity check
            content_key = self._normalize_content_for_dedup(content)
            if content_key not in seen_contents:
                seen_contents.add(content_key)
                normalized.append(fact)
        
        return normalized
    
    def _normalize_content_for_dedup(self, content: str) -> str:
        """Normalize content for deduplication."""
        # Remove punctuation, convert to lowercase, remove extra spaces
        normalized = re.sub(r'[^\w\s]', '', content.lower())
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        return normalized
    
    def serialize_fact(self, fact: Union[BaseFact, Dict[str, Any]]) -> Dict[str, Any]:
        """Serialize fact to dictionary for storage."""
        if PYDANTIC_AVAILABLE and isinstance(fact, BaseModel):
            return fact.dict()
        elif isinstance(fact, dict):
            return fact
        elif hasattr(fact, '__dict__'):
            return asdict(fact) if hasattr(asdict, '__call__') else fact.__dict__
        else:
            return {"content": str(fact), "fact_type": "unknown"}
    
    def get_extraction_stats(self, session_id: str) -> Dict[str, Any]:
        """Get extraction statistics for debugging."""
        return {
            "session_id": session_id,
            "patterns_enabled": len(self.extraction_patterns),
            "llm_extraction_enabled": self.enable_llm_extraction,
            "min_confidence_threshold": self.min_confidence_threshold,
            "fact_types": [ft.value for ft in FactType]
        }
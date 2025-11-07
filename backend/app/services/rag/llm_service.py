# llm_service.py (upgraded)
import os
import time
import logging
import asyncio
from typing import List, Optional, AsyncGenerator, Callable, Any, Dict
from contextlib import asynccontextmanager

# External libs (install as needed)
# pip install redis backoff prometheus-client
try:
    import redis
except Exception:
    redis = None

try:
    from prometheus_client import Counter, Histogram
except Exception:
    Counter = None
    Histogram = None

# Placeholders for LangChain/OpenAI wrappers used previously
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# --- Logger setup ---
logger = logging.getLogger("llm_service")
if not logger.handlers:
    handler = logging.StreamHandler()
    fmt = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    )
    handler.setFormatter(fmt)
    logger.addHandler(handler)
logger.setLevel(os.getenv("LLM_SERVICE_LOG_LEVEL", "INFO"))

# --- Metrics (optional) ---
REQUEST_COUNTER = Counter("llm_requests_total", "Total LLM requests") if Counter else None
REQUEST_LATENCY = Histogram("llm_request_latency_seconds", "LLM request latency seconds") if Histogram else None

# --- Simple token counting utility (placeholder) ---
def simple_token_count(text: str) -> int:
    # TODO: replace with model-specific tokenizer (tiktoken)
    return len(text.split())

def truncate_by_tokens(text: str, max_tokens: int) -> str:
    tokens = text.split()
    if len(tokens) <= max_tokens:
        return text
    return " ".join(tokens[-max_tokens:])  # keep recent tokens

# --- Retry decorator (synchronous) ---
def retry_on_exception(max_attempts=3, base_delay=0.5, exceptions=(Exception,)):
    def deco(fn):
        def wrapped(*args, **kwargs):
            attempts = 0
            while True:
                try:
                    return fn(*args, **kwargs)
                except exceptions as e:
                    attempts += 1
                    logger.warning("Retryable error in %s: %s (attempt %d/%d)", fn.__name__, e, attempts, max_attempts)
                    if attempts >= max_attempts:
                        logger.exception("Max retry attempts reached for %s", fn.__name__)
                        raise
                    time.sleep(base_delay * (2 ** (attempts - 1)))
        return wrapped
    return deco

# --- Async retry decorator ---
def aretry_on_exception(max_attempts=3, base_delay=0.5, exceptions=(Exception,)):
    def deco(fn):
        async def wrapped(*args, **kwargs):
            attempts = 0
            while True:
                try:
                    return await fn(*args, **kwargs)
                except exceptions as e:
                    attempts += 1
                    logger.warning("Async retryable error in %s: %s (attempt %d/%d)", fn.__name__, e, attempts, max_attempts)
                    if attempts >= max_attempts:
                        logger.exception("Max async retry attempts reached for %s", fn.__name__)
                        raise
                    await asyncio.sleep(base_delay * (2 ** (attempts - 1)))
        return wrapped
    return deco

# --- Exceptions ---
class TransientAPIError(Exception):
    pass

class ModerationError(Exception):
    pass

# --- LLM Adapter Interface (keeps underlying llm swappable) ---
class BaseLLMAdapter:
    def invoke(self, prompt: str) -> Any:
        raise NotImplementedError

    async def astream(self, prompt: str):
        raise NotImplementedError

    def get_model_name(self) -> str:
        raise NotImplementedError

# --- Concrete adapter for ChatOpenAI used previously ---
class ChatOpenAIAdapter(BaseLLMAdapter):
    def __init__(self, llm_instance: ChatOpenAI):
        self.llm = llm_instance

    @retry_on_exception(max_attempts=3, base_delay=0.8, exceptions=(TransientAPIError, Exception))
    def invoke(self, prompt: str):
        # Expect llm.invoke to return an object with .content
        try:
            res = self.llm.invoke(prompt)
            return res
        except Exception as e:
            # Map known transient errors if possible
            raise

    @aretry_on_exception(max_attempts=2, base_delay=0.5, exceptions=(TransientAPIError, Exception))
    async def astream(self, prompt: str):
        # Expect llm.astream to be an async generator yielding chunk objects with .content
        async for chunk in self.llm.astream(prompt):
            yield chunk

    def get_model_name(self) -> str:
        return getattr(self.llm, "model", "unknown")

# --- Memory persistence optional (Redis-backed) ---
class MemoryStore:
    def __init__(self, redis_url: Optional[str] = None, prefix: str = "llm:mem:"):
        self.prefix = prefix
        self.enabled = False
        self._client = None
        if redis_url and redis:
            try:
                self._client = redis.from_url(redis_url, decode_responses=True)
                self.enabled = True
            except Exception as e:
                logger.warning("Redis init failed: %s. Falling back to in-memory store.", e)
                self.enabled = False
        self._in_memory = {}

    def _key(self, session_id: str) -> str:
        return f"{self.prefix}{session_id}"

    def get(self, session_id: str) -> List[Dict]:
        if self.enabled:
            data = self._client.get(self._key(session_id))
            if not data:
                return []
            import json
            return json.loads(data)
        return self._in_memory.get(session_id, []).copy()

    def set(self, session_id: str, messages: List[Dict]) -> None:
        if self.enabled:
            import json
            self._client.set(self._key(session_id), json.dumps(messages))
        else:
            self._in_memory[session_id] = messages.copy()

    def clear(self, session_id: str) -> None:
        if self.enabled:
            self._client.delete(self._key(session_id))
        else:
            self._in_memory.pop(session_id, None)

# --- Moderation hook (placeholder) ---
def moderate_text(text: str) -> bool:
    # TODO: integrate with real moderation API; return True if allowed, False if blocked
    blocked_terms = os.getenv("LLM_BLOCKED_TERMS", "").split(",")
    for t in blocked_terms:
        if t and t.strip().lower() in text.lower():
            return False
    return True

# --- Vector retrieval hook (placeholder) ---
def default_retriever(query: str, k: int = 5) -> List[Document]:
    # TODO: integrate with real vector DB and reranker
    return []

# --- Main LLMService class (public API unchanged) ---
class LLMService:
    """
    Upgraded LLMService with improved robustness and extensibility while keeping public APIs.
    """

    def __init__(
        self,
        open_ai_base_url: str,
        openai_api_key: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        memory_window: int = 10,
        streaming: bool = True,
        max_prompt_tokens: int = 4000,
        redis_url: Optional[str] = None,
        session_id_getter: Optional[Callable[[], str]] = None,
        retriever: Optional[Callable[[str, int], List[Document]]] = None,
        moderation_hook: Optional[Callable[[str], bool]] = None
    ):
        """
        Keep constructor signature compatible but add optional integrations.
        session_id_getter: callable returning a session/user identifier for per-session memory persistence.
        retriever: function(query, k) -> List[Document]
        moderation_hook: function(text)->bool
        """
        # basic config
        self.model = model
        self.temperature = temperature
        self.memory_window = memory_window
        self.max_prompt_tokens = max_prompt_tokens

        # Validate env-based API key usage
        if not openai_api_key:
            raise ValueError("openai_api_key must be provided via env or parameter")
        self.openai_api_key = openai_api_key
        self.open_ai_base_url = open_ai_base_url

        # Initialize underlying llm instance as before
        self.llm = ChatOpenAI(
            base_url=self.open_ai_base_url,
            model=self.model,
            temperature=self.temperature,
            streaming=streaming,
            openai_api_key=self.openai_api_key
        )
        self.adapter = ChatOpenAIAdapter(self.llm)

        # in-memory chat history (default, per-process)
        self.chat_history: List[Dict] = []

        # memory persistence
        self.memory_store = MemoryStore(redis_url=redis_url)
        self.session_id_getter = session_id_getter or (lambda: "default-session")

        # retriever and moderation
        self.retriever = retriever or default_retriever
        self.moderation_hook = moderation_hook or moderate_text

        # streaming control
        self._active_stream_tasks: Dict[str, asyncio.Task] = {}

        logger.info("LLMService initialized: model=%s, streaming=%s", self.model, streaming)

    # --- Prompt building (unchanged API) ---
    def build_prompt(
        self,
        system_message: Optional[str] = None
    ) -> ChatPromptTemplate:
        """
        Build a chat prompt template with system message and memory.
        
        Args:
            system_message: Optional custom system message
            
        Returns:
            ChatPromptTemplate: Configured prompt template
        """
        default_system = """You are a helpful AI assistant with access to a comprehensive knowledge base.

Your role is to:
- Answer questions based on the knowledge base using the search tool
- Provide accurate, detailed, and well-structured responses
- If the user, use the wrong syntax word, try to find the word have the same meaning about 80% and repeat with the correct word
- Cite sources when possible
- Be conversational and helpful
- Show the whitelist tool of project in Whitelist
- Answer the question base on the asker role in project
- Try to summarize all the knowledge you know and answer in an human answer, do not you to must syntax.
- If you don't find relevant information, say so honestly

Always use the knowledge_base_search tool to find relevant information before answering."""
        system = system_message or default_system

        prompt = ChatPromptTemplate.from_messages([
            ("system", system),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        return prompt

    def build_context_prompt(
        self,
        query: str,
        context_docs: List[Document]
    ) -> str:
        """
        Build a prompt with retrieved context for non-agent workflows.
        
        Args:
            query: User query
            context_docs: Retrieved documents for context
            
        Returns:
            str: Formatted prompt with context
        """
        context = "\n\n".join([
            f"Source: {doc.metadata.get('source', 'Unknown')}\n{doc.page_content}"
            for doc in context_docs
        ])
        prompt = f"""Based on the following context, answer the question.

Context:
{context}

Question: {query}

Answer:"""
        return prompt

    # --- Internal helpers ---
    def _get_session_id(self) -> str:
        try:
            return self.session_id_getter()
        except Exception:
            return "default-session"

    def _append_memory(self, role: str, content: str) -> None:
        session_id = self._get_session_id()
        entry = {"role": role, "content": content, "timestamp": time.time()}
        self.chat_history.append(entry)
        # respect memory window
        if len(self.chat_history) > self.memory_window:
            self.chat_history = self.chat_history[-self.memory_window:]
        # persist
        try:
            existing = self.memory_store.get(session_id)
            existing.append(entry)
            if len(existing) > self.memory_window:
                existing = existing[-self.memory_window:]
            self.memory_store.set(session_id, existing)
        except Exception as e:
            logger.debug("Memory persistence skipped: %s", e)

    def _get_memory_messages(self) -> List[Dict]:
        session_id = self._get_session_id()
        persisted = self.memory_store.get(session_id) or []
        # Merge (persisted as source of truth)
        # Keep in-memory for quick usage too
        return persisted

    def _enforce_token_limit(self, prompt: str) -> str:
        prompt_tokens = simple_token_count(prompt)
        if prompt_tokens <= self.max_prompt_tokens:
            return prompt
        logger.warning("Prompt tokens (%d) exceed max (%d). Truncating context.", prompt_tokens, self.max_prompt_tokens)
        return truncate_by_tokens(prompt, self.max_prompt_tokens)

    # --- Moderation check ---
    def _moderate(self, text: str) -> None:
        allowed = self.moderation_hook(text)
        if not allowed:
            logger.warning("Content blocked by moderation.")
            raise ModerationError("Input blocked by moderation policy")

    # --- Public API: generate non-streaming (keeps same signature) ---
    def generate_answer(
        self,
        query: str,
        context_docs: Optional[List[Document]] = None
    ) -> str:
        session_id = self._get_session_id()
        logger.info("generate_answer called, session=%s", session_id)
        if REQUEST_COUNTER:
            REQUEST_COUNTER.inc()
        start = time.time()
        try:
            # moderation of input
            self._moderate(query)

            # If no explicit context docs, do retrieval (RAG)
            used_context = context_docs
            if not used_context:
                try:
                    used_context = self.retriever(query, k=5)
                except Exception as e:
                    logger.debug("Retriever failed: %s", e)
                    used_context = []

            if used_context:
                prompt = self.build_context_prompt(query, used_context)
            else:
                prompt = query

            # add memory to prompt if available
            memory_msgs = self._get_memory_messages()
            if memory_msgs:
                mem_text = "\n".join([f"{m['role']}: {m['content']}" for m in memory_msgs])
                prompt = f"Conversation history:\n{mem_text}\n\n{prompt}"

            # enforce token limits
            prompt = self._enforce_token_limit(prompt)

            # call llm (wrapped)
            res = self.adapter.invoke(prompt)
            # Some adapters return object with .content; try to be robust
            content = getattr(res, "content", res if isinstance(res, str) else str(res))

            # post-moderation of output
            if not self.moderation_hook(content):
                raise ModerationError("Model output blocked by moderation")

            # append memory
            self._append_memory("user", query)
            self._append_memory("assistant", content)

            return content
        finally:
            if REQUEST_LATENCY:
                REQUEST_LATENCY.observe(time.time() - start)

    # --- Public API: streaming (keeps same signature) ---
    async def generate_answer_stream(
        self,
        query: str,
        context_docs: Optional[List[Document]] = None
    ) -> AsyncGenerator[str, None]:
        session_id = self._get_session_id()
        logger.info("generate_answer_stream called, session=%s", session_id)
        if REQUEST_COUNTER:
            REQUEST_COUNTER.inc()
        start = time.time()
        # moderation of input
        self._moderate(query)

        used_context = context_docs
        if not used_context:
            try:
                used_context = self.retriever(query, k=5)
            except Exception as e:
                logger.debug("Retriever failed: %s", e)
                used_context = []

        if used_context:
            prompt = self.build_context_prompt(query, used_context)
        else:
            prompt = query

        memory_msgs = self._get_memory_messages()
        if memory_msgs:
            mem_text = "\n".join([f"{m['role']}: {m['content']}" for m in memory_msgs])
            prompt = f"Conversation history:\n{mem_text}\n\n{prompt}"

        prompt = self._enforce_token_limit(prompt)

        # create a cancellation token via task tracking
        task = asyncio.current_task()
        task_id = f"{session_id}:{id(task)}"
        self._active_stream_tasks[task_id] = task

        buffer = []
        try:
            async for chunk in self.adapter.astream(prompt):
                # chunk may be object with .content or str
                content = getattr(chunk, "content", chunk if isinstance(chunk, str) else str(chunk))
                if not content:
                    continue
                # optionally post-moderate partial chunks (cheap heuristic)
                if not self.moderation_hook(content):
                    logger.warning("Stream chunk blocked by moderation. Cancelling stream.")
                    raise ModerationError("Stream output blocked by moderation")
                buffer.append(content)
                yield content
            # after stream completes, join and persist to memory
            full = "".join(buffer)
            self._append_memory("user", query)
            self._append_memory("assistant", full)
        finally:
            self._active_stream_tasks.pop(task_id, None)
            if REQUEST_LATENCY:
                REQUEST_LATENCY.observe(time.time() - start)

    # --- Allow external cancellation of active stream by session id (optional) ---
    def cancel_streams_for_session(self, session_id: str) -> int:
        canceled = 0
        keys = [k for k in self._active_stream_tasks.keys() if k.startswith(f"{session_id}:")]
        for k in keys:
            t = self._active_stream_tasks.get(k)
            if t and not t.done():
                t.cancel()
                canceled += 1
        return canceled

    # --- Public accessors (unchanged signatures) ---
    def get_llm_instance(self) -> ChatOpenAI:
        return self.llm

    def get_memory_instance(self) -> List:
        # return merged persisted memory for current session
        try:
            return self._get_memory_messages()
        except Exception:
            return self.chat_history

    def clear_memory(self) -> None:
        session_id = self._get_session_id()
        self.chat_history.clear()
        try:
            self.memory_store.clear(session_id)
        except Exception as e:
            logger.debug("Memory clear failed: %s", e)

    def get_stats(self) -> dict:
        # We don't expose tokens by default for privacy, but include config
        return {
            "model": self.model,
            "temperature": self.temperature,
            "memory_window": self.memory_window,
            "provider": "OpenAI",
            "max_prompt_tokens": self.max_prompt_tokens,
            "memory_persisted": self.memory_store.enabled
        }

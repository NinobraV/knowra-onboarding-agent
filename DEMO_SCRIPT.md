"""
Script to generate presentation markdown for RAG Onboarding AI-Agent project
"""

def create_presentation_markdown():
    content = """# Script Thuyết Trình: RAG Onboarding AI-Agent

## 1. GIỚI THIỆU DỰ ÁN

Xin chào mọi người, hôm nay tôi xin trình bày về dự án **RAG Onboarding AI-Agent** - một hệ thống chatbot thông minh giúp nhân viên mới onboarding nhanh chóng thông qua việc truy vấn tài liệu công ty.

---

## 2. TECHSTACK

### 2.1 Backend
- **FastAPI**: Framework web hiện đại, hiệu suất cao cho Python
- **LangChain**: Framework để xây dựng ứng dụng LLM
- **OpenAI GPT-4o-mini**: Large Language Model chính
- **MongoDB**: Database NoSQL lưu trữ sessions và chat history
- **Redis**: In-memory cache cho short-term memory
- **FAISS/ChromaDB**: Vector store để lưu embeddings
- **Sentence Transformers**: Tạo embeddings từ text

### 2.2 Frontend
- **React 18**: UI library
- **Vite**: Build tool nhanh
- **Axios**: HTTP client
- **CSS Modules**: Styling

### 2.3 Infrastructure
- **Docker**: Containerization
- **Prometheus**: Metrics collection (optional)

---

## 3. KIẾN TRÚC TỔNG QUAN

```
User → Frontend (React) → Backend (FastAPI) → LLM Service
                                ↓
                          Vector Store (FAISS)
                                ↓
                          MongoDB (Chat History)
                                ↓
                          Redis (Short-term Memory)
```

---

## 4. FLOW HOẠT ĐỘNG CHI TIẾT

### 4.1 Initialization Flow

**Bước 1: Khởi động Backend**
```python
# main.py
app = FastAPI(title="OnboardingAI Backend")
```
- Khởi tạo FastAPI application
- Load config từ environment variables
- Setup CORS để frontend có thể gọi API

**Bước 2: Initialize Services**
```python
# dependencies.py
def get_rag_service():
    if not rag_service_instance:
        init_rag_service()
    return rag_service_instance
```
- Singleton pattern cho RAG service
- Tránh khởi tạo nhiều lần

**Bước 3: Load Documents & Create Embeddings**
```python
# vector_store_service.py
def load_documents(self, directory: str):
    # Load markdown files
    # Split into chunks
    # Create embeddings
    # Store in FAISS
```

### 4.2 Query Flow (Chi tiết từng bước)

**Bước 1: User gửi query**
```javascript
// Frontend: useChat.js
const sendMessage = async (message) => {
    const response = await apiService.sendMessage(sessionId, message);
}
```

**Bước 2: API Endpoint nhận request**
```python
# routes.py
@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    result = await rag_service.query(
        session_id=request.session_id,
        query=request.message
    )
```

**Bước 3: RAG Pipeline Processing**

**3.1. Safety Check**
```python
# safety_service.py
def check_safety(self, text: str) -> SafetyResult:
    # Kiểm tra prompt injection
    # Kiểm tra toxic content
    # Return SafetyResult
```
**Tại sao?** Bảo vệ hệ thống khỏi các input độc hại

**3.2. Moderation**
```python
# llm_service.py
def _moderate(self, text: str):
    allowed = self.moderation_hook(text)
    if not allowed:
        raise ModerationError()
```
**Tại sao?** Lọc nội dung không phù hợp trước khi xử lý

**3.3. Semantic Search**
```python
# semantic_search_service.py
def search(self, query: str, k: int = 5):
    # Tạo query embedding
    query_embedding = self.embedding_service.embed_query(query)
    
    # Search trong vector store
    results = self.vector_store.similarity_search_with_score(
        query_embedding, k=k
    )
    return results
```
**Tại sao k=5?** Balance giữa context quality và token limit

**3.4. Retrieve Context**
```python
# vector_store_service.py
def similarity_search_with_score(self, query: str, k: int = 5):
    # FAISS tìm k documents gần nhất
    docs = self.vectorstore.similarity_search_with_score(query, k=k)
    return docs
```

**3.5. Ranking & Reranking**
```python
# ranking_service.py
def rerank_documents(self, query: str, documents: List):
    # Tính relevance score cho mỗi doc
    # Sắp xếp theo score giảm dần
    # Return top documents
```
**Tại sao rerank?** Vector search không luôn đúng, cần semantic scoring

**3.6. Memory Integration**

**3.6.1. Short-term Memory (Redis)**
```python
# llm_service.py - MemoryStore
def get(self, session_id: str) -> List[Dict]:
    if self.enabled:
        data = self._client.get(f"{self.prefix}{session_id}")
        return json.loads(data)
```
**Tại sao Redis?** 
- Fast in-memory access
- TTL cho session expiry
- Fallback to in-memory nếu Redis down

**3.6.2. Long-term Memory (MongoDB)**
```python
# chat_persistence_service.py
def save_message(self, session_id: str, message: dict):
    self.messages_collection.insert_one({
        "session_id": session_id,
        "message": message,
        "timestamp": datetime.utcnow()
    })
```
**Tại sao MongoDB?**
- Document-oriented phù hợp với chat data
- Flexible schema
- Good for historical queries

**3.7. Prompt Construction**
```python
# llm_service.py
structured_prompt = f\"\"\"You are OnboardingAI...

Rules:
- Provide accurate, concise answers
- Never hallucinate
- Use previous messages for continuity

Conversation context:
{context_text}

Previous conversation:
{message_history_text}

User question: {query}

Instructions: Provide a helpful and direct answer.\"\"\"
```

**Tại sao structured prompt?**
- Giúp LLM hiểu rõ vai trò
- Context được tổ chức rõ ràng
- Instructions cụ thể tránh hallucination

**3.8. Token Limit Enforcement**
```python
def _enforce_token_limit(self, prompt: str) -> str:
    if prompt_tokens > self.max_prompt_tokens:
        # Intelligent truncation
        # Priority: System > Query > Context > History
```
**Tại sao max_prompt_tokens=4000?**
- GPT-4o-mini context window: 128K tokens
- Reserve tokens cho response
- Cost optimization

**3.9. LLM Generation**
```python
# llm_service.py
def generate_answer(self, query: str):
    res = self.adapter.invoke(structured_prompt)
    content = res.content
    
    # Post-moderation
    if not self.moderation_hook(content):
        raise ModerationError()
    
    # Append to memory
    self._append_memory("user", query)
    self._append_memory("assistant", content)
```

**3.10. Response Streaming**
```python
async def generate_answer_stream(self, query: str):
    async for chunk in self.adapter.astream(prompt):
        yield chunk
```
**Tại sao streaming?** Better UX, user thấy response real-time

**Bước 4: Return Response**
```python
# routes.py
return ChatResponse(
    session_id=session_id,
    response=result["response"],
    metadata=result["metadata"]
)
```

---

## 5. CẤU HÌNH CHI TIẾT CÁC MODULE

### 5.1 LLM Service Configuration

```python
# llm_service.py - __init__
def __init__(
    self,
    model: str = "gpt-4o-mini",           # Model nhỏ, nhanh, rẻ
    temperature: float = 0.7,              # Balance creativity vs consistency
    memory_window: int = 10,               # Giữ 10 messages gần nhất
    streaming: bool = True,                # Enable streaming
    max_prompt_tokens: int = 4000,         # Token limit
    redis_url: Optional[str] = None,       # Redis connection
    session_id_getter: Optional[Callable] = None,
    retriever: Optional[Callable] = None,
    moderation_hook: Optional[Callable] = None
):
```

**Giải thích từng tham số:**

1. **model="gpt-4o-mini"**
   - Tại sao? Cost-effective, đủ cho onboarding tasks
   - Alternative: gpt-4-turbo cho complex reasoning

2. **temperature=0.7**
   - 0.0 = deterministic, 1.0 = creative
   - 0.7 = balanced cho Q&A
   - Tại sao không 0.0? Cần flexibility trong cách trả lời

3. **memory_window=10**
   - Giữ 10 messages gần nhất
   - Tại sao? Balance context vs token cost
   - Older messages vẫn trong MongoDB cho analytics

4. **streaming=True**
   - Server-Sent Events (SSE)
   - Better UX: progressive response
   - User không phải chờ full response

5. **max_prompt_tokens=4000**
   - Reserve ~3000 tokens cho response
   - Prevent context overflow
   - Cost optimization

### 5.2 Vector Store Configuration

```python
# vector_store_service.py
class VectorStoreService:
    def __init__(
        self,
        persist_directory: str = ".vectorstore",
        collection_name: str = "onboarding_docs",
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ):
```

**Giải thích:**

1. **persist_directory=".vectorstore"**
   - Local file storage cho FAISS index
   - Tại sao? Không cần rebuild index mỗi lần restart

2. **collection_name="onboarding_docs"**
   - Logical grouping
   - Multiple collections có thể cho different doc types

3. **embedding_model="all-MiniLM-L6-v2"**
   - Fast, lightweight (80MB)
   - Good balance: speed vs quality
   - 384 dimensions
   - Alternative: "all-mpnet-base-v2" (more accurate, slower)

### 5.3 Chunking Configuration

```python
# chunking_service.py
class ChunkingService:
    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        separators: List[str] = ["\\n\\n", "\\n", ". ", " "]
    ):
```

**Giải thích:**

1. **chunk_size=512**
   - Sweet spot cho semantic coherence
   - Tại sao không 1000? Quá dài, loss of focus
   - Tại sao không 200? Quá ngắn, mất context

2. **chunk_overlap=50**
   - Prevent information loss at boundaries
   - 50 tokens = ~10% overlap
   - Tại sao? Câu bị cắt vẫn có context

3. **separators=["\\n\\n", "\\n", ". ", " "]**
   - Priority-based splitting
   - Ưu tiên: paragraph > line > sentence > word
   - Tại sao? Preserve semantic boundaries

### 5.4 Semantic Search Configuration

```python
# semantic_search_service.py
def search(
    self,
    query: str,
    k: int = 5,                    # Top K results
    score_threshold: float = 0.7,  # Minimum relevance
    metadata_filters: dict = None
):
```

**Giải thích:**

1. **k=5**
   - Balance: quality vs context length
   - Tại sao không 10? Too much noise
   - Tại sao không 3? Miss relevant context

2. **score_threshold=0.7**
   - Cosine similarity threshold
   - 0.7 = reasonably relevant
   - Tại sao? Filter out irrelevant results

### 5.5 Safety Service Configuration

```python
# safety_service.py
class SafetyService:
    PROMPT_INJECTION_PATTERNS = [
        r"ignore previous instructions",
        r"system:",
        r"<\\|im_start\\|>",
    ]
    
    MAX_QUERY_LENGTH = 2000
    MAX_REPETITION_RATIO = 0.5
```

**Giải thích:**

1. **PROMPT_INJECTION_PATTERNS**
   - Regex patterns cho common attacks
   - "ignore previous" = jailbreak attempt
   - "system:" = role confusion attack

2. **MAX_QUERY_LENGTH=2000**
   - Prevent DOS attacks
   - 2000 chars = ~400 tokens
   - Reasonable cho most questions

3. **MAX_REPETITION_RATIO=0.5**
   - Detect spam/abuse
   - 50% repeated chars = suspicious

### 5.6 Retry Configuration

```python
# llm_service.py
@retry_on_exception(
    max_attempts=3,
    base_delay=0.8,
    exceptions=(TransientAPIError, Exception)
)
def invoke(self, prompt: str):
```

**Giải thích:**

1. **max_attempts=3**
   - Tại sao 3? Balance reliability vs latency
   - Most transient errors resolve sau 1-2 retries

2. **base_delay=0.8**
   - Exponential backoff: 0.8s, 1.6s, 3.2s
   - Tại sao? Give API time to recover

### 5.7 Memory Persistence

```python
# chat_persistence_service.py
class ChatPersistenceService:
    def __init__(self, ttl_days: int = 30):
        self.ttl_seconds = ttl_days * 24 * 60 * 60
```

**Giải thích:**

1. **ttl_days=30**
   - Auto-cleanup old sessions
   - Tại sao 30? Balance storage vs analytics needs
   - GDPR compliance consideration

### 5.8 Intelligent Truncation Strategy

```python
# llm_service.py
def _truncate_simple_structured_prompt(self, prompt: str) -> str:
    # Priority: Instructions (keep) > User question (keep) 
    #           > Context (truncate) > History (truncate)
    
    # Allocate: 70% to context, 30% to history
    context_budget = int(available_tokens * 0.7)
    history_budget = int(available_tokens * 0.3)
```

**Tại sao 70/30 split?**
- Context (documents) quan trọng hơn cho accuracy
- History cần thiết cho continuity nhưng có thể summarize
- System instructions và query không bao giờ truncate

---

## 6. ERROR HANDLING & MONITORING

### 6.1 Error Handling Strategy

```python
try:
    result = await rag_service.query(query)
except ModerationError:
    return {"error": "Content blocked"}
except TransientAPIError:
    # Auto-retry handled
    pass
except Exception as e:
    logger.exception("Unexpected error")
    return {"error": "Internal error"}
```

### 6.2 Monitoring

```python
# Optional Prometheus metrics
REQUEST_COUNTER = Counter("llm_requests_total")
REQUEST_LATENCY = Histogram("llm_request_latency_seconds")
```

**Tại sao?**
- Track usage patterns
- Performance monitoring
- Cost analysis

---

## 7. DEPLOYMENT CONSIDERATIONS

### 7.1 Docker Configuration

```dockerfile
# Backend Dockerfile
FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 7.2 Environment Variables

```bash
# Backend .env
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://api.openai.com/v1
MONGODB_URL=mongodb://localhost:27017
REDIS_URL=redis://localhost:6379
LLM_MODEL=gpt-4o-mini
MEMORY_WINDOW=10
MAX_PROMPT_TOKENS=4000
```

---

## 8. PERFORMANCE OPTIMIZATIONS

1. **Caching**: Redis cho short-term memory
2. **Batch Processing**: Embed multiple docs at once
3. **Connection Pooling**: MongoDB, Redis connections
4. **Lazy Loading**: Initialize services on-demand
5. **Streaming**: Progressive response rendering

---

## 9. SECURITY MEASURES

1. **Input Validation**: Safety service checks
2. **Output Moderation**: Post-generation filtering
3. **Rate Limiting**: Prevent abuse
4. **API Key Management**: Environment variables
5. **CORS Configuration**: Whitelist frontend origin

---

## 10. KEY DESIGN DECISIONS

### 10.1 Adapter Pattern cho LLM
```python
class BaseLLMAdapter:
    def invoke(self, prompt: str) -> Any
    async def astream(self, prompt: str)
```
**Tại sao?**
- Easy to swap LLM providers (OpenAI → Anthropic → Local)
- Consistent interface
- Testability

### 10.2 Two-Tier Memory
- **Short-term (Redis)**: Fast access, recent context
- **Long-term (MongoDB)**: Historical data, analytics

**Tại sao không chỉ 1?**
- Performance vs Persistence tradeoff
- Redis down → fallback to in-memory
- MongoDB cho audit trail

### 10.3 Moderation Hook Pattern
```python
def moderation_hook(text: str) -> bool:
    # Pluggable moderation logic
```
**Tại sao?**
- Pre và post moderation
- Customizable per deployment
- Compliance requirements

---

## 11. FRONTEND ARCHITECTURE

### 11.1 Component Structure
```
App.jsx
├── Header
├── SessionManager
├── WelcomeScreen
├── MessageList
│   └── ChatMessage
├── ChatInput
├── StatusBar
└── ErrorBanner
```

### 11.2 Custom Hooks
```javascript
// useChat.js
const { messages, sendMessage, loading } = useChat(sessionId);

// useSessionManager.js
const { sessionId, sessions, createSession } = useSessionManager();

// useHealthCheck.js
const { status } = useHealthCheck();
```

**Tại sao custom hooks?**
- Separation of concerns
- Reusability
- Easier testing

---

## 12. API ENDPOINTS

```python
# Health check
GET /health

# Chat
POST /chat
{
  "session_id": "uuid",
  "message": "What is the onboarding process?"
}

# Session management
POST /sessions/create
GET /sessions/{session_id}
GET /sessions/{session_id}/history
DELETE /sessions/{session_id}
```

---

## 13. FUTURE ENHANCEMENTS

1. **Multi-modal RAG**: Images, PDFs, videos
2. **Advanced routing**: Question classification → specialized models
3. **Fine-tuning**: Domain-specific knowledge
4. **Analytics Dashboard**: Usage metrics, popular queries
5. **Multi-language**: i18n support
6. **Voice interface**: Speech-to-text integration
7. **Feedback loop**: User ratings → model improvement

---

## 14. LESSONS LEARNED

### 14.1 Token Management is Critical
- Always enforce limits
- Intelligent truncation > simple truncation
- Monitor costs closely

### 14.2 Memory Management
- Short-term + Long-term = Best of both worlds
- Redis fallback essential for reliability
- Window size affects quality significantly

### 14.3 Safety First
- Pre-moderation prevents wasted API calls
- Post-moderation ensures output quality
- Multiple layers of defense

### 14.4 Streaming Improves UX
- Users perceive faster response
- Must handle connection drops
- Cancel mechanism important

---

## 15. METRICS & KPIs

### 15.1 Technical Metrics
- **Latency**: P50, P95, P99 response times
- **Token usage**: Average per query
- **Cache hit rate**: Redis efficiency
- **Error rate**: 4xx, 5xx responses

### 15.2 Business Metrics
- **User engagement**: Sessions per user
- **Query success rate**: Helpful vs not helpful
- **Time to answer**: Employee onboarding speed
- **Cost per query**: API + infrastructure costs

---

## 16. TESTING STRATEGY

### 16.1 Unit Tests
```python
def test_token_truncation():
    prompt = "x" * 10000
    truncated = llm_service._enforce_token_limit(prompt)
    assert simple_token_count(truncated) <= 4000
```

### 16.2 Integration Tests
```python
async def test_full_rag_pipeline():
    result = await rag_service.query("test query")
    assert "response" in result
    assert "metadata" in result
```

### 16.3 End-to-End Tests
- Selenium for UI testing
- Load testing with Locust
- Chaos engineering (Redis down scenario)

---

## KẾT LUẬN

RAG Onboarding AI-Agent là một hệ thống production-ready với:
- ✅ Robust error handling
- ✅ Scalable architecture
- ✅ Memory management
- ✅ Security measures
- ✅ Performance optimizations
- ✅ Comprehensive configuration
- ✅ Monitoring & observability

**Key Takeaways:**
1. **RAG = Better accuracy** than pure LLM
2. **Memory = Better continuity** in conversations
3. **Safety = Production requirement**, not optional
4. **Monitoring = Continuous improvement** path
5. **Configuration = Flexibility** for different use cases

**Success Factors:**
- Clear separation of concerns
- Pluggable architecture
- Comprehensive error handling
- Intelligent resource management
- User-centric design

---

**Q&A**

Cảm ơn mọi người đã lắng nghe!

---

## PHỤ LỤC: TROUBLESHOOTING GUIDE

### A.1 Common Issues

**Issue**: Redis connection failed
- **Solution**: System falls back to in-memory storage
- **Impact**: No persistence across restarts

**Issue**: Token limit exceeded
- **Solution**: Intelligent truncation applied automatically
- **Impact**: Some context may be lost

**Issue**: LLM API rate limit
- **Solution**: Exponential backoff retry (3 attempts)
- **Impact**: Slight delay in response

### A.2 Performance Tuning

1. **Adjust memory_window**: Lower = faster, less context
2. **Tune chunk_size**: Smaller = more precise, more searches
3. **Modify k parameter**: Higher = more context, slower
4. **Optimize embeddings**: Switch model based on needs

---

## PHỤ LỤC: CONFIGURATION REFERENCE

### B.1 All Environment Variables

```bash
# LLM Configuration
OPENAI_API_KEY=required
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7
MEMORY_WINDOW=10
MAX_PROMPT_TOKENS=4000
LLM_STREAMING=true

# Vector Store
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
VECTOR_STORE_DIR=.vectorstore
CHUNK_SIZE=512
CHUNK_OVERLAP=50

# Memory & Persistence
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=onboarding_ai
REDIS_URL=redis://localhost:6379
SESSION_TTL_DAYS=30

# Search Configuration
SEARCH_TOP_K=5
SEARCH_SCORE_THRESHOLD=0.7

# Safety
MAX_QUERY_LENGTH=2000
MAX_REPETITION_RATIO=0.5
BLOCKED_TERMS=comma,separated,list

# Server
HOST=0.0.0.0
PORT=8000
WORKERS=4
LOG_LEVEL=INFO

# Frontend
VITE_API_URL=http://localhost:8000
VITE_APP_TITLE=OnboardingAI
```

### B.2 Performance Tuning Matrix

| Use Case | memory_window | chunk_size | k | max_tokens |
|----------|---------------|------------|---|------------|
| Fast Response | 5 | 256 | 3 | 2000 |
| Balanced | 10 | 512 | 5 | 4000 |
| Max Context | 20 | 1024 | 10 | 8000 |
| Cost Optimized | 5 | 512 | 3 | 2000 |

---

## TÀI LIỆU THAM KHẢO

1. **LangChain Documentation**: https://python.langchain.com/
2. **OpenAI API Reference**: https://platform.openai.com/docs/
3. **FastAPI Documentation**: https://fastapi.tiangolo.com/
4. **React Documentation**: https://react.dev/
5. **RAG Papers**: 
   - "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"
   - "Self-RAG: Learning to Retrieve, Generate, and Critique"
"""
    
    # Write to file
    output_path = "/Users/tuantran/Documents/Elevate_AI_FPT_Couse/final_proj/PRESENTATION_SCRIPT.md"
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Successfully created presentation script at: {output_path}")
        print(f"📄 File size: {len(content)} characters")
        print(f"📝 Total sections: 16 main sections + appendices")
    except Exception as e:
        print(f"❌ Error creating file: {e}")

if __name__ == "__main__":
    create_presentation_markdown()
# MongoDB Chat History Migration Guide

This guide explains the new MongoDB-backed chat history architecture and how to migrate from the previous Redis-only implementation.

## Overview

The application now uses a **dual-storage architecture**:

- **MongoDB**: Persistent storage for chat sessions and message history
- **Redis** (optional): Short-term session metadata and caching
- **Vector Store** (Pinecone/Local): Document embeddings and semantic search (unchanged)

## Architecture Changes

### Before (Redis-only)
```
┌─────────────┐
│   Frontend  │
└──────┬──────┘
       │
┌──────▼──────────────┐
│   FastAPI Backend   │
├─────────────────────┤
│  Session Service    │◄────► Redis (session metadata)
│  RAG Service        │◄────► Vector Store (embeddings)
│  Memory Service     │◄────► Redis (short-term memory)
└─────────────────────┘
```

### After (MongoDB + Redis)
```
┌─────────────┐
│   Frontend  │
└──────┬──────┘
       │
┌──────▼──────────────┐
│   FastAPI Backend   │
├─────────────────────┤
│  Session Service    │◄────► Redis (optional, metadata)
│  RAG Service        │◄────► Vector Store (embeddings)
│  Persistence Svc    │◄────► MongoDB (sessions + messages)
│  Memory Service     │◄────► Redis (short-term memory)
└─────────────────────┘
```

## MongoDB Collections

### 1. `chat_sessions` Collection

Stores session metadata with automatic title generation.

**Schema:**
```javascript
{
  _id: "session-abc-123",           // Session ID
  user_id: "user-123",               // Optional user identifier
  project_id: "project-onboarding",  // Project scope
  title: "Questions about onboarding", // Auto-generated title
  message_count: 25,                 // Number of messages
  metadata: {},                      // Additional metadata
  created_at: ISODate("2025-11-14T12:00:00Z"),
  updated_at: ISODate("2025-11-14T13:30:00Z")
}
```

**Indexes:**
- `user_id` (ascending)
- `project_id` (ascending)
- `(user_id, project_id)` (compound)
- `updated_at` (descending) - for recent sessions
- `created_at` (descending)

### 2. `chat_messages` Collection

Stores all chat messages with RAG metadata.

**Schema:**
```javascript
{
  _id: "msg-abc-123",                // Message ID
  session_id: "session-abc-123",     // Parent session
  role: "assistant",                 // "user" or "assistant"
  content: "The onboarding process...", // Message text
  sources: [                         // Retrieved documents
    {
      id: "doc_123",
      score: 0.89,
      text: "Excerpt...",
      metadata: {
        source: "01_ONBOARDING_GUIDE.md",
        section: "Overview"
      }
    }
  ],
  routing_info: {                    // RAG routing decision
    decision: "kb_and_memory",
    confidence: 0.85
  },
  safety_info: {                     // Safety analysis
    level: "safe"
  },
  tokens: 150,                       // Token count
  metadata: {},                      // Additional metadata
  created_at: ISODate("2025-11-14T12:00:30Z")
}
```

**Indexes:**
- `(session_id, created_at)` (compound) - **most important for pagination**
- `session_id` (ascending)
- `created_at` (descending)
- `role` (ascending) - optional

## Installation & Setup

### 1. Install Dependencies

```bash
cd backend
pip install motor==3.6.0 pymongo==4.10.1
```

### 2. Start MongoDB

#### Option A: Local MongoDB (Docker)
```bash
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=password \
  -v mongodb_data:/data/db \
  mongo:7.0
```

#### Option B: MongoDB Atlas (Cloud)
1. Create free cluster at https://cloud.mongodb.com
2. Get connection string
3. Add to `.env` file

### 3. Configure Environment Variables

Add to your `.env` file:

```bash
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=knowra_chatbot
MONGODB_MAX_POOL_SIZE=10
MONGODB_MIN_POOL_SIZE=1
MONGODB_TIMEOUT_MS=5000

# Redis (optional - for session metadata caching)
REDIS_URL=redis://localhost:6379/0
```

For MongoDB Atlas:
```bash
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
```

### 4. Verify Installation

Start the backend:
```bash
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Check logs for:
```
📦 Initializing MongoDB...
✅ MongoDB initialized successfully
Created indexes on chat_sessions collection
Created indexes on chat_messages collection
```

## Migration Strategies

### Strategy 1: Fresh Start (Recommended)

**When to use:**
- Development/testing environment
- No critical existing data
- Want clean slate with new architecture

**Steps:**
1. Install MongoDB and dependencies
2. Update `.env` with MongoDB settings
3. Start application - collections and indexes created automatically
4. Previous Redis sessions remain but are separate from MongoDB history

**Pros:**
- Simple, no data migration needed
- Clean separation of old and new data
- Immediate access to all new features

**Cons:**
- Existing chat history not preserved in MongoDB
- Previous sessions in Redis not automatically migrated

---

### Strategy 2: Gradual Migration

**When to use:**
- Production environment
- Want to preserve some existing sessions
- Gradual transition preferred

**Steps:**

1. **Install MongoDB** (as above)

2. **Run application** - both Redis and MongoDB active
   - New sessions → MongoDB
   - Old Redis sessions → still accessible via Redis

3. **Optional: Migrate specific sessions**

   Create a migration script `migrate_sessions.py`:
   
   ```python
   import asyncio
   from app.services.mongodb_service import get_mongodb_service
   from app.services.chat_persistence_service import get_chat_persistence_service
   from app.services.session_service import SessionService
   
   async def migrate_session(redis_session, persistence_service):
       """Migrate a single session from Redis to MongoDB"""
       # Create session in MongoDB
       session = await persistence_service.create_session(
           user_id=redis_session.user_id,
           project_id=redis_session.project_id,
           title=redis_session.session_name
       )
       
       # If you have Redis message history, migrate messages
       # (This depends on your Redis message storage implementation)
       # ...
       
       return session.id
   
   async def main():
       # Initialize services
       from app.core.dependencies import initialize_mongodb
       await initialize_mongodb()
       
       persistence = get_chat_persistence_service()
       
       # Get Redis sessions (using your existing SessionService)
       redis_service = SessionService(redis_url="redis://localhost:6379")
       sessions = redis_service.list_sessions(limit=1000)
       
       migrated_count = 0
       for redis_session in sessions:
           try:
               await migrate_session(redis_session, persistence)
               migrated_count += 1
               print(f"Migrated session: {redis_session.session_id}")
           except Exception as e:
               print(f"Failed to migrate {redis_session.session_id}: {e}")
       
       print(f"\nMigration complete: {migrated_count}/{len(sessions)} sessions migrated")
   
   if __name__ == "__main__":
       asyncio.run(main())
   ```

4. **Run migration script:**
   ```bash
   python migrate_sessions.py
   ```

---

### Strategy 3: Dual Operation

**When to use:**
- High-availability production system
- Zero downtime requirement
- Need time to validate MongoDB performance

**Steps:**

1. Deploy MongoDB alongside existing Redis
2. Configure both storage backends
3. **Write to both** - Modify persistence service to write to MongoDB and Redis
4. **Read from MongoDB** - Use MongoDB as primary, Redis as fallback
5. **Monitor and validate** for 1-2 weeks
6. **Phase out Redis** once confidence established

This requires custom code modifications not included in the base implementation.

## Data Persistence Behavior

### What Gets Persisted to MongoDB

✅ **Persisted:**
- Session metadata (title, timestamps, user/project IDs)
- All user messages
- All assistant responses
- Retrieved document sources (metadata + excerpts)
- RAG routing decisions
- Safety analysis results
- Token counts

❌ **Not Persisted to MongoDB:**
- Vector embeddings (stay in Pinecone/Vector Store)
- Full document content (stay in vector store)
- Short-term LLM memory (Redis, optional)
- Temporary computation state

### Vector Store (Unchanged)

The vector store (Pinecone or local) continues to operate independently:
- Document chunking and embedding
- Semantic search
- Retrieved sources

**MongoDB stores references** to retrieved docs, not the embeddings themselves.

## API Changes

### New Endpoints

#### Get Session Messages (Paginated)
```http
GET /api/sessions/{session_id}/messages?page=1&page_size=50&ascending=true
```

Response:
```json
{
  "messages": [
    {
      "id": "msg-abc-123",
      "session_id": "session-abc-123",
      "role": "user",
      "content": "What is the onboarding process?",
      "created_at": "2025-11-14T12:00:00Z"
    },
    {
      "id": "msg-abc-124",
      "session_id": "session-abc-123",
      "role": "assistant",
      "content": "The onboarding process consists of...",
      "sources": [...],
      "routing_info": {...},
      "created_at": "2025-11-14T12:00:05Z"
    }
  ],
  "total_count": 50,
  "page": 1,
  "page_size": 50,
  "has_more": false
}
```

#### Get Recent Messages
```http
GET /api/sessions/{session_id}/messages/recent?limit=10
```

Returns the 10 most recent messages in chronological order.

#### Get Session History Stats
```http
GET /api/sessions/{session_id}/history-stats
```

Response:
```json
{
  "session_id": "session-abc-123",
  "title": "Onboarding Questions",
  "total_messages": 50,
  "user_messages": 25,
  "assistant_messages": 25,
  "total_tokens": 5000,
  "created_at": "2025-11-14T12:00:00Z",
  "updated_at": "2025-11-14T13:30:00Z"
}
```

#### Get Global Stats
```http
GET /api/stats/global
```

Response:
```json
{
  "chat_history": {
    "total_sessions": 100,
    "total_messages": 2500,
    "unique_users": 25,
    "unique_projects": 5
  },
  "rag_system": {
    "documents_loaded": 9,
    "vector_store_type": "Pinecone",
    "embedding_model": "text-embedding-3-small"
  }
}
```

### Modified Endpoints

#### POST /api/chat
Now automatically persists messages to MongoDB:
1. Creates session if doesn't exist
2. Persists user message
3. Generates title on first message
4. Gets RAG response
5. Persists assistant response with metadata

#### POST /api/sessions
Now creates session in MongoDB (was Redis-only before).

#### GET /api/sessions
Returns paginated results from MongoDB with `page` and `page_size` parameters.

#### DELETE /api/sessions/{session_id}
Cascade deletes messages when deleting session.

## Frontend Integration

The frontend automatically works with the new endpoints. New functions available:

```javascript
import { 
  getSessionMessages,
  getRecentMessages,
  getSessionHistoryStats,
  getGlobalStats 
} from './services/api.service';

// Get paginated messages
const result = await getSessionMessages('session-123', {
  page: 1,
  pageSize: 50,
  ascending: true
});

// Get recent messages for context
const recent = await getRecentMessages('session-123', 10);

// Get detailed session stats
const stats = await getSessionHistoryStats('session-123');

// Get global statistics
const globalStats = await getGlobalStats();
```

## Performance Considerations

### Indexes

The system creates optimal indexes automatically:

1. **Compound Index** on `(session_id, created_at)`:
   - Primary index for message pagination
   - Efficient chronological retrieval
   - Supports both ascending and descending sorts

2. **Single Indexes**:
   - `session_id` - fast session filtering
   - `created_at` - time-based queries
   - `updated_at` - recent sessions

### Pagination Best Practices

✅ **Recommended:**
- Use `page_size` of 20-50 for UI display
- Use `ascending=true` for chronological chat display
- Use `getRecentMessages(limit=10)` for quick context loading

❌ **Avoid:**
- Very large page sizes (>200)
- Loading all messages at once for long sessions
- Frequent polling without caching

### Scalability

**Expected Performance:**
- Sessions: Handles 100K+ sessions efficiently
- Messages: Handles millions of messages with proper indexing
- Queries: <100ms for paginated message retrieval
- Inserts: <50ms for message persistence

**Optimization Tips:**
1. Use pagination, not full message loads
2. Implement client-side caching for recently viewed messages
3. Consider TTL indexes for automatic cleanup (90+ days)
4. Monitor MongoDB index usage with `db.collection.stats()`

## Monitoring & Maintenance

### Health Checks

The `/api/health` endpoint now includes MongoDB status:

```bash
curl http://localhost:8000/api/health
```

### MongoDB Monitoring

#### Check collection stats:
```javascript
use knowra_chatbot
db.chat_sessions.stats()
db.chat_messages.stats()
```

#### Check index usage:
```javascript
db.chat_messages.aggregate([
  { $indexStats: {} }
])
```

#### Monitor slow queries:
```javascript
db.setProfilingLevel(1, { slowms: 100 })
db.system.profile.find().limit(10).sort({ ts: -1 })
```

### Backup & Recovery

#### Backup:
```bash
mongodump --uri="mongodb://localhost:27017" --db=knowra_chatbot --out=/backup/$(date +%Y%m%d)
```

#### Restore:
```bash
mongorestore --uri="mongodb://localhost:27017" --db=knowra_chatbot /backup/20251114/knowra_chatbot
```

#### Automated Backups (cron):
```bash
# Daily at 2 AM
0 2 * * * mongodump --uri="mongodb://localhost:27017" --db=knowra_chatbot --out=/backup/$(date +\%Y\%m\%d)
```

### Cleanup & Maintenance

#### Optional TTL Index for Auto-Cleanup

To automatically delete messages older than 90 days:

```javascript
db.chat_messages.createIndex(
  { "created_at": 1 },
  { expireAfterSeconds: 7776000 }  // 90 days
)
```

#### Manual Cleanup

Delete sessions older than 6 months:
```javascript
const sixMonthsAgo = new Date();
sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);

// Find old sessions
const oldSessions = db.chat_sessions.find({
  updated_at: { $lt: sixMonthsAgo }
});

// Delete messages and sessions
oldSessions.forEach(session => {
  db.chat_messages.deleteMany({ session_id: session._id });
  db.chat_sessions.deleteOne({ _id: session._id });
});
```

## Troubleshooting

### MongoDB Connection Fails

**Error:** `Failed to connect to MongoDB: ServerSelectionTimeoutError`

**Solutions:**
1. Verify MongoDB is running: `docker ps` or `systemctl status mongod`
2. Check connection string in `.env`
3. Ensure network connectivity: `telnet localhost 27017`
4. Check firewall settings

### Application Starts Without MongoDB

The application gracefully degrades if MongoDB is unavailable:
- Chat endpoints will return errors
- RAG functionality continues to work
- Sessions not persisted

Check logs for:
```
⚠️  MongoDB initialization failed: ...
   Continuing without persistent chat history...
```

### Slow Message Retrieval

1. **Check indexes exist:**
   ```javascript
   db.chat_messages.getIndexes()
   ```

2. **Verify index is used:**
   ```javascript
   db.chat_messages.find({ session_id: "session-123" })
     .sort({ created_at: 1 })
     .explain("executionStats")
   ```

3. **Look for:**
   - `"stage": "IXSCAN"` (good - using index)
   - `"stage": "COLLSCAN"` (bad - full collection scan)

### Title Generation Fails

If session titles remain "New Conversation":
1. Check LLM service is initialized
2. Verify OpenAI API key is valid
3. Check logs for title generation errors
4. Titles fall back to first message excerpt if LLM fails

## Rollback Plan

If you need to roll back to Redis-only:

1. **Stop the application**

2. **Revert code changes:**
   ```bash
   git revert <commit-hash>
   ```

3. **Remove MongoDB dependencies:**
   ```bash
   pip uninstall motor pymongo
   ```

4. **Update `.env` - remove MongoDB settings**

5. **Restart application**

Note: MongoDB data remains intact and can be re-enabled later.

## Support & Resources

- **MongoDB Documentation**: https://docs.mongodb.com/
- **Motor Documentation**: https://motor.readthedocs.io/
- **Pymongo Documentation**: https://pymongo.readthedocs.io/
- **MongoDB Atlas**: https://cloud.mongodb.com/

## Summary

The MongoDB integration provides:

✅ **Persistent chat history** across restarts
✅ **Efficient pagination** for long conversations  
✅ **Rich metadata** (sources, routing, safety)
✅ **Scalable architecture** for production use
✅ **Automatic title generation** for sessions
✅ **Session statistics** and analytics
✅ **Backward compatibility** with existing Redis sessions

The vector store and RAG pipeline remain **unchanged** - MongoDB only handles chat persistence, not document embeddings.

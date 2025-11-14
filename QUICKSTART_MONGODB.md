# MongoDB Chat History - Quick Start Guide

## 🚀 Get Started in 5 Minutes

This guide will get your MongoDB-backed chat history up and running quickly.

## Prerequisites

- Python 3.8+ with pip
- Node.js 16+ (for frontend)
- Docker (recommended) or MongoDB installed locally

## Step 1: Install Dependencies

```bash
cd backend
pip install motor==3.6.0 pymongo==4.10.1
```

## Step 2: Start MongoDB

### Option A: Docker (Recommended)

```bash
docker run -d \
  --name knowra-mongodb \
  -p 27017:27017 \
  -v mongodb_data:/data/db \
  mongo:7.0
```

Verify it's running:
```bash
docker ps | grep mongodb
```

### Option B: MongoDB Atlas (Free Cloud)

1. Go to https://cloud.mongodb.com
2. Create free cluster (takes 3-5 minutes)
3. Click "Connect" → "Connect your application"
4. Copy connection string

## Step 3: Configure Environment

Create/update `.env` in project root:

```bash
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=knowra_chatbot

# Or for MongoDB Atlas:
# MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority

# Existing configuration...
OPENAI_API_KEY=your_key_here
# ... rest of your config
```

## Step 4: Start Backend

```bash
cd backend
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Look for these log messages:**

```
📦 Initializing MongoDB...
✅ MongoDB initialized successfully
Created indexes on chat_sessions collection
Created indexes on chat_messages collection
✅ RAG Service initialized successfully
```

✅ **Success!** MongoDB is connected and ready.

⚠️ **Warning shown?**
```
⚠️  MongoDB initialization failed: ...
   Continuing without persistent chat history...
```
This means MongoDB couldn't connect, but the app will still work (without persistence). Check Step 2.

## Step 5: Start Frontend

```bash
cd frontend
npm install  # if first time
npm run dev
```

Open http://localhost:5173

## Step 6: Test It Out

### Test 1: Send a Message

1. Open the frontend
2. Type: "What is the onboarding process?"
3. Send message

**Expected:** You get a response, and the message is saved to MongoDB.

### Test 2: Verify in MongoDB

```bash
# Connect to MongoDB
mongosh mongodb://localhost:27017

# Switch to database
use knowra_chatbot

# Check sessions
db.chat_sessions.find().pretty()

# Check messages
db.chat_messages.find().pretty()
```

You should see your session and messages!

### Test 3: Check Session Title

Refresh the page or check your session list. The session should have an auto-generated title like:

- "Onboarding Process Questions"
- "What Is Onboarding"

(Title generated from your first message using LLM)

### Test 4: Load Conversation History

1. Send a few more messages
2. Refresh the page
3. Select the session from the session list

**Expected:** All your messages load from MongoDB, including sources and metadata.

## Verify Everything Works

### Backend Health Check

```bash
curl http://localhost:8000/api/health
```

**Expected output:**
```json
{
  "status": "healthy",
  "stats": {
    "documents_loaded": 9,
    "vector_store_type": "Pinecone",
    "enhanced_pipeline": true
  }
}
```

### Get Sessions

```bash
curl http://localhost:8000/api/sessions
```

**Expected:** List of your sessions with titles and message counts.

### Get Messages for a Session

```bash
# Replace {session_id} with actual ID from previous response
curl http://localhost:8000/api/sessions/{session_id}/messages?page=1&page_size=10
```

**Expected:** Paginated list of messages with sources and metadata.

## Common Issues & Fixes

### Issue: MongoDB connection timeout

```
ServerSelectionTimeoutError: localhost:27017
```

**Fix:**
```bash
# Check if MongoDB is running
docker ps | grep mongodb

# If not running, start it
docker start knowra-mongodb

# Or restart
docker restart knowra-mongodb
```

### Issue: Port 27017 already in use

```
Error starting userland proxy: listen tcp4 0.0.0.0:27017: bind: address already in use
```

**Fix:**
```bash
# Find what's using the port
lsof -i :27017

# Stop existing MongoDB
brew services stop mongodb-community
# OR
sudo systemctl stop mongod

# Then start Docker MongoDB again
docker start knowra-mongodb
```

### Issue: Title generation not working

Session stays as "New Conversation"

**Possible causes:**
1. LLM service initialization failed
2. OpenAI API key invalid
3. First message too short

**Check logs** for errors like:
```
⚠️  Failed to generate session title: ...
```

Titles will fall back to first message excerpt if LLM fails - this is expected behavior.

### Issue: Messages not persisting

**Check:**
1. MongoDB is running: `docker ps | grep mongodb`
2. `.env` has correct `MONGODB_URL`
3. Backend logs show: `✅ MongoDB initialized successfully`

If you see:
```
⚠️  MongoDB initialization failed
```

MongoDB isn't connected. Check Step 2 & 3.

## What's Next?

### View Data in MongoDB Compass (GUI)

1. Download: https://www.mongodb.com/products/compass
2. Connect to: `mongodb://localhost:27017`
3. Navigate to `knowra_chatbot` database
4. Explore `chat_sessions` and `chat_messages` collections

### Load More Messages (Pagination)

Frontend automatically paginates. To load more manually:

```bash
curl "http://localhost:8000/api/sessions/{session_id}/messages?page=2&page_size=20"
```

### Get Session Statistics

```bash
curl http://localhost:8000/api/sessions/{session_id}/history-stats
```

Returns:
- Total messages
- User vs assistant message counts
- Total tokens used
- Created/updated timestamps

### Get Global Statistics

```bash
curl http://localhost:8000/api/stats/global
```

Returns:
- Total sessions across all users
- Total messages
- Unique users and projects
- RAG system stats

## Understanding the Data Structure

### Session Document
```javascript
{
  _id: "session-abc-123",           // Auto-generated
  user_id: null,                    // Optional
  project_id: "default",            // Default project
  title: "Onboarding Questions",    // LLM-generated
  message_count: 6,                 // Auto-updated
  created_at: ISODate("..."),       // Auto-set
  updated_at: ISODate("...")        // Auto-updated
}
```

### Message Document
```javascript
{
  _id: "msg-xyz-789",
  session_id: "session-abc-123",    // Links to session
  role: "assistant",                // "user" or "assistant"
  content: "The onboarding...",     // Message text
  sources: [                        // RAG retrieved docs
    {
      id: "doc_123",
      score: 0.89,
      text: "Relevant excerpt...",
      metadata: {
        source: "01_ONBOARDING_GUIDE.md"
      }
    }
  ],
  routing_info: {                   // RAG routing decision
    decision: "kb_and_memory",
    confidence: 0.85
  },
  safety_info: {                    // Safety analysis
    level: "safe"
  },
  tokens: 150,                      // Token count
  created_at: ISODate("...")
}
```

## Performance Tips

### Pagination Best Practices

✅ **Good:**
```javascript
// Load 20-50 messages at a time
getSessionMessages(sessionId, { page: 1, pageSize: 50 });

// Get recent context (last 10)
getRecentMessages(sessionId, 10);
```

❌ **Avoid:**
```javascript
// Don't load all messages at once
getSessionMessages(sessionId, { page: 1, pageSize: 10000 });
```

### Efficient Session Loading

✅ **Good:**
```javascript
// List sessions with reasonable page size
listSessions({ limit: 50 });

// Filter by project
listSessions({ projectId: "onboarding", limit: 50 });
```

## Monitoring

### Check MongoDB Status

```bash
# Via Docker
docker logs knowra-mongodb

# Via mongosh
mongosh mongodb://localhost:27017
> db.serverStatus()
```

### Check Collection Sizes

```javascript
use knowra_chatbot

// Document counts
db.chat_sessions.countDocuments()
db.chat_messages.countDocuments()

// Storage sizes
db.chat_sessions.stats()
db.chat_messages.stats()
```

### Check Index Usage

```javascript
// View indexes
db.chat_messages.getIndexes()

// Check if query uses index
db.chat_messages.find({ session_id: "session-123" })
  .sort({ created_at: 1 })
  .explain("executionStats")
```

Look for `"stage": "IXSCAN"` - this means the index is being used.

## Backup Your Data

### Quick Backup

```bash
# Backup entire database
mongodump --uri="mongodb://localhost:27017" --db=knowra_chatbot --out=./backup

# Restore from backup
mongorestore --uri="mongodb://localhost:27017" --db=knowra_chatbot ./backup/knowra_chatbot
```

### Automated Daily Backups

Add to crontab:
```bash
# Daily at 2 AM
0 2 * * * mongodump --uri="mongodb://localhost:27017" --db=knowra_chatbot --out=/backups/$(date +\%Y\%m\%d)
```

## Getting Help

### Logs to Check

1. **Backend logs** - Console where you ran `uvicorn`
2. **MongoDB logs** - `docker logs knowra-mongodb`
3. **Frontend logs** - Browser console (F12)

### Useful Debug Commands

```bash
# Check MongoDB is accessible
telnet localhost 27017

# Check backend health
curl http://localhost:8000/api/health

# Check if collections exist
mongosh mongodb://localhost:27017/knowra_chatbot --eval "db.getCollectionNames()"

# View recent errors in MongoDB
docker logs knowra-mongodb --tail 50
```

### Documentation

- **Full Implementation Guide**: [MONGODB_IMPLEMENTATION.md](./MONGODB_IMPLEMENTATION.md)
- **Migration Guide**: [MONGODB_MIGRATION_GUIDE.md](./MONGODB_MIGRATION_GUIDE.md)
- **API Docs**: http://localhost:8000/docs (when backend running)

## Success Checklist

✅ MongoDB running (Docker or Atlas)  
✅ Backend shows "MongoDB initialized successfully"  
✅ Can send messages and get responses  
✅ Messages visible in MongoDB  
✅ Session titles auto-generated  
✅ Can reload page and see conversation history  
✅ Health check returns "healthy"  

**All checked?** You're all set! 🎉

## What Changed from Before?

**Before:** 
- Sessions stored in Redis (lost on restart)
- No persistent message history
- Manual session names

**Now:**
- Sessions stored in MongoDB (persistent)
- Full message history with metadata
- Auto-generated session titles
- Pagination for long conversations
- Statistics and analytics

**What stayed the same:**
- Vector store (Pinecone/Local) - unchanged
- RAG pipeline - unchanged
- Frontend UI - works as before (now with persistence)
- API compatibility - existing clients still work

## Next Steps

1. **Customize titles** - Edit `title_generator.py` for different title styles
2. **Add user management** - Set `user_id` when creating sessions
3. **Implement multi-project** - Use `project_id` to separate different knowledge bases
4. **Enable TTL** - Auto-delete old messages after X days
5. **Add analytics** - Use `get_global_stats()` for insights
6. **Setup monitoring** - Add MongoDB metrics to your dashboards

Happy chatting! 💬

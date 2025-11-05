# RCA Copilot - Worker Architecture Setup Guide

## 🏗️ Architecture Overview

The RCA Copilot now uses a **worker-based architecture** with three components running in parallel:

1. **Redis Server** - Message queue for communication
2. **API Server** (`main.py`) - Receives HTTP requests and queues them
3. **Worker** (`worker.py`) - Processes queries and stores results

```
┌─────────┐      ┌─────────┐      ┌──────────┐      ┌────────┐
│ Client  │─────>│   API   │─────>│  Redis   │─────>│ Worker │
│ (curl)  │      │ main.py │      │  Queue   │      │worker.py│
└─────────┘      └─────────┘      └──────────┘      └────────┘
     │                                                     │
     │              ┌──────────┐                          │
     └─────────────>│  Redis   │<─────────────────────────┘
                    │ Results  │
                    └──────────┘
```

---

## 📦 Step 1: Install Dependencies

### Install Redis

**Windows:**
```powershell
# Download Redis for Windows from:
# https://github.com/microsoftarchive/redis/releases
# Or use WSL/Docker
```

**Using Docker (Recommended for Windows):**
```bash
docker run -d -p 6379:6379 --name redis redis:latest
```

**Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# Mac
brew install redis
brew services start redis
```

### Install Python Dependencies

```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install redis fastapi uvicorn python-dotenv langchain langchain-openai pandas
```

---

## 🚀 Step 2: Start the Services

You need **THREE separate terminals** running in parallel:

### Terminal 1: Redis Server

```bash
# If Redis is not running as a service, start it:
redis-server

# Or if using Docker:
docker start redis
```

**Verify Redis is running:**
```bash
redis-cli ping
# Should return: PONG
```

---

### Terminal 2: API Server

```bash
cd C:\Users\INADKAK\OneDrive - ABB\Desktop\RCA_Copilot_Kraken
python main.py
```

**Expected Output:**
```
======================================================================
🚀 Starting RCA Copilot API Server
======================================================================
INFO:     Started server process
✓ Connected to Redis successfully
API ready to accept requests
Make sure the worker is running: python worker.py
======================================================================
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

### Terminal 3: Worker Process

```bash
cd C:\Users\INADKAK\OneDrive - ABB\Desktop\RCA_Copilot_Kraken
python worker.py
```

**Expected Output:**
```
======================================================================
🔧 Initializing RCA Copilot Worker
======================================================================
Connecting to Redis...
✓ Connected to Redis successfully
Initializing RCA Copilot Master Agent...
======================================================================
Available Agents:
  • Sensor Data Agent: Analyzes time-series sensor data...
  • Operator Agent: Searches operator incident reports...
  • Maintenance Agent: Searches maintenance logs...
======================================================================
✓ Master Agent initialized successfully
======================================================================
✓ Worker initialized and ready to process queries
======================================================================
🚀 Worker started - Listening for queries...
Press Ctrl+C to stop
```

---

## 📡 Step 3: Send Requests

### Using cURL

**Submit a Query:**
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"What caused the temperature spike in MCH_003?\"}"
```

**Response:**
```json
{
  "query_id": "abc-123-def-456",
  "query": "What caused the temperature spike in MCH_003?",
  "status": "queued",
  "message": "Query queued for processing. Use /result/abc-123-def-456 to get results."
}
```

**Get the Result:**
```bash
curl http://localhost:8000/result/abc-123-def-456
```

---

### Using Python

```python
import requests
import time

# Submit query
response = requests.post(
    "http://localhost:8000/ask",
    json={"query": "What caused the temperature spike in MCH_003?"}
)
query_id = response.json()["query_id"]
print(f"Query ID: {query_id}")

# Wait a moment for processing
time.sleep(2)

# Get result
result = requests.get(f"http://localhost:8000/result/{query_id}")
print(result.json()["rca_report"])
```

---

## 📊 Step 4: Watch the Logs

### API Logs (Terminal 2)
You'll see:
```
INFO - Received query [ID: abc-123]: What caused...
INFO - Query abc-123 added to processing queue
```

### Worker Logs (Terminal 3) - **THIS IS WHERE YOU SEE PROCESSING!**
You'll see the full RCA workflow:
```
📥 Received query from queue: abc-123
======================================================================
🔍 Processing Query ID: abc-123
Query: What caused the temperature spike in MCH_003?
======================================================================
Invoking Master Agent for query abc-123...
======================================================================
Master Agent Processing Query: What caused...
======================================================================
Routing Decision: {'sensor_agent': True, 'operator_agent': True...}
→ Invoking Sensor Data Agent...
✓ Sensor Agent completed (15 records)
→ Invoking Operator Agent...
✓ Operator Agent completed (3 documents)
→ Invoking Maintenance Agent...
✓ Maintenance Agent completed (5 documents)
→ Generating RCA Report using LLM Chain...
✓ RCA Report generated
Query processed successfully
✓ Query abc-123 completed successfully
======================================================================
✓ Query abc-123 processing complete
======================================================================
✓ Query abc-123 completed and result stored
```

---

## 🔍 Monitoring and Debugging

### Check Redis Queue Status

```bash
# Check pending queries
redis-cli LLEN rca_queue

# View queued items
redis-cli LRANGE rca_queue 0 -1

# View all stored results
redis-cli KEYS "result:*"

# Get a specific result
redis-cli GET "result:abc-123-def"
```

### Health Check

```bash
curl http://localhost:8000/health
```

**Response:**
```json
{
  "status": "healthy",
  "message": "RCA Copilot API is running",
  "redis": "connected",
  "pending_queries": 0
}
```

### List All Queries

```bash
curl http://localhost:8000/results
```

---

## 🛠️ Troubleshooting

### Issue: "Redis not connected"
```bash
# Check if Redis is running
redis-cli ping

# Start Redis
redis-server  # or: brew services start redis
```

### Issue: Worker not processing
1. Check that worker.py is running in Terminal 3
2. Check Redis queue: `redis-cli LLEN rca_queue`
3. Look for errors in worker logs

### Issue: Query stays in "queued" status
- Worker is not running or crashed
- Check Terminal 3 for error messages
- Restart worker: `python worker.py`

---

## 📝 Query Status Flow

1. **queued** - Query submitted to Redis, waiting for worker
2. **processing** - Worker picked up the query and is processing
3. **completed** - RCA report generated successfully
4. **failed** - Error occurred during processing (check error field)

---

## 🎯 Complete Workflow Example

```bash
# Terminal 1: Start Redis
redis-server

# Terminal 2: Start API
python main.py

# Terminal 3: Start Worker  
python worker.py

# Terminal 4: Submit query
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "Analyze MCH_003 failure"}'

# Copy query_id from response, then get result
curl http://localhost:8000/result/<query_id>
```

**Watch Terminal 3 (Worker) for all the detailed processing logs!** 🔍📊

---

## 🔄 Stopping the Services

1. Press `Ctrl+C` in Terminal 3 (Worker) - Worker will gracefully shutdown
2. Press `Ctrl+C` in Terminal 2 (API) - API server stops
3. Press `Ctrl+C` in Terminal 1 (Redis) or `brew services stop redis`

---

## 💡 Benefits of Worker Architecture

✅ **Non-blocking API** - API responds immediately, doesn't wait for processing
✅ **Scalable** - Run multiple workers for parallel processing
✅ **Resilient** - If worker crashes, queries remain in queue
✅ **Observable** - See detailed logs in worker terminal
✅ **Separation of Concerns** - API handles HTTP, Worker handles AI processing

---

## 📚 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check + queue status |
| `/ask` | POST | Submit RCA query |
| `/result/{query_id}` | GET | Get RCA report |
| `/results` | GET | List all queries |
| `/docs` | GET | Interactive API docs |

---

**Now you can see ALL the processing logs in the Worker terminal!** 🎉

# Quick Start Guide - RCA Copilot with Worker Architecture

## Overview
This guide will help you start the RCA Copilot system with the worker architecture using Docker Redis.

## Prerequisites
✅ Docker Desktop installed and running
✅ Redis container running on Docker
✅ Python virtual environment set up (`pa-hackathon-venv`)
✅ Azure OpenAI credentials configured in `.env`

## Step-by-Step Startup

### 1. Verify Docker Redis is Running

Open PowerShell and check:
```powershell
docker ps | Select-String redis
```

If not running, start it:
```powershell
# Find your Redis container
docker ps -a | Select-String redis

# Start the container (replace <container-id>)
docker start <container-id>
```

Or create a new one:
```powershell
docker run -d --name redis-pa-hackathon -p 6379:6379 redis:latest
```

### 2. Open Three Terminal Windows

You'll need three separate PowerShell terminals:
- **Terminal 1**: Redis logs (optional, for monitoring)
- **Terminal 2**: FastAPI server
- **Terminal 3**: Worker process

---

## Terminal 1: Redis Monitoring (Optional)

```powershell
# Monitor Redis logs
docker logs -f <container-id>

# Or monitor Redis commands
docker exec -it <container-id> redis-cli -n 1 MONITOR
```

---

## Terminal 2: Start API Server

```powershell
# Navigate to project directory
cd "C:\Users\INADKAK\OneDrive - ABB\Desktop\RCA_Copilot_Kraken"

# Activate virtual environment
.\pa-hackathon-venv\Scripts\activate

# Start FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
✓ Connected to Redis successfully
✓ Project initialized: PA_Hackathon
INFO:     Application startup complete.
```

**API is ready when you see**: `Application startup complete`

**Test API Health:**
```powershell
curl http://localhost:8000/health
```

---

## Terminal 3: Start Worker Process

```powershell
# Navigate to project directory
cd "C:\Users\INADKAK\OneDrive - ABB\Desktop\RCA_Copilot_Kraken"

# Activate virtual environment
.\pa-hackathon-venv\Scripts\activate

# Start worker
python worker.py
```

**Expected Output:**
```
======================================================================
🔧 Initializing RCA Copilot Worker
======================================================================
Connecting to Redis (Docker container)...
✓ Connected to Redis successfully (Docker container)
✓ Using Redis database 1 for PA_Hackathon
✓ Project namespace: PA_Hackathon
Initializing RCA Copilot Master Agent...
======================================================================
Available Agents:
  • sensor_agent: Analyzes sensor data and time-series measurements
  • operator_agent: Reviews operator reports and human observations
  • maintenance_agent: Examines maintenance logs and service records
======================================================================
✓ Master Agent initialized successfully
======================================================================
✓ Worker initialized and ready to process queries
======================================================================
🚀 Worker started - Listening for queries...
Press Ctrl+C to stop
```

**Worker is ready when you see**: `Worker started - Listening for queries...`

---

## Testing the System

### Option 1: Using test_api.py Script

```powershell
# In a new terminal or use Terminal 1
cd "C:\Users\INADKAK\OneDrive - ABB\Desktop\RCA_Copilot_Kraken"
.\pa-hackathon-venv\Scripts\activate

# Run test script
python test_api.py
```

### Option 2: Using curl Commands

**Submit a Query:**
```powershell
curl -X POST http://localhost:8000/ask `
  -H "Content-Type: application/json" `
  -d '{"query": "What is causing the temperature sensor to read high values?"}'
```

**Response:**
```json
{
  "query_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "status": "queued",
  "message": "Query submitted for processing"
}
```

**Check Worker Terminal (Terminal 3):**
You should see detailed processing logs:
```
📥 Received query from queue: a1b2c3d4...
======================================================================
🔍 Processing Query ID: a1b2c3d4...
Query: What is causing the temperature sensor to read high values?
======================================================================
Invoking Master Agent for query a1b2c3d4...
[... detailed agent processing logs ...]
✓ Query a1b2c3d4... completed successfully
======================================================================
✓ Query a1b2c3d4... processing complete
======================================================================
```

**Retrieve Result (wait 10-20 seconds):**
```powershell
curl http://localhost:8000/result/a1b2c3d4-5678-90ab-cdef-1234567890ab
```

**Response:**
```json
{
  "query_id": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "query": "What is causing the temperature sensor to read high values?",
  "status": "completed",
  "rca_report": "Root cause: Sensor calibration drift. Evidence: Consistent +5°C offset across readings. Action: Recalibrate sensor immediately. Prevention: Implement quarterly calibration schedule.",
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

### Option 3: Using Browser (Interactive API Docs)

1. Open browser: http://localhost:8000/docs
2. Click on "POST /ask"
3. Click "Try it out"
4. Enter query in request body:
   ```json
   {
     "query": "What is causing the vibration increase?"
   }
   ```
5. Click "Execute"
6. Copy the `query_id` from response
7. Click on "GET /result/{query_id}"
8. Enter your `query_id`
9. Click "Execute" to see results

---

## Monitoring and Debugging

### Check API Health
```powershell
curl http://localhost:8000/health
```

**Healthy Response:**
```json
{
  "status": "healthy",
  "redis": "connected",
  "project": "PA_Hackathon",
  "queue_length": 0
}
```

### List All Results
```powershell
curl http://localhost:8000/results
```

### View Redis Keys (in Redis CLI)
```powershell
docker exec -it <container-id> redis-cli -n 1 KEYS "pa_hackathon:*"
```

### Check Queue Length
```powershell
docker exec -it <container-id> redis-cli -n 1 LLEN pa_hackathon:rca_queue
```

---

## Stopping the System

### Stop Worker (Terminal 3)
Press `Ctrl+C` in the worker terminal

**Output:**
```
⚠ Received shutdown signal
Worker stopped
Worker shutdown complete
```

### Stop API Server (Terminal 2)
Press `Ctrl+C` in the API terminal

**Output:**
```
INFO:     Shutting down
INFO:     Finished server process
```

### Stop Redis (Optional)
```powershell
docker stop <container-id>
```

---

## Troubleshooting

### Problem: API won't start - "Redis connection failed"

**Check:**
1. Is Docker running? `docker ps`
2. Is Redis container running? Look for redis in `docker ps` output
3. Start Redis: `docker start <container-id>`

### Problem: Worker won't start - "Failed to connect to Redis"

**Solution:**
Same as above. Ensure Docker Redis is running on localhost:6379

### Problem: Query status stays "queued", never completes

**Check:**
1. Is worker running? Check Terminal 3
2. Check worker logs for errors
3. Verify Azure OpenAI credentials in `.env`

### Problem: Worker shows "Master Agent initialization failed"

**Solution:**
1. Check `.env` file exists with:
   ```
   AZURE_OPENAI_ENDPOINT=your_endpoint
   AZURE_OPENAI_API_KEY=your_key
   ```
2. Verify credentials are valid
3. Check network connection

### Problem: API returns 404 on /result/query_id

**Check:**
1. Did worker complete processing? Check Terminal 3 logs
2. Is query_id correct?
3. Did result expire? (TTL is 1 hour)

---

## System Architecture Recap

```
┌─────────────┐
│   Client    │ ← (1) POST /ask with query
│ (Browser/   │
│   curl)     │ → (5) GET /result/{query_id}
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│   FastAPI Server (Terminal 2)       │
│   - Receives HTTP requests          │
│   - Generates query_id              │
│   - Pushes to Redis queue          │
│   - Returns results from Redis     │
└───────────┬─────────────────────────┘
            │
            ▼
     ┌──────────────┐
     │    Redis     │ ← Database 1
     │  (Docker)    │   Namespace: pa_hackathon:
     │  Terminal 1  │   - Queue: pa_hackathon:rca_queue
     └──────┬───────┘   - Results: pa_hackathon:result:{id}
            │
            ▼
┌─────────────────────────────────────┐
│   Worker Process (Terminal 3)       │
│   - Monitors Redis queue (BLPOP)   │
│   - Processes RCA queries          │
│   - Shows detailed logs            │
│   - Stores results in Redis        │
└─────────────────────────────────────┘
```

---

## Key Features

✅ **Non-blocking API**: Returns immediately with query_id
✅ **Visible Processing**: All logs visible in worker terminal
✅ **Namespace Isolation**: Uses `pa_hackathon:` prefix and db 1
✅ **Concise Reports**: RCA reports are 3-4 sentences
✅ **Centralized Config**: All Redis settings in `redis_config.py`
✅ **Structured Logging**: No print statements, only logger
✅ **Auto-expiry**: Results expire after 1 hour

---

## Next Steps

1. ✅ Start all three terminals
2. ✅ Submit test queries
3. ✅ Verify worker processes correctly
4. ✅ Check results are concise (3-4 sentences)
5. ✅ Monitor Redis keys for proper namespacing

For more details:
- **Redis Configuration**: See `REDIS_SETUP.md`
- **API Documentation**: See `API_GUIDE.md`
- **Worker Details**: See `WORKER_SETUP.md`

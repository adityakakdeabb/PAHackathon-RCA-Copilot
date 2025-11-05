# Redis Setup Guide - PA_Hackathon Project

## Overview
This project uses a Docker Redis container with dedicated namespace isolation for the PA_Hackathon project. All Redis keys are prefixed with `pa_hackathon:` and stored in database 1.

## Redis Configuration

### Connection Details
- **Host**: localhost
- **Port**: 6379
- **Database**: 1 (dedicated for PA_Hackathon)
- **Namespace Prefix**: `pa_hackathon:`

### Key Structure
All Redis keys use the centralized configuration from `redis_config.py`:

```python
# Queue for incoming RCA queries
QUEUE_NAME = 'pa_hackathon:rca_queue'

# Result storage prefix
RESULT_PREFIX = 'pa_hackathon:result:'

# Project identifier
PROJECT_KEY = 'pa_hackathon:project:name'

# Result TTL (1 hour)
RESULT_TTL = 3600
```

## Docker Redis Setup

### 1. Check if Redis Container is Running
```powershell
docker ps | Select-String redis
```

### 2. Start Existing Container (if stopped)
```powershell
docker start <container-id>
```

### 3. Create New Redis Container (if needed)
```powershell
docker run -d --name redis-pa-hackathon -p 6379:6379 redis:latest
```

### 4. Verify Connection
```powershell
docker exec -it <container-id> redis-cli ping
```
Expected output: `PONG`

### 5. Check Database 1 Keys
```powershell
docker exec -it <container-id> redis-cli -n 1 KEYS "pa_hackathon:*"
```

## Architecture

### Three-Terminal Setup

**Terminal 1 - Redis (Docker)**
```powershell
# View Redis logs
docker logs -f <container-id>
```

**Terminal 2 - API Server**
```powershell
# Activate virtual environment
.\pa-hackathon-venv\Scripts\activate

# Start FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 3 - Worker Process**
```powershell
# Activate virtual environment
.\pa-hackathon-venv\Scripts\activate

# Start worker
python worker.py
```

## Workflow

1. **Submit Query** → API receives request at `/ask`
2. **Queue Storage** → API stores query in Redis queue: `pa_hackathon:rca_queue`
3. **Worker Polling** → Worker monitors queue using BLPOP
4. **Processing** → Worker executes full RCA workflow (visible in worker terminal)
5. **Result Storage** → Worker stores result in Redis: `pa_hackathon:result:{query_id}`
6. **Result Retrieval** → Client fetches result from `/result/{query_id}`

## Key Features

### Namespace Isolation
- Database 1 dedicated to PA_Hackathon
- All keys prefixed with `pa_hackathon:`
- Easy cleanup: `redis-cli -n 1 FLUSHDB`
- No interference with other projects

### Result Management
- Automatic TTL: Results expire after 1 hour
- Pattern matching: List all results with `KEYS pa_hackathon:result:*`
- JSON storage: Results stored as JSON strings

### Centralized Configuration
All Redis settings managed in `redis_config.py`:
- Connection parameters
- Key naming conventions
- TTL values
- Database selection

## Testing

### 1. Test API Health
```powershell
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "redis": "connected",
  "project": "PA_Hackathon",
  "queue_length": 0
}
```

### 2. Submit Test Query
```powershell
curl -X POST http://localhost:8000/ask `
  -H "Content-Type: application/json" `
  -d '{"query": "What is causing the temperature spike?"}'
```

Expected response:
```json
{
  "query_id": "abc123...",
  "status": "queued",
  "message": "Query submitted for processing"
}
```

### 3. Check Worker Logs
Worker terminal should show:
```
📥 Received query from queue: abc123...
🔍 Processing Query ID: abc123...
Query: What is causing the temperature spike?
======================================================================
[Master Agent processing logs...]
✓ Query abc123... completed successfully
```

### 4. Retrieve Result
```powershell
curl http://localhost:8000/result/abc123...
```

## Redis Commands Reference

### Check Queue Length
```bash
redis-cli -n 1 LLEN pa_hackathon:rca_queue
```

### View All Results
```bash
redis-cli -n 1 KEYS "pa_hackathon:result:*"
```

### Get Specific Result
```bash
redis-cli -n 1 GET pa_hackathon:result:<query_id>
```

### Clear All PA_Hackathon Data
```bash
redis-cli -n 1 FLUSHDB
```

### Monitor Redis Operations
```bash
redis-cli -n 1 MONITOR
```

## Troubleshooting

### Problem: Worker can't connect to Redis
**Solution:**
1. Check if Docker container is running: `docker ps`
2. Verify port mapping: Container should expose 6379:6379
3. Check firewall settings allowing localhost:6379

### Problem: Keys not found
**Solution:**
1. Verify database selection: Must use `-n 1` in redis-cli
2. Check key prefix: All keys start with `pa_hackathon:`
3. Check TTL: Results expire after 3600 seconds

### Problem: Queue not processing
**Solution:**
1. Confirm worker is running: Check Terminal 3
2. Verify queue name: `pa_hackathon:rca_queue`
3. Check worker logs for errors

### Problem: Results missing
**Solution:**
1. Check result TTL: Results expire after 1 hour
2. Verify query_id correctness
3. Check worker completion: Worker logs should show "✓ Query completed"

## Migration from Old Setup

If migrating from hardcoded Redis keys:

### Old Key Pattern → New Key Pattern
- `rca_queue` → `pa_hackathon:rca_queue`
- `result:{id}` → `pa_hackathon:result:{id}`
- `project:name` → `pa_hackathon:project:name`
- Database 0 → Database 1

### Migration Steps
1. Stop API and Worker
2. Update `redis_config.py` if needed
3. Clear old data (optional): `redis-cli FLUSHDB`
4. Restart API and Worker
5. Verify connection using `/health` endpoint

## Environment Variables (Optional)

You can override Redis connection via environment variables:

```powershell
$env:REDIS_HOST = "localhost"
$env:REDIS_PORT = "6379"
$env:REDIS_DB = "1"
```

Update `redis_config.py` to read from env vars:
```python
import os

REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_DB = int(os.getenv('REDIS_DB', '1'))
```

## Best Practices

1. **Always use centralized config**: Import `redis_config` module
2. **Never hardcode keys**: Use constants from `redis_config.py`
3. **Monitor queue length**: Check `/health` endpoint regularly
4. **Clean up old results**: Consider reducing TTL for testing
5. **Use separate databases**: Keep projects isolated
6. **Namespace everything**: All keys start with project prefix

## References

- FastAPI Docs: https://fastapi.tiangolo.com/
- Redis Python: https://redis-py.readthedocs.io/
- Docker Redis: https://hub.docker.com/_/redis

# RCA Copilot API - Quick Start Guide

## 🚀 Starting the API Server

```bash
python main.py
```

The API will start on `http://localhost:8000`

## 📡 API Endpoints

### 1. Health Check
**GET** `/health`

Check if the API is running and the Master Agent is initialized.

```bash
curl http://localhost:8000/health
```

### 2. Submit a Query (Ask)
**POST** `/ask`

Submit an RCA query for processing.

**Request Body:**
```json
{
  "query": "What caused the temperature spike in MCH_003?"
}
```

**Response:**
```json
{
  "query_id": "550e8400-e29b-41d4-a716-446655440000",
  "query": "What caused the temperature spike in MCH_003?",
  "status": "accepted",
  "message": "Query accepted and processed. Use /result/{query_id} to get results."
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What caused the temperature spike in MCH_003?"}'
```

### 3. Get Result
**GET** `/result/{query_id}`

Retrieve the RCA report for a previously submitted query.

**Response:**
```json
{
  "query_id": "550e8400-e29b-41d4-a716-446655440000",
  "query": "What caused the temperature spike in MCH_003?",
  "status": "completed",
  "rca_report": "The primary root cause is bearing failure...",
  "error": null,
  "timestamp": "2025-11-05T10:30:45.123456"
}
```

**Example:**
```bash
curl http://localhost:8000/result/550e8400-e29b-41d4-a716-446655440000
```

### 4. List All Results
**GET** `/results`

Get a list of all queries and their statuses.

```bash
curl http://localhost:8000/results
```

## 🧪 Testing the API

### Using Python Script
Run the provided test script:
```bash
python test_api.py
```

### Using PowerShell
```powershell
# Submit a query
$response = Invoke-RestMethod -Uri "http://localhost:8000/ask" -Method Post -ContentType "application/json" -Body '{"query": "What caused the temperature spike?"}'
$queryId = $response.query_id

# Get the result
Invoke-RestMethod -Uri "http://localhost:8000/result/$queryId"
```

### Using curl (Windows)
```bash
# Submit a query
curl -X POST http://localhost:8000/ask -H "Content-Type: application/json" -d "{\"query\": \"What caused the temperature spike?\"}"

# Get result (replace QUERY_ID with the actual ID from above)
curl http://localhost:8000/result/QUERY_ID
```

## 📚 Interactive API Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Open these URLs in your browser to explore and test the API interactively!

## 🔄 Workflow

1. **Start the server**: `python main.py`
2. **Submit a query**: POST to `/ask` with your question
3. **Get query_id**: Save the `query_id` from the response
4. **Retrieve results**: GET from `/result/{query_id}`

## 💡 Example Queries

- "What caused the temperature spike in MCH_003?"
- "Show me all critical sensor alerts from yesterday"
- "What maintenance was performed on machines with vibration issues?"
- "Analyze the root cause of the recent equipment failure"
- "What are the common patterns in operator reports?"

## 🛠️ Status Codes

- `200 OK`: Request successful
- `404 Not Found`: Query ID not found
- `500 Internal Server Error`: Processing error
- `503 Service Unavailable`: Master Agent not initialized

## 📝 Response Statuses

- `processing`: Query is being processed
- `completed`: Query processed successfully
- `failed`: Query processing failed (check error field)

"""
FastAPI Example - REST API for RCA Copilot
Optional API wrapper for the Master Agent
"""
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
from agents.master_agent import MasterAgent

# Get logger for this module
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="RCA Copilot API",
    description="AI-Powered Root Cause Analysis Automation",
    version="1.0.0"
)

# Initialize Master Agent
master_agent = None

class QueryRequest(BaseModel):
    """Request model for RCA queries"""
    query: str
    machine_id: Optional[str] = None
    sensor_type: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    top_k: Optional[int] = 5

class QueryResponse(BaseModel):
    """Response model for RCA queries"""
    success: bool
    query: str
    rca_report: Optional[str] = None
    error: Optional[str] = None
    agent_responses: Optional[Dict[str, Any]] = None

@app.on_event("startup")
async def startup_event():
    """Initialize Master Agent on startup"""
    global master_agent
    logger.info("Initializing RCA Copilot Master Agent...")
    master_agent = MasterAgent()
    logger.info("✓ Master Agent ready")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "RCA Copilot API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agent_initialized": master_agent is not None
    }

@app.get("/agents")
async def get_agents():
    """Get available agents"""
    if master_agent is None:
        raise HTTPException(status_code=503, detail="Master Agent not initialized")
    
    return {
        "agents": master_agent.get_available_agents()
    }

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process an RCA query
    
    Example:
    ```json
    {
        "query": "What caused the temperature spike in MCH_003?",
        "machine_id": "MCH_003",
        "top_k": 5
    }
    ```
    """
    if master_agent is None:
        raise HTTPException(status_code=503, detail="Master Agent not initialized")
    
    try:
        # Build kwargs from optional parameters
        kwargs = {}
        if request.machine_id:
            kwargs['machine_id'] = request.machine_id
        if request.sensor_type:
            kwargs['sensor_type'] = request.sensor_type
        if request.start_date:
            kwargs['start_date'] = request.start_date
        if request.end_date:
            kwargs['end_date'] = request.end_date
        if request.top_k:
            kwargs['top_k'] = request.top_k
        
        # Process query
        result = master_agent.process_query(request.query, **kwargs)
        
        return QueryResponse(
            success=result.get("success", False),
            query=result.get("query", ""),
            rca_report=result.get("rca_report"),
            error=result.get("error"),
            agent_responses=result.get("agent_responses")
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: QueryRequest):
    """
    Simplified chat endpoint - returns only RCA report text
    
    Example:
    ```json
    {
        "query": "Show critical sensor alerts from yesterday"
    }
    ```
    """
    if master_agent is None:
        raise HTTPException(status_code=503, detail="Master Agent not initialized")
    
    try:
        report = master_agent.chat(request.query)
        return {
            "query": request.query,
            "report": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    logger.info("=" * 70)
    logger.info("🚀 Starting RCA Copilot API Server")
    logger.info("=" * 70)
    logger.info("API Documentation: http://localhost:8000/docs")
    logger.info("Health Check: http://localhost:8000/health")
    logger.info("=" * 70)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
